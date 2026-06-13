from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


REPORT_FILE = Path("output/daily_web_update.json")
SHEET_FILE = Path("output/daily_web_update_sources.csv")


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sources(settings: Any) -> list[dict[str, str]]:
    store = settings.shopify_public_domain or "bakabo.club"
    return [
        {"name": "Storefront", "kind": "live_site", "url": f"https://{store}", "purpose": "Homepage availability and trust baseline."},
        {"name": "Sitemap", "kind": "live_site", "url": f"https://{store}/sitemap.xml", "purpose": "Product/page discoverability for Google."},
        {"name": "New Arrivals", "kind": "live_site", "url": f"https://{store}/collections/new-arrivals", "purpose": "Primary campaign landing page."},
        {"name": "Contact", "kind": "trust_page", "url": f"https://{store}/pages/contact", "purpose": "Customer contact visibility."},
        {"name": "Shipping Policy", "kind": "trust_page", "url": f"https://{store}/policies/shipping-policy", "purpose": "Shipping disclosure."},
        {"name": "Refund Policy", "kind": "trust_page", "url": f"https://{store}/policies/refund-policy", "purpose": "Returns/refunds disclosure."},
        {"name": "Google Misrepresentation Policy", "kind": "policy", "url": "https://support.google.com/merchants/answer/6150127?hl=it", "purpose": "Official policy baseline."},
    ]


def check_source(source: dict[str, str], *, live: bool) -> dict[str, Any]:
    row: dict[str, Any] = {**source, "status": "not_checked", "http_status": "", "ms": "", "error": "", "checked_at": _now()}
    if not live:
        return row
    started = datetime.now(timezone.utc)
    try:
        response = requests.get(source["url"], timeout=15, headers={"User-Agent": "BKS-Master-Daily-Update/1.0"})
        elapsed = datetime.now(timezone.utc) - started
        row["http_status"] = str(response.status_code)
        row["ms"] = str(int(elapsed.total_seconds() * 1000))
        row["status"] = "pass" if 200 <= response.status_code < 400 else "needs_fix"
        text = response.text[:200000] if "text" in response.headers.get("content-type", "") else ""
        if source["kind"] == "live_site":
            row["gtm_present"] = "GTM-PF5Z85KS" in text
            row["ga4_present"] = "G-" in text or "googletagmanager" in text
        if source["kind"] == "trust_page":
            row["trust_text_present"] = len(text.strip()) > 500
    except requests.RequestException as exc:
        row["status"] = "error"
        row["error"] = f"{type(exc).__name__}: {exc}"
    return row


def _write_sheet(settings: Any, rows: list[dict[str, Any]]) -> str:
    path = settings.root_dir / SHEET_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["name", "kind", "url", "purpose", "status", "http_status", "ms", "gtm_present", "ga4_present", "trust_text_present", "error", "checked_at"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
    return _relative(settings.root_dir, path)


def _load_report(settings: Any) -> dict[str, Any]:
    path = settings.root_dir / REPORT_FILE
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def run(settings: Any, snapshot: dict[str, Any], *, live: bool = False) -> dict[str, Any]:
    rows = [check_source(source, live=live) for source in sources(settings)]
    sheet = _write_sheet(settings, rows)
    next_action = snapshot.get("actions", {}).get("next_action", {})
    report = {
        "summary": {
            "mode": "live" if live else "local_snapshot",
            "checked_at": _now(),
            "sources": len(rows),
            "pass": sum(1 for row in rows if row["status"] == "pass"),
            "needs_fix": sum(1 for row in rows if row["status"] == "needs_fix"),
            "errors": sum(1 for row in rows if row["status"] == "error"),
            "not_checked": sum(1 for row in rows if row["status"] == "not_checked"),
            "sheet": sheet,
            "report": _relative(settings.root_dir, settings.root_dir / REPORT_FILE),
            "next_action": next_action.get("title", ""),
        },
        "sources": rows,
        "next_action": next_action,
        "market": snapshot.get("market", {}).get("summary", {}),
        "weekly": snapshot.get("weekly", {}).get("summary", {}),
    }
    path = settings.root_dir / REPORT_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    existing = _load_report(settings)
    if existing:
        return existing
    return run(settings, snapshot, live=False)
