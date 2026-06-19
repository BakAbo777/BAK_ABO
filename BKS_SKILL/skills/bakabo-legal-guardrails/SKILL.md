---
name: bakabo-legal-guardrails
description: Legal/compliance guardrail skill for BKS Master Agent. Use when drafting customer replies, checking supplier contracts, reviewing privacy/payment compliance, or assessing Merchant appeal readiness.
store: bakabo.club
theme_id: 202392961362
related: [[bakabo-commercial-strategy]], [[bakabo-members]], [[bakabo-bitcoin-payments]]
---

# BKS Legal Guardrails

Operational legal/compliance guardrails for BKS Master Agent.
This is a checklist and evidence system, not legal advice.

## Operating Rule

The agent may draft customer replies, supplier checklists and compliance evidence.
It must request Roberto review for: legal, privacy, payment, supplier contract, product safety, complaint and Merchant appeal actions.
Never reduce customer statutory rights based on internal supplier limitations or made-to-order language.
AI conversations with customers require disclosure, opt-in and human escalation path.

## Customer Guarantees

| Area | P | Trust gate | Status | Agent rule |
| --- | --- | --- | --- | --- |
| Business identity | p0 | `trust_foundation` | `needs_fix` | Do not hide BKS identity or imply affiliation with another brand. Do not request Merchant review while About/Contact are broken. |
| Consumer information before purchase | p0 | `trust_foundation` | `pass` | Every campaign must link to matching product/collection and official policies. |
| Guarantees and returns | p0 | `trust_foundation` | `pass` | Never tell a customer statutory rights are excluded by made-to-order language. Crypto refund policy URL must be set. |
| Product safety | p1 | `collection_identity` | `manual_pending` | Escalate safety complaints immediately and pause product promotion until reviewed by Roberto. |
| Privacy and consent | p0 | `trust_foundation` | `pass` | Use open/click/mobile signals only when transparent, lawful and not sensitive. Never store PII from AI conversations without consent. |
| Email marketing | p0 | `collection_identity` | `pass` | No deceptive subject lines, no fake urgency, no marketing after opt-out. Require Roberto approval before any campaign send. |
| Payments and crypto | p0 | `conversion_support` | `pass` | Bitcoin is optional payment only — never a financial promise. Crypto refund policy URL must be set and accessible before any crypto-related promotion. |
| AI transparency | p1 | `collection_identity` | `pass` | Never impersonate a human. Always disclose AI identity in the first message of any customer conversation. Offer human handoff path. |

## Supplier / Producer Relationship Controls

| Supplier | Risk | Trust gate | Status | Agent rule |
| --- | --- | --- | --- | --- |
| Printify / production partners | critical | `trust_foundation` | `active_needs_contract_review` | Keep product traceability by SKU/order/provider. Escalate defects before promoting affected products. |
| Shopify | critical | `trust_foundation` | `active_needs_contract_review` | Do not bypass Shopify checkout for payment or personal data. Theme publishes require Roberto confirmation. |
| Payment providers | critical | `conversion_support` | `active_needs_contract_review` | Payment method changes require human approval and customer disclosure. Crypto refund policy must be live before crypto is promoted. |
| Cloudflare Workers | high | `trust_foundation` | `planned_contract` | bks-agent-refresh Worker runs at 12:00 CET. Do not store personal customer data in Worker KV without DPA. |
| OpenAI / Anthropic (AI services) | high | `trust_foundation` | `active_needs_contract_review` | Anonymize customer context before sending to AI APIs. Never send order IDs, emails or payment data in prompts. |
| HeyGen / creative AI | medium | `collection_identity` | `active_needs_contract_review` | Do not use customer likeness or private data for avatar training without explicit written consent. |
| Meta / Instagram / Facebook | high | `campaign_layer` | `active_needs_contract_review` | Autonomous campaigns remain draft/supervised until google_trust_contract P0 is green. Never run retargeting without consent. |
| Logistics/shipping partners | high | `trust_foundation` | `planned_contract` | Do not promise delivery dates beyond verified carrier/Shopify checkout data. |
| WhatsApp Business / Telegram | medium | `collection_identity` | `planned_contract` | Do not initiate conversations without explicit opt-in. Human escalation path must be available at all times. |

## Approval Gate

- Legal/privacy/payment/supplier/product safety actions require Roberto review before execution.
- Supplier terms must cover: product quality, safety, traceability, defects, SLA, data processing and IP/licensing.
- Customer statutory rights are never reduced by internal supplier limitations.
- AI conversations with customers require disclosure, opt-in and human escalation path.

## Sources

- [EU Consumer Rights Directive](https://commission.europa.eu/law/law-topic/consumer-protection-law/consumer-contract-law/consumer-rights-directive_en)
- [EU guarantees](https://europa.eu/youreurope/citizens/consumers/shopping/guarantees/index_en.htm)
- [EU product safety / GPSR](https://commission.europa.eu/topics/business-and-industry/doing-business-eu/eu-product-safety-and-labelling/product-safety_en)
- [EDPB consent guidance](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en)
- [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)
- [Google Merchant misrepresentation policy](https://support.google.com/merchants/answer/6150127?hl=it)
- [EU AI Act](https://digital-strategy.ec.europa.eu/en/policies/european-approach-artificial-intelligence)
