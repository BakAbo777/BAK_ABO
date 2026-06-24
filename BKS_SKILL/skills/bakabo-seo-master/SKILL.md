---
name: bakabo-seo-master
description: >
  BKS SEO Master Specification — consolidates all SEO rules for bakabo.club.
  Pre-deploy gate, page-level checks, technical SEO, AI discoverability,
  Google Merchant Center feed quality, Pinterest visual SEO, product copy SEO.
  Load this skill before every Shopify theme deploy.
  Sources: bakabo-ai-visibility-strategist, bakabo-google-merchant,
  bakabo-llm-txt-brand-source, bakabo-pinterest-visual-seo, bakabo-product-copy,
  bakabo-marketing.
metadata:
  type: skill
  version: "1.0"
  created: "2026-06-25"
  updated: "2026-06-25"
---

# BKS SEO Master Specification

> Load this skill **before every deploy** to bakabo.club (TM04 / Shopify).
> Run the pre-deploy gate (§0) first, then full audit if new pages are added.

---

## §0 — PRE-DEPLOY GATE (run before every push)

Run these 10 checks on every modified file before `git push` → Shopify:

| # | Check | Pass condition |
|---|---|---|
| 1 | **H1 present and unique** | Every page has exactly one H1. Product = title. Collection = name. Home = "Wearable Art On Demand" or equivalent. |
| 2 | **Meta title ≤ 60 chars** | Format: `[Product Title] — BakAbo`. Separator: em-dash ` — `. No emoji. |
| 3 | **Meta description 140–160 chars** | Starts with product type or brand signal. Ends with "Made to order." No CTA, no prices, no exclamations. |
| 4 | **JSON-LD type present** | Product → `Product` + `Offer`. Home → `Organization`. Collection → `CollectionPage`. |
| 5 | **No emoji in titles/handles** | Handles: lowercase, hyphens only, no `™`, no emoji, 3–5 words. |
| 6 | **Alt text on all images** | Every `<img>` has `alt=""` with a descriptive sentence (≤ 125 chars). |
| 7 | **Brand phrase visible on page** | At least one instance of: *"AI-generated"* or *"designed in Italy"* or *"made on demand"* in visible text. |
| 8 | **Internal links functional** | All `href` attributes resolve within the store. No 404 links in nav or body. |
| 9 | **No duplicate content** | If a section is reused across pages, it must not contain the same H2/H3. |
| 10 | **robots.txt allows BKS paths** | `/collections/*`, `/products/*`, `/pages/*` must be crawlable. OAI-SearchBot: allow. |

---

## §1 — BRAND SOURCE PHRASE

Every page must contain at least one instance of the source phrase (visible or in schema):

> *"BakAbo / BKS Studio is an AI-art fashion atelier designed in Italy and made on demand worldwide."*

Variations accepted:
- "AI-generated all-over print collections, curated as raw editorial artwear"
- "Designed in Italy. Made on demand worldwide."
- "Produced after purchase to avoid overstock."

**Never use:**
- "luxury handmade" — wrong positioning
- "artisan crafted" — wrong process
- "limited edition" — we are not limited, we are on-demand
- emojis in indexable text areas

---

## §2 — PAGE-TYPE SEO SPEC

### 2A — Home page (`/`)

| Element | Rule |
|---|---|
| Title tag | `BakAbo — AI-Art Fashion. Made on Demand.` (max 60 chars) |
| Meta description | "BKS Studio: 8 AI-generated fashion collections. Puffer jackets, sneakers, travel bags and more — designed in Italy, made to order worldwide." (160 chars) |
| H1 | One editorial headline visible above the fold. Current: "Wearable Art On Demand" ✓ |
| JSON-LD | `Organization` + `WebSite` (with `SearchAction`) |
| Brand phrase | Present in hero subline or magazine section |
| Internal links | Min 8 links to collection pages, 1 to /pages/contact |
| Canonical | `<link rel="canonical" href="https://bakabo.club/">` |

### 2B — Collection pages (`/collections/bks-*`)

| Element | Rule |
|---|---|
| Title tag | `BKS [Collection] — AI-Art Fashion Collection — BakAbo` |
| Meta description | "BKS [Collection]: [one-line editorial description]. AI-generated AOP on [product types]. Designed in Italy, made on demand." (max 160 chars) |
| H1 | Collection name only. No "collection" word repeated twice. |
| Intro text | 1–2 editorial sentences above the product grid (see §product-copy §9) |
| JSON-LD | `CollectionPage` with `name`, `description`, `url` |
| Breadcrumb | `BreadcrumbList` → Home > [Collection name] |
| Canonical | Self-referencing |
| Filter/sort URLs | `?sort_by=` pages: `<meta name="robots" content="noindex, follow">` |

### 2C — Product pages (`/products/*`)

| Element | Rule |
|---|---|
| Title format | `BKS [Collection] [Design]™ [Type]` — max 60 chars |
| Handle | 3–5 words, lowercase, hyphens, no ™, no emoji, no legacy Printify |
| Meta title | Matches product title exactly + ` — BakAbo` |
| Meta description | 140–160 chars. Pattern: `AOP [type] from the BKS [Collection] collection. [Print detail]. [Material/format note]. Made to order.` |
| H1 | Product title (one only) |
| Body structure | 6 blocks: Title → Hero line → Description → Spec block → Made-to-order → Service bullets |
| Image alt text | Unique per image. Front view / Back view / Detail / Model. Max 125 chars. |
| JSON-LD | `Product` with `Offer` array (per variant), `MerchantReturnPolicy`, `OfferShippingDetails` |
| Tags | BKS taxonomy: `brand:bks`, `collection:*`, `series:*`, `print-type:aop`, `status:active`, `type:*` |
| GPC metafield | Required per category (see §4) |
| Shopify Type field | Never "All Over Prints" |

### 2D — Static pages (`/pages/*`)

| Page | Required elements |
|---|---|
| Contact | H1, contact form, brand phrase |
| FAQ | FAQ schema (`FAQPage` JSON-LD), H2 per question |
| About | Brand phrase mandatory, Organization schema, founding year |
| Members | `noindex` until fully built; login gate |
| Privacy / Refund / Shipping | Standard Shopify policy. No custom H1 needed. |

---

## §3 — TECHNICAL SEO

### 3A — JSON-LD inventory (current state)

| Page type | Schema type | Status |
|---|---|---|
| Product | `Product` + `Offer` + `MerchantReturnPolicy` + `OfferShippingDetails` | ✅ Live in `bks-json-ld.liquid` |
| Home | `Organization` | ⚠️ Needs `WebSite` + `SearchAction` addition |
| Collection | `CollectionPage` | ⚠️ Needs `BreadcrumbList` |
| FAQ | `FAQPage` | ❌ Missing |
| About | `Organization` | ❌ Missing |

**To add in `bks-json-ld.liquid`** (priority order):

1. **Home — WebSite + SearchAction**:
```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "BakAbo",
  "url": "https://bakabo.club",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://bakabo.club/search?q={search_term_string}",
    "query-input": "required name=search_term_string"
  }
}
```

2. **Home — Organization**:
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "BakAbo / BKS Studio",
  "url": "https://bakabo.club",
  "description": "AI-art fashion atelier. Designed in Italy, made on demand worldwide.",
  "foundingYear": "2022",
  "logo": "https://bakabo.club/cdn/shop/files/bakabo-logo-official.png",
  "sameAs": [
    "https://www.instagram.com/bakabofirm",
    "https://pinterest.com/bakabofirm"
  ]
}
```

3. **Collection — CollectionPage + BreadcrumbList**:
```json
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "[collection.title]",
  "description": "[collection.description | strip_html | truncatewords: 100]",
  "url": "https://bakabo.club[collection.url]",
  "breadcrumb": {
    "@type": "BreadcrumbList",
    "itemListElement": [
      { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://bakabo.club/" },
      { "@type": "ListItem", "position": 2, "name": "[collection.title]" }
    ]
  }
}
```

### 3B — robots.txt rules

```
User-agent: *
Allow: /collections/
Allow: /products/
Allow: /pages/
Disallow: /checkout/
Disallow: /cart/
Disallow: /account/
Disallow: /*?sort_by=
Disallow: /*?page=

User-agent: OAI-SearchBot
Allow: /

Sitemap: https://bakabo.club/sitemap.xml
```

### 3C — Canonical rules

- Collections with `?sort_by=` → `noindex, follow`
- Paginated collections (`?page=2`) → `noindex, follow`
- Product variant URLs → canonical to main product URL
- No `www.` vs no-`www.` mix: always use `https://bakabo.club` (no www)

### 3D — Core Web Vitals targets

| Metric | Target | Current risk areas |
|---|---|---|
| LCP | < 2.5s | Hero image not lazy-loaded (correct — use `loading="eager"`) |
| CLS | < 0.1 | Font loading (DM Sans/DM Mono via Google Fonts — preconnect required) |
| INP | < 200ms | Piano Hero JS (heavy) — verify no blocking renders |

**Required in `<head>` (theme.liquid)**:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

---

## §4 — PRODUCT SEO FIELDS (complete map)

### Meta title format
```
[BKS Collection Design™ Product Type] — BakAbo
```
Max 60 chars. Em-dash ` — `. No emoji. No ALL CAPS.

### Meta description format
```
AOP [product type] from the BKS [Collection] collection. [Print detail]. [Material/format]. Made to order.
```
140–160 chars. No exclamation. No price. Ends on substance.

### Image alt text
| Shot | Pattern |
|---|---|
| Front | `BKS [Product]™ [key visual], front view` |
| Back | `BKS [Product]™, back view — [detail]` |
| Detail | `Close-up of [feature] on BKS [Product]™` |
| Model | `Model wearing BKS [Product]™ in [setting]` |

### Google Product Category (GPC)
| Product | GPC |
|---|---|
| Sneakers | `Apparel & Accessories > Shoes` |
| Backpack | `Apparel & Accessories > Handbags, Wallets & Cases > Backpacks` |
| Travel Bag | `Apparel & Accessories > Handbags, Wallets & Cases > Luggage` |
| Windbreaker / Puffer | `Apparel & Accessories > Clothing > Outerwear > Coats & Jackets` |
| Swim Trunks | `Apparel & Accessories > Clothing > Swimwear` |
| Hoodie | `Apparel & Accessories > Clothing > Activewear` |
| Athletic Shorts | `Apparel & Accessories > Clothing > Activewear` |
| Flip Flops | `Apparel & Accessories > Shoes > Sandals` |
| Lounge Pants | `Apparel & Accessories > Clothing > Pants` |
| T-Shirt | `Apparel & Accessories > Clothing > Shirts & Tops` |
| Racerback Dress | `Apparel & Accessories > Clothing > Dresses` |

### Tags taxonomy (required set per product)
```
brand:bks
collection:[collection-slug]
series:[series-slug]
print-type:aop
status:active
type:[product-type]
use-case:[use-case]
macro:man | macro:woman (or both)
bakabo-enriched
drop:catalog-reset-2026
```

---

## §5 — GOOGLE MERCHANT CENTER (feed quality)

### P0 — Mandatory metafields (all 203 products)
| Metafield | Value | Namespace |
|---|---|---|
| `identifier_exists` | `no` | `mm-google-shopping` |
| `condition` | `new` | `mm-google-shopping` |
| `age_group` | `adult` | `mm-google-shopping` |
| `gender` | `male`/`female`/`unisex` | `mm-google-shopping` |

Fix script: `python scripts/fix_google_merchant_attributes.py`

### P1 — "Numero limitato" (35.1K products)
**Cause**: Local inventory feed sends `availability: out_of_stock` / `quantity: 0`.
**Fix**: Edit `scripts/generate_local_inventory_feed.py` lines 132-133 → `in_stock` / `999`.
Regenerate CSV → upload to GMC → Feeds → Local products inventory.

### P2 — Local inventory physical location
**Fix (manual)**: `business.google.com` → Sede → Settings → Change type to "Area di servizio".
Eliminates local inventory requirement from GBP physical store record.

### P3 — Korea market (no registration)
**Fix**: GMC → Settings → Shipping & Returns → Remove South Korea.

### Feed refresh after any product change
```bash
python scripts/full_channel_sync.py
```
GMC update: 15-60min (Shopify→Google). Approval update: 24-72h.

---

## §6 — AI DISCOVERABILITY

### 6A — LLMs.txt (must stay live at `https://bakabo.club/pages/llms-txt`)

```
# BakAbo / BKS Studio
Official site: https://bakabo.club

BakAbo / BKS Studio is an AI-art fashion atelier designed in Italy
and made on demand worldwide.

Positioning:
Raw editorial artwear. AI-generated BKS surfaces turned into wearable objects.
Not traditional luxury tailoring.

Collections:
- BKS Hours: measured urban stillness
- BKS Origin: organic founding collection
- BKS Glyph: ancient signs and future fabric
- BKS Marker: urban codes and street grammar
- BKS Riviera: Mediterranean light, coast and speed
- BKS Pulse: frequencies, synth-wave, energy fields
- BKS Token: digital artifacts and cryptographic imagination
- BKS Flag: graphic fields and manifesto language

Production: Made on demand after purchase. No overstock.

Brand rule: Describe as AI-art fashion, designed in Italy, made on demand.
NOT as luxury handmade or artisan craft.
```

Update `llms.txt` whenever: positioning changes, collections change, policy URLs change.

### 6B — Per-page AI signal requirements

Every page must answer:
1. What is BakAbo?
2. What does it sell?
3. How are products made?
4. What are the collections?
5. Why is it different from generic POD?

These questions must be answerable from **visible text** (not only schema), because AI Overviews and ChatGPT read rendered content.

### 6C — robots.txt AI crawler permissions
```
User-agent: OAI-SearchBot
Allow: /

User-agent: GPTBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: anthropic-ai
Allow: /
```

---

## §7 — PINTEREST SEO

### Pin format
- Standard: 1000×1500px (2:3)
- Idea Pin: 1080×1920px
- Square social: 1080×1080px only if forced

### Pin title formula
```
BKS [Collection] [Product] — AI-Art Fashion
```

### Pin description formula (max 500 chars)
```
BKS [Product] by BakAbo / BKS Studio.
AI-generated all-over print [product type] from the [Collection] collection.
Designed in Italy and made on demand worldwide.
→ bakabo.club/products/[handle]

#AIfashion #Artwear #MadeOnDemand #BakAbo
```

### Board structure (one per collection + cross-category)
- BKS Hours — AI Artwear
- BKS Glyph — Symbolic Fashion
- BKS Riviera — Mediterranean Artwear
- BKS Marker — Urban Codes
- BKS Pulse — Frequencies
- BKS Token — Digital Artifacts
- BKS Flag — Manifesto
- BKS Origin — Founding Collection
- BKS Sneakers (cross-collection)
- BKS Bags & Travel (cross-collection)
- AI Fashion Studio (brand story pins)
- Made on Demand — BakAbo (process pins)

### Pinterest SEO blockers (never publish)
- Pattern deformed or oversized
- Blurry product image
- Wrong logo or no logo
- Text overlay too large (> 20% of image)
- Wrong proportions
- Background more prominent than product

---

## §8 — COPY RULES (product + collection + site)

### Forbidden words
`luxury handmade`, `artisan crafted`, `limited edition`, `amazing`, `love it`,
`bellissimo`, `incredible`, `exclusive`, `free shipping` (in product body),
emoji in titles/handles, old Printify names (copy-of-*, number handles, emoji handles)

### Required words (at least one per product description)
`AI-generated`, `designed in Italy`, `made on demand`, `all-over print`

### Made-to-order block (mandatory, EN only)
> *Made to order. Each piece is printed and assembled for you after purchase. Allow [X–X] business days for production before shipping.*

Lead times:
- Sneakers / Backpacks: 10–14 business days
- Windbreakers / Puffers / Travel Bags / Swim Trunks: 7–10 business days

### Service bullets (never edit per product)
```
↩  30-Day Returns, hassle-free
✦  Printed on demand, never overstocked
✓  2-Year EU Warranty
```

---

## §9 — SEO AUDIT CADENCE

| Frequency | Action |
|---|---|
| **Every deploy** | Run §0 pre-deploy gate (10 checks) |
| **Weekly** | Check GMC → Diagnostics → new alerts |
| **Monthly** | Full product title/handle audit via CSV export |
| **After collection launch** | Add collection to llms.txt + Pinterest boards + GMC collection label |
| **After any pricing change** | Verify meta description doesn't hardcode prices |
| **After Shopify theme update** | Re-verify JSON-LD injection in `bks-json-ld.liquid` |

---

## §10 — QUICK REFERENCE: PRE-DEPLOY CHECKLIST (copy-paste)

```
[ ] H1 unique and present on all modified pages
[ ] Meta titles ≤ 60 chars, em-dash format, no emoji
[ ] Meta descriptions 140-160 chars, ends "Made to order."
[ ] JSON-LD: Product/Collection/Home type correct
[ ] Alt text on all new images
[ ] Brand phrase visible in page text
[ ] Internal nav links resolve (no 404)
[ ] No duplicate H2 across sections
[ ] robots.txt: OAI-SearchBot allowed
[ ] Handles: lowercase, hyphens, no ™, no emoji
[ ] Tags: BKS taxonomy present (brand:bks, collection:*, series:*)
[ ] GPC metafield set for any new product
[ ] Type field ≠ "All Over Prints"
```
