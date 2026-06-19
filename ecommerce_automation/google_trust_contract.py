from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

BAKABO_STORE_DOMAIN = "bakabo.club"
BKS_TM04_THEME_ID = "202392961362"
BKS_LIVE_COLLECTIONS = frozenset({"hours", "glyph", "marker", "riviera", "pulse", "token", "flag", "origin"})

# P0 = hard blocker for Merchant appeal; P1 = important but not blocking
BKS_P0_NEEDS = frozenset({
    "Business identity",
    "Product truth",
    "Collection and theme identity",
    "Returns and refunds",
    "Secure checkout",
})

TRUST_NEEDS: tuple[dict[str, str], ...] = (
    {
        "need": "Business identity",
        "priority": "p0",
        "google_question": "Can customers understand who is selling?",
        "evidence": "About page, contact page, footer identity, domain consistency.",
        "agent_rule": "Do not request Merchant review while About/contact are broken.",
    },
    {
        "need": "Product truth",
        "priority": "p0",
        "google_question": "Are products available and landing pages consistent with the feed?",
        "evidence": "HTTP 200 product/collection pages, local_inventory_errors == 0, unavailable_pages == 0, no stale deleted items.",
        "agent_rule": "Do not push ads or shopping campaigns until local_inventory_errors and unavailable_pages are both 0.",
    },
    {
        "need": "Collection and theme identity",
        "priority": "p0",
        "google_question": "Are collection pages live with correct names and served on the active TM04 theme?",
        "evidence": f"TM04 theme ID {BKS_TM04_THEME_ID} published; 8 BKS collections live (Hours/Glyph/Marker/Riviera/Pulse/Token/Flag/Origin); no 'folklore' tag or handle in feed.",
        "agent_rule": "Do not promote collections until TM04 is published and Origin replaces Folklore in all tags, handles and feed entries.",
    },
    {
        "need": "Price and offer clarity",
        "priority": "p1",
        "google_question": "Are prices, discounts and countdowns real and verifiable?",
        "evidence": "Checkout price, real discount code, visible timer terms, campaign landing page.",
        "agent_rule": "Do not display discounts or urgency unless they have a real source and expiry.",
    },
    {
        "need": "Shipping clarity",
        "priority": "p1",
        "google_question": "Can customers understand shipping costs and delivery expectations?",
        "evidence": "Shipping policy, checkout shipping display, made-to-order disclosure.",
        "agent_rule": "Keep made-to-order language visible near trust strip or product pages.",
    },
    {
        "need": "Returns and refunds",
        "priority": "p0",
        "google_question": "Can customers understand how refunds work, including crypto payments?",
        "evidence": "Refund policy, terms of service, crypto refund clarification.",
        "agent_rule": "Do not promote Bitcoin/crypto without refund-policy clarity.",
    },
    {
        "need": "Secure checkout",
        "priority": "p0",
        "google_question": "Are payment methods clear, safe and not misleading?",
        "evidence": "Shopify checkout, PayPal/card/wallet/crypto availability, no investment claims.",
        "agent_rule": "Frame Bitcoin as optional payment only, never financial opportunity.",
    },
    {
        "need": "Measurable trust",
        "priority": "p1",
        "google_question": "Can we measure visits/events without duplicate or missing tags?",
        "evidence": "GTM target, GA4 coverage, no legacy duplicate GTM.",
        "agent_rule": "Fix tag coverage before market adaptation decisions.",
    },
    {
        "need": "Network and sender trust",
        "priority": "p1",
        "google_question": "Are domain, email authentication, DSN/bounces and tracking suffixes technically trustworthy?",
        "evidence": f"Apex/www DNS, HTTPS on {BAKABO_STORE_DOMAIN}, MX, SPF, DKIM, DMARC, DSN capture, clean canonical URL rules.",
        "agent_rule": "Do not scale email/social campaigns until DMARC, bounce capture and endpoint checks are green or explicitly approved.",
    },
    {
        "need": "Support and handoff",
        "priority": "p1",
        "google_question": "Can customers reach a human path when needed?",
        "evidence": "Contact page, support email, opt-in messaging, Telegram/WhatsApp human handoff.",
        "agent_rule": "Automated customer conversations require opt-in and human escalation.",
    },
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _status_for_need(need: str, snapshot: dict[str, Any]) -> tuple[str, str]:
    google = snapshot.get("google", {})
    google_summary = google.get("summary", {})
    marketing = snapshot.get("marketing", {})
    payments = snapshot.get("payments", {})
    network = snapshot.get("network", {})
    theme = snapshot.get("theme", {}).get("summary", {})
    collections = snapshot.get("collections", {})
    tag = google.get("tag_summary", {})
    trust_pages = google.get("trust_pages", [])
    trust_fail = [row for row in trust_pages if row.get("status") != "pass"]
    feed = google.get("feed", {}).get("summary", {})

    if need == "Business identity":
        about_ok = any(r.get("check") in {"About", "About Us"} and r.get("status") == "pass" for r in trust_pages)
        contact_ok = any(r.get("check") == "Contact" and r.get("status") == "pass" for r in trust_pages)
        if about_ok and contact_ok:
            return "pass", "About + Contact pages live"
        issues = []
        if not about_ok:
            issues.append("About page missing or HTTP error")
        if not contact_ok:
            issues.append("Contact page missing or HTTP error")
        return "needs_fix", "; ".join(issues) or f"{len(trust_fail)} trust page issues"

    if need == "Product truth":
        local_inv = int(google_summary.get("local_inventory_errors", -1) or -1)
        unavail = int(google_summary.get("unavailable_pages", -1) or -1)
        missing = int(feed.get("missing_required", 0) or 0)
        issues = []
        if local_inv > 0:
            issues.append(f"{local_inv} local inventory errors")
        elif local_inv < 0:
            issues.append("local inventory status unknown — run google_merchant_monitor")
        if unavail > 0:
            issues.append(f"{unavail} unavailable product pages")
        elif unavail < 0:
            issues.append("unavailable pages status unknown — run google_merchant_monitor")
        if missing:
            issues.append(f"{missing} missing required feed fields")
        if not issues:
            return "pass", "feed clean; local_inventory_errors=0; all product pages live"
        return "needs_fix" if (local_inv != 0 or unavail != 0) else "manual_pending", "; ".join(issues)

    if need == "Collection and theme identity":
        tm04_ok = theme.get("theme_id") == BKS_TM04_THEME_ID or theme.get("tm04_active", False)
        missing_cols = collections.get("missing", [])
        folklore_tag = any(
            "folklore" in str(v).lower()
            for row in feed.get("tag_samples", [])
            for v in (row if isinstance(row, list) else [row])
        )
        # also check feed summary tags field if present
        feed_tags_raw = google.get("feed", {}).get("tags", [])
        folklore_in_feed = folklore_tag or any("folklore" in str(t).lower() for t in feed_tags_raw)
        issues = []
        if not tm04_ok:
            tid = theme.get("theme_id", "unknown")
            issues.append(f"TM04 not published (active: {tid})" if tid != "unknown" else "TM04 status unknown — run ShopifyClient.active_theme_summary()")
        if missing_cols:
            issues.append(f"missing collections: {', '.join(missing_cols)}")
        if folklore_in_feed:
            issues.append("'folklore' handle/tag still in feed — rename to origin everywhere")
        if not issues:
            return "pass", f"TM04 live; {len(BKS_LIVE_COLLECTIONS)} collections present; no folklore residue"
        return "needs_fix", "; ".join(issues)

    if need == "Price and offer clarity":
        compliance = marketing.get("summary", {}).get("compliance", "")
        return ("pass" if compliance == "google_safe" else "needs_fix", compliance or "timer compliance not checked")

    if need == "Shipping clarity":
        shipping = next((row for row in trust_pages if row.get("check") == "Shipping policy"), {})
        return ("pass" if shipping.get("status") == "pass" else "needs_fix", shipping.get("http_status", "missing"))

    if need == "Returns and refunds":
        refund = next((row for row in trust_pages if row.get("check") == "Refund policy"), {})
        bitcoin = payments.get("summary", {}).get("bitcoin", "unknown")
        status = "pass" if refund.get("status") == "pass" else "needs_fix"
        return status, f"refund {refund.get('http_status', 'missing')}; bitcoin payment: {bitcoin}"

    if need == "Secure checkout":
        bitcoin = payments.get("summary", {}).get("bitcoin", "unknown")
        return "manual_pending", f"checkout verification required; bitcoin payment mode: {bitcoin}"

    if need == "Measurable trust":
        gtm = float(tag.get("expected_gtm_percent", 0) or 0)
        ga4 = float(tag.get("ga4_percent", 0) or 0)
        legacy = int(tag.get("legacy_gtm", 0) or 0)
        status = "pass" if gtm >= 95 and ga4 >= 95 and legacy == 0 else "needs_fix"
        return status, f"GTM {gtm:.0f}% / GA4 {ga4:.0f}% / legacy duplicate GTMs: {legacy}"

    if need == "Network and sender trust":
        summary = network.get("summary", {})
        needs_fix = int(summary.get("needs_fix", 0) or 0)
        status = "pass" if needs_fix == 0 and summary.get("status") == "pass" else "needs_fix"
        return status, f"{needs_fix} network blockers; DMARC/DSN/email auth checked via network_trust_monitor"

    if need == "Support and handoff":
        contact = next((row for row in trust_pages if row.get("check") == "Contact"), {})
        return ("pass" if contact.get("status") == "pass" else "needs_fix", contact.get("http_status", "missing"))

    return "needs_review", ""


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, str]] = []
    for spec in TRUST_NEEDS:
        status, evidence_value = _status_for_need(spec["need"], snapshot)
        rows.append({**spec, "status": status, "current_evidence": evidence_value})

    p0_rows = [row for row in rows if row.get("priority") == "p0"]
    p0_pass = sum(1 for row in p0_rows if row["status"] == "pass")
    p0_blockers = [row["need"] for row in p0_rows if row["status"] != "pass"]
    merchant_appeal_ready = len(p0_blockers) == 0
    total = len(rows)
    total_pass = sum(1 for row in rows if row["status"] == "pass")
    next_blocking = next((row for row in rows if row["status"] not in {"pass", "manual_pending"}), None)

    path = settings.root_dir / "output" / "google_trust_contract.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["priority", "need", "status", "google_question", "current_evidence", "evidence", "agent_rule"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in rows])

    return {
        "summary": {
            "pass": total_pass,
            "needs_fix": sum(1 for row in rows if row["status"] == "needs_fix"),
            "manual_pending": sum(1 for row in rows if row["status"] == "manual_pending"),
            "total": total,
            "percent_complete": round(total_pass / total * 100) if total else 0,
            "p0_total": len(p0_rows),
            "p0_pass": p0_pass,
            "p0_blockers": p0_blockers,
            "merchant_appeal_ready": merchant_appeal_ready,
            "next_blocking_need": next_blocking["need"] if next_blocking else "",
            "sheet": _relative(settings.root_dir, path),
        },
        "rows": rows,
        "principle": "Google trust is the central gate before growth. P0 blockers must clear before Merchant appeal, paid ads, or campaign layer.",
    }
