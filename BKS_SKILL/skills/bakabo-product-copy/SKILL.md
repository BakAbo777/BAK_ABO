---
name: bakabo-product-copy
description: Use this skill whenever creating, rewriting, or reviewing Shopify product content for the BakAbo / BKS store (bakabo.club). Triggers include writing product titles, descriptions, bullet specs, meta title and meta description for SEO, image alt text, URL handles, product tags, and collection page intros. Also use when auditing an existing product page for SEO or structure. This skill defines structure and SEO rules; for tone of voice, the bakabo-brand skill applies simultaneously. Do not use for non-product copy (newsletters, ads, policies).
---

# BakAbo — Product Copy & SEO

This skill defines the **anatomy, SEO rules, and structural patterns** for every product page on bakabo.club. Tone of voice is handled by the `bakabo-brand` skill — both skills should be active when writing product content.

## 1. Anatomy of a BakAbo product page

Every product page follows this exact six-block structure, in this order:

```
1. PRODUCT TITLE         (one line)
2. HERO LINE             (one sentence, italic, identity statement)
3. DESCRIPTION           (2–3 short sentences)
4. SPEC BLOCK            (bullet list: Material · Fit/Capacity · Print · Care)
5. MADE-TO-ORDER BLOCK   (mandatory, always present)
6. SERVICE BULLETS       (standard, never edited per-product)
```

Anything outside these six blocks does not belong on the page.

## 2. Block-by-block template

### Block 1 — Product Title

Format: `BKS [Design System]™ [Product Type]`

- ✅ `BKS Hours Cipher™ Sneakers`
- ✅ `BKS Folklore Rogue™ Backpack`
- ✅ `BKS Marker Brush™ Windbreaker Jacket`
- ❌ `Amazing AI-Art Sneakers Limited Edition 2025 🔥`
- ❌ `BKS BakAbo Mediterranean Lines Luxury Sneakers Streetwear Designer`

**Title naming pattern by category:**
- Sneakers: `BKS [Collection] [Design]™ Sneakers`
- Backpack: `BKS [Collection] [Design]™ Backpack`
- Travel Bag: `BKS [Collection] [Design]™ Travel Bag`
- Windbreaker: `BKS [Collection] [Design]™ Windbreaker Jacket`
- Puffer: `BKS [Collection] [Design]™ Puffer` (no "Jacket" — keep short)
- Swim Trunks: `BKS [Collection] [Design]™ Swim Trunks`

Length: **max 60 characters** including spaces.

### Block 2 — Hero line

One italic sentence that names what the piece *is* in BakAbo's voice. Not a feature, not a benefit — an identity.

- ✅ *Low-top canvas built on the visual language of BKS Hours.*
- ✅ *Backpack in a midnight shoal — gold fish adrift in the dark, one red among them.*
- ✅ *Windbreaker jacket in a painted foliage field — impressionist brushwork over terracotta geometry.*

### Block 3 — Description

Two to three sentences. Cover, in this order:
1. **What it is** — silhouette, construction
2. **What makes it BakAbo** — the print, the design system, the AI-art origin
3. **Where/how it lives** — context of use, not "perfect for"

### Block 4 — Spec block

Always in this order, always these labels. Vary the fourth label by product type:

**Sneakers / Footwear:**
```
· Material: [composition]
· Fit: [Regular / Relaxed] — [fit note]
· Print: [AOP / placement]
· Care: [washing instruction]
```

**Bags / Backpacks / Travel Bags:**
```
· Material: [composition]
· Comfort: [carry system]
· Capacity: [dimensions/volume/compartments]
· Closure: [zipper / magnetic / etc.]
· Care: [cleaning instruction]
```

**Outerwear (Windbreaker / Puffer):**
```
· Material: [composition]
· Fit: [Regular / Relaxed] — [fit note]
· Closure: [zipper type]
· Pockets: [description]
· Cuffs: [description]
· Print: [AOP / placement]
· Care: [washing instruction]
```

### Block 5 — Made-to-Order block

Mandatory. Only EN on bakabo.club (removed Italian from all product bodies):

**EN:**
> *Made to order. Each piece is printed and assembled for you after purchase. Allow [X–X] business days for production before shipping.*

Lead times by category:
- Sneakers / Backpacks: 10–14 business days
- Windbreakers / Puffer Jackets / Travel Bags: 7–10 business days
- Swim Trunks: 7–10 business days

### Block 6 — Service bullets

**Never include** the Free Shipping bullet in the product body — shipping thresholds vary by market. The service block is:

```
↩  30-Day Returns, hassle-free
✦  Printed on demand, never overstocked
✓  2-Year EU Warranty
```

> **Critical:** Free Shipping thresholds differ by market (Italy, International, US, Korea). Never hardcode a shipping threshold in product body copy. Manage it in the footer/policy pages only.

## 3. SEO fields (Shopify-specific)

### URL handle

- **Lowercase**, hyphens only, no spaces, no special characters, **no ™ symbol**
- **3–5 words maximum**
- No `bks-` prefix unless handle conflicts require disambiguation

**Handle conflicts — resolution protocol:**
When Shopify returns "handle already in use", prepend `bks-` or the collection name:
- `hours-cipher-sneakers` taken → try `bks-hours-cipher-sneakers`
- `folklore-tide-sneakers` taken → `bks-folklore-tide-sneakers`
- `bks-coral-sneakers` taken → `folklore-coral-sneakers` (use collection)

Always set a 301 redirect when changing an existing live handle.

**Legacy Printify handle patterns to always replace:**
- Emoji handles: `mythicharmonia-bks-👾swim-trunks` → `marker-flux-swim-trunks`
- Designer-name handles: `artistica-dashielle-low-top` → `marker-hybrid-sneakers`
- Product-description handles: `navy-floral-waterproof-travel-bag-weekender-duffle-with-elegant-blue-damask-print` → `folklore-manor-travel-bag`
- Number handles: `waterproof-travel-bag-998` → `riviera-stripe-travel-bag`
- ™ in handle: `bks-coral™-sneakers` → remove ™

### Meta title (Page title in Shopify SEO tab)

Format: `[Product Title] — BakAbo`

- **Max 60 characters**
- Separator is em-dash ` — ` (not hyphen)
- No emoji, no symbols, no ALL CAPS
- Must match the product Title exactly (no diverging names)

Examples:
- ✅ `BKS Hours Cipher™ Sneakers — BakAbo` (37 chars)
- ✅ `BKS Folklore Rogue™ Backpack — BakAbo` (38 chars)
- ❌ `BKS Digital Citizens™ BUZZ - Low Top Sneakers | Bakabo Club` (wrong format + old name)
- ❌ `BKS Folklore Tide™ Sneakers BakAbo` (missing em-dash)

### Meta description

- **140–160 characters**, one or two sentences
- Pattern: `AOP [product type] from the BKS [Collection] collection. [Key visual/print detail]. [Material/format note]. Made to order.`
- Must NOT contain: exclamations, prices, promo codes, emoji, old Printify names
- End on a substantive note, not a CTA

Examples by category:
- Sneakers (141): `AOP sneakers from the BKS Hours collection. Hyperrealist graphic field, edge-to-edge digital print, low-top canvas silhouette. Made to order.`
- Backpack (140): `AOP backpack from the BKS Glyph collection. Bone diamond grid on deep black, hand-drawn in register. 13L, four compartments. Made to order.`
- Travel Bag (143): `AOP waterproof travel bag from the BKS Marker collection. Urban assemblage — a face emerging from layered ochre fields, edge to edge. Made to order.`
- Windbreaker (148): `AOP windbreaker from the BKS Marker collection. Painterly foliage field in yellow, green and orange, bold chevron in black and white. Made to order.`
- Puffer (142): `AOP puffer from the BKS Folklore collection. Folk block-print grid of carnations and tulips in red, cobalt and white on deep black. Made to order.`
- Swim Trunks (140): `AOP swim trunks from the BKS Glyph collection. Geometric embroidery code in gold and navy, edge-to-edge. Quick-dry fabric, made to order.`

### Image alt text

- **One sentence**, under 125 characters
- Describe what is visible, not what you want to rank for
- Different alt text per image
- Pattern by shot:
  - **Front**: `BKS [Product]™ [key visual description], front view`
  - **Back**: `BKS [Product]™, back view showing [detail]`
  - **Detail**: `Close-up of [specific feature] on BKS [Product]™`
  - **Model**: `Model wearing BKS [Product]™ in [setting]`

## 4. Product tags (Shopify) — BKS taxonomy

Tags are for internal filtering and merchandising. Apply all that fit in this exact format (lowercase, colon-separated, no spaces):

```
brand:bks
collection:[collection-name]
series:[series-name]
macro:man
macro:woman
print-type:aop
status:active
type:[product-type]
use-case:[use-case]
curation:keep
drop:catalog-reset-2026
bakabo-enriched
```

**Collection → Series mapping:**
| Collection tag | Series tag |
|---|---|
| `collection:folklore` | `series:naif` |
| `collection:riviera` | `series:islands` |
| `collection:flag` | `series:neo-dada` |
| `collection:hours` | `series:hyperrealism` |
| `collection:marker` | `series:neo-expressionism` |
| `collection:token` | `series:arcade` |
| `collection:pulse` | `series:optical` |
| `collection:glyph` | `series:brut` |

**Type tags by product:**
| Product | `type:` tag |
|---|---|
| Sneakers | `type:shoes` |
| Backpack | `type:backpack` |
| Travel Bag | `type:travel-bag` |
| Windbreaker | `type:outerwear` |
| Puffer | `type:outerwear` |
| Swim Trunks | `type:swimwear` |

**Use-case tags by product:**
| Product | `use-case:` tag |
|---|---|
| Sneakers, Outerwear | `use-case:streetwear` |
| Swim Trunks | `use-case:beachwear` |
| Travel Bag, Backpack | `use-case:travel` or `use-case:streetwear` |

**Placement tags** (only when applicable):
- `placement-front` — for products with a front placement illustration
- `placement-back` — for products with a back placement illustration

**Special tags to never use in product taxonomy:**
- Bare `aop` (use `print-type:aop`)
- Emoji or symbols in tags
- Product title in tags (e.g. `BKS Flag Bloc™ Swim Trunks` as a tag — this happened and breaks filtering)
- Free-form designer names or old Printify tags

## 5. Google Product Category (GPC metafield)

Always set this metafield on every product:

| Product type | GPC value |
|---|---|
| Sneakers | `Apparel & Accessories > Shoes` |
| Backpack | `Apparel & Accessories > Handbags, Wallets & Cases > Backpacks` |
| Travel Bag | `Apparel & Accessories > Handbags, Wallets & Cases > Luggage` |
| Windbreaker / Puffer | `Apparel & Accessories > Clothing > Outerwear > Coats & Jackets` |
| Swim Trunks | `Apparel & Accessories > Clothing > Swimwear` |

## 6. Shopify Type field

| Product | Type value |
|---|---|
| Sneakers | `Shoes` |
| Backpack | `Backpack` |
| Travel Bag | `Travel Bag` |
| Windbreaker / Puffer | `Outerwear` |
| Swim Trunks | `Swimwear` |

**Never use:** `All Over Prints` (this is Printify's internal label, not a Shopify product type).

## 7. Category metafields (Shopify standard taxonomy)

These metafields power Google Shopping and Shopify search. Apply per product category:

### Sneakers
```
Footwear material:   canvas; synthetic; rubber; leather
Activity:            universal
Age group:           adults
Care instructions:   soft-bristled-brush; hand-wash
Closure type:        lace-up
Heel height type:    flat
Occasion style:      casual
Shoe features:       100-nylon-canvas; soft-foam-insole; pleather-round-toe; breathable-design; cushioned; lightweight
Shoe fit:            regular; wide
Shoe size:           [US sizes only — no EU values]
Sneaker style:       low-top; fashion
Target gender:       unisex
Toe style:           round
```

**Shoe size — US only:** Values must use US sizing format (`4`, `4-5`, `5`, ..., `14`). EU values (36, 38, 40, 42...) must be removed from this field — they belong in the EU size guide table in the body HTML, not in the metafield.

### Backpacks & Travel Bags
```
Bag/Case material:          polyester; mesh (backpack) | polyester; waterproof-coating (travel bag)
Bag/Case closure:           zipper
Bag/Case features:          lightweight; padded-straps; adjustable-size (backpack) | waterproof; lightweight; adjustable-size (travel bag)
Bag/Case storage features:  laptop-sleeve; front-pocket; side-pocket; built-in-compartments
Care instructions:          soft-bristled-brush; hand-wash
Carry options:              backpack-straps; shoulder-straps; top-handle; adjustable-straps
Luggage/Bag closure:        zipper
```

### Color metafield
Derived from the actual print description — not from generic Printify color codes. Avoid non-standard internal codes (`gft-6`, `vfr-54`, `ciano-b`, `acqua-2`, `gold-8`). Use descriptive terms:

| Instead of | Use |
|---|---|
| `ciano-b` | `cyan` or `teal` |
| `gold-8` | `gold` |
| `vfr-54` | `navy` or `cobalt` (inspect actual color) |
| `acqua-2` | `aqua` or `teal` |
| `gft-6` | `geometric` + actual color names |

## 8. CSV bulk import — audit checklist

When working with Shopify export CSVs for bulk correction:

**Critical checks per product row:**
- [ ] Title starts with `BKS`, contains `™`, max 60 chars
- [ ] Handle: lowercase, hyphens only, no ™, no emoji, no legacy Printify names
- [ ] SEO Title: matches product title exactly, ends ` — BakAbo`, max 60 chars
- [ ] SEO Description: 140–160 chars, no old names, no emoji, correct format
- [ ] Type: correct Shopify type (not `All Over Prints`)
- [ ] Tags: BKS taxonomy format, includes `series:*`, `collection:*`, `status:active`
- [ ] GPC metafield: correct category string
- [ ] Color metafield: no internal codes
- [ ] Shoe size metafield: US values only
- [ ] Body HTML: EN only, no Italian, no Free Shipping bullet, no old names
- [ ] No duplicate products (same title with different legacy handles)

**Duplicate detection and resolution:**
When a CSV contains duplicate product titles (same title, different handles), keep the version with:
1. The correct/preferred handle format
2. The most complete SEO data
3. The most complete tags

Remove the inferior duplicate along with all its variant rows.

## 9. Collection page intros

Every collection landing page gets a 1–2 sentence intro placed above the grid.

Pattern:
> *[Collection Name]. [One line on the design system or series]. [One line on the product range].*

## 10. Self-check before saving

- [ ] Title under 60 chars, follows `BKS [Collection] [Design]™ [Type]` pattern
- [ ] Hero line is one italic sentence, not a feature list
- [ ] Description is 2–3 sentences, mentions AI-art origin once
- [ ] Spec block format matches the product category
- [ ] Made-to-order block present, EN only, correct lead time
- [ ] Service bullets: no Free Shipping, only Returns/Printed-on-demand/Warranty
- [ ] URL handle: 3–5 words, no ™, no emoji, no legacy names
- [ ] Meta title under 60 chars, ends ` — BakAbo`, matches product title
- [ ] Meta description 140–160 chars
- [ ] Every image has unique alt text
- [ ] Tags follow BKS taxonomy, include `series:*`
- [ ] GPC metafield set
- [ ] Type field correct (not `All Over Prints`)
