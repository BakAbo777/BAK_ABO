---
name: bakabo-editorial-typographer
description: >
  BKS editorial typography and page layout system. Use this skill for: composing product cards,
  designing hero sections, auditing page layouts for editorial consistency, placing type over images,
  deciding font size/weight/spacing for any BKS page, fixing "patchwork" or "confusing" layouts.
  Works with bakabo-armocromia (color), bakabo-photo-studio (photography), bakabo-theme-build (code).
metadata:
  type: skill
  version: "2.0"
  created: "2026-06-19"
  replaces: "v1 (fired — correct rules but applied per-collection instead of as unified system)"
---

# BKS Editorial Typographer Skill v2
## One voice. Every page.

The v1 skill had good composition rules but the implementation allowed typography to vary
per-collection, reinforcing the patchwork effect. 

**The rule: typography must be a unified system. The reader should never feel they changed publication.**

---

## 1. Core Philosophy

> A fashion magazine has ONE voice across ALL pages. What changes is the photograph, not the typeface.

Three principles that override everything:

1. **Silence is luxury.** If in doubt, reduce. Less type, more air, bigger product.
2. **Hierarchy before decoration.** A layout is broken when the eye doesn't know where to go first.
3. **Consistency creates authority.** Change fonts within a brand and it reads as amateurism.

---

## 2. BKS Type System — The Only Fonts in Use

| Font | Variable | Role |
|---|---|---|
| **Bebas Neue** | `--font-heading-family` | Display headlines ONLY — never for body |
| **DM Sans** | `--font-body-family` | Product names, navigation, body text, CTAs |
| **DM Mono** | `--bks-font-mono` | All metadata: prices, labels, kickers, chips, tags |

**This is the complete type palette. No exceptions. No Google Fonts additions.**

---

## 3. Typography Scale — Exact Values

| Role | Font | Size | Weight | Letter-spacing | Line-height |
|---|---|---|---|---|---|
| **Page title / Hero** | Bebas Neue | 64–96px | 400 | -0.01em | 0.95 |
| **Collection name** | Bebas Neue | 40–64px | 400 | 0 | 1.0 |
| **Section head** | DM Sans | 28–40px | 700 | -0.015em | 1.1 |
| **Product name (card)** | DM Sans | 14–16px | 500 | 0 | 1.3 |
| **Body text** | DM Sans | 14–16px | 400 | 0 | 1.65 |
| **Navigation** | DM Mono | 13–14px (0.85–0.88rem) | 500 | 0.10em | 1.0 |
| **Kicker / eyebrow** | DM Mono | 10–11px | 600 | 0.22–0.28em | 1.0 |
| **Price** | DM Mono | 14–15px | 600 | 0 | 1.0 |
| **Label / chip / tag** | DM Mono | 10–11px | 500 | 0.14em | 1.0 |
| **Caption / metadata** | DM Mono | 11px | 400 | 0.06em | 1.5 |
| **Button** | DM Mono | 12–13px | 600 | 0.14em | 1.0 |

### Hard Rules:
- **Bebas Neue = display and collection names ONLY.** Never use it for body, labels, prices.
- **Navigation must be DM Mono at 0.85–0.88rem (13–14px).** Never below 13px.
- **Never mix more than 2 sizes within one card.**
- **Letter-spacing on display: negative.** Letter-spacing on labels/kickers: positive.
- **Price always uses `font-variant-numeric: tabular-nums`.**
- **No italic except pull-quotes.** Italic = editorial quote only.

---

## 4. Grid System — 12 Columns

```
Page width: 1600px max
Gutter: 8px (spacing_grid_horizontal in settings_data.json)
Margins: clamp(20px, 4vw, 80px)

Desktop layouts:
  Hero full-bleed:    12 cols
  2-column feature:   5 + 7 or 6 + 6
  Product grid:       3 cols (4 products/row) or editorial 4+3+5
  Sidebar + main:     3 + 9

Mobile:
  Single column: all sections
  Product grid: 2 cols

Tablet:
  Product grid: 2–3 cols
```

**Editorial product grid on collection pages:**
Row 1: cols 1-5 (large) + cols 6-9 (medium) + cols 10-12 (small)
Row 2: cols 1-4 (small) + cols 5-8 (medium) + cols 9-12 (large)
→ The asymmetry creates editorial rhythm. Not a uniform 3-col grid.

---

## 5. The 5 BKS Layout Schemes

### Scheme A — DROP (product card)
```
┌─────────────────────────────────┐
│  BKS Studio · Collection name   │  ← kicker: DM Mono 10px, 0.24em, muted
│                                 │
│   ┌───────────────────────────┐ │
│   │                           │ │
│   │     PRODUCT (centered)    │ │  ← 60-70% of card height
│   │                           │ │
│   └───────────────────────────┘ │
│                                 │
│  Product Name in DM Sans 14px   │  ← 500 weight
│  € PRICE in DM Mono 14px        │  ← tabular-nums
└─────────────────────────────────┘
```
Use: product card, catalog grid, Piano Hero panel

---

### Scheme B — FLOAT (collection hero)
```
┌────────────────┬────────────────┐
│                │                │
│  COLLECTION    │                │
│  NAME in       │                │
│  Bebas 56px    │  PRODUCT       │
│                │  (right col,   │
│  Editorial     │   oversized,   │
│  copy in       │   bleeds top)  │
│  DM Sans 15px  │                │
│                │                │
│  CTA button    │                │
└────────────────┴────────────────┘
```
Use: collection hero, homepage feature. Product in right 7 cols, copy in left 5 cols.

---

### Scheme C — STAMP (product feature)
```
┌─────────────────────────────────┐
│  ┌─────────────────────────┐    │
│  │                         │    │  ← 1px ink border
│  │  PRODUCT                │    │
│  │                         │    │
│  │  BKS GLYPH   Sneakers   │    │  ← reversed bar: ink BG, sand text
│  └─────────────────────────┘    │
│  Caption in DM Mono 11px        │
└─────────────────────────────────┘
```
Use: product pop-out cards, editorial panels

---

### Scheme D — BLEED (hero banner)
```
┌─────────────────────────────────┐
│                                 │
│       PRODUCT FILLS FRAME       │  ← bleeds to edges
│                                 │
│  BKS · GLYPH      € 149        │  ← type in negative space
│  DM Mono 11px      DM Mono 15px │
└─────────────────────────────────┘
```
Use: hero banners, full-width sections, Instagram.
Rule: identify negative space BEFORE placing type. Never cover product detail.

---

### Scheme E — NEWSPAPER (product grid row)
```
┌──────┬──────┬──────┬──────┐
│  A   │  B   │  C   │  D   │  ← equal height columns
│      │      │      │      │
│ slug │ slug │ slug │ slug │  ← DM Mono 10px chip
│      │      │      │      │
│  €   │  €   │  €   │  €   │  ← DM Mono 14px, tabular
└──────┴──────┴──────┴──────┘
     ← 1px ink column rules →
```
Use: product grid rows, collection browse. No card shadows — flat newspaper.

---

## 6. Section Layout Rules — Rhythm

**Every page is a sequence: Dark → Light → Dark.**

```
HEADER          #fafaf7 / transparent sticky
HERO            #0a0a0a (dark, full-width, Bebas headline)
PRODUCT GRID    gradient #0a0a0a → #fafaf7 (transition zone)
CONTENT         #fafaf7 (light, readable)
FOOTER          #0a0a0a (dark bookend)
```

This rhythm must NOT be broken by inserting colored accent-scheme sections.
If a section break is needed: use `background-2` (`#efeae0`) for the lightest variation,
or `inverse` (`#242833`) for a mid-dark. Never use `accent-2` as a section background.

---

## 7. What "Editorial" Means Concretely

The patchwork diagnosis (what was wrong with v1 result):
- ✗ Orange glow on sneakers collection, green glow on origin, purple glow on token...
- ✗ Each collection hero had a different accent color dominating the entire section
- ✗ Product cards had colored badge backgrounds in different colors per type
- ✗ Typography changed style between sections (creating visual discontinuity)

The editorial fix (v2 standard):
- ✓ All collection heroes: dark `#0a0a0a` background, white Bebas headline, product image
- ✓ Accent bars: 2-3px sand `#c9b79c` maximum, ONE per section, at border only
- ✓ Product cards: paper background `#fafaf7`, ink text `#0a0a0a`, DM Sans product name, DM Mono price
- ✓ Badges: white chip with ink text, no colored backgrounds on product type badges
- ✓ One typography voice: Bebas for headlines, DM Sans for content, DM Mono for metadata

---

## 8. Audit Checklist — Before Any Deploy

Ask these questions:

1. **Is the eye path clear?** Headline → subhead → product → price → CTA. If you hesitate, the hierarchy is broken.
2. **Is Bebas Neue used ONLY for display?** If it appears in body or labels, fix it.
3. **Is DM Mono ONLY for metadata?** If it appears in hero copy, fix it.
4. **Is there more than one accent color on the page?** Fix it. Remove all but the sand.
5. **Do all card badges use the same visual system?** If some are colored squares and others are outlines, unify.
6. **Does the page look like a different brand vs. other pages?** If yes, find the divergent element and fix.
7. **Navigation text: is it ≥ 13px?** If below 13px, it's illegible and unprofessional. Fix.
8. **Is there a "Pre-Publish Gate" sign-off?** armocromia + tipografo + copy + photo-studio + commercial-strategy all must pass.

---

## 9. Specific Fixes for Known Issues (TM04 Live 2026-06-19)

### Product page too long
Problem: `bks-product-system` section repeated the product hero.
Fix: section now has compact header (kicker + chips only) + size guide panels. Hero removed. ✅ deployed.

### Footer text invisible on dark
Problem: `color-accent-1` section had inherited `color-foreground` not resolving to white.
Fix: explicit `color: #fafaf7` added to `footer.footer.color-accent-1`. ✅ deployed.

### Header nav text too small
Problem: `.bks-gh__nav a` was `0.72rem` = ~11.5px = below legibility threshold.
Fix: changed to `0.88rem` = ~14px. ✅ deployed.

### Black badge squares on product cards
Status: not yet investigated. Likely in `card-product.liquid` — badge background set to `accent-1` (#0a0a0a) without contrasting text.
Fix needed: audit `card-product.liquid` for `.badge` and `.card__badge` — set background to chip style (1px ink border, paper bg, ink text).

### Wishlist hearts not activating
Status: JS issue in `bks-member.js` or `bks-wishlist.js`. Not yet investigated.

---

## 10. This skill works with

- `bakabo-armocromia` — color identity and model photography
- `bakabo-photo-studio` — product photography technical execution
- `bakabo-theme-build` — CSS/Liquid implementation
- `bakabo-commercial-strategy` — conversion validation
