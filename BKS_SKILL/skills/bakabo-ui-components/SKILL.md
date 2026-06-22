---
name: bakabo-ui-components
description: >
  BKS standardized UI component library for bakabo.club TM04 theme.
  Use this skill for: building or auditing any card, button, chip, list, or
  interactive element in the Shopify theme. Enforces the armocromia one-accent
  rule, the typography system, and the "products are the color" principle.
  Works with bakabo-armocromia (color), bakabo-editorial-typographer (type),
  bakabo-theme-build (implementation).
metadata:
  type: skill
  version: "1.0"
  created: "2026-06-22"
---

# BKS UI Component System

## 0. The master rule

The UI is a neutral frame. Every component uses the same brand palette.
Collection identity comes from the product dot/chip (one small color indicator),
never from structural chrome (borders, backgrounds, button fills).

---

## 1. Card — Base Pattern

```css
.bks-card {
  background: #fafaf7;                      /* --bks-paper */
  border: 1px solid rgba(10,10,10,0.1);
  border-top: 2px solid #c9b79c;            /* sand accent — ONE brand accent */
  border-radius: 0;
  padding: clamp(20px, 3vw, 28px);
  text-decoration: none;
  color: #0a0a0a;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: transform 0.22s cubic-bezier(0.22,1,0.36,1), box-shadow 0.22s ease;
}
.bks-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 32px rgba(0,0,0,0.08);
}
```

**Collection identifier dot** (allowed exception — metadata only):
```css
.bks-card__dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--collection-accent);   /* set inline per collection */
  flex-shrink: 0; opacity: 0.82;
}
```
Rule: max ONE dot per card. The dot is metadata — never structural.

---

## 2. Card — Dark Variant

```css
.bks-card--dark {
  background: rgba(250,250,247,0.04);
  border-color: rgba(250,250,247,0.1);
  border-top-color: rgba(201,183,156,0.55);
  color: #fafaf7;
}
```

---

## 3. Product Card (grid)

Product cards follow the same base but are simpler:
```
- No top border accent (let the product image lead)
- Background: #fafaf7
- On hover: subtle lift (translateY -3px), no border change
- Product name: DM Sans 14-16px weight 500
- Price: DM Mono 14px weight 600
- Collection chip: DM Mono 10px, letter-spacing 0.22em — collection color background, 
  opacity 0.12 (very subtle fill) with collection color text
```

---

## 4. Button system

| Variant | Style |
|---|---|
| Primary | Background #0a0a0a, color #fafaf7, DM Mono 0.72rem tracking 0.14em, uppercase, no border-radius |
| Secondary | Border 1px #0a0a0a, color #0a0a0a, transparent bg, same font |
| Ghost (on dark) | Border 1px rgba(250,250,247,0.4), color #fafaf7 |
| Hover all | opacity or bg shift 0.12 — never color change |

**Never:** colored button fills, round corners (> 0px), uppercase bold weight.

---

## 5. Chip / Tag

```css
.bks-chip {
  font-family: DM Mono;
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  padding: 4px 10px;
  border: 1px solid rgba(10,10,10,0.2);
  background: transparent;
  color: rgba(10,10,10,0.55);
}
```
Collection chips: use collection color as `border-color` only (no fill).

---

## 6. Section headers

Every section in the theme uses this pattern exactly:

```
1. EYEBROW  → DM Mono, 0.68rem, weight 700, tracking 0.28em, uppercase, muted (46%)
2. HEADLINE → Bebas Neue, clamp(2.8rem,6vw,6rem), line-height 0.9, uppercase
3. SUBTITLE → DM Sans, clamp(0.96rem,1.1vw,1.08rem), lh 1.62, max-width 52ch, muted (62%)
4. CONTENT  → section-specific
```

---

## 7. Page anatomy baseline (all pages)

Every page on bakabo.club must have:

| Element | Spec |
|---|---|
| H1 | One per page, Bebas Neue, 64-96px |
| Service bar | Once per page: "Free Shipping >€60 · 30-Day Returns · Printed on demand" |
| Navigation | Global header identical on all pages |
| Footer | Four-column layout, identical on all pages |
| Background | #fafaf7 default, #0a0a0a for full-bleed dark sections only |
| Language | ONE selector, never duplicated |

---

## 8. Patchwork prevention checklist

Before deploying any section:
- [ ] How many different accent colors are visible on this page at once? → must be 0 or 1 (sand)
- [ ] Are collection colors being used only as dots/chips (metadata), never borders/bg?
- [ ] Does the page background stay within the 3 approved values?
- [ ] Does the card hover use translateY only (no color changes)?
- [ ] Is there a single H1?
- [ ] Does the font usage match: Bebas Neue (display only) / DM Sans (body) / DM Mono (meta)?
