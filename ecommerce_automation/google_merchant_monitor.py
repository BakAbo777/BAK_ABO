from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any


LIVE_AUDIT = Path("output/live_site_audit/live_pages.csv")
STATE_DOC = Path("00_PROCEDURA/02_STATO_ATTUALE.md")
PRODUCT_EXPORT = Path("output/products_export_updated.csv")

CLAIM_RE = re.compile(
    r"\b("
    r"free|gratis|guarantee|guaranteed|garantito|garanzia|official|ufficiale|"
    r"certified|certificato|miracle|miracolo|cheapest|lowest price|prezzo piu basso|"
    r"discount|sconto|sale|liquidazione"
    r")\b",
    re.IGNORECASE,
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _as_int(value: str) -> int:
    try:
        return int(float(str(value or "0").strip()))
    except ValueError:
        return 0


def _percent(value: float, total: float) -> float:
    if not total:
        return 0.0
    return round((value / total) * 100, 1)


def _state_value(text: str, label: str, default: str = "") -> str:
    pattern = rf"\|\s*{re.escape(label)}\s*\|\s*`?([^`|\n]+)`?\s*\|"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else default


def merchant_state(root_dir: Path, settings: Any) -> dict[str, str]:
    doc = root_dir / STATE_DOC
    text = doc.read_text(encoding="utf-8", errors="ignore") if doc.exists() else ""
    merchant_id = settings.google_merchant_id or _state_value(text, "Merchant Center ID", "5295165689")
    return {
        "account": _state_value(text, "Account", "bakabo.club"),
        "merchant_id": merchant_id,
        "status": settings.google_merchant_status or "suspended",
        "reason": settings.google_merchant_reason or "misrepresentation",
        "local_inventory_missing": _state_value(text, "Dati inventario locale mancanti", "68,3K prodotti, 95,1%"),
        "product_page_unavailable": _state_value(text, "Pagina prodotto non disponibile", "8,39K prodotti, 11,7%"),
        "additional_sample": _state_value(text, "Esempio aggiuntivo", "Taglia mancante"),
        "analytics_account": _state_value(text, "Account Analytics", ""),
        "analytics_property": _state_value(text, "Proprieta selezionata", _state_value(text, "Proprietà selezionata", "")),
        "ga4_property_id": settings.ga4_property_id or _state_value(text, "Property ID visibile", ""),
        "gtm_target": settings.gtm_target or _state_value(text, "Container ID", "GTM-PF5Z85KS"),
    }


def live_tag_diagnostics(root_dir: Path, gtm_target: str) -> dict[str, Any]:
    rows = _read_csv(root_dir / LIVE_AUDIT)
    checked = len(rows)
    http_ok = sum(1 for row in rows if 200 <= _as_int(row.get("status", "")) < 400)
    expected_gtm = sum(1 for row in rows if row.get("expected_gtm", "").lower() == "yes")
    legacy_gtm = sum(1 for row in rows if row.get("legacy_gtm", "").strip())
    ga4_rows = sum(1 for row in rows if row.get("ga_ids", "").strip())
    unique_ga4 = sorted({item for row in rows for item in row.get("ga_ids", "").split(";") if item})

    issue_rows: list[dict[str, str]] = []
    for row in rows:
        issues: list[str] = []
        status = _as_int(row.get("status", ""))
        url = row.get("url", "")
        if status < 200 or status >= 400:
            issues.append("http_not_ok")
        if row.get("expected_gtm", "").lower() != "yes":
            issues.append("missing_expected_gtm")
        if row.get("legacy_gtm", "").strip():
            issues.append("legacy_gtm_present")
        if not row.get("ga_ids", "").strip():
            issues.append("missing_ga4")
        if issues:
            issue_rows.append(
                {
                    "url": url,
                    "status": row.get("status", ""),
                    "gtm_ids": row.get("gtm_ids", ""),
                    "expected_gtm": row.get("expected_gtm", ""),
                    "ga_ids": row.get("ga_ids", ""),
                    "issue": ";".join(issues),
                }
            )

    trust_pages = _trust_pages(rows)
    return {
        "rows": rows,
        "issue_rows": issue_rows,
        "trust_pages": trust_pages,
        "summary": {
            "checked": checked,
            "http_ok": http_ok,
            "http_ok_percent": _percent(http_ok, checked),
            "expected_gtm": expected_gtm,
            "expected_gtm_percent": _percent(expected_gtm, checked),
            "legacy_gtm": legacy_gtm,
            "ga4_rows": ga4_rows,
            "ga4_percent": _percent(ga4_rows, checked),
            "unique_ga4": ";".join(unique_ga4),
            "gtm_target": gtm_target,
        },
    }


def _trust_pages(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    checks = (
        ("About", "/pages/about", "Identity and business explanation"),
        ("Contact", "/pages/contact", "Visible customer contact path"),
        ("FAQ / Help", "/pages/help-faq", "Pre-purchase support information"),
        ("Shipping policy", "/policies/shipping-policy", "Shipping terms"),
        ("Refund policy", "/policies/refund-policy", "Returns and refunds"),
        ("Privacy policy", "/policies/privacy-policy", "Data usage disclosure"),
        ("Terms of service", "/policies/terms-of-service", "Merchant terms"),
    )
    result: list[dict[str, str]] = []
    for label, fragment, purpose in checks:
        match = next((row for row in rows if fragment in row.get("url", "")), None)
        status = _as_int(match.get("status", "")) if match else 0
        ok = bool(match and 200 <= status < 400)
        result.append(
            {
                "check": label,
                "status": "pass" if ok else "fail",
                "url": match.get("url", f"https://bakabo.club{fragment}") if match else f"https://bakabo.club{fragment}",
                "http_status": str(status or ""),
                "purpose": purpose,
                "next_action": "OK" if ok else "Publish page, fix URL, or remove the broken navigation target.",
            }
        )
    return result


def product_feed_diagnostics(root_dir: Path) -> dict[str, Any]:
    rows = _read_csv(root_dir / PRODUCT_EXPORT)
    product_rows = [row for row in rows if row.get("Title", "").strip()]
    required_fields = (
        "Handle",
        "Title",
        "Body (HTML)",
        "Vendor",
        "Google Shopping / Google Product Category",
        "Google Shopping / Gender",
        "Google Shopping / Age Group",
        "Google Shopping / Condition",
        "Google Shopping / Custom Product",
    )
    missing_rows: list[dict[str, str]] = []
    claim_rows: list[dict[str, str]] = []
    tag_rows: list[dict[str, str]] = []

    for row in product_rows:
        missing = [field for field in required_fields if not row.get(field, "").strip()]
        if missing:
            missing_rows.append(
                {
                    "handle": row.get("Handle", ""),
                    "title": row.get("Title", ""),
                    "issue": "missing_required_fields",
                    "detail": ";".join(missing),
                }
            )

        claim_text = " ".join(
            row.get(field, "")
            for field in ("Title", "Tags", "SEO Title", "SEO Description", "Body (HTML)")
        )
        claim_match = CLAIM_RE.search(claim_text)
        if claim_match:
            claim_rows.append(
                {
                    "handle": row.get("Handle", ""),
                    "title": row.get("Title", ""),
                    "issue": "review_claim",
                    "detail": claim_match.group(0),
                }
            )

        tags = row.get("Tags", "")
        tag_checks = {
            "brand": "brand:" in tags,
            "collection": "collection:" in tags,
            "drop": "drop:" in tags,
            "status": "status:" in tags,
            "made_to_order": "made-to-order" in tags,
            "ai_art": "ai-art" in tags,
        }
        missing_tags = [key for key, ok in tag_checks.items() if not ok]
        if missing_tags:
            tag_rows.append(
                {
                    "handle": row.get("Handle", ""),
                    "title": row.get("Title", ""),
                    "issue": "missing_structured_tags",
                    "detail": ";".join(missing_tags),
                }
            )

    return {
        "summary": {
            "csv": str(PRODUCT_EXPORT),
            "rows_total": len(rows),
            "product_rows": len(product_rows),
            "missing_required": len(missing_rows),
            "claim_review": len(claim_rows),
            "missing_tags": len(tag_rows),
        },
        "missing_rows": missing_rows[:80],
        "claim_rows": claim_rows[:80],
        "tag_rows": tag_rows[:80],
    }


def issue_bars(merchant: dict[str, str], live: dict[str, Any], feed: dict[str, Any]) -> list[dict[str, Any]]:
    live_summary = live["summary"]
    feed_summary = feed["summary"]
    product_rows = max(int(feed_summary.get("product_rows", 0)), 1)
    return [
        {"label": "HTTP OK", "value": live_summary["http_ok"], "total": live_summary["checked"], "percent": live_summary["http_ok_percent"]},
        {"label": "GTM target", "value": live_summary["expected_gtm"], "total": live_summary["checked"], "percent": live_summary["expected_gtm_percent"]},
        {"label": "GA4 coverage", "value": live_summary["ga4_rows"], "total": live_summary["checked"], "percent": live_summary["ga4_percent"]},
        {"label": "Feed fields OK", "value": product_rows - feed_summary["missing_required"], "total": product_rows, "percent": _percent(product_rows - feed_summary["missing_required"], product_rows)},
        {"label": "Local inventory missing", "value": merchant["local_inventory_missing"], "total": "Merchant", "percent": 95.1},
        {"label": "Product page unavailable", "value": merchant["product_page_unavailable"], "total": "Merchant", "percent": 11.7},
    ]


def remediation_actions(live: dict[str, Any], feed: dict[str, Any]) -> list[dict[str, str]]:
    trust_fail = [row for row in live["trust_pages"] if row["status"] != "pass"]
    tag_summary = live["summary"]
    feed_summary = feed["summary"]
    actions = [
        {
            "priority": "P0",
            "area": "Misrepresentation",
            "status": "needs_fix" if trust_fail else "pass",
            "action": "Fix trust pages before appeal",
            "detail": "Publish About and FAQ/help pages or remove broken links. Keep contact, shipping, refund, privacy and terms visible.",
            "verification": "All trust pages return HTTP 2xx/3xx in live_site_audit.",
        },
        {
            "priority": "P0",
            "area": "Merchant feed",
            "status": "manual_pending",
            "action": "Clean stale products from Google Merchant feed",
            "detail": "Remove deleted/unavailable products, resync Shopify feed, then wait for Merchant diagnostics to refresh.",
            "verification": "Merchant Center no longer reports product page unavailable/local inventory residue.",
        },
        {
            "priority": "P1",
            "area": "Copy claims",
            "status": "needs_review" if feed_summary["claim_review"] else "pass",
            "action": "Remove misleading claims from product copy",
            "detail": "Avoid official/certified/free/guaranteed/discount claims unless they are provable on the landing page.",
            "verification": "Product copy scanner returns zero high-risk claim tokens.",
        },
        {
            "priority": "P1",
            "area": "Tags",
            "status": "needs_fix" if tag_summary["expected_gtm_percent"] < 95 or tag_summary["ga4_percent"] < 95 or tag_summary["legacy_gtm"] else "pass",
            "action": "Verify GTM and GA4 tags",
            "detail": "Use one target GTM and keep GA4 firing consistently. Account login subdomain can be monitored separately.",
            "verification": "GTM and GA4 coverage stay above 95%, legacy GTM stays zero.",
        },
        {
            "priority": "P2",
            "area": "Product data",
            "status": "needs_fix" if feed_summary["missing_required"] else "pass",
            "action": "Complete Google Shopping attributes",
            "detail": "Product rows need category, gender, age group, condition and custom-product attributes.",
            "verification": "Product feed scanner returns zero missing required fields on product rows.",
        },
    ]
    return actions


def write_matrix(root_dir: Path, actions: list[dict[str, str]]) -> str:
    path = root_dir / "output" / "google_merchant_analytics_matrix.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(actions[0].keys()))
        writer.writeheader()
        writer.writerows(actions)
    return _relative(root_dir, path)


def payload(settings: Any) -> dict[str, Any]:
    root_dir = settings.root_dir
    merchant = merchant_state(root_dir, settings)
    live = live_tag_diagnostics(root_dir, merchant["gtm_target"])
    feed = product_feed_diagnostics(root_dir)
    actions = remediation_actions(live, feed)
    matrix = write_matrix(root_dir, actions)
    blocker_count = sum(1 for row in actions if row["priority"] == "P0" and row["status"] != "pass")
    pass_count = sum(1 for row in actions if row["status"] == "pass")
    return {
        "merchant": merchant,
        "summary": {
            "status": merchant["status"],
            "reason": merchant["reason"],
            "merchant_id": merchant["merchant_id"],
            "blockers": blocker_count,
            "passes": pass_count,
            "actions": len(actions),
            "matrix": matrix,
        },
        "charts": issue_bars(merchant, live, feed),
        "tag_summary": live["summary"],
        "tag_issues": live["issue_rows"],
        "trust_pages": live["trust_pages"],
        "feed": feed,
        "actions": actions,
        "policy_sources": [
            {
                "label": "Google Merchant misrepresentation policy",
                "url": "https://support.google.com/merchants/answer/6150127?hl=it",
            }
        ],
    }
