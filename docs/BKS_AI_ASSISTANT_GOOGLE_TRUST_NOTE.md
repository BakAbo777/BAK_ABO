# BKS AI Assistant - Google Trust Note

This file explains why the customer-facing assistant is a trust feature, not a misleading sales device.

## Position

BKS AI Assistant is designed as a transparent customer support layer. It identifies itself as AI, uses the BKS knowledge database and official store policies, and avoids unverified product, price or availability claims.

## Google Merchant alignment

- Clear identity: the assistant says it is the BKS AI Assistant and does not impersonate a human, Google, Shopify or another brand.
- Relevant information before purchase: shipping, refunds, privacy, terms and contact routes are linked from official store pages.
- No misleading offers: the assistant does not invent discounts, countdowns, scarcity, certifications or partnerships.
- No unavailable offers: product price and availability are delegated to the product page and checkout.
- No sensitive data collection: it does not ask for card data, passwords or private payment information.
- Human handoff: support questions can be routed to the contact page or human support.

## Evidence to keep

- Theme section: `sections/bks-ai-assistant.liquid`
- Knowledge database: `ecommerce_automation/database.db`, table `agent_knowledge`
- Assistant protocol: `output/dialogic_agent_protocol.json`
- Google trust contract: `output/google_trust_contract.csv`

## Sources used for policy framing

- Google Merchant misrepresentation policy: https://support.google.com/merchants/answer/6150127?hl=it
- Google Merchant product data specification: https://support.google.com/merchants/answer/7052112
