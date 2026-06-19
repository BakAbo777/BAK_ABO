---
name: bakabo-design-system
description: Use this skill whenever generating, evaluating, or implementing any visual element of the BakAbo brand — UI components, page layouts, mockups, design proposals, or frontend code where visual treatment matters. Triggers include design decisions on colors, typography, spacing, layout, components (buttons, cards, navigation, forms), animations, or visual hierarchy; reviewing design work from external designers to check brand consistency; producing a brief for handoff to a designer. Works alongside bakabo-brand (voice and identity). Do not use for written content alone (use bakabo-brand and bakabo-product-copy).
---

# BakAbo Design System

The canonical visual language for BakAbo. Tokens, typography, color, spacing, layout, components, motion, and accessibility — defined once, applied everywhere.

This skill serves two audiences. **For Claude:** the rules to follow when generating any visual element or frontend code. **For humans:** the brief to hand to an external designer; once they deliver, the same document is the acceptance checklist.

## 1. Four design principles

These four anchors precede every other rule. When tokens and principles conflict, principles win.

1. **Editorial over commercial.** Layouts read like a magazine spread, not like a sales page. Generous white space, confident typography, restrained color. If a screen feels busy, it is.
2. **Asymmetry, never accidental.** Symmetric layouts are easy and forgettable. BakAbo's compositions are intentionally asymmetric — left-weighted hero, off-grid type, deliberate empty quadrants. Asymmetry must look composed, never sloppy.
3. **Type is the hero.** Imagery and type share the page, but in moments of doubt, type leads. A large, well-set headline beats a clever image with weak type.
4. **One accent, never two.** Each page may carry one moment of color or scale accent. Two accents compete and cancel each other.

## 2. Color tokens

Built around three neutrals + accents derived from the BakAbo color dictionary (shared with `bakabo-printify-sync` for variant naming, kept consistent).

### Primary neutrals (the workhorses)

| Token | Hex | Use |
|---|---|---|
| `--bks-onyx` | `#0A0A0A` | Primary text, primary backgrounds in dark mode, borders at full strength |
| `--bks-salt` | `#FAFAF7` | Primary background, primary text in dark mode |
| `--bks-bone` | `#EFEAE0` | Secondary background, card surfaces, soft separators |

### Supporting neutrals

| Token | Hex | Use |
|---|---|---|
| `--bks-graphite` | `#3D3D3D` | Secondary text, captions |
| `--bks-ash` | `#9A9A9A` | Tertiary text, disabled states, placeholders |
| `--bks-dune` | `#C9B79C` | Warm accent, muted highlights |

### Extended neutrals (warm / dark alternatives)

These extend, not replace, the primary and supporting sets. Use them when context calls for warmer or moodier neutrals than the defaults provide.

| Token | Hex | Use |
|---|---|---|
| `--bks-mocha` | `#443C3C` | Warm dark neutral. Alternative to `--bks-graphite` when the surrounding palette is warm (paired with `--bks-bone`, `--bks-dune`, earthy product imagery). Lookbooks and Mediterranean-leaning content lean here. |
| `--bks-shadow` | `#242833` | Dark neutral with blue undertone. Alternative to `--bks-onyx` when a dark background needs personality without going cold like `--bks-ink`. Good for the AI-art panel background, footer variants, and cinematic editorial sections. |

**Rule:** within a single page, pick a temperature lane (warm = mocha/bone/dune; neutral = onyx/salt/graphite; cool = shadow/ink). Mixing temperatures inside one section reads as inconsistent. Across pages, the temperature can shift by collection or content.

### Accents (one per page, never two)

| Token | Hex | Use |
|---|---|---|
| `--bks-ink` | `#0F2240` | Calm accent; Mediterranean Lines / Aqua Citizens |
| `--bks-coral` | `#C84B3D` | Energy accent; Lava Motion / Drop Energy |
| `--bks-lagoon` | `#2A8B85` | Cool accent; Neo Matrix / Cyber |
| `--bks-cinnabar` | `#7A1E1E` | Premium accent; rare use only |

### Semantic colors (functional only)

| Token | Hex | Use |
|---|---|---|
| `--bks-success` | `#2F6F4F` | Success states, confirmation |
| `--bks-error` | `#A33B2A` | Form errors, validation |
| `--bks-warning` | `#B58A2C` | Warnings, caution |

Use semantic colors **only** for system feedback. Never style decorative elements with these tokens.

### Contrast rules

All text must meet **WCAG AA**: 4.5:1 for body text, 3:1 for large text (18pt+ or 14pt+ bold). The neutral palette is built to comply; the burden is on you when introducing accents.

## 3. Typography

### Font families

The brand uses two families, optionally three.

| Role | Recommended | Open-source fallback | When to use |
|---|---|---|---|
| **Display** | GT America, Söhne, Suisse Int'l, Neue Haas Grotesk | **Inter Display**, Space Grotesk | Headlines, hero, navigation, large numerals |
| **Body** | Same as display (single-family lockup) | **Inter** | Paragraphs, descriptions, UI text |
| **Mono** (optional) | GT America Mono, Söhne Mono | **JetBrains Mono**, IBM Plex Mono | Product codes, prices, technical detail, timestamps |

Default to a **single-family lockup** (display = body, just different weights). Multi-family lockups need a real designer to balance — don't improvise.

### Type scale (modular, 1.250 ratio)

Mobile-first; desktop scales up via `clamp()`.

| Token | Mobile | Desktop | Weight | Letter-spacing |
|---|---|---|---|---|
| `--text-xs` | 11px | 12px | 500 | +0.04em |
| `--text-sm` | 13px | 14px | 400 | +0.01em |
| `--text-base` | 15px | 16px | 400 | 0 |
| `--text-md` | 17px | 18px | 400 | 0 |
| `--text-lg` | 20px | 22px | 500 | -0.005em |
| `--text-xl` | 26px | 32px | 500 | -0.01em |
| `--text-2xl` | 34px | 44px | 600 | -0.02em |
| `--text-3xl` | 44px | 64px | 600 | -0.03em |
| `--text-4xl` | 56px | 88px | 700 | -0.035em |
| `--text-hero` | 72px | 128px | 700 | -0.04em |

### Type rules

- **Line-height:** 1.1 for headlines (≥`--text-xl`), 1.5 for body, 1.3 for captions and UI elements.
- **Tracking on UPPERCASE:** always +0.06em or more. Uppercase without tracking is amateur.
- **Numbers in product context:** prefer **tabular figures** so prices and sizes align (`font-variant-numeric: tabular-nums`).
- **Italics:** reserved for the *hero line* of product pages (see `bakabo-product-copy`) and rare emphasis. Never italicize entire paragraphs.
- **One typographic anomaly per page max.** A single oversized headline. A single mono detail. Two anomalies cancel.

## 4. Spacing scale

Base unit **8px** (4px for fine-tuning only). All margin, padding, and gap values come from this scale.

| Token | Value | Use |
|---|---|---|
| `--space-1` | 4px | Icon-to-text, fine adjustments |
| `--space-2` | 8px | Inline pairs, badge padding |
| `--space-3` | 12px | Tight stack |
| `--space-4` | 16px | Default gap within a component |
| `--space-5` | 24px | Default gap between components |
| `--space-6` | 32px | Section internal padding (mobile) |
| `--space-7` | 48px | Section gap (mobile) |
| `--space-8` | 64px | Section gap (desktop), section padding (mobile) |
| `--space-9` | 96px | Section padding (desktop) |
| `--space-10` | 128px | Hero spacing, page-level separation |
| `--space-11` | 192px | Editorial gaps; rare, intentional |

**Rule:** never invent a spacing value outside this scale. If the scale doesn't fit, the layout is wrong, not the scale.

## 5. Layout grid

- **Desktop:** 12-column grid, 24px gutter, 1440px max content width, 80px side padding
- **Tablet:** 8-column grid, 16px gutter, 48px side padding
- **Mobile:** 4-column grid, 16px gutter, 24px side padding

Hero and editorial sections may **break the grid** intentionally (full-bleed images, headline overflowing into the gutter). Everything else respects it.

## 6. Breakpoints

Mobile-first. Min-width queries.

| Token | Value | Notes |
|---|---|---|
| `--bp-sm` | 480px | Larger mobile |
| `--bp-md` | 768px | Tablet portrait |
| `--bp-lg` | 1024px | Tablet landscape / small desktop |
| `--bp-xl` | 1440px | Standard desktop |
| `--bp-2xl` | 1920px | Wide desktop |

Test on real devices at 375px (iPhone SE), 390px (iPhone 14), 768px, 1280px, 1920px.

## 7. Components — rules, not code

This section defines *how* each component behaves and feels. Actual CSS lives in the theme (`bakabo-theme-build`).

### Button

- **Primary:** `--bks-onyx` background, `--bks-salt` text, no border, no shadow. Hover: invert (salt bg, onyx text, onyx border). Active: 95% scale.
- **Secondary:** transparent bg, `--bks-onyx` text, 1px `--bks-onyx` border. Hover: filled onyx.
- **Tertiary / text:** no bg, no border, underline on hover.
- **Sizing:** 48px height standard, 56px on hero, 40px on dense UI. Horizontal padding = 1.5× height.
- **Label:** uppercase, +0.06em tracking, weight 500. Never sentence case in primary buttons.
- **Never:** gradients, drop shadows, rounded corners >2px, animated pulsing, "BUY NOW!!!" energy.

### Card (product, collection, content)

- Background: `--bks-salt` or `--bks-bone`. Border: none, or 1px `--bks-bone` if needed for separation.
- Corner radius: **0 or 2px max**. No soft rounded cards.
- Image: 4:5 portrait for products, 16:9 for editorial, 1:1 for compact.
- Hover: subtle scale on image (1.02), no shadow lift, no border change.
- Text below image: 16px top padding, hierarchy = title → meta → price.

### Navigation (header)

- **Height:** 64px mobile, 80px desktop. Sticky on scroll.
- **Logo:** left-aligned, never centered.
- **Menu items:** uppercase, `--text-sm`, weight 500, +0.06em tracking. Underline animates on hover (left-to-right).
- **Cart / search icons:** right-aligned, 24px square. Cart shows count as a small dot, not a number badge.
- **No emoji**, no flag icons. Language selector is a text dropdown.

### Form input

- **Height:** 48px. Border: 1px `--bks-ash`. Border-radius: 0.
- **Focus:** border becomes `--bks-onyx`, outline-offset 4px solid `--bks-bone`.
- **Label:** above the input, never floating. `--text-xs`, uppercase, tracking +0.06em.
- **Error state:** border `--bks-error`, message below in `--text-xs --bks-error`.

### Badge / tag

- Inline, no background, 1px border + 4px padding, uppercase `--text-xs`. Used for drop numbers, line names, "Made to Order".

### Modal / drawer

- Backdrop: `rgba(10,10,10,0.6)`, fade-in 200ms.
- Container: full-width on mobile, max 560px on desktop. Padding `--space-7`.
- Close: top-right, `×` 24px, no background.

### Accordion (FAQ, product specs)

- Full-width row, 1px bottom border `--bks-bone`. Plus/minus icon, never chevron arrow.
- Open animation: height auto, 240ms ease-out.

## 8. Motion

Two motion roles only:

1. **Functional** (state changes, focus, hover, open/close): 150–240ms, ease-out
2. **Editorial** (hero reveal, scroll-in fades): 400–600ms, custom curve

**Never:**
- Parallax beyond 10% offset
- Carousel auto-rotate
- Animated text typing
- Bounce, spring, or attention-grabbing motion
- Anything that delays content >300ms on entry

**Always:**
- Respect `prefers-reduced-motion: reduce` — disable all non-functional motion
- Animate transform and opacity only (never width/height/top for perf)

## 9. Imagery direction

- **AI-art prints:** treat as the brand's primary visual material. Show them edge-to-edge, full-bleed where possible.
- **Lifestyle / model shots:** editorial register — Mediterranean light, architectural setting, model expression neutral. No staged "happy customer" smiles.
- **Product cutouts:** plain `--bks-bone` background, soft directional shadow only if it adds form definition.
- **Aspect ratios:** 4:5 product, 16:9 editorial, 1:1 compact. No mixing within a grid.
- **Image treatment:** unedited beyond color correction. No filters, no oversaturation, no AI upscaling artifacts.
- **Alt text:** see `bakabo-product-copy` §3 — descriptive, never keyword-stuffed.

## 10. Iconography

- **Style:** line, 1.5px stroke, square or rounded caps, 24px default size on 24px artboard.
- **Source:** prefer a single icon library across the whole site (Lucide, Phosphor, Heroicons line). Mixing libraries reads as amateur.
- **No emoji** in any structural element (buttons, navigation, labels, meta).
- **Brand-specific symbols:** the typographic set `◇ ◈ ▣ ◧ ≋ ⌁ ⬚ ◑ ✦ ✧ ∞` may be used as decorative accents, especially on homepage panels (consistent with current site usage).

## 11. Accessibility

WCAG 2.1 AA is the floor, not the ceiling. Enforced:

- All interactive elements have a visible focus state (4px offset outline, not removed).
- All form fields have associated `<label>` (not just placeholder).
- Color is never the only signal (error states pair color with icon or text).
- Icon-only buttons have `aria-label`.
- Heading hierarchy is sequential (no `h2 → h4` skips).
- Tap targets are minimum 44×44px on touch.
- Motion respects `prefers-reduced-motion`.
- Text is never embedded in non-decorative images.

## 12. Handoff to an external designer

When briefing a real designer, give them:

1. This file (the design system) as the canonical reference
2. `bakabo-brand` (voice and identity)
3. The current `sito.zip` (existing theme, as starting point)
4. The current homepage screenshot (what's live now)
5. The list of pages to redesign with priority (use `bakabo-pages-design`)

Tell them: *"Respect every token in section 2–6, every component rule in section 7. You have full latitude on layout, composition, imagery direction within those constraints."*

The acceptance test: open their delivery, walk this skill section by section, mark every violation. A delivery with zero token-level violations and no principle violations from section 1 is acceptable. Anything else goes back.

## 13. What this skill cannot do

Honest limits to set expectations:

- Cannot replace a designer's eye for proportion, balance, and pixel-level polish.
- Cannot evaluate "does this *feel* right" — that's a human judgment.
- Cannot guarantee visual originality; it guarantees coherence and quality floor.

The skill builds a **floor of professionalism**. Brilliance still requires a person.
