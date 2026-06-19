# BKS Network Monitor

Updated: 2026-06-18T17:51:34+00:00

## What The Agent Watches

- DNS storefront: apex, www, MX, SPF, DKIM, DMARC.
- DSN/email delivery: bounce capture, TLS sending, unsubscribe readiness, reputation checks.
- HTTPS endpoints: storefront, policies, contact, sitemap, assistant endpoint.
- Data suffixes: UTM, click IDs and consent-sensitive email/read signals.

## Current Priority

1. Add or verify DMARC for `bakabo.club`:
   `v=DMARC1; p=none; rua=mailto:crew@bakabo.club; adkim=s; aspf=s`
2. Keep SPF as a single record containing every sender used by BKS.
3. Keep DKIM active for the real sending provider.
4. Configure IMAP for `crew@bakabo.club` so DSN/bounces can enter the Knowledge DB.
5. Keep UTM/click suffixes for analytics only; canonical URLs must stay clean.

## Rules

- The agent can monitor DNS/network status without approval.
- DNS changes, email sending scale, paid ads and customer outreach require human approval.
- Tracking is never a substitute for truth: prices, offers, stock, delivery and policies must match the storefront.
