from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

BAKABO_STORE_DOMAIN = "bakabo.club"
BAKABO_CREW_EMAIL = "crew@bakabo.club"
BKS_TM04_THEME_ID = "202392961362"

LEGAL_SHEET = Path("output/legal_guardrails_matrix.csv")
SUPPLIER_SHEET = Path("output/supplier_contract_matrix.csv")
# Authoritative skill doc — live alongside other resident skills
SKILL_DOC = Path("BKS_SKILL/skills/bakabo-legal-guardrails/SKILL.md")
# Legacy path kept for backward-compat output
LEGAL_DOC = Path("docs/BKS_LEGAL_GUARDRAILS.md")

# Guards that block Merchant appeal and campaign layer if not passing
BLOCKING_AREAS = frozenset({"Business identity", "Guarantees and returns", "Payments and crypto"})


CUSTOMER_GUARDS: tuple[dict[str, str], ...] = (
    {
        "area": "Business identity",
        "priority": "p0",
        "trust_gate": "trust_foundation",
        "requirement": "Customers must understand who sells, how to contact BKS and which domain/brand they are dealing with.",
        "evidence": f"About page, contact page, footer identity, official email {BAKABO_CREW_EMAIL}.",
        "agent_rule": "Do not hide BKS identity or imply affiliation with another brand. Do not request Merchant review while About/Contact are broken.",
        "source": "Google Merchant misrepresentation policy",
        "source_url": "https://support.google.com/merchants/answer/6150127?hl=it",
    },
    {
        "area": "Consumer information before purchase",
        "priority": "p0",
        "trust_gate": "trust_foundation",
        "requirement": "Distance contracts need clear pre-contract information, withdrawal procedure, delivery and risk information.",
        "evidence": "Product page, shipping policy, refund policy, terms, checkout disclosures.",
        "agent_rule": "Every campaign must link to matching product/collection and official policies.",
        "source": "EU Consumer Rights Directive",
        "source_url": "https://commission.europa.eu/law/law-topic/consumer-protection-law/consumer-contract-law/consumer-rights-directive_en",
    },
    {
        "area": "Guarantees and returns",
        "priority": "p0",
        "trust_gate": "trust_foundation",
        "requirement": "EU consumers have statutory guarantee rights; returns/refunds must be explained clearly regardless of made-to-order model.",
        "evidence": "Refund policy live on bakabo.club, order support workflow, supplier defect handling via Printify.",
        "agent_rule": "Never tell a customer statutory rights are excluded by made-to-order language. Crypto refund policy URL must be set.",
        "source": "Your Europe guarantees",
        "source_url": "https://europa.eu/youreurope/citizens/consumers/shopping/guarantees/index_en.htm",
    },
    {
        "area": "Product safety",
        "priority": "p1",
        "trust_gate": "collection_identity",
        "requirement": "Only safe products available; product risk, warnings and responsible operators must be traceable.",
        "evidence": "Printify product specs, material info, safety warnings per product type, recall/escalation path.",
        "agent_rule": "Escalate safety complaints immediately and pause product promotion until reviewed by Roberto.",
        "source": "EU product safety / GPSR",
        "source_url": "https://commission.europa.eu/topics/business-and-industry/doing-business-eu/eu-product-safety-and-labelling/product-safety_en",
    },
    {
        "area": "Privacy and consent",
        "priority": "p0",
        "trust_gate": "trust_foundation",
        "requirement": "Personal data and tracking must have a lawful basis; consent must be transparent where needed.",
        "evidence": "Privacy policy live, cookie/consent setup, email tracking disclosure transparent_opt_in, opt-out records.",
        "agent_rule": "Use open/click/mobile signals only when transparent, lawful and not sensitive. Never store PII from AI conversations without consent.",
        "source": "EDPB consent guidance",
        "source_url": "https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en",
    },
    {
        "area": "Email marketing",
        "priority": "p0",
        "trust_gate": "collection_identity",
        "requirement": "Commercial email must use truthful sender/subject, clear opt-out and compliant marketing content.",
        "evidence": f"{BAKABO_CREW_EMAIL}, unsubscribe URL in every marketing email, message approval logs.",
        "agent_rule": "No deceptive subject lines, no fake urgency, no marketing after opt-out. Require Roberto approval before any campaign send.",
        "source": "FTC CAN-SPAM guide",
        "source_url": "https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business",
    },
    {
        "area": "Payments and crypto",
        "priority": "p0",
        "trust_gate": "conversion_support",
        "requirement": "Payment methods must be clear, secure and not framed as investment opportunity.",
        "evidence": "Shopify checkout, PayPal/card/wallet/crypto all listed, crypto_refund_policy_url set and live.",
        "agent_rule": "Bitcoin is optional payment only — never a financial promise. Crypto refund policy URL must be set and accessible before any crypto-related promotion.",
        "source": "BKS payments guardrail",
        "source_url": "BKS_SKILL/skills/bakabo-bitcoin-payments/SKILL.md",
    },
    {
        "area": "AI transparency",
        "priority": "p1",
        "trust_gate": "collection_identity",
        "requirement": "Customers must know when they are interacting with an AI agent, not a human.",
        "evidence": "Agent disclosure in bot welcome message, opt-in before AI conversation, human escalation path always available.",
        "agent_rule": "Never impersonate a human. Always disclose AI identity in the first message of any customer conversation. Offer human handoff path.",
        "source": "EU AI Act / consumer transparency",
        "source_url": "https://digital-strategy.ec.europa.eu/en/policies/european-approach-artificial-intelligence",
    },
)


SUPPLIER_GUARDS: tuple[dict[str, str], ...] = (
    {
        "supplier": "Printify / production partners",
        "relationship": "Producer/fulfillment",
        "risk": "critical",
        "trust_gate": "trust_foundation",
        "minimum_terms": "Product specs, print quality, defect handling, fulfillment SLA, returns/claims flow, product safety docs, SKU traceability.",
        "agent_rule": "Keep product traceability by SKU/order/provider. Escalate defects before promoting affected products.",
    },
    {
        "supplier": "Shopify",
        "relationship": "Storefront/checkout platform",
        "risk": "critical",
        "trust_gate": "trust_foundation",
        "minimum_terms": "Platform terms, checkout security, order data processing, theme/app permissions, TM04 theme publishing rights.",
        "agent_rule": "Do not bypass Shopify checkout for payment or personal data. Theme publishes require Roberto confirmation.",
    },
    {
        "supplier": "Payment providers",
        "relationship": "Payments",
        "risk": "critical",
        "trust_gate": "conversion_support",
        "minimum_terms": "Settlement, refunds, disputes, chargebacks, crypto handling, prohibited investment claims.",
        "agent_rule": "Payment method changes require human approval and customer disclosure. Crypto refund policy must be live before crypto is promoted.",
    },
    {
        "supplier": "Cloudflare Workers",
        "relationship": "Infrastructure / Edge",
        "risk": "high",
        "trust_gate": "trust_foundation",
        "minimum_terms": "API token scope, Worker rate limits, bks-agent-refresh cron permissions, data-in-transit privacy.",
        "agent_rule": "bks-agent-refresh Worker runs at 12:00 CET. Do not store personal customer data in Worker KV without DPA.",
    },
    {
        "supplier": "OpenAI / Anthropic (AI services)",
        "relationship": "Agent intelligence",
        "risk": "high",
        "trust_gate": "trust_foundation",
        "minimum_terms": "Data processing terms, no sensitive customer data unless anonymized, prompt/output review, retention policy.",
        "agent_rule": "Anonymize customer context before sending to AI APIs. Never send order IDs, emails or payment data in prompts.",
    },
    {
        "supplier": "HeyGen / creative AI",
        "relationship": "Avatar/content production",
        "risk": "medium",
        "trust_gate": "collection_identity",
        "minimum_terms": "Avatar usage rights, commercial license, export retention, consent for likeness/voice, takedown path.",
        "agent_rule": "Do not use customer likeness or private data for avatar training without explicit written consent.",
    },
    {
        "supplier": "Meta / Instagram / Facebook",
        "relationship": "Distribution/ads",
        "risk": "high",
        "trust_gate": "campaign_layer",
        "minimum_terms": "API permissions, platform ad policies, campaign transparency, ad account governance, data sharing terms.",
        "agent_rule": "Autonomous campaigns remain draft/supervised until google_trust_contract P0 is green. Never run retargeting without consent.",
    },
    {
        "supplier": "Logistics/shipping partners",
        "relationship": "Delivery",
        "risk": "high",
        "trust_gate": "trust_foundation",
        "minimum_terms": "Delivery times, carrier tracking, lost parcel process, customer communication handoff, GDPR compliance for address data.",
        "agent_rule": "Do not promise delivery dates beyond verified carrier/Shopify checkout data.",
    },
    {
        "supplier": "WhatsApp Business / Telegram",
        "relationship": "Customer messaging",
        "risk": "medium",
        "trust_gate": "collection_identity",
        "minimum_terms": "Meta/Telegram platform terms, opt-in requirement, no spam policy, message archive, data retention.",
        "agent_rule": "Do not initiate conversations without explicit opt-in. Human escalation path must be available at all times.",
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
    google = snapshot.get("google", {})
    trust_contract = snapshot.get("trust_contract", {})
    tc_p0_blockers: list[str] = trust_contract.get("summary", {}).get("p0_blockers", [])
    inbox = snapshot.get("official_inbox", {}).get("summary", {})

    area = guard["area"]

    if area == "Business identity":
        trust_pages = google.get("trust_pages", [])
        about_ok = any(r.get("check") in {"About", "About Us"} and r.get("status") == "pass" for r in trust_pages)
        contact_ok = any(r.get("check") == "Contact" and r.get("status") == "pass" for r in trust_pages)
        if tc_p0_blockers and "Business identity" in tc_p0_blockers:
            return "needs_fix", "trust_contract P0 blocker: About/Contact not passing"
        if about_ok and contact_ok and settings.official_inbox_email:
            return "pass", f"About + Contact live; email {settings.official_inbox_email}"
        issues = []
        if not about_ok:
            issues.append("About page missing/broken")
        if not contact_ok:
            issues.append("Contact page missing/broken")
        if not settings.official_inbox_email:
            issues.append("official_inbox_email not set")
        return "needs_fix", "; ".join(issues)

    if area == "Consumer information before purchase":
        has_terms = _policy_exists(settings, "terms_of_service")
        has_shipping = _policy_exists(settings, "shipping_policy")
        shipping_page_ok = any(r.get("check") == "Shipping policy" and r.get("status") == "pass" for r in google.get("trust_pages", []))
        all_ok = has_terms and (has_shipping or shipping_page_ok)
        return (
            "pass" if all_ok else "needs_review",
            f"terms local: {has_terms}; shipping local: {has_shipping}; shipping page: {shipping_page_ok}",
        )

    if area == "Guarantees and returns":
        has_refund = _policy_exists(settings, "returns_refund_policy") or _policy_exists(settings, "refund_policy")
        refund_page_ok = any(r.get("check") == "Refund policy" and r.get("status") == "pass" for r in google.get("trust_pages", []))
        crypto_refund_url = str(getattr(settings, "crypto_refund_policy_url", "") or "")
        if tc_p0_blockers and "Returns and refunds" in tc_p0_blockers:
            return "needs_fix", "trust_contract P0: refund policy page not live"
        all_ok = (has_refund or refund_page_ok) and bool(crypto_refund_url)
        return (
            "pass" if all_ok else "needs_fix",
            f"refund local: {has_refund}; refund page: {refund_page_ok}; crypto_refund_url: {crypto_refund_url or 'not set'}",
        )

    if area == "Product safety":
        return "manual_pending", "Printify product safety specs must be collected per product type"

    if area == "Privacy and consent":
        has_privacy = _policy_exists(settings, "privacy_policy")
        tracking = inbox.get("tracking_mode", settings.official_email_tracking_consent_mode)
        return (
            "pass" if has_privacy else "needs_fix",
            f"privacy local: {has_privacy}; tracking mode: {tracking}",
        )

    if area == "Email marketing":
        unsub_url = str(settings.official_email_unsubscribe_url or "")
        ok = bool(settings.official_inbox_email) and bool(unsub_url)
        return ("pass" if ok else "needs_fix", f"sender: {settings.official_inbox_email}; unsubscribe: {unsub_url or 'not set'}")

    if area == "Payments and crypto":
        bitcoin_active = str(getattr(settings, "bitcoin_payments_enabled", "") or "").lower() == "true"
        crypto_refund_url = str(getattr(settings, "crypto_refund_policy_url", "") or "")
        if tc_p0_blockers and "Secure checkout" in tc_p0_blockers:
            return "needs_fix", "trust_contract P0: secure checkout not passing"
        if bitcoin_active and not crypto_refund_url:
            return "needs_fix", "bitcoin enabled but crypto_refund_policy_url not set"
        return "pass", f"bitcoin active: {bitcoin_active}; refund url: {crypto_refund_url or 'n/a'}"

    if area == "AI transparency":
        chat_enabled = str(getattr(settings, "agent_customer_chat_enabled", "") or "").lower() == "true"
        if chat_enabled:
            return "manual_pending", "AGENT_CUSTOMER_CHAT_ENABLED=true — verify AI disclosure in bot welcome message"
        return "pass", "customer chat disabled; no active disclosure risk"

    return "needs_review", ""


def customer_rows(settings: Any, snapshot: dict[str, Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for guard in CUSTOMER_GUARDS:
        status, evidence = _customer_status(settings, guard, snapshot)
        result.append({**guard, "type": "customer", "status": status, "current_evidence": evidence})
    return result


def supplier_rows(settings: Any) -> list[dict[str, str]]:
    configured: dict[str, bool] = {
        "Printify / production partners": bool(settings.printify_api_token and settings.printify_shop_id),
        "Shopify": bool(settings.shopify_store and settings.shopify_admin_token),
        "Payment providers": bool(settings.stripe_secret_key or settings.paypal_client_id or settings.crypto_payments_enabled),
        "Cloudflare Workers": bool(getattr(settings, "cloudflare_api_token", "") and getattr(settings, "cloudflare_account_id", "")),
        "OpenAI / Anthropic (AI services)": bool(settings.openai_api_key or getattr(settings, "anthropic_api_key", "")),
        "HeyGen / creative AI": bool(settings.heygen_api_key),
        "Meta / Instagram / Facebook": bool(settings.meta_access_token or settings.facebook_page_id),
        "Logistics/shipping partners": False,
        "WhatsApp Business / Telegram": bool(getattr(settings, "whatsapp_business_token", "") or settings.telegram_bot_token),
    }
    result: list[dict[str, str]] = []
    for guard in SUPPLIER_GUARDS:
        status = "active_needs_contract_review" if configured.get(guard["supplier"], False) else "planned_contract"
        result.append({**guard, "type": "supplier", "status": status})
    return result


def _skill_lines(customer: list[dict[str, str]], supplier: list[dict[str, str]]) -> list[str]:
    lines = [
        "---",
        "name: bakabo-legal-guardrails",
        "description: Legal/compliance guardrail skill for BKS Master Agent. Use when drafting customer replies, checking supplier contracts, reviewing privacy/payment compliance, or assessing Merchant appeal readiness.",
        f"store: {BAKABO_STORE_DOMAIN}",
        f"theme_id: {BKS_TM04_THEME_ID}",
        "related: [[bakabo-commercial-strategy]], [[bakabo-members]], [[bakabo-bitcoin-payments]]",
        "---",
        "",
        "# BKS Legal Guardrails",
        "",
        "Operational legal/compliance guardrails for BKS Master Agent.",
        "This is a checklist and evidence system, not legal advice.",
        "",
        "## Operating Rule",
        "",
        "The agent may draft customer replies, supplier checklists and compliance evidence.",
        "It must request Roberto review for: legal, privacy, payment, supplier contract, product safety, complaint and Merchant appeal actions.",
        "Never reduce customer statutory rights based on internal supplier limitations or made-to-order language.",
        "AI conversations with customers require disclosure, opt-in and human escalation path.",
        "",
        "## Customer Guarantees",
        "",
        "| Area | P | Trust gate | Status | Agent rule |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in customer:
        lines.append(
            f"| {row['area']} | {row.get('priority', '')} | `{row.get('trust_gate', '')}` "
            f"| `{row['status']}` | {row['agent_rule']} |"
        )
    lines.extend([
        "",
        "## Supplier / Producer Relationship Controls",
        "",
        "| Supplier | Risk | Trust gate | Status | Agent rule |",
        "| --- | --- | --- | --- | --- |",
    ])
    for row in supplier:
        lines.append(
            f"| {row['supplier']} | {row['risk']} | `{row.get('trust_gate', '')}` "
            f"| `{row['status']}` | {row['agent_rule']} |"
        )
    lines.extend([
        "",
        "## Approval Gate",
        "",
        "- Legal/privacy/payment/supplier/product safety actions require Roberto review before execution.",
        "- Supplier terms must cover: product quality, safety, traceability, defects, SLA, data processing and IP/licensing.",
        "- Customer statutory rights are never reduced by internal supplier limitations.",
        "- AI conversations with customers require disclosure, opt-in and human escalation path.",
        "",
        "## Sources",
        "",
        "- [EU Consumer Rights Directive](https://commission.europa.eu/law/law-topic/consumer-protection-law/consumer-contract-law/consumer-rights-directive_en)",
        "- [EU guarantees](https://europa.eu/youreurope/citizens/consumers/shopping/guarantees/index_en.htm)",
        "- [EU product safety / GPSR](https://commission.europa.eu/topics/business-and-industry/doing-business-eu/eu-product-safety-and-labelling/product-safety_en)",
        "- [EDPB consent guidance](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en)",
        "- [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)",
        "- [Google Merchant misrepresentation policy](https://support.google.com/merchants/answer/6150127?hl=it)",
        "- [EU AI Act](https://digital-strategy.ec.europa.eu/en/policies/european-approach-artificial-intelligence)",
        "",
    ])
    return lines


def write_skill(settings: Any, customer: list[dict[str, str]], supplier: list[dict[str, str]]) -> tuple[str, str]:
    skill_path = settings.root_dir / SKILL_DOC
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text("\n".join(_skill_lines(customer, supplier)), encoding="utf-8")

    legacy_path = settings.root_dir / LEGAL_DOC
    legacy_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_path.write_text("\n".join(_skill_lines(customer, supplier)), encoding="utf-8")

    return _relative(settings.root_dir, skill_path), _relative(settings.root_dir, legacy_path)


def write_sheets(settings: Any, customer: list[dict[str, str]], supplier: list[dict[str, str]]) -> tuple[str, str]:
    legal_sheet = settings.root_dir / LEGAL_SHEET
    legal_sheet.parent.mkdir(parents=True, exist_ok=True)
    legal_fields = ["type", "area", "priority", "trust_gate", "status", "requirement", "current_evidence", "evidence", "agent_rule", "source", "source_url"]
    with legal_sheet.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=legal_fields)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in legal_fields} for row in customer])

    supplier_sheet = settings.root_dir / SUPPLIER_SHEET
    supplier_sheet.parent.mkdir(parents=True, exist_ok=True)
    supplier_fields = ["type", "supplier", "relationship", "risk", "trust_gate", "status", "minimum_terms", "agent_rule"]
    with supplier_sheet.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=supplier_fields)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in supplier_fields} for row in supplier])

    return _relative(settings.root_dir, legal_sheet), _relative(settings.root_dir, supplier_sheet)


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    customer = customer_rows(settings, snapshot)
    suppliers = supplier_rows(settings)
    skill, _legacy = write_skill(settings, customer, suppliers)
    legal_sheet, supplier_sheet = write_sheets(settings, customer, suppliers)

    customer_pass = sum(1 for row in customer if row["status"] == "pass")
    p0_blockers = [row["area"] for row in customer if row.get("priority") == "p0" and row["status"] not in {"pass", "manual_pending"}]
    critical_review = [row["supplier"] for row in suppliers if row["risk"] == "critical" and "active" in row["status"]]
    next_action = next((row["area"] for row in customer if row["status"] not in {"pass", "manual_pending"}), "")
    merchant_appeal_blocked = bool(set(p0_blockers) & BLOCKING_AREAS)
    total = len(customer)

    return {
        "summary": {
            "customer_pass": customer_pass,
            "customer_needs": sum(1 for row in customer if row["status"] != "pass"),
            "percent_complete": round(customer_pass / total * 100) if total else 0,
            "p0_blockers": p0_blockers,
            "merchant_appeal_blocked": merchant_appeal_blocked,
            "next_action": next_action,
            "supplier_active": sum(1 for row in suppliers if row["status"].startswith("active")),
            "critical_supplier_review": critical_review,
            "status": "attention" if p0_blockers else "guarded",
            "skill": skill,
            "legal_sheet": legal_sheet,
            "supplier_sheet": supplier_sheet,
        },
        "customer": customer,
        "suppliers": suppliers,
        "approval_gate": [
            "Legal/privacy/payment/supplier/product safety actions require Roberto review before execution.",
            "Supplier terms must cover: product quality, safety, traceability, defects, SLA, data processing and IP/licensing.",
            "Customer statutory rights are never reduced by internal supplier limitations or made-to-order language.",
            "AI conversations with customers require disclosure, opt-in and human escalation path.",
        ],
    }
