from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any


LIVE_AUDIT = Path("output/live_site_audit/live_pages.csv")
STATE_DOC = Path("00_PROCEDURA/02_STATO_ATTUALE.md")
PRODUCT_EXPORT = Path("output/products_export_updated.csv")
COUNTRY_POLICY_MATRIX = Path("output/merchant_country_policy_matrix.csv")

SCREENSHOT_ISSUES: tuple[dict[str, str], ...] = (
    {
        "issue": "local_inventory_missing",
        "merchant_label": "Dati di inventario locale mancanti",
        "impact": "65.6K products / 91%",
        "status": "needs_fix",
        "first_action": "Disable local inventory ads/free local listings unless BKS has physical-store inventory, or upload a local inventory feed with id, store_code, availability and quantity.",
    },
    {
        "issue": "product_page_unavailable",
        "merchant_label": "Pagina del prodotto non disponibile",
        "impact": "13.2K products / 18.3%",
        "status": "needs_fix",
        "first_action": "Remove stale products from Merchant, resync Shopify feed, verify each product link returns the product page on desktop and mobile.",
    },
    {
        "issue": "missing_size",
        "merchant_label": "Taglia mancante",
        "impact": "23.5K products",
        "status": "needs_fix",
        "first_action": "Populate size variant/metafields and expose the size guide on every product page.",
    },
    {
        "issue": "missing_color",
        "merchant_label": "Colore mancante",
        "impact": "7.51K products",
        "status": "needs_fix",
        "first_action": "Populate color variants/metafields and make color visible on landing pages.",
    },
    {
        "issue": "missing_gender",
        "merchant_label": "Genere mancante",
        "impact": "6.58K products",
        "status": "needs_fix",
        "first_action": "Normalize Google Shopping gender to male, female or unisex where applicable.",
    },
    {
        "issue": "missing_age_group",
        "merchant_label": "Eta mancante",
        "impact": "6.47K products",
        "status": "needs_fix",
        "first_action": "Normalize Google Shopping age_group to adult for current BKS apparel unless a child product is explicitly created.",
    },
    {
        "issue": "korea_business_registration",
        "merchant_label": "Numero di registrazione dell'attivita coreano mancante",
        "impact": "24 products",
        "status": "manual_pending",
        "first_action": "If South Korea remains a target country, add the required business registration data; otherwise pause Korea until configured.",
    },
)

COUNTRY_COLUMNS: tuple[dict[str, str], ...] = (
    {"country": "Italy", "code": "IT", "included": "Included / Italy", "price": "Price / Italy", "return_policy": "standard-eu"},
    {"country": "United States", "code": "US", "included": "Included / United States", "price": "Price / United States", "return_policy": "standard-us"},
    {"country": "South Korea", "code": "KR", "included": "Included / Corea del Sud", "price": "Price / Corea del Sud", "return_policy": "requires-business-registration-review"},
    {"country": "International", "code": "INTL", "included": "Included / International", "price": "Price / International", "return_policy": "international-default"},
    {"country": "India", "code": "IN", "included": "Included / India", "price": "Price / India", "return_policy": "not-configured-in-current-csv"},
)

APPAREL_HINTS = (
    "apparel",
    "clothing",
    "shirt",
    "shorts",
    "pants",
    "swimwear",
    "dress",
    "hoodie",
    "windbreaker",
    "sneakers",
    "shoes",
    "flip-flop",
    "slipper",
    "bag",
    "backpack",
)

VALID_GENDERS = {"male", "female", "unisex"}
VALID_AGE_GROUPS = {"newborn", "infant", "toddler", "kids", "adult"}

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
        "local_inventory_missing": _state_value(text, "Dati inventario locale mancanti", "65,6K prodotti, 91%"),
        "product_page_unavailable": _state_value(text, "Pagina prodotto non disponibile", "13,2K prodotti, 18,3%"),
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


def _clean(value: str) -> str:
    return str(value or "").strip()


def _lower(value: str) -> str:
    return _clean(value).lower()


def _is_truthy(value: str) -> bool:
    return _lower(value) in {"true", "yes", "1", "included", "si", "sì"}


def _product_context(row: dict[str, str]) -> str:
    fields = (
        "Product Category",
        "Type",
        "Tags",
        "Title",
        "Handle",
        "Google Shopping / Google Product Category",
        "Google Product Category (product.metafields.custom.google_product_category)",
    )
    return " ".join(_lower(row.get(field, "")) for field in fields)


def _is_apparel_like(row: dict[str, str]) -> bool:
    context = _product_context(row)
    return any(hint in context for hint in APPAREL_HINTS)


def _option_value(row: dict[str, str], names: tuple[str, ...]) -> str:
    for index in (1, 2, 3):
        option_name = _lower(row.get(f"Option{index} Name", ""))
        if any(name in option_name for name in names):
            return _clean(row.get(f"Option{index} Value", ""))
    return ""


def _first_nonempty(row: dict[str, str], fields: tuple[str, ...]) -> str:
    for field in fields:
        value = _clean(row.get(field, ""))
        if value:
            return value
    return ""


def _size_value(row: dict[str, str]) -> str:
    return _option_value(row, ("size", "taglia")) or _first_nonempty(
        row,
        (
            "Size (product.metafields.shopify.size)",
            "Shoe size (product.metafields.shopify.shoe-size)",
            "Accessory size (product.metafields.shopify.accessory-size)",
        ),
    )


def _color_value(row: dict[str, str]) -> str:
    return _option_value(row, ("color", "colour", "colore")) or _first_nonempty(
        row,
        ("Color (product.metafields.shopify.color-pattern)",),
    )


def _gender_value(row: dict[str, str]) -> str:
    return _first_nonempty(
        row,
        (
            "Google Shopping / Gender",
            "Target gender (product.metafields.shopify.target-gender)",
        ),
    )


def _age_value(row: dict[str, str]) -> str:
    return _first_nonempty(
        row,
        (
            "Google Shopping / Age Group",
            "Age group (product.metafields.shopify.age-group)",
        ),
    )


def _country_policy_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    product_rows = [row for row in rows if row.get("Title", "").strip()]
    result: list[dict[str, str]] = []
    for country in COUNTRY_COLUMNS:
        included_field = country["included"]
        price_field = country["price"]
        has_columns = any(included_field in row or price_field in row for row in product_rows)
        included_count = sum(1 for row in product_rows if _is_truthy(row.get(included_field, "")))
        price_count = sum(1 for row in product_rows if _clean(row.get(price_field, "")))
        status = "pass" if has_columns and included_count and price_count else "needs_config"
        if country["code"] == "IN" and not has_columns:
            status = "not_enabled"
        if country["code"] == "KR" and included_count:
            status = "manual_pending"
        result.append(
            {
                "country": country["country"],
                "code": country["code"],
                "status": status,
                "included_products": str(included_count),
                "priced_products": str(price_count),
                "shipping_source": price_field if has_columns else "missing_column",
                "return_policy_label": country["return_policy"],
                "next_action": (
                    "OK: keep checkout, product page and Merchant feed consistent."
                    if status == "pass"
                    else "Configure country shipping/returns in Shopify and Merchant, or remove this country from active destinations."
                ),
            }
        )
    return result


def write_country_policy_matrix(root_dir: Path, rows: list[dict[str, str]]) -> str:
    path = root_dir / COUNTRY_POLICY_MATRIX
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["country", "code", "status", "included_products", "priced_products", "shipping_source", "return_policy_label", "next_action"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in rows])
    return _relative(root_dir, path)


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
    attribute_rows: list[dict[str, str]] = []

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

        if _is_apparel_like(row):
            attr_missing: list[str] = []
            size = _size_value(row)
            color = _color_value(row)
            gender = _gender_value(row)
            age_group = _age_value(row)
            if not size:
                attr_missing.append("size")
            if not color:
                attr_missing.append("color")
            if _lower(gender) not in VALID_GENDERS:
                attr_missing.append("gender")
            if _lower(age_group) not in VALID_AGE_GROUPS:
                attr_missing.append("age_group")
            if attr_missing:
                attribute_rows.append(
                    {
                        "handle": row.get("Handle", ""),
                        "title": row.get("Title", ""),
                        "issue": "missing_or_nonstandard_apparel_attributes",
                        "detail": ";".join(attr_missing),
                        "size": size,
                        "color": color,
                        "gender": gender,
                        "age_group": age_group,
                    }
                )

    country_rows = _country_policy_rows(product_rows)

    return {
        "summary": {
            "csv": str(PRODUCT_EXPORT),
            "rows_total": len(rows),
            "product_rows": len(product_rows),
            "missing_required": len(missing_rows),
            "claim_review": len(claim_rows),
            "missing_tags": len(tag_rows),
            "attribute_issues": len(attribute_rows),
            "missing_size": sum(1 for row in attribute_rows if "size" in row["detail"].split(";")),
            "missing_color": sum(1 for row in attribute_rows if "color" in row["detail"].split(";")),
            "missing_gender": sum(1 for row in attribute_rows if "gender" in row["detail"].split(";")),
            "missing_age_group": sum(1 for row in attribute_rows if "age_group" in row["detail"].split(";")),
            "country_needs_config": sum(1 for row in country_rows if row["status"] in {"needs_config", "manual_pending"}),
        },
        "missing_rows": missing_rows[:80],
        "claim_rows": claim_rows[:80],
        "tag_rows": tag_rows[:80],
        "attribute_rows": attribute_rows[:100],
        "country_rows": country_rows,
    }


def issue_bars(merchant: dict[str, str], live: dict[str, Any], feed: dict[str, Any]) -> list[dict[str, Any]]:
    live_summary = live["summary"]
    feed_summary = feed["summary"]
    product_rows = max(int(feed_summary.get("product_rows", 0)), 1)
    attribute_issues = int(feed_summary.get("attribute_issues", 0) or 0)
    country_needs_config = int(feed_summary.get("country_needs_config", 0) or 0)
    return [
        {"label": "HTTP OK", "value": live_summary["http_ok"], "total": live_summary["checked"], "percent": live_summary["http_ok_percent"]},
        {"label": "GTM target", "value": live_summary["expected_gtm"], "total": live_summary["checked"], "percent": live_summary["expected_gtm_percent"]},
        {"label": "GA4 coverage", "value": live_summary["ga4_rows"], "total": live_summary["checked"], "percent": live_summary["ga4_percent"]},
        {"label": "Feed fields OK", "value": product_rows - feed_summary["missing_required"], "total": product_rows, "percent": _percent(product_rows - feed_summary["missing_required"], product_rows)},
        {"label": "Apparel attrs OK", "value": product_rows - attribute_issues, "total": product_rows, "percent": _percent(product_rows - attribute_issues, product_rows)},
        {"label": "Country policy OK", "value": len(COUNTRY_COLUMNS) - country_needs_config, "total": len(COUNTRY_COLUMNS), "percent": _percent(len(COUNTRY_COLUMNS) - country_needs_config, len(COUNTRY_COLUMNS))},
        {"label": "Local inventory missing", "value": merchant["local_inventory_missing"], "total": "Merchant", "percent": 91},
        {"label": "Product page unavailable", "value": merchant["product_page_unavailable"], "total": "Merchant", "percent": 18.3},
        {"label": "Missing size", "value": feed_summary["missing_size"], "total": "local CSV", "percent": _percent(feed_summary["missing_size"], product_rows)},
        {"label": "Missing color", "value": feed_summary["missing_color"], "total": "local CSV", "percent": _percent(feed_summary["missing_color"], product_rows)},
        {"label": "Missing gender", "value": feed_summary["missing_gender"], "total": "local CSV", "percent": _percent(feed_summary["missing_gender"], product_rows)},
        {"label": "Missing age", "value": feed_summary["missing_age_group"], "total": "local CSV", "percent": _percent(feed_summary["missing_age_group"], product_rows)},
    ]


def remediation_actions(live: dict[str, Any], feed: dict[str, Any]) -> list[dict[str, str]]:
    trust_fail = [row for row in live["trust_pages"] if row["status"] != "pass"]
    tag_summary = live["summary"]
    feed_summary = feed["summary"]
    actions = [
        {
            "priority": "P0",
            "area": "Local inventory",
            "status": "needs_fix",
            "action": "Resolve missing local inventory data",
            "detail": "BKS appears online/print-on-demand. Disable local inventory ads/free local listings unless physical-store inventory is real, or upload a local inventory feed with id, store_code, availability and quantity.",
            "verification": "Merchant no longer reports local inventory missing; local inventory feed either complete or destination disabled.",
        },
        {
            "priority": "P0",
            "area": "Product availability",
            "status": "needs_fix",
            "action": "Clean product page unavailable errors",
            "detail": "Remove stale/deleted products from Merchant, resync Shopify, verify product URLs on desktop and mobile, then request re-crawl.",
            "verification": "Merchant no longer reports product page unavailable and sample URLs return HTTP 200 product pages.",
        },
        {
            "priority": "P1",
            "area": "Apparel attributes",
            "status": "needs_fix" if feed_summary["attribute_issues"] else "pass",
            "action": "Complete size, color, gender and age attributes",
            "detail": "Normalize Google Shopping gender/age_group and ensure size/color values are visible in variants/metafields and product pages.",
            "verification": "Local scanner returns zero apparel attribute issues; Merchant stops showing size/color/gender/age missing suggestions.",
        },
        {
            "priority": "P1",
            "area": "Country policies",
            "status": "needs_fix" if feed_summary["country_needs_config"] else "pass",
            "action": "Align shipping and returns by destination country",
            "detail": "Keep only countries that have Shopify shipping, Merchant destination, return policy and checkout availability aligned. Pause India/Korea until fully configured if needed.",
            "verification": "Country policy matrix is green or non-ready countries are removed from destinations.",
        },
        {
            "priority": "P1",
            "area": "Misrepresentation",
            "status": "needs_fix" if trust_fail else "pass",
            "action": "Fix trust pages before appeal",
            "detail": "Publish About and FAQ/help pages or remove broken links. Keep contact, shipping, refund, privacy and terms visible.",
            "verification": "All trust pages return HTTP 2xx/3xx in live_site_audit.",
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
            "priority": "P2",
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
    country_matrix = write_country_policy_matrix(root_dir, feed.get("country_rows", []))
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
            "country_matrix": country_matrix,
            "first_action": actions[0]["action"] if actions else "",
        },
        "charts": issue_bars(merchant, live, feed),
        "merchant_issues": list(SCREENSHOT_ISSUES),
        "tag_summary": live["summary"],
        "tag_issues": live["issue_rows"],
        "trust_pages": live["trust_pages"],
        "feed": feed,
        "country_policy": feed.get("country_rows", []),
        "actions": actions,
        "policy_sources": [
            {
                "label": "Google Merchant misrepresentation policy",
                "url": "https://support.google.com/merchants/answer/6150127?hl=it",
            },
            {
                "label": "Google product data specification",
                "url": "https://support.google.com/merchants/answer/7052112",
            },
            {
                "label": "Google landing page requirements",
                "url": "https://support.google.com/merchants/answer/4752265",
            },
            {
                "label": "Google local inventory data specification",
                "url": "https://support.google.com/merchants/answer/14819809",
            }
        ],
    }
