---
name: bakabo-shopify-theme-auditor
description: >
  BKS Shopify theme auditor for bakabo.club TM04.
  Use this skill for: full theme audit, finding broken links, verifying schema
  validity, checking mobile CSS, auditing templates/sections/snippets, and
  generating a prioritized fix list.
  Works with bakabo-ui-ux-pro-max (quality gate) and bakabo-page-by-page (page spec).
metadata:
  type: skill
  version: "1.0"
  created: "2026-06-24"
---

# BKS Shopify Clean Theme Auditor

## Audit scope — 10 areas

### 1. Navigation
- Header: single header, correct menu handle (`main-menu-1` → fallback `main-menu`)
- Menu: dropdown subitems present for Collections (8) and Product Types (16)
- Footer: 4 policy links + contact + Track Order + social icons
- Mobile drawer: hamburger opens/closes, submenus expand

### 2. Template coverage
- Each of 8 collections has a `collection.bks-*.json` template
- Each of 8 collections has a `page.bks-*.json` editorial page
- Each product type has a `page.bks-[type].json` page
- `list-collections.json` is the `/collections` route
- `page.bks-verse.json` covers BKS Verse
- `index.json` is the homepage

### 3. Section schema validity
- All section `.liquid` files have valid `{% schema %}` blocks
- No `url` type settings with `default` values (Shopify 422 error)
- All block types used in templates are defined in their section schema

### 4. Liquid correctness
- No `href="#"` anchor links (broken)
- All `collections[handle]` lookups have fallback: `/collections/` + handle
- No undefined variables without `| default`
- No `color-mix()` CSS without Webkit prefix (Safari < 16 compatibility)

### 5. Product grid
- `main-collection-product-grid` section present on all collection pages
- `enable_filtering: true` set
- `columns_desktop: 4`, `columns_mobile: "2"`
- `products_per_page: 36`

### 6. Canonical taglines (must match)
```
bks-hours:   "Measured urban stillness"
bks-origin:  "Invented narrative marks"
bks-glyph:   "Constructed signs"
bks-marker:  "Gesture and motion"
bks-riviera: "Coastal geometry"
bks-pulse:   "Optical movement"
bks-token:   "Digital objects"
bks-flag:    "Graphic fields"
```
Any other tagline is a bug.

### 7. BKS Verse
- `bks-verse-intro.liquid` deployed and in italiano
- `page.bks-verse.json` has 3 sections: intro → submit → leaderboard
- All verse section text in Italian (no English)

### 8. SEO
- Theme `<title>` and `<meta description>` in `theme.liquid`
- JSON-LD structured data: `bks-json-ld.liquid` present
- `robots.txt.liquid`: OAI-SearchBot allowed
- No emoji in collection handles

### 9. CSS / Performance
- `bks-member.css`, `bks-cart.css`, `bks-responsive.css`, `bks-dynamic-theme.css` loaded
- No `!important` overload in global CSS
- Mobile viewport meta: `width=device-width,initial-scale=1`
- Images: `loading="lazy"` on below-fold images

### 10. Member system
- Gold ring CSS on account icon (header)
- Tier-aware CTAs in member dashboard
- `bks-member-dashboard.liquid` section present

---

## Audit output format

For each issue found:

```
[PRIORITY] AREA — Description
File: path/to/file.liquid (line N)
Impact: what breaks
Fix: specific change needed
```

Priority levels:
- `[P0]` — Broken (page doesn't load / href="#" / 404)
- `[P1]` — Visible bug (wrong text / broken layout)
- `[P2]` — Quality (contrast / mobile / performance)
- `[P3]` — Enhancement (missing feature / UX improvement)

---

## Quick audit script

```bash
# Check for href="#" in all template files
grep -r 'href="#"' "04_TEMA_SHOPIFY/_merged_tm04/"

# Check for wrong Origin tagline
grep -r "Roots, marks" "04_TEMA_SHOPIFY/_merged_tm04/"
grep -r "Roots, Marks" "04_TEMA_SHOPIFY/_merged_tm04/"

# Check for missing section types
grep -rL "bks-collection-signal" "04_TEMA_SHOPIFY/_merged_tm04/templates/collection.bks-*.json"

# Check for url default values (causes Shopify 422)
grep -rn '"type": "url"' "04_TEMA_SHOPIFY/_merged_tm04/sections/" | head -20
```
