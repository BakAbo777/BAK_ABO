---
name: bakabo-official-inbox
description: Supervise crew@bakabo.club communications — triage, draft, compliance, escalation.
metadata:
  type: skill
  trust_gate: trust_foundation
  store: bakabo.club
---

# bakabo-official-inbox — crew@bakabo.club

Official skill for supervising `crew@bakabo.club` communications.

## Mission

The agent monitors official email, classifies messages, drafts replies, records learning signals and escalates sensitive cases. It must not send risky customer, privacy, payment, complaint or legal replies without human review.

## Transparent marketing rule

Every marketing intervention must be clear about sender identity, reason for contact, unsubscribe path, real offer terms and final checkout authority for price/availability.

## Consent-aware signals

Email opened, clicked, returned from smartphone, or website revisit signals are useful only when they are transparent, lawful and connected through consented campaign IDs or aggregate analytics. The agent uses them to prioritize helpful follow-up, not to pressure customers.

## Response loop

1. Read official inbox metadata and permitted content.
2. Classify message category.
3. Search Knowledge DB for product/policy/evidence.
4. Draft answer in the customer's language.
5. Apply transparency/compliance checks.
6. Ask approval when the case is sensitive or promotional.
7. Save outcome to Knowledge DB.

## Sources

- [FTC CAN-SPAM compliance guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)
- [EDPB GDPR consent guidelines](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en)
- [Google Merchant misrepresentation policy](https://support.google.com/merchants/answer/6150127?hl=it)
