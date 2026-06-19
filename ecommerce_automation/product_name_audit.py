from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from typing import Any

import requests
import urllib3

AUDIT_CSV = Path("output/product_name_audit.csv")
BAKABO_STORE_DOMAIN = "bakabo.club"

TYPO_FIXES: tuple[tuple[str, str], ...] = (
    ("on linr", "online"),
    ("on line", "online"),
    ("bak abo", "BakAbo"),
    ("bakabo", "BakAbo"),
    ("bks studio studio", "BKS Studio"),
)

EXPECTED_COLLECTIONS = ("Hours", "Glyph", "Marker", "Riviera", "Pulse", "Token", "Flag", "Origin")
EXPECTED_PREFIXES = ("BKS", "BakAbo")
EXPECTED_MARKER_PATTERN = re.compile(r"\b(BKS|BakAbo)\b", flags=re.IGNORECASE)
DECORATIVE_SYMBOL_PATTERN = re.compile(r"[™®©★☆◆◇●○■□▲△▶▷✓✔✦✧]")
VARIATION_SELECTOR_PATTERN = re.compile("[\ufe0e\ufe0f\u200d]")
EMOJI_PATTERN = re.compile(
    "["
    "\U0001f1e6-\U0001f1ff"
    "\U0001f300-\U0001f5ff"
    "\U0001f600-\U0001f64f"
    "\U0001f680-\U0001f6ff"
    "\U0001f700-\U0001f77f"
    "\U0001f780-\U0001f7ff"
    "\U0001f800-\U0001f8ff"
    "\U0001f900-\U0001f9ff"
    "\U0001fa00-\U0001fa6f"
    "\U0001fa70-\U0001faff"
    "\u2600-\u27bf"
    "]+",
    flags=re.UNICODE,
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _title_from_handle(handle: str) -> str:
    words = [part for part in re.split(r"[-_]+", handle or "") if part]
    return " ".join(word.upper() if word.lower() == "bks" else word.capitalize() for word in words)


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip()).lower()


def _suggest_title(title: str, handle: str) -> str:
    suggestion = re.sub(r"\s+", " ", (title or "").strip())
    suggestion = EMOJI_PATTERN.sub("", suggestion).strip()
    suggestion = DECORATIVE_SYMBOL_PATTERN.sub("", suggestion).strip()
    suggestion = VARIATION_SELECTOR_PATTERN.sub("", suggestion).strip()
    for bad, good in TYPO_FIXES:
        suggestion = re.sub(re.escape(bad), good, suggestion, flags=re.IGNORECASE)
    suggestion = re.sub(r"\bBks\b", "BKS", suggestion)
    suggestion = re.sub(r"\bBKS\s+BKS\b", "BKS", suggestion)
    suggestion = re.sub(r"\s+([,.;:])", r"\1", suggestion)
    suggestion = re.sub(r"(?<=\S)(\()", r" \1", suggestion)
    suggestion = re.sub(r"([)\]])(?=\S)", r"\1 ", suggestion)
    suggestion = re.sub(r"\s+", " ", suggestion).strip()
    if not suggestion and handle:
        suggestion = _title_from_handle(handle)
    return suggestion


def _issues(row: dict[str, Any], duplicate_titles: Counter[str], duplicate_handles: Counter[str]) -> tuple[str, str, str]:
    handle = str(row.get("handle", "") or "").strip()
    title = str(row.get("title", "") or "").strip()
    collection = str(row.get("bks_collection", "") or "").strip()
    status = str(row.get("status", "") or "").strip()
    issues: list[str] = []
    severity = "pass"

    def mark(level: str) -> None:
        nonlocal severity
        if level == "needs_fix" or severity == "pass":
            severity = level

    if not handle:
        issues.append("missing_handle")
    if not title:
        issues.append("missing_title")
        mark("needs_fix")
    if title and not EXPECTED_MARKER_PATTERN.search(title):
        issues.append("missing_bks_marker")
        mark("needs_review")
    if title and DECORATIVE_SYMBOL_PATTERN.search(title):
        issues.append("decorative_symbol_in_title")
        mark("needs_fix")
    if title and re.search(r"\b(copy|test|draft|sample|untitled)\b", title, flags=re.IGNORECASE):
        issues.append("draft_word_in_title")
        mark("needs_fix")
    if title and re.search(r"\s{2,}", title):
        issues.append("double_spaces")
    if title and re.search(r"[!]", title):
        issues.append("exclamation_mark")
    if title and EMOJI_PATTERN.search(title):
        issues.append("emoji_or_symbol_in_title")
        mark("needs_fix")
    if title and any(bad in title.lower() for bad, _ in TYPO_FIXES):
        issues.append("known_typo")
        mark("needs_fix")
    if collection and collection not in EXPECTED_COLLECTIONS:
        issues.append("unknown_collection")
        mark("needs_review")
    if collection and title and collection.lower() not in title.lower():
        issues.append("collection_not_in_title")
    if handle and title:
        handle_tokens = {part for part in re.split(r"[-_]+", handle.lower()) if len(part) > 2}
        title_tokens = set(re.findall(r"[a-z0-9]+", title.lower()))
        if handle_tokens and len(handle_tokens & title_tokens) < max(1, min(3, len(handle_tokens) // 2)):
            issues.append("handle_title_mismatch")
            mark("needs_review")
    if duplicate_titles[_normalized(title)] > 1 and title:
        issues.append("duplicate_title")
        mark("needs_review")
    if duplicate_handles[_normalized(handle)] > 1 and handle:
        issues.append("duplicate_handle")
        mark("needs_fix")
    if status.lower() in {"archived", "draft"}:
        issues.append(f"shopify_status_{status.lower()}")

    return severity if issues else "pass", ";".join(issues) if issues else "ok", _suggest_title(title, handle)


def audit_rows(products: list[dict[str, Any]]) -> list[dict[str, str]]:
    titles = Counter(_normalized(str(row.get("title", ""))) for row in products if str(row.get("title", "")).strip())
    handles = Counter(_normalized(str(row.get("handle", ""))) for row in products if str(row.get("handle", "")).strip())
    rows: list[dict[str, str]] = []
    for row in products:
        severity, issues, suggestion = _issues(row, titles, handles)
        rows.append(
            {
                "status": severity,
                "issues": issues,
                "handle": str(row.get("handle", "") or ""),
                "title": str(row.get("title", "") or ""),
                "suggested_title": suggestion,
                "collection": str(row.get("bks_collection", "") or ""),
                "source_status": str(row.get("status", "") or ""),
                "shopify_product_id": str(row.get("shopify_product_id", "") or ""),
                "printify_product_id": str(row.get("printify_product_id", "") or ""),
            }
        )
    rows.sort(key=lambda item: (item["status"] == "pass", item["collection"], item["title"]))
    return rows


def _from_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = list(csv.DictReader(path.open("r", encoding="utf-8-sig", newline="")))
    products: dict[str, dict[str, Any]] = {}
    for row in rows:
        handle = (row.get("Handle") or row.get("handle") or "").strip()
        title = (row.get("Title") or row.get("title") or "").strip()
        if not handle:
            continue
        current = products.setdefault(
            handle,
            {
                "handle": handle,
                "title": title,
                "bks_collection": row.get("BKS Collection (product.metafields.bks.collection)", "") or "",
                "status": row.get("Status", "") or "",
                "shopify_product_id": "",
                "printify_product_id": "",
            },
        )
        if title and not current.get("title"):
            current["title"] = title
    return list(products.values())


def _from_live_shopify(root_dir: Path) -> list[dict[str, Any]]:
    path = root_dir / "output" / "live_shopify_products.csv"
    if not path.exists():
        return []
    rows = list(csv.DictReader(path.open("r", encoding="utf-8-sig", newline="")))
    return [
        {
            "handle": row.get("handle", ""),
            "title": row.get("title", ""),
            "bks_collection": row.get("bks_collection", ""),
            "status": row.get("status", ""),
            "shopify_product_id": row.get("shopify_product_id", ""),
            "printify_product_id": "",
        }
        for row in rows
    ]

def _from_public_shopify(settings: Any) -> list[dict[str, Any]]:
    domain = str(getattr(settings, "primary_domain", "") or getattr(settings, "shopify_public_domain", "") or BAKABO_STORE_DOMAIN)
    domain = domain.replace("https://", "").replace("http://", "").strip("/")
    if not domain:
        return []
    url = f"https://{domain}/products.json?limit=250"
    try:
        response = requests.get(url, timeout=30, headers={"User-Agent": "BKS-Master-Product-Name-Audit/1.0"})
    except requests.exceptions.SSLError:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(url, timeout=30, verify=False, headers={"User-Agent": "BKS-Master-Product-Name-Audit/1.0"})
    except requests.RequestException:
        return []
    if not response.ok:
        return []
    try:
        products = response.json().get("products", [])
    except ValueError:
        return []
    return [
        {
            "handle": product.get("handle", ""),
            "title": product.get("title", ""),
            "bks_collection": "",
            "status": "online_public",
            "shopify_product_id": str(product.get("id", "") or ""),
            "printify_product_id": "",
        }
        for product in products
        if isinstance(product, dict)
    ]


def payload(settings: Any, *, products: list[dict[str, Any]] | None = None, live: bool = False) -> dict[str, Any]:
    source = "live_shopify"
    product_rows = products if products is not None else (_from_public_shopify(settings) if live else _from_live_shopify(settings.root_dir))
    if live:
        source = "public_shopify_online"
    if not product_rows:
        source = "active_csv"
        candidates = [
            settings.root_dir / "collezioni_csv" / "collezione 12_06_2026_SHOPIFY_IMPORT_READY_SEO_TAGS_READY.csv",
            settings.root_dir / "collezioni_csv" / "collezione 12_06_2026_SHOPIFY_IMPORT_READY.csv",
            settings.root_dir / "collezioni_csv" / "collezione_12_06_2026_VERIFIED.csv",
        ]
        for candidate in candidates:
            product_rows = _from_csv(candidate)
            if product_rows:
                break

    rows = audit_rows(product_rows)
    path = settings.root_dir / AUDIT_CSV
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["status", "issues", "handle", "title", "suggested_title", "collection", "source_status", "shopify_product_id", "printify_product_id"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in rows])

    return {
        "summary": {
            "source": source,
            "products": len(rows),
            "pass": sum(1 for row in rows if row["status"] == "pass"),
            "needs_review": sum(1 for row in rows if row["status"] == "needs_review"),
            "needs_fix": sum(1 for row in rows if row["status"] == "needs_fix"),
            "sheet": _relative(settings.root_dir, path),
            "status": "needs_fix" if any(row["status"] == "needs_fix" for row in rows) else ("needs_review" if any(row["status"] == "needs_review" for row in rows) else "pass"),
        },
        "rows": rows[:250],
    }
