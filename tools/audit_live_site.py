"""Audit public BakAbo storefront links, metadata and analytics snippets."""

from __future__ import annotations

import csv
import re
import ssl
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "live_site_audit"
OUT_CSV = OUT_DIR / "live_pages.csv"
OUT_MD = OUT_DIR / "live_site_audit.md"
OUT_LINKS = OUT_DIR / "live_internal_links.csv"

EXPECTED_GTM = "GTM-PF5Z85KS"
LEGACY_GTM = {"GTM-M4ND7QL", "GT-TWMGQB9"}
BASE_URL = "https://bakabo.club"

PATHS = [
    "/",
    "/collections",
    "/collections/new-arrivals",
    "/collections/bks-hours",
    "/collections/bks-glyph",
    "/collections/bks-marker",
    "/collections/bks-riviera",
    "/collections/bks-pulse",
    "/collections/bks-token",
    "/collections/bks-flag",
    "/collections/bks-folklore",
    "/collections/swimwear",
    "/collections/outerwear",
    "/collections/sneakers",
    "/collections/puffer-jacket",
    "/collections/windbreaker",
    "/collections/backpack",
    "/pages/about",
    "/pages/help-faq",
    "/pages/contact",
    "/policies/shipping-policy",
    "/policies/refund-policy",
    "/policies/privacy-policy",
    "/policies/terms-of-service",
]

DOMAINS = [
    "https://bakabo.club",
    "https://www.bakabo.club",
    "https://account.bakabo.club",
    "https://11628e-2.myshopify.com",
    "https://bakabo.myshopify.com",
]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.meta_description = ""
        self.canonical = ""
        self.links: list[tuple[str, str]] = []
        self._in_title = False
        self._title_parts: list[str] = []
        self._current_link = ""
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "title":
            self._in_title = True
        elif tag.lower() == "meta":
            if attrs_dict.get("name", "").lower() == "description":
                self.meta_description = attrs_dict.get("content", "")
        elif tag.lower() == "link":
            if attrs_dict.get("rel", "").lower() == "canonical":
                self.canonical = attrs_dict.get("href", "")
        elif tag.lower() == "a":
            self._current_link = attrs_dict.get("href", "")
            self._current_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False
            self.title = " ".join("".join(self._title_parts).split())
        elif tag.lower() == "a" and self._current_link:
            text = " ".join("".join(self._current_text).split())
            self.links.append((self._current_link, text[:140]))
            self._current_link = ""
            self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)
        if self._current_link:
            self._current_text.append(data)


def fetch(url: str, verify_ssl: bool = True) -> tuple[int, str, str, str, str]:
    request = Request(
        url,
        headers={
            "User-Agent": "BKS-Live-Audit/1.0 (+https://bakabo.club)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    context = ssl.create_default_context() if verify_ssl else ssl._create_unverified_context()
    try:
        with urlopen(request, timeout=25, context=context) as response:
            status = int(response.status)
            final_url = response.geturl()
            content_type = response.headers.get("content-type", "")
            raw = response.read(1_200_000)
            charset = response.headers.get_content_charset() or "utf-8"
            return status, final_url, content_type, raw.decode(charset, errors="replace"), ""
    except HTTPError as exc:
        raw = exc.read(200_000)
        return int(exc.code), exc.geturl(), exc.headers.get("content-type", ""), raw.decode("utf-8", errors="replace"), ""
    except URLError as exc:
        if verify_ssl and "CERTIFICATE_VERIFY_FAILED" in str(exc):
            status, final_url, content_type, html, error = fetch(url, verify_ssl=False)
            warning = f"SSL_VERIFY_BYPASSED: {exc}"
            return status, final_url, content_type, html, warning if not error else f"{warning} | {error}"
        return 0, url, "", "", f"NETWORK_ERROR: {exc}"
    except Exception as exc:
        return 0, url, "", "", f"ERROR: {exc}"


def analyze_url(url: str) -> tuple[dict[str, str | int], list[dict[str, str]]]:
    status, final_url, content_type, html, error = fetch(url)
    parser = PageParser()
    if "html" in content_type.lower() or html.lstrip().startswith("<"):
        parser.feed(html)

    gtm_ids = sorted(set(re.findall(r"GTM-[A-Z0-9]+", html)))
    ga_ids = sorted(set(re.findall(r"\bG-[A-Z0-9]+\b", html)))
    legacy_gtm = sorted(LEGACY_GTM.intersection(gtm_ids))
    internal_links: list[dict[str, str]] = []
    host = urlparse(BASE_URL).netloc
    for href, text in parser.links:
        absolute = urljoin(final_url, href)
        parsed = urlparse(absolute)
        if parsed.netloc.endswith(host) or parsed.netloc in {"www.bakabo.club", "account.bakabo.club"}:
            internal_links.append({"source": url, "href": absolute.split("#", 1)[0], "text": text})

    row = {
        "url": url,
        "status": status,
        "final_url": final_url,
        "content_type": content_type,
        "title": parser.title,
        "title_chars": len(parser.title),
        "meta_description": parser.meta_description,
        "meta_chars": len(parser.meta_description),
        "canonical": parser.canonical,
        "gtm_ids": ";".join(gtm_ids),
        "expected_gtm": "yes" if EXPECTED_GTM in gtm_ids else "no",
        "legacy_gtm": ";".join(legacy_gtm),
        "ga_ids": ";".join(ga_ids),
        "internal_link_count": len(internal_links),
        "welcome_placeholder": "yes" if "Welcome to our store" in html else "no",
        "error": error,
    }
    return row, internal_links


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    urls = DOMAINS + [urljoin(BASE_URL, path) for path in PATHS]
    rows: list[dict[str, str | int]] = []
    links: list[dict[str, str]] = []
    seen: set[str] = set()

    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        row, page_links = analyze_url(url)
        rows.append(row)
        links.extend(page_links)
        error = f" error={row['error']}" if row["error"] else ""
        print(f"{row['status']} {url} title={row['title'][:60]!r} gtm={row['gtm_ids']}{error}")
        time.sleep(0.8)

    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    unique_links: dict[str, dict[str, str]] = {}
    for link in links:
        unique_links.setdefault(link["href"], link)
    with OUT_LINKS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source", "href", "text"])
        writer.writeheader()
        writer.writerows(unique_links.values())

    ok = sum(1 for row in rows if int(row["status"]) in range(200, 400))
    missing_gtm = [row for row in rows if row["expected_gtm"] == "no" and int(row["status"]) in range(200, 400)]
    legacy = [row for row in rows if row["legacy_gtm"]]
    placeholders = [row for row in rows if row["welcome_placeholder"] == "yes"]
    ssl_warnings = [row for row in rows if str(row["error"]).startswith("SSL_VERIFY_BYPASSED")]
    network_errors = [row for row in rows if row["error"] and not str(row["error"]).startswith("SSL_VERIFY_BYPASSED")]

    md = [
        "# BakAbo Live Site Audit",
        "",
        f"Base URL: `{BASE_URL}`",
        f"Expected GTM: `{EXPECTED_GTM}`",
        "",
        "| Check | Result |",
        "|---|---:|",
        f"| URLs checked | {len(rows)} |",
        f"| HTTP 2xx/3xx | {ok} |",
        f"| Missing expected GTM on live HTML | {len(missing_gtm)} |",
        f"| Legacy GTM present | {len(legacy)} |",
        f"| `Welcome to our store` placeholder present | {len(placeholders)} |",
        f"| SSL verification bypassed by local audit runtime | {len(ssl_warnings)} |",
        f"| Network/tool errors | {len(network_errors)} |",
        f"| Unique internal links collected | {len(unique_links)} |",
        "",
        "## Files",
        "",
        f"- `{OUT_CSV.relative_to(ROOT)}`",
        f"- `{OUT_LINKS.relative_to(ROOT)}`",
    ]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
