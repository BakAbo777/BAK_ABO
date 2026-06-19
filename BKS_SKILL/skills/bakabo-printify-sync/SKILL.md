---
name: bakabo-printify-sync
description: Use this skill whenever a product has been synced from Printify to the BakAbo Shopify store (bakabo.club) and needs enrichment, or when designing/maintaining the Make.com automation that performs this enrichment. Triggers include any mention of "Printify just pushed a product", "the product came in empty", "fix this synced product", "missing size chart", "missing specs", "missing SEO", "color names are wrong", or any request to build, edit, or document the Printify-to-Shopify workflow. This skill operates alongside bakabo-brand (voice) and bakabo-product-copy (structure). Do not use this skill for products created manually in Shopify from scratch — those go through bakabo-product-copy only.
---

# BakAbo — Printify → Shopify Enrichment

This skill solves a specific operational problem: products published from Printify arrive in Shopify with **critical fields missing or wrong**. It also covers bulk CSV correction of existing catalog data.

Products missing enrichment can be identified by these signals:
- Handle contains emoji, numbers, or legacy designer names (e.g. `mythicharmonia-bks-👾swim-trunks`, `artistica-dashielle-low-top`, `waterproof-travel-bag-998`)
- SEO Title is `nan` or contains old Printify product names
- Type field is `All Over Prints` instead of the correct Shopify type
- Tags contain bare `aop` instead of `print-type:aop`, or contain free-form text
- GPC metafield is empty
- Body HTML contains Italian text or Free Shipping bullet

## PART A — Manual enrichment (per product)

### A.1 What the user must provide

1. **Shopify product handle or URL**
2. **Printify product type** — determines size chart and spec defaults
3. **BKS Collection and Design name** — e.g. `Folklore / Bloom`, `Token / Vault`
4. **Variant list as received from Printify** — colors and sizes
5. **Materials** — from the Printify blueprint page if not auto-transferred
6. **Target language** — EN only for product body (IT removed from all bodies)

### A.2 Size chart library

Output as HTML table, placed between the Spec block and Made-to-Order block.

#### Sneakers — EU / US / UK conversion

| EU | US (M) | US (W) | UK |
|---|---|---|---|
| 36 | 4 | 5.5 | 3.5 |
| 38 | 5.5 | 7 | 5 |
| 40 | 7 | 8.5 | 6.5 |
| 42 | 8.5 | 10 | 8 |
| 44 | 10 | 11.5 | 9.5 |
| 46 | 11.5 | 13 | 11 |

> **Shoe size metafield:** The `Shoe size` metafield accepts **US values only**. EU values (36, 38, 40, 42, 44, 46) belong in the size chart table in the body HTML — never in the metafield. Clean EU values out of the metafield on every enrichment.

#### Unisex T-Shirts / Hoodies / Sweatshirts (cm)

| Size | Chest | Length | Sleeve |
|---|---|---|---|
| XS | 46 | 66 | 19 |
| S | 51 | 70 | 21 |
| M | 56 | 73 | 22 |
| L | 61 | 76 | 23 |
| XL | 66 | 79 | 25 |
| XXL | 71 | 81 | 26 |

#### Swimwear — Trunks (Men) and One-Piece (Women) (cm)

| Size | Waist (M) | Bust (W) | Hips (W) |
|---|---|---|---|
| S | 76–81 | 82–86 | 88–92 |
| M | 81–86 | 86–90 | 92–96 |
| L | 86–91 | 90–96 | 96–102 |
| XL | 91–97 | 96–102 | 102–108 |

#### Bags / Travel Bags — fixed dimensions

No size chart. Use a dimensions block:
- **Backpack:** 13L main compartment, front pocket, side bottle pocket, internal laptop sleeve
- **Travel Bag:** Large main compartment, front pocket, side pockets; waterproof coating

### A.3 Spec blocks by product type

**Sneakers (canvas AOP low-top):**
```
· Material: Canvas upper, synthetic leather toe cap, vulcanized rubber cupsole
· Fit: Regular — true to size. Half-size up for wide feet.
· Print: All-over digital print, edge-to-edge on canvas panels
· Care: Wipe clean with warm water and dish soap. Do not machine wash.
```

**Backpack:**
```
· Material: 100% lightweight polyester — durable, shape-retaining, quick-dry
· Comfort: Padded mesh back panel and straps for breathable carry
· Capacity: 13L main pocket, front pocket, side bottle pocket, internal laptop sleeve
· Closure: Durable zipper closures, adjustable shoulder straps
· Care: Remove all items. Pre-treat stains. Clean with warm water and mild detergent using a soft brush. Air dry.
```

**Waterproof Travel Bag:**
```
· Material: 100% polyester with waterproof coating
· Capacity: Large main compartment, front pocket, side pockets
· Closure: Durable zipper closures
· Carry: Top handle and adjustable shoulder strap
· Care: Wipe clean with damp cloth and mild detergent. Air dry.
```

**Windbreaker (zip-up, hood, standard construction):**
```
· Material: 100% polyester shell, mesh lining
· Fit: Relaxed — size up for layering
· Print: All-over, edge-to-edge digital print
· Care: Machine wash 30°C, gentle cycle. Do not tumble dry. Do not iron.
```

**Windbreaker (sublimation, elastic cuffs, US-assembled):**
```
· Material: 100% polyester, 4.8 oz/yd² — lightweight and quick-drying
· Construction: Water- and wind-resistant shell, full front zipper closure
· Pockets: Two front pockets
· Cuffs: Elastic for secure fit
· Print: All-over sublimation print, assembled in USA from globally sourced parts
· Care: Machine wash cold 30°C, gentle cycle. Tumble dry low. Do not iron.
```

**Puffer Jacket:**
```
· Material: 100% polyester shell, black quilted lining
· Fit: Regular — true to size [or: Regular, unisex-cut]
· Closure: Full-length zip with stand-up collar
· Pockets: Two front zip pockets
· Cuffs: Elastic with [color/accent description]
· Print: All-over, edge-to-edge digital print [or: placement-specific description]
· Care: Machine wash 30°C. Do not tumble dry. Do not iron. Do not bleach.
```

**Swim Trunks:**
```
· Material: Quick-dry recycled polyester
· Fit: Regular — true to size
· Print: All-over digital print, edge-to-edge
· Care: Rinse in fresh water after use. Hang dry. Do not machine wash.
```

### A.4 Made-to-Order block

**EN only** (Italian removed from all product bodies):

> *Made to order. Each [piece/pair/bag/jacket] is printed and assembled for you after purchase. Allow [X–X] business days for production before shipping.*

Lead times:
- Sneakers, Backpacks: **10–14 business days**
- Windbreakers, Puffers, Travel Bags, Swim Trunks: **7–10 business days**
- Special sublimation windbreakers/puffers (US assembly): **5–7 business days**

### A.5 Service block

**No Free Shipping bullet** — threshold varies by market. Use only:

```
↩  30-Day Returns, hassle-free
✦  Printed on demand, never overstocked
✓  2-Year EU Warranty
```

### A.6 SEO field generation

Follow `bakabo-product-copy` §3. For Printify-synced products specifically:

- **Meta title** — `BKS [Collection] [Design]™ [Type] — BakAbo`, max 60 chars
- **Meta description** — 140–160 chars
- **URL handle** — `[collection]-[design]-[type]`, no ™, no emoji, no Printify legacy names
- If handle conflicts, prepend `bks-` or use collection name as disambiguation

**Old handle → New handle reference (catalog-reset-2026):**
| Old | New |
|---|---|
| `mythicharmonia-bks-👾swim-trunks` | `marker-flux-swim-trunks` |
| `artistica-dashielle-low-top` | `marker-hybrid-sneakers` |
| `carlo-colorbrush-low-top` | `folklore-coral-sneakers` |
| `navy-floral-waterproof-travel-bag-weekender-...` | `folklore-manor-travel-bag` |
| `waterproof-travel-bag-998` | `riviera-stripe-travel-bag` |
| `messina-bks💼waterproof-travel-bag` | `glyph-stride-travel-bag` |
| `bks-coral-sneakers` (conflict) | `folklore-coral-sneakers` |
| Any handle with ™ | Remove ™ from handle |
| Any handle with emoji | Replace entirely |

### A.7 Color metafield

Values must be descriptive, not internal codes. Standard clean-up:

| Remove | Replace with |
|---|---|
| `ciano-b`, `ciano-t`, `ciano-2` | `cyan`, `teal`, or `cobalt` |
| `gold-8`, `gold-f` | `gold` |
| `vfr-54` | `navy` or inspect actual color |
| `acqua`, `acqua-2` | `aqua` or `teal` |
| `gft-6`, `gft-6-1` | inspect and use actual color name |
| `viol-b`, `vba-78` | `violet` or `lavender` |
| `r-6903` | `red` or `crimson` |
| `blue-f` | `cobalt` or `royal blue` |
| `ce-45` | `teal` or inspect |
| `camouflage` (on non-camo products) | actual dominant color |

### A.8 Tag taxonomy

Follow `bakabo-product-copy` §4 exactly. Key rules:
- Never use bare `aop` — use `print-type:aop`
- Always include `series:*` — map from collection
- Always include `status:active`
- Never include product title as a tag
- Never include legacy Printify names or free-form text
- Max 12–13 tags per product (not 15 — keep it tight)

### A.9 Intruder product detection

When processing a CSV file, check that every product row belongs to the correct category. Known contaminations:
- Sneaker products appearing in windbreaker/puffer CSV exports
- `BKS Digital Citizens™ - Low Top Sneakers` appearing in bag/jacket exports

Remove intruder rows before processing.

---

## PART B — Bulk CSV enrichment

### B.1 Workflow for bulk CSV correction

```
1. Load CSV → identify products (Title notna() rows)
2. Audit: handle, SEO Title, SEO Description, Type, Tags, GPC, Color
3. Detect duplicates (same Title, different handles)
4. Resolve duplicates: keep preferred handle version, drop inferior
5. Apply fixes: handle_map, title_fix, seo_data, tags, metafields
6. Validate: no errors on all fields
7. Export corrected CSV → zip for import
```

### B.2 Deduplication strategy

When a product appears twice with different handles (common in early catalog):
- Keep the version with the **correct/preferred handle** (clean, no ™, no legacy)
- Keep the version with **more complete SEO data**
- Drop the inferior version along with **all its variant rows** (identified by matching handle in Title=NaN rows)

### B.3 Field validation rules

| Field | Rule |
|---|---|
| Title | Starts with `BKS`, contains `™`, max 60 chars |
| Handle | Lowercase, hyphens only, no `™`, no emoji, no legacy patterns |
| SEO Title | Contains product title, ends ` — BakAbo`, max 60 chars |
| SEO Description | 140–160 chars, no emoji, no old names |
| Type | Must be correct Shopify type, never `All Over Prints` |
| Tags | Must contain `series:*`, `collection:*`, `status:active` |
| GPC | Must be set with correct category string |
| Body HTML | EN only, no Italian, no Free Shipping bullet, no old product names |

---

## PART C — Make.com automation

### C.1 Scenario flow

```
Printify webhook (product published)
         ↓
Fetch full product from Printify API
         ↓
Check if "bakabo-enriched" tag exists → if yes, skip
         ↓
AI Module 1: Generate description + spec block
         ↓
AI Module 2: Generate SEO fields (title, description, handle)
         ↓
AI Module 3: Map Printify colors to BKS names
         ↓
AI Module 4: Select size chart template
         ↓
Build full body_html with all six blocks
         ↓
PUT to Shopify API → update product
         ↓
Add "bakabo-enriched" tag
```

### C.2 AI prompts — production-ready

#### Prompt 1 — Description generation

```
You are writing a product page for BakAbo (bakabo.club), a contemporary
fashion brand. Tone: editorial, minimal, urban-luxury. No exclamations,
no emoji in body copy, no "amazing/stunning/perfect for".

Product data:
- Type: {{product_type}}
- BKS Collection: {{collection_name}}
- Design name: {{design_name}}
- Material: {{material}}
- Print method: {{print_method}}

Generate in EN only. Structure:
1. HERO LINE — one italic sentence, identity statement
2. DESCRIPTION — 2–3 sentences: what it is, AI-art origin, context
3. SPEC BLOCK — bullets: Material, Fit/Capacity, Print, Care

Output as JSON only (no preamble):
{
  "hero": "...",
  "description": "...",
  "spec_material": "...",
  "spec_fit": "...",
  "spec_print": "...",
  "spec_care": "..."
}
```

#### Prompt 2 — SEO fields

```
Generate SEO fields for a BakAbo product page.
Rules:
- Meta title: max 60 chars, "BKS [System]™ [Type] — BakAbo"
- Meta description: 140–160 chars, pattern:
  "AOP [type] from the BKS [collection] collection. [visual detail]. Made to order."
- URL handle: 3–5 words, lowercase, hyphens, no ™, no emoji

Product: {{product_title}}
Collection: {{collection}}
Key visual: {{hero_description}}

Output as JSON only:
{
  "meta_title": "...",
  "meta_description": "...",
  "handle": "..."
}
```

#### Prompt 3 — Color mapping

```
Map Printify color codes to BakAbo descriptive names.
Rules: English only, descriptive terms, no internal codes.

Replace these known codes:
ciano-b → cyan, gold-8 → gold, vfr-54 → navy,
acqua → aqua, camouflage → use actual dominant color,
gft-6 → inspect actual color, viol-b → violet

Printify variants: {{color_list}}
Design system context: {{design_name}}

Output as JSON array:
[{"printify": "...", "bakabo": "..."}]
```

### C.3 Error handling

1. **Printify API timeout** → retry once (30s delay), then tag `bakabo-needs-review`
2. **AI returns invalid JSON** → Try/Catch in Make.com, log to Google Sheet, tag `bakabo-ai-failed`
3. **Shopify update fails** → exponential backoff (3 attempts), then tag `bakabo-update-failed`

Never let a half-enriched product go live. The `bakabo-enriched` tag is the contract.

---

## D — Pre-publish checklist

- [ ] Title: `BKS [Collection] [Design]™ [Type]`, max 60 chars, starts with BKS
- [ ] Handle: clean, no ™, no emoji, no legacy Printify patterns
- [ ] Body HTML: six-block structure, EN only, no Italian, no Free Shipping bullet
- [ ] Spec block: correct format for product category
- [ ] Made-to-Order: present, correct lead time
- [ ] Service bullets: Returns + Printed-on-demand + Warranty only
- [ ] Meta title: under 60 chars, ends ` — BakAbo`, matches product title
- [ ] Meta description: 140–160 chars
- [ ] All images: unique alt text
- [ ] Type: correct Shopify type (not `All Over Prints`)
- [ ] Tags: BKS taxonomy, includes `series:*`, `collection:*`, `status:active`, `bakabo-enriched`
- [ ] GPC metafield: correct category string
- [ ] Color metafield: no internal codes
- [ ] Shoe size metafield (sneakers): US values only, no EU
- [ ] Product assigned to correct collections
- [ ] No intruder products from other categories in the export
