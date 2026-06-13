from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


INBOX_SHEET = Path("output/official_inbox_matrix.csv")
PROTOCOL_DOC = Path("docs/bakabo-official-inbox_SKILL.md")


CATEGORY_RULES: tuple[dict[str, str], ...] = (
    {
        "category": "order_support",
        "signals": "order, shipping, delivery, tracking, return, refund",
        "agent_action": "Prepare a factual draft using official policies and order data if connected.",
        "approval": "human_review_before_send",
        "sla": "same business day",
    },
    {
        "category": "merchant_google",
        "signals": "Google, Merchant, suspension, misrepresentation, feed, verification",
        "agent_action": "Route to Google Trust Contract and preserve evidence for appeal.",
        "approval": "human_review_before_appeal",
        "sla": "priority",
    },
    {
        "category": "privacy_unsubscribe",
        "signals": "unsubscribe, privacy, data, delete, GDPR, consent",
        "agent_action": "Respect opt-out, avoid marketing, route privacy requests to human owner.",
        "approval": "human_review_required",
        "sla": "priority",
    },
    {
        "category": "complaint_risk",
        "signals": "complaint, scam, misleading, chargeback, not received, legal",
        "agent_action": "Escalate, draft calm answer, record issue in Knowledge DB.",
        "approval": "human_review_required",
        "sla": "priority",
    },
    {
        "category": "sales_interest",
        "signals": "price, collection, availability, size, gift, bulk, wholesale",
        "agent_action": "Answer transparently, link product/policy pages, suggest next best collection.",
        "approval": "draft_or_supervised_send",
        "sla": "same business day",
    },
    {
        "category": "partnership_press",
        "signals": "collaboration, creator, press, partnership, affiliate",
        "agent_action": "Prepare brand-safe partnership reply and require founder review.",
        "approval": "human_review_required",
        "sla": "48h",
    },
)


TRANSPARENCY_RULES: tuple[dict[str, str], ...] = (
    {
        "rule": "Official identity",
        "meaning": "Use crew@bakabo.club as the official mailbox and do not hide the business identity.",
        "source": "Google Merchant trust",
    },
    {
        "rule": "No deceptive subject/body",
        "meaning": "Subjects must match the email content; no false urgency, fake discounts or unavailable offers.",
        "source": "FTC CAN-SPAM guidance",
    },
    {
        "rule": "Opt-out respected",
        "meaning": "Marketing emails need a clear opt-out path; unsubscribe requests are never used for targeting.",
        "source": "FTC CAN-SPAM guidance",
    },
    {
        "rule": "Consent-aware tracking",
        "meaning": "Email open/click/mobile signals are used only when transparent, consented where required, and not as sensitive profiling.",
        "source": "EDPB GDPR consent guidance",
    },
    {
        "rule": "Human escalation",
        "meaning": "Complaints, privacy, payment and legal issues require human review before sending.",
        "source": "BKS approval gate",
    },
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _enabled(value: str) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "enabled"}


def status_rows(settings: Any) -> list[dict[str, str]]:
    imap_ready = bool(settings.official_inbox_imap_host and settings.official_inbox_imap_user and settings.official_inbox_imap_password)
    smtp_ready = bool(settings.smtp_host and settings.smtp_user and settings.smtp_password)
    tracking_ready = _enabled(settings.official_email_tracking_enabled) and bool(settings.official_email_tracking_provider)
    return [
        {
            "area": "Official mailbox",
            "status": "configured" if settings.official_inbox_email else "missing",
            "value": settings.official_inbox_email or "",
            "next_action": "Keep as official customer and management address.",
        },
        {
            "area": "IMAP read monitor",
            "status": "configured" if imap_ready else "missing_config",
            "value": settings.official_inbox_imap_host or settings.official_inbox_provider or "",
            "next_action": "Add IMAP credentials for read-only inbox triage.",
        },
        {
            "area": "SMTP draft/send",
            "status": "configured" if smtp_ready else "missing_config",
            "value": settings.smtp_host or "",
            "next_action": "Use drafts first; enable sending only with approval gate.",
        },
        {
            "area": "Email open/click tracking",
            "status": "configured" if tracking_ready else "consent_pending",
            "value": settings.official_email_tracking_provider or "not configured",
            "next_action": "Use only with visible notice, consent where required, and unsubscribe compliance.",
        },
        {
            "area": "Mobile visit correlation",
            "status": "manual_pending" if settings.ga4_property_id or settings.gtm_target else "missing_config",
            "value": settings.ga4_property_id or settings.gtm_target or "",
            "next_action": "Correlate only through consented campaign IDs/UTM and aggregate GA4 device signals.",
        },
    ]


def write_sheet(settings: Any, rows: list[dict[str, str]]) -> str:
    path = settings.root_dir / INBOX_SHEET
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["type", "name", "status", "signals", "agent_action", "approval", "sla", "source", "next_action", "value"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
    return _relative(settings.root_dir, path)


def write_protocol(settings: Any) -> str:
    path = settings.root_dir / PROTOCOL_DOC
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# bakabo-official-inbox",
        "",
        "Official skill for supervising `crew@bakabo.club` communications.",
        "",
        "## Mission",
        "",
        "The agent monitors official email, classifies messages, drafts replies, records learning signals and escalates sensitive cases. It must not send risky customer, privacy, payment, complaint or legal replies without human review.",
        "",
        "## Transparent marketing rule",
        "",
        "Every marketing intervention must be clear about sender identity, reason for contact, unsubscribe path, real offer terms and final checkout authority for price/availability.",
        "",
        "## Consent-aware signals",
        "",
        "Email opened, clicked, returned from smartphone, or website revisit signals are useful only when they are transparent, lawful and connected through consented campaign IDs or aggregate analytics. The agent uses them to prioritize helpful follow-up, not to pressure customers.",
        "",
        "## Response loop",
        "",
        "1. Read official inbox metadata and permitted content.",
        "2. Classify message category.",
        "3. Search Knowledge DB for product/policy/evidence.",
        "4. Draft answer in the customer's language.",
        "5. Apply transparency/compliance checks.",
        "6. Ask approval when the case is sensitive or promotional.",
        "7. Save outcome to Knowledge DB.",
        "",
        "## Sources",
        "",
        "- FTC CAN-SPAM guidance: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business",
        "- EDPB GDPR consent guidance: https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en",
        "- Google Merchant misrepresentation policy: https://support.google.com/merchants/answer/6150127?hl=it",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return _relative(settings.root_dir, path)


def classify_subject(text: str) -> dict[str, str]:
    lower = (text or "").lower()
    for spec in CATEGORY_RULES:
        tokens = [token.strip().lower() for token in spec["signals"].split(",")]
        if any(token and token in lower for token in tokens):
            return {
                "category": spec["category"],
                "agent_action": spec["agent_action"],
                "approval": spec["approval"],
                "sla": spec["sla"],
            }
    return {
        "category": "general",
        "agent_action": "Prepare factual reply from Knowledge DB and official pages.",
        "approval": "draft_or_supervised_send",
        "sla": "same business day",
    }


def payload(settings: Any) -> dict[str, Any]:
    status = status_rows(settings)
    category_rows = [{"type": "category", "name": row["category"], **row} for row in CATEGORY_RULES]
    transparency_rows = [{"type": "transparency", "name": row["rule"], **row} for row in TRANSPARENCY_RULES]
    status_export_rows = [{"type": "status", "name": row["area"], **row} for row in status]
    sheet = write_sheet(settings, status_export_rows + category_rows + transparency_rows)
    protocol = write_protocol(settings)
    configured = sum(1 for row in status if row["status"] == "configured")
    needs = sum(1 for row in status if row["status"] != "configured")
    return {
        "summary": {
            "official_email": settings.official_inbox_email,
            "configured": configured,
            "needs_attention": needs,
            "tracking_mode": settings.official_email_tracking_consent_mode,
            "status": "ready_for_drafts" if settings.official_inbox_email else "missing_email",
            "sheet": sheet,
            "protocol": protocol,
            "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
        "status_rows": status,
        "categories": list(CATEGORY_RULES),
        "transparency": list(TRANSPARENCY_RULES),
        "guardrails": [
            "Draft first; send only when approval and channel policy allow it.",
            "Complaints, privacy, payments, legal and Google issues always escalate.",
            "Email open/click/mobile signals require transparency and consent discipline.",
            "Marketing messages must include real sender identity, truthful subject, offer terms and opt-out path.",
        ],
        "sources": [
            {"label": "FTC CAN-SPAM compliance guide", "url": "https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business"},
            {"label": "EDPB consent guidelines", "url": "https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en"},
            {"label": "Google Merchant misrepresentation policy", "url": "https://support.google.com/merchants/answer/6150127?hl=it"},
        ],
    }
