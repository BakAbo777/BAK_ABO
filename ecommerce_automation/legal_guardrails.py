from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


LEGAL_SHEET = Path("output/legal_guardrails_matrix.csv")
SUPPLIER_SHEET = Path("output/supplier_contract_matrix.csv")
LEGAL_DOC = Path("docs/BKS_LEGAL_GUARDRAILS.md")


CUSTOMER_GUARDS: tuple[dict[str, str], ...] = (
    {
        "area": "Business identity",
        "requirement": "Customers must understand who sells, how to contact BKS and which domain/brand they are dealing with.",
        "evidence": "About page, contact page, footer identity, official email crew@bakabo.club.",
        "agent_rule": "Do not hide BKS identity or imply affiliation with another brand.",
        "source": "Google Merchant misrepresentation policy",
        "source_url": "https://support.google.com/merchants/answer/6150127?hl=it",
    },
    {
        "area": "Consumer information before purchase",
        "requirement": "Distance contracts need clear pre-contract information, withdrawal procedure, delivery and risk information.",
        "evidence": "Product page, shipping policy, refund policy, terms, checkout disclosures.",
        "agent_rule": "Every campaign must link to matching product/collection and official policies.",
        "source": "EU Consumer Rights Directive",
        "source_url": "https://commission.europa.eu/law/law-topic/consumer-protection-law/consumer-contract-law/consumer-rights-directive_en",
    },
    {
        "area": "Guarantees and returns",
        "requirement": "EU consumers have statutory guarantee rights; returns/refunds must be explained clearly.",
        "evidence": "Refund policy, order support workflow, supplier defect handling.",
        "agent_rule": "Never tell a customer statutory rights are excluded by made-to-order language.",
        "source": "Your Europe guarantees",
        "source_url": "https://europa.eu/youreurope/citizens/consumers/shopping/guarantees/index_en.htm",
    },
    {
        "area": "Product safety",
        "requirement": "Only safe products should be available; product risk, warnings and responsible operators must be traceable.",
        "evidence": "Supplier product specs, material info, safety warnings, recall path.",
        "agent_rule": "Escalate safety complaints and pause product promotion until reviewed.",
        "source": "EU product safety / GPSR",
        "source_url": "https://commission.europa.eu/topics/business-and-industry/doing-business-eu/eu-product-safety-and-labelling/product-safety_en",
    },
    {
        "area": "Privacy and consent",
        "requirement": "Personal data and tracking must have a lawful basis; consent must be transparent where needed.",
        "evidence": "Privacy policy, cookie/consent setup, email tracking disclosure, opt-out records.",
        "agent_rule": "Use open/click/mobile signals only when transparent, lawful and not sensitive.",
        "source": "EDPB consent guidance",
        "source_url": "https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en",
    },
    {
        "area": "Email marketing",
        "requirement": "Commercial email must use truthful sender/subject, clear opt-out and compliant marketing content.",
        "evidence": "crew@bakabo.club, unsubscribe URL, message logs, approval history.",
        "agent_rule": "No deceptive subject lines, no fake urgency, no marketing after opt-out.",
        "source": "FTC CAN-SPAM guide",
        "source_url": "https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business",
    },
    {
        "area": "Payments and crypto",
        "requirement": "Payment methods must be clear, secure and not framed as investment opportunity.",
        "evidence": "Checkout methods, refund policy, crypto payment notes.",
        "agent_rule": "Bitcoin is optional payment only; no financial promise.",
        "source": "BKS payments guardrail",
        "source_url": "docs/bakabo-bitcoin-payments_SKILL.md",
    },
)


SUPPLIER_GUARDS: tuple[dict[str, str], ...] = (
    {
        "supplier": "Printify / production partners",
        "relationship": "Producer/fulfillment",
        "minimum_terms": "Product specs, print quality, defect handling, fulfillment SLA, returns/claims flow, product safety info.",
        "risk": "high",
        "agent_rule": "Keep product traceability by SKU/order/provider and escalate defects.",
    },
    {
        "supplier": "Shopify",
        "relationship": "Storefront/checkout platform",
        "minimum_terms": "Platform terms, checkout security, order data processing, theme/app permissions.",
        "risk": "critical",
        "agent_rule": "Do not bypass checkout for payment or personal data.",
    },
    {
        "supplier": "Payment providers",
        "relationship": "Payments",
        "minimum_terms": "Settlement, refunds, disputes, chargebacks, crypto handling, prohibited claims.",
        "risk": "critical",
        "agent_rule": "Payment changes need human approval and clear customer disclosures.",
    },
    {
        "supplier": "HeyGen / creative AI providers",
        "relationship": "Avatar/content production",
        "minimum_terms": "Usage rights, consent for avatar/voice, commercial license, export retention, takedown path.",
        "risk": "medium",
        "agent_rule": "Do not use customer likeness or private data for avatar without explicit consent.",
    },
    {
        "supplier": "OpenAI / AI services",
        "relationship": "Agent intelligence",
        "minimum_terms": "Data minimization, no sensitive customer data unless necessary, prompt/output review.",
        "risk": "medium",
        "agent_rule": "Use anonymized context for customer learning where possible.",
    },
    {
        "supplier": "Social platforms",
        "relationship": "Distribution/ads",
        "minimum_terms": "API permissions, platform policies, campaign transparency, ad account governance.",
        "risk": "high",
        "agent_rule": "Autonomous campaigns must remain draft/supervised until channel compliance is green.",
    },
    {
        "supplier": "Logistics/shipping partners",
        "relationship": "Delivery",
        "minimum_terms": "Delivery times, tracking, lost parcel process, customer communication handoff.",
        "risk": "high",
        "agent_rule": "Do not promise delivery dates beyond verified carrier/checkout data.",
    },
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _policy_exists(settings: Any, name: str) -> bool:
    candidates = [
        settings.root_dir / "output" / "site_texts_v1" / f"{name}_reviewed.html",
        settings.root_dir / "output" / "site_texts_v1" / f"{name}.html",
        settings.root_dir / "05_TESTI_POLICY" / f"{name}.md",
    ]
    return any(path.exists() for path in candidates)


def _customer_status(settings: Any, guard: dict[str, str], snapshot: dict[str, Any]) -> tuple[str, str]:
    trust = snapshot.get("trust", {}).get("summary", {})
    google = snapshot.get("google", {})
    payments = snapshot.get("payments", {}).get("summary", {})
    inbox = snapshot.get("official_inbox", {}).get("summary", {})
    if guard["area"] == "Business identity":
        fails = [row for row in google.get("trust_pages", []) if row.get("check") in {"About", "Contact"} and row.get("status") != "pass"]
        return ("pass" if not fails and settings.official_inbox_email else "needs_fix", f"{len(fails)} identity page issues; email {settings.official_inbox_email}")
    if guard["area"] == "Consumer information before purchase":
        ok = _policy_exists(settings, "terms_of_service") and _policy_exists(settings, "shipping_policy")
        return ("pass" if ok else "needs_review", "terms/shipping policy local files")
    if guard["area"] == "Guarantees and returns":
        ok = _policy_exists(settings, "returns_refund_policy") or _policy_exists(settings, "refund_policy")
        return ("pass" if ok else "needs_fix", "refund policy local file")
    if guard["area"] == "Product safety":
        return ("manual_pending", "supplier product safety docs must be collected")
    if guard["area"] == "Privacy and consent":
        ok = _policy_exists(settings, "privacy_policy")
        tracking = inbox.get("tracking_mode", settings.official_email_tracking_consent_mode)
        return ("pass" if ok else "needs_fix", f"privacy policy; tracking {tracking}")
    if guard["area"] == "Email marketing":
        return ("pass" if settings.official_inbox_email and settings.official_email_unsubscribe_url else "needs_fix", settings.official_email_unsubscribe_url)
    if guard["area"] == "Payments and crypto":
        return ("manual_pending" if payments.get("bitcoin") == "active" else "pass", f"bitcoin {payments.get('bitcoin', 'unknown')}")
    return ("needs_review", "")


def customer_rows(settings: Any, snapshot: dict[str, Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for guard in CUSTOMER_GUARDS:
        status, evidence = _customer_status(settings, guard, snapshot)
        result.append({**guard, "type": "customer", "status": status, "current_evidence": evidence})
    return result


def supplier_rows(settings: Any) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    configured = {
        "Printify / production partners": bool(settings.printify_api_token and settings.printify_shop_id),
        "Shopify": bool(settings.shopify_store and settings.shopify_admin_token),
        "Payment providers": bool(settings.stripe_secret_key or settings.paypal_client_id or settings.crypto_payments_enabled),
        "HeyGen / creative AI providers": bool(settings.heygen_api_key),
        "OpenAI / AI services": bool(settings.openai_api_key),
        "Social platforms": bool(settings.meta_access_token or settings.youtube_channel_id or settings.telegram_bot_token),
        "Logistics/shipping partners": False,
    }
    for guard in SUPPLIER_GUARDS:
        status = "active_needs_contract_review" if configured.get(guard["supplier"], False) else "planned_contract"
        result.append({**guard, "type": "supplier", "status": status})
    return result


def write_docs(settings: Any, customer: list[dict[str, str]], supplier: list[dict[str, str]]) -> tuple[str, str, str]:
    legal_path = settings.root_dir / LEGAL_DOC
    legal_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# BKS Legal Guardrails",
        "",
        "Operational legal/compliance guardrails for BKS Master Agent. This is a checklist and evidence system, not legal advice.",
        "",
        "## Customer Guarantees",
        "",
    ]
    lines.extend(f"- {row['area']}: {row['requirement']} Status: {row['status']}." for row in customer)
    lines.extend(
        [
            "",
            "## Supplier / Producer Relationship Controls",
            "",
        ]
    )
    lines.extend(f"- {row['supplier']}: {row['minimum_terms']} Status: {row['status']}." for row in supplier)
    lines.extend(
        [
            "",
            "## Agent rule",
            "",
            "The agent may draft customer replies, supplier checklists and compliance evidence. It must request human review for legal, privacy, payment, supplier contract, product safety, complaint and Merchant appeal actions.",
            "",
            "## Sources",
            "",
            "- EU Consumer Rights Directive: https://commission.europa.eu/law/law-topic/consumer-protection-law/consumer-contract-law/consumer-rights-directive_en",
            "- EU guarantees: https://europa.eu/youreurope/citizens/consumers/shopping/guarantees/index_en.htm",
            "- EU product safety: https://commission.europa.eu/topics/business-and-industry/doing-business-eu/eu-product-safety-and-labelling/product-safety_en",
            "- EDPB consent guidance: https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en",
            "- FTC CAN-SPAM guide: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business",
            "- Google Merchant misrepresentation policy: https://support.google.com/merchants/answer/6150127?hl=it",
        ]
    )
    legal_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    legal_sheet = settings.root_dir / LEGAL_SHEET
    legal_sheet.parent.mkdir(parents=True, exist_ok=True)
    legal_fields = ["type", "area", "status", "requirement", "current_evidence", "evidence", "agent_rule", "source", "source_url"]
    with legal_sheet.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=legal_fields)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in legal_fields} for row in customer])

    supplier_sheet = settings.root_dir / SUPPLIER_SHEET
    supplier_sheet.parent.mkdir(parents=True, exist_ok=True)
    supplier_fields = ["type", "supplier", "relationship", "status", "risk", "minimum_terms", "agent_rule"]
    with supplier_sheet.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=supplier_fields)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in supplier_fields} for row in supplier])

    return _relative(settings.root_dir, legal_path), _relative(settings.root_dir, legal_sheet), _relative(settings.root_dir, supplier_sheet)


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    customer = customer_rows(settings, snapshot)
    suppliers = supplier_rows(settings)
    doc, legal_sheet, supplier_sheet = write_docs(settings, customer, suppliers)
    return {
        "summary": {
            "customer_pass": sum(1 for row in customer if row["status"] == "pass"),
            "customer_needs": sum(1 for row in customer if row["status"] != "pass"),
            "supplier_active": sum(1 for row in suppliers if row["status"].startswith("active")),
            "supplier_review": sum(1 for row in suppliers if "contract" in row["status"]),
            "status": "attention" if any(row["status"] != "pass" for row in customer) else "guarded",
            "doc": doc,
            "legal_sheet": legal_sheet,
            "supplier_sheet": supplier_sheet,
        },
        "customer": customer,
        "suppliers": suppliers,
        "approval_gate": [
            "Legal/privacy/payment/supplier/product safety messages require human review.",
            "Supplier terms must cover product quality, safety, traceability, defects, SLA, data and IP/licensing.",
            "Customer rights are never reduced by internal supplier limitations.",
        ],
    }
