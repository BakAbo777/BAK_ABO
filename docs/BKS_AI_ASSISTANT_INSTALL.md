# BKS AI Assistant Install

## Purpose

Customer-facing AI assistant for the Shopify theme. It is designed to answer only from BKS data, store policies and safe public guidance.

## Files

- `sections/bks-ai-assistant.liquid`
- `BKS_AI_ASSISTANT_GOOGLE_TRUST_NOTE.md`

## Activation

1. Add the section `BKS AI assistant` to the theme.
2. Keep it disabled until the public endpoint is reachable over HTTPS.
3. Set `Public API endpoint` to: `not configured yet`
4. Set `Public routing token` only if the endpoint expects one.
5. Enable the section after verifying a test question about shipping, refunds and product availability.

## Current runtime flags

- `AGENT_CUSTOMER_CHAT_ENABLED`: false
- `BKS_ASSISTANT_PUBLIC_ENDPOINT`: not configured yet

## Required guardrails

- Always disclose that it is an AI assistant.
- Do not collect card details, passwords or payment data.
- Do not promise discounts, availability or delivery beyond the product page and checkout.
- Link to official policies for shipping, refunds, privacy and terms.
- Log customer questions as learning signals without storing sensitive personal data.
