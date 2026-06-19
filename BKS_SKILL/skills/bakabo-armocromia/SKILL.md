---
name: bakabo-armocromia
description: >
  BKS Store UI color identity + model photography palette.
  Use this skill for: choosing store UI accent colors, verifying color consistency across pages,
  auditing a theme section for patchwork effect, selecting model skin tone for product shots,
  writing on-model prompts, planning editorial shoots.
  Works with bakabo-editorial-typographer (layout), bakabo-photo-studio (photography), bakabo-theme-build (implementation).
metadata:
  type: skill
  version: "2.0"
  created: "2026-06-19"
  replaces: "v1 (fired — did not address store UI color identity)"
---

# BKS Armocromia Skill v2
## Store Identity First. Model Photography Second.

The v1 skill failed because it focused on model skin tones but ignored the fundamental
problem: **the store UI was using 8 different accent colors for 8 collections**,
creating a patchwork effect instead of a fashion magazine identity.

**The rule: UI color must be a neutral stage. Products and photography create visual identity.**

---

## 1. BKS Brand Palette — Non-Negotiable

| Token | Value | Use |
|---|---|---|
| `--bks-paper` | `#fafaf7` | All light backgrounds: header, product grid, pages |
| `--bks-ink` | `#0a0a0a` | All body text, borders, dark sections |
| `--bks-bone` | `#efeae0` | Secondary surfaces (cards, sidebars) |
| `--bks-sand` | `#c9b79c` | **THE ONE BRAND ACCENT** — accent-2 in Shopify |
| `--bks-muted` | `rgba(10,10,10,0.42)` | Captions, labels, metadata |
| `--bks-warm-dark` | `#2e2b22` | Intermediate dark sections, not full black |

**These 6 values are the only colors needed for BKS store UI.**

---

## 2. The One-Accent Rule

**BKS uses ONE accent color across the entire store: `#c9b79c` (sand).**

This is not a limitation. It is what makes a brand recognizable.
Vogue uses red. System uses black. BKS uses sand.

### Where `#c9b79c` appears:
- Accent bars (2-3px lines, not fills)
- Left border of pull-quotes
- Active state on buttons/links (on hover, not default)
- Member Gold Ring (different opacity)
- Price highlights on dark backgrounds

### Where `#c9b79c` does NOT appear:
- Body text — never
- Background fills — never (exceptions: Sale badge which uses Shopify accent-2 scheme)
- Multiple elements simultaneously on the same page — max ONE accent element per screen viewport

---

## 3. Collection Identity — NOT via UI Color

**WRONG approach (v1):** Each collection gets its own accent color (green, teal, purple, red...)
**CORRECT approach (v2):** All collections share the brand palette. Collection identity comes from:

| Identity element | How it works |
|---|---|
| **Hero photography** | Style direction per collection (see bakabo-photo-studio) |
| **Typography scale** | Section headline size signals the collection's energy |
| **Editorial copy tone** | BKS Glyph = dense intellectual, BKS Riviera = light sensory |
| **Product palette** | The prints themselves carry the color of each collection |
| **Gradient direction** | Dark-to-light or light-to-dark per section — subtle only |

The PRODUCTS are the color. The UI is black, white, and sand.

---

## 4. Audit — Patchwork Test

Before any deploy, ask: **"Does this page look like it belongs to the same brand as every other page?"**

Signs of patchwork (REJECT):
- 2+ different colored accent bars visible at once
- Section backgrounds that don't match `#fafaf7`, `#0a0a0a`, or `#efeae0`
- Colored button fills (not standard ink/paper)
- Typography that changes color for emphasis (use weight, not color)
- Badge backgrounds in bright non-brand colors

Signs of editorial unity (APPROVE):
- Eye moves smoothly from section to section with no visual jolt
- If you squint, the page is black + white + the faintest warm cream
- Products visually pop because the UI is silent
- The sand accent appears precisely once per view, pointing at the most important action

---

## 5. Color Schemes — Shopify TM04 Usage Rules

| Scheme | Background | When to use |
|---|---|---|
| `background-1` | `#fafaf7` | Default: all page content, product grid, header |
| `background-2` | `#efeae0` | Subtle section breaks, member tier bands (use sparingly) |
| `inverse` | `#242833` | Mid-page dark sections — NOT the hero (too cold) |
| `accent-1` | `#0a0a0a` | Footer ONLY + full-bleed hero dark sections |
| `accent-2` | `#c9b79c` | Sale badges ONLY (Shopify native badge system) |

**Never use `accent-2` as a section background.** Sand at full saturation as a section fill looks cheap.

---

## 6. Photography Palette — Model Selection by Collection

The v1 content on model skin tones was correct. The rule:
> **The model is the context. The product is the protagonist. Enough contrast to read the print.**

| Collection | Print palette | Recommended model undertone |
|---|---|---|
| BKS Hours | Monochrome (black/white/grey) | Winter: high contrast, cool — porcelain or deep ebony |
| BKS Glyph | Gold/ochre on black | Autumn: warm bronze/terracotta — the gold resonates |
| BKS Marker | Urban gestural marks, black patches | Winter/Autumn: bold contrast or warm tone |
| BKS Riviera | Teal, sand, coral, sky | Spring/Summer: luminous, warm-cool balance |
| BKS Pulse | Geometric black/white movement | Winter: extreme contrast for kinetic effect |
| BKS Token | Pixel grid, cyan/magenta/yellow | Winter or Spring: very fair OR golden luminous |
| BKS Flag | Pop color fields, graphic | Winter: strong contrast for graphic pop |
| BKS Origin | Natural green, earth, stone | Autumn: warm bronze/olive reads earthy and grounded |

### Model Prompt Formula (OpenAI)
```
Adult model, [undertone descriptor from table above].
Expression: neutral, editorial — no smile, no direct eye contact unless specified.
Pose: [from §7 below].
No celebrity resemblance. Age: adult, 25–35 apparent.
Background: [solid studio surface OR location matching collection mood].
```

---

## 7. Pose Library

### Sneakers
```
Low angle, model on concrete, one foot forward, slight weight shift.
Ankle visible above shoe. Cropped at knee level.
```

### Bags (duffle/backpack/travel)
```
Duffle: held one hand at side, arm straight, body 3/4 to camera.
Backpack: both shoulders, slightly turned. Cropped waist to hip, bag fully visible.
```

### Outerwear (windbreaker/puffer/hoodie)
```
Standing, jacket half-zipped, collar up. Arms slightly away to show silhouette.
3/4 turn toward camera.
```

### Swimwear / Riviera
```
Seated on travertine ledge or pool edge.
Waistband and drawstring visible. Legs relaxed. Mediterranean light.
Crop at chest level.
```

### Dresses / Women's Editorial
```
Standing, looking away or down at 45°. Fabric in movement from natural wind/fan.
3/4 profile. Full figure or cropped at hips.
```

---

## 8. Styling Rules (Anti-Distraction)

| Element | Rule |
|---|---|
| Hair | Clean, natural, or neatly styled — never elaborate |
| Jewelry | None — diverts attention from the print |
| Make-up | Minimal natural — no theatrical effects |
| Nails | Nude or bare — never bright colors |
| Footwear | Product-matched or plain (white/black) unless footwear is the product |

---

## 9. This skill works with

- `bakabo-editorial-typographer` — layout and type placement
- `bakabo-photo-studio` — photography technical execution
- `bakabo-theme-build` — CSS implementation of color tokens
- `bakabo-commercial-strategy` — conversion validation before applying accent
