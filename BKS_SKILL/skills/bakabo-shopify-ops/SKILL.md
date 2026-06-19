---
name: bakabo-shopify-ops
description: Use this skill for operational Shopify store management of bakabo.club that is NOT product copy or Printify enrichment. Triggers include launching a drop or collection, building/auditing the collection and navigation taxonomy, writing or reviewing policy pages (refund, shipping, privacy, terms), configuring markets/currencies/languages, managing the app stack, handling made-to-order inventory and fulfillment logistics, maintaining the homepage, or deciding which KPIs to track. Works alongside bakabo-brand (voice) and bakabo-product-copy (per-product structure). Do not use for writing individual product pages (use bakabo-product-copy) or fixing Printify-synced products (use bakabo-printify-sync).
---

# BakAbo — Shopify Operations

This skill covers store-level operations: launches, taxonomy, policies, markets, apps, fulfillment, homepage, and metrics. Per-product copy is handled by `bakabo-product-copy`; Printify enrichment by `bakabo-printify-sync`; voice always by `bakabo-brand`.

Two facts shape everything: BakAbo is **made-to-order** and **multi-market** (EU primary in EUR, plus US, Korea, and others). Both have operational and legal consequences throughout.

## 1. Drop / collection launch checklist

**T-minus (prep):**
- [ ] All products created, synced, and enriched (`bakabo-enriched` tag present on all)
- [ ] All products: correct Shopify Type, BKS taxonomy tags, GPC metafield set
- [ ] All handles clean: no ™, no emoji, no legacy Printify names
- [ ] All SEO titles/descriptions verified (140–160 chars, correct format)
- [ ] Free Shipping bullet removed from all product bodies (managed per-market in footer)
- [ ] Italian text removed from all product bodies (EN only)
- [ ] Collection page created with clean handle and 1–2 sentence intro
- [ ] All products assigned to correct collections
- [ ] Drop tag applied (`drop:catalog-reset-2026` or next drop identifier)
- [ ] Soundtrack selected from `bakabo-sound` (Rights OK = cleared)
- [ ] Homepage hero updated
- [ ] Navigation updated to surface the new collection

**Launch:**
- [ ] Products set to Active
- [ ] Collection set to visible
- [ ] Test full checkout in each active market/currency
- [ ] Test on mobile

**Post-launch:**
- [ ] Confirm ParcelPanel tracking firing on test order
- [ ] Monitor first 48h: traffic, add-to-cart, checkout completion
- [ ] Clear any `bakabo-needs-review` / `bakabo-ai-failed` products

## 2. Collection & navigation taxonomy

**Rule 1 — Clean collection handles.** The canonical collection URL is `/collections/[handle]` — short, lowercase, hyphenated. The keyword-stacked filter URLs (`/collections/x/TAG+TAG+TAG+...`) are Shopify tag-filter URLs. Never use them as canonical, never link externally, never put in sitemap. 301-redirect any indexed ones to the clean handle.

**Rule 2 — No emoji in structural names.** Collection names, menu labels, and handles contain no emoji. Emoji break SEO, accessibility, and editorial voice.

**Navigation structure** (max two levels):

```
MAN          WOMAN        ACCESSORIES    DROPS
 ├ Outerwear  ├ Dresses    ├ Bags         ├ Drop current
 ├ Tops       ├ Swim       ├ Footwear     └ Archive
 ├ Swim       ├ Lounge     └ Towels
 └ Footwear   └ Footwear
```

## 2b. Product title schema (BKS naming rule — from bakabo-brand)

**Single formula, no exceptions:**
```
BKS [Product Type] — [Collection]
```
Multiple products of the same type in same collection → add two-digit suffix:
```
BKS Athletic Shorts — Riviera 01
BKS Athletic Shorts — Riviera 02
```

**Correct examples:** `BKS Athletic Shorts — Flag`, `BKS Sneakers — Pulse`, `BKS Swim Trunks — Riviera`

**Forbidden:** ™ in title, emoji, legacy AI-generated names, adjectives like "Premium/Urban/Luxury", generic product type stacking (`BKS Pulse™ Urban Luxury Sneakers`).

**Applied 2026-06-19 — Athletic Shorts category (11 products):**
- Flag, Hours, Origin, Pulse, Token → single (no number suffix)
- Glyph 01/02, Marker 01/02, Riviera 01/02 → two products each, numbered
- **Next categories to align:** Sneakers, Swim Trunks, Hoodies, One-Piece Swimsuits, Lounge Pants

When creating or renaming any product, apply this schema first. Check for existing same-type products in the same collection before assigning a number.

---

## 3. Shipping threshold — multi-market management

**Critical:** Free Shipping thresholds vary by market and must **never** be hardcoded in product body copy. The `✈ Free Shipping on orders over €60` bullet has been removed from all product bodies.

Manage shipping thresholds exclusively in:
- Shopify Markets shipping settings (per market/currency)
- Footer sitewide banner or policy page
- Homepage service block

Known markets and their operational considerations:
- **Italy / EU:** EUR, VAT-inclusive pricing
- **International:** EUR or local currency via Shopify Markets
- **United States:** USD, pre-tax (tax at checkout)
- **Corea del Sud:** local currency

When setting shipping thresholds per market, use clean local numbers (not raw conversions). Test currency display, tax behavior, shipping cost, and full checkout before announcing.

## 4. Policy pages

| Page | Must cover | BakAbo specifics |
|---|---|---|
| **Shipping** | Carriers, zones, times, costs, tracking | Production lead time stated **separately** from shipping time; threshold varies by market |
| **Returns/Refund** | Window, condition, process, who pays | 30-day returns (more generous than 14-day EU minimum) |
| **Privacy** | GDPR: data collected, purpose, rights, contact | Cookie consent, data processor list: Shopify, Printify, ParcelPanel, payment providers |
| **Terms** | Sale terms, liability, jurisdiction | 2-Year EU warranty; Italian jurisdiction |

**Made-to-order legal nuance:** EU Consumer Rights Directive art. 16 allows exemption from withdrawal for goods made to consumer's specifications. BakAbo's products are printed-on-demand but generally not customized per individual buyer, so the exemption likely does **not** apply. The 30-day returns policy is both safer legally and better for the brand. Do not state the exemption applies without lawyer confirmation.

## 5. Made-to-order inventory & fulfillment

- **Inventory:** effectively unlimited (printed on demand). Do not let Shopify mark items "sold out" unless a blueprint is discontinued.
- **Lead time is a promise.** Production time stated on product pages must match Printify provider actual delivery. If times change, update product pages.
- **Lead times by category:**
  - Sneakers, Backpacks: 10–14 business days
  - Windbreakers, Puffers, Travel Bags, Swim Trunks: 7–10 business days
  - Special sublimation products (US assembly): 5–7 business days
- **Fulfillment chain:** order → Printify production → carrier → ParcelPanel tracking → customer
- **Returns of made-to-order goods:** 30-day policy applies. Each piece is produced individually — factor return rate into pricing, cannot easily resell returned printed items.

## 6. App stack

Keep minimal — every app is a cost, performance hit, and privacy/data-processor entry.

Current known apps:
- **ParcelPanel** — order tracking. Core to fulfillment chain.
- **Printify** — production (covered by `bakabo-printify-sync`).

Before adding any app: does it solve a real problem, does it duplicate native Shopify features, what is the monthly cost, does it add a GDPR data processor? Prefer native Shopify features over apps.

## 7. Homepage maintenance

On each drop:
- Update hero to current drop (image + `Enter [X]` / `Shop Drop 0X` CTA)
- Keep panel structure (the `◇ ◈ ▣` typographic system)
- Service commitments visible (30-Day Returns, AI-art, 2-Year EU Warranty) — Free Shipping managed per-market in footer/header, not hardcoded in homepage copy
- Never let an old drop sit as hero after a new one launches

## 8. KPIs

Track in priority order:

1. **Conversion rate** (sessions → orders) — master health metric
2. **Checkout completion** (reached checkout → paid) — catches friction in payment/shipping/tax
3. **Add-to-cart rate** — catches product-page or pricing problems
4. **AOV** (average order value) — watch vs free-shipping threshold per market
5. **Return rate by product** — high rate on made-to-order erodes margin fast
6. **Traffic source mix** — where buyers actually come from
7. **Production-to-ship time (actual)** — does it match promised lead time?

## 9. Operational cadence

- **Per drop:** §1 launch checklist
- **Weekly:** check KPIs, clear review-tag products, confirm tracking firing
- **Monthly:** audit handles for ™/emoji/legacy creep, review app stack cost, check production times vs promises
- **Quarterly:** review policy pages for legal currency, review market/currency/tax config, audit Free Shipping thresholds per market
