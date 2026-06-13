from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


TRUST_NEEDS: tuple[dict[str, str], ...] = (
    {
        "need": "Business identity",
        "google_question": "Can customers understand who is selling?",
        "evidence": "About page, contact page, footer identity, domain consistency.",
        "agent_rule": "Do not request Merchant review while About/contact are broken.",
    },
    {
        "need": "Product truth",
        "google_question": "Are products available and landing pages consistent with the feed?",
        "evidence": "HTTP 200 product/collection pages, clean feed, no stale deleted items.",
        "agent_rule": "Do not push ads or shopping campaigns until feed residue is cleaned.",
    },
    {
        "need": "Price and offer clarity",
        "google_question": "Are prices, discounts and countdowns real and verifiable?",
        "evidence": "Checkout price, real discount code, visible timer terms, campaign landing page.",
        "agent_rule": "Do not display discounts or urgency unless they have a real source and expiry.",
    },
    {
        "need": "Shipping clarity",
        "google_question": "Can customers understand shipping costs and delivery expectations?",
        "evidence": "Shipping policy, checkout shipping display, made-to-order disclosure.",
        "agent_rule": "Keep made-to-order language visible near trust strip or product pages.",
    },
    {
        "need": "Returns and refunds",
        "google_question": "Can customers understand how refunds work, including crypto payments?",
        "evidence": "Refund policy, terms of service, crypto refund clarification.",
        "agent_rule": "Do not promote Bitcoin/crypto without refund-policy clarity.",
    },
    {
        "need": "Secure checkout",
        "google_question": "Are payment methods clear, safe and not misleading?",
        "evidence": "Shopify checkout, PayPal/card/wallet/crypto availability, no investment claims.",
        "agent_rule": "Frame Bitcoin as optional payment only, never financial opportunity.",
    },
    {
        "need": "Measurable trust",
        "google_question": "Can we measure visits/events without duplicate or missing tags?",
        "evidence": "GTM target, GA4 coverage, no legacy duplicate GTM.",
        "agent_rule": "Fix tag coverage before market adaptation decisions.",
    },
    {
        "need": "Network and sender trust",
        "google_question": "Are domain, email authentication, DSN/bounces and tracking suffixes technically trustworthy?",
        "evidence": "Apex/www DNS, HTTPS endpoint, MX, SPF, DKIM, DMARC, DSN capture, clean canonical URL rules.",
        "agent_rule": "Do not scale email/social campaigns until DMARC, bounce capture and endpoint checks are green or explicitly approved.",
    },
    {
        "need": "Support and handoff",
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
    marketing = snapshot.get("marketing", {})
    payments = snapshot.get("payments", {})
    network = snapshot.get("network", {})
    tag = google.get("tag_summary", {})
    trust_pages = google.get("trust_pages", [])
    trust_fail = [row for row in trust_pages if row.get("status") != "pass"]
    feed = google.get("feed", {}).get("summary", {})

    if need == "Business identity":
        return ("pass" if not trust_fail else "needs_fix", f"{len(trust_fail)} trust page issues")
    if need == "Product truth":
        unavailable = google.get("merchant", {}).get("product_page_unavailable", "")
        missing = int(feed.get("missing_required", 0))
        return ("needs_fix" if missing else "manual_pending", f"{missing} feed field issues; GMC says {unavailable}")
    if need == "Price and offer clarity":
        compliance = marketing.get("summary", {}).get("compliance", "")
        return ("pass" if compliance == "google_safe" else "needs_fix", compliance or "timer not checked")
    if need == "Shipping clarity":
        shipping = next((row for row in trust_pages if row.get("check") == "Shipping policy"), {})
        return ("pass" if shipping.get("status") == "pass" else "needs_fix", shipping.get("http_status", "missing"))
    if need == "Returns and refunds":
        refund = next((row for row in trust_pages if row.get("check") == "Refund policy"), {})
        bitcoin = payments.get("summary", {}).get("bitcoin", "unknown")
        return ("pass" if refund.get("status") == "pass" else "needs_fix", f"refund {refund.get('http_status', 'missing')}; bitcoin {bitcoin}")
    if need == "Secure checkout":
        bitcoin = payments.get("summary", {}).get("bitcoin", "unknown")
        return ("manual_pending", f"checkout verification required; bitcoin {bitcoin}")
    if need == "Measurable trust":
        gtm = float(tag.get("expected_gtm_percent", 0))
        ga4 = float(tag.get("ga4_percent", 0))
        legacy = int(tag.get("legacy_gtm", 0))
        status = "pass" if gtm >= 95 and ga4 >= 95 and legacy == 0 else "needs_fix"
        return status, f"GTM {gtm}% / GA4 {ga4}% / legacy {legacy}"
    if need == "Network and sender trust":
        summary = network.get("summary", {})
        needs_fix = int(summary.get("needs_fix", 0) or 0)
        status = "pass" if needs_fix == 0 and summary.get("status") == "pass" else "needs_fix"
        return status, f"{needs_fix} network blockers; DMARC/DSN/email auth checked in Network Trust Monitor"
    if need == "Support and handoff":
        contact = next((row for row in trust_pages if row.get("check") == "Contact"), {})
        return ("pass" if contact.get("status") == "pass" else "needs_fix", contact.get("http_status", "missing"))
    return "needs_review", ""


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, str]] = []
    for spec in TRUST_NEEDS:
        status, evidence_value = _status_for_need(spec["need"], snapshot)
        rows.append({**spec, "status": status, "current_evidence": evidence_value})

    path = settings.root_dir / "output" / "google_trust_contract.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["need", "status", "google_question", "current_evidence", "evidence", "agent_rule"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in rows])

    return {
        "summary": {
            "pass": sum(1 for row in rows if row["status"] == "pass"),
            "needs_fix": sum(1 for row in rows if row["status"] == "needs_fix"),
            "manual_pending": sum(1 for row in rows if row["status"] == "manual_pending"),
            "total": len(rows),
            "sheet": _relative(settings.root_dir, path),
        },
        "rows": rows,
        "principle": "Google trust is the central gate before growth actions.",
    }
