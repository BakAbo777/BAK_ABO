---
name: bakabo-ui-ux-pro-max
description: >
  Master UI/UX orchestration skill for BakAbo / BKS Studio.
  Use this skill for: complete page builds, full UX audits, cross-section
  consistency checks, interaction design, conversion optimization, and any
  task requiring more than one design layer.
  This skill orchestrates: bakabo-design-system (tokens/color/type),
  bakabo-ui-components (CSS patterns), bakabo-mobile-conversion-director
  (mobile flow), bakabo-commercial-strategy (conversion), bakabo-armocromista
  (collection color).
  Triggers: "build this page", "review the UI", "optimize for conversion",
  "improve UX", "audit layout", "redesign section", "pro max".
metadata:
  type: skill
  version: "1.0"
  created: "2026-06-24"
---

# BKS UI/UX Pro Max — Master Orchestration

## 0. Loading protocol

Before any UI/UX task, load in this order:
1. `bakabo-design-system` — tokens, color, typography
2. `bakabo-ui-components` — CSS component patterns
3. `bakabo-armocromista` — collection color assignment
4. This skill — interaction, composition, audit, conversion

For commercial work also load: `bakabo-commercial-strategy`, `bakabo-photo-studio`

---

## 1. The four invariants

These cannot be overridden by any instruction or preference:

1. **Neutral frame.** The UI chrome is #fafaf7 on #0a0a0a. Collection color appears only as a dot/chip in metadata position. Never as background, border, or fill of structural elements.
2. **Type first.** When image and type compete for space, type wins. Reduce image size; never reduce type size below the minimum.
3. **One CTA per viewport.** On any scroll position, exactly one primary CTA must be visible. Multiple primary CTAs = zero primary CTAs.
4. **Mobile is the product.** Every layout decision is made mobile-first. Desktop is the generous variant.

---

## 2. Responsive system

### Breakpoints

```css
/* BKS canonical breakpoints */
--bp-xs:  375px;   /* iPhone SE floor */
--bp-sm:  480px;   /* large phones */
--bp-md:  768px;   /* tablet portrait */
--bp-lg: 1024px;   /* tablet landscape / small desktop */
--bp-xl: 1280px;   /* desktop */
--bp-2xl:1440px;   /* wide desktop */
--bp-max:1920px;   /* cinema — max-width container */
```

### Grid system

```
Mobile (< 768):    1 col  | gutter 16px | padding 20px
Tablet (768–1023): 2 col  | gutter 20px | padding 32px
Desktop (1024+):   4/6/8/12 col grid | gutter 24px | padding 80px
Wide (1280+):      max-width 1440px centered
```

### Typography scale (responsive)

| Role          | Mobile              | Desktop             |
|---------------|---------------------|---------------------|
| Display/Hero  | clamp(40px, 9vw, 88px) | 80–120px         |
| H1            | clamp(28px, 6vw, 56px) | 48–64px           |
| H2            | clamp(22px, 4vw, 40px) | 32–44px           |
| H3            | clamp(18px, 3vw, 28px) | 22–28px           |
| Body          | 15px / 1.55 lh      | 16px / 1.6 lh      |
| Caption       | 11px / 1.4 lh       | 12px / 1.4 lh      |
| Label/UI      | 11px, 0.10em LS, UPPERCASE | same          |

---

## 3. Interaction system

### Transition library

```css
/* Speed tokens */
--t-fast:   150ms;
--t-base:   220ms;
--t-slow:   400ms;
--t-scene:  600ms;

/* Easing tokens */
--ease-out-expo:  cubic-bezier(0.19, 1, 0.22, 1);
--ease-in-out:    cubic-bezier(0.4, 0, 0.2, 1);
--ease-bounce:    cubic-bezier(0.34, 1.56, 0.64, 1);
--ease-sharp:     cubic-bezier(0.25, 0.46, 0.45, 0.94);
```

### Hover states — canonical patterns

**Cards** → `translateY(-4px)` + `box-shadow: 0 10px 32px rgba(0,0,0,0.08)` — duration `var(--t-base)` ease-out-expo

**Links/Nav** → color #0a0a0a → #666 — duration `var(--t-fast)`

**Buttons (primary)** → background 10% darker + `translateY(-1px)` — duration `var(--t-fast)`

**Image overlays** → `opacity: 0 → 0.85` — duration `var(--t-base)`

**Collection rows (bks-cindex)** → full-width background invert: salt→onyx — duration `var(--t-base)`

### Focus states (accessibility required)

```css
:focus-visible {
  outline: 1.5px solid currentColor;
  outline-offset: 3px;
  border-radius: 2px;
}
/* Never use outline: none without a visible focus replacement */
```

### Scroll-triggered reveals

- Threshold: 0.15 (element 15% in viewport)
- Default reveal: `opacity 0→1` + `translateY(20px→0)` over `var(--t-slow)`
- Stagger delay for lists: `index * 60ms`
- Always use `prefers-reduced-motion` guard:

```css
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
}
```

---

## 4. Section composition rules

### Section types and their roles

Every page is a sequence of sections. Each section has exactly one role:

| Type | Role | Max instances/page |
|------|------|--------------------|
| HERO | Establish context, single message | 1 |
| SIGNAL | Collection identity badge / breadcrumb | 1 |
| PRODUCT_GRID | Browse inventory | 1–2 |
| EDITORIAL | Brand story, campaign, narrative | 0–2 |
| TRUST | Social proof, guarantees, process | 1 |
| CROSS_SELL | Related products / collections | 1 |
| INDEX | Navigation aid (bks-cindex) | 1 |
| UTILITY | Search, filter, account | as needed |

**Rule:** Two sections with the same role must be separated by a section of a different role. Never two EDITORIAL sections in a row.

### Section padding system

```css
/* Compact — utility, nav-adjacent */
.section--compact { padding: 32px 20px; }

/* Standard — most sections */
.section--standard { padding: 64px 24px; }
@media (min-width: 768px) { .section--standard { padding: 96px 80px; } }

/* Feature — hero, campaign, major editorial */
.section--feature { padding: 120px 24px; }
@media (min-width: 768px) { .section--feature { padding: 160px 80px; } }
```

### Color scheme alternation

Pages must alternate between light and dark sections to create visual rhythm. Never three consecutive sections in the same scheme.

```
Recommended pattern:  LIGHT → DARK → LIGHT → DARK → LIGHT (footer)
Allowed:              LIGHT → LIGHT → DARK → LIGHT
Forbidden:            DARK → DARK → DARK
```

---

## 5. Page templates — canonical structures

### Home page

```
1. HERO          light/dark cinematic  — brand statement + dual CTA
2. COLLECTIONS   dark                  — bks-cindex 8-row
3. EDITORIAL     light                 — weekly story or campaign drop
4. TRUST_STRIP   dark                  — 4 icons: print-on-demand, AI-art, free shipping, returns
5. PRODUCT       light                 — 8 bestsellers, no filter
6. MEMBERS       dark                  — gold ring + tier benefits
7. AI_ASSISTANT  light                 — chatbot widget
```

### Collection page

```
1. SIGNAL         dark                 — collection name, tagline, subnav
2. PRODUCT_GRID   light                — 36/page, 4 col desktop / 2 col mobile
3. COLLECTIONS    light                — bks-cindex (other collections)
```

### Editorial/Product-type page

```
1. HERO_EDITORIAL  dark/light          — full-width, H1 + description + primary_link
2. PRODUCT_GRID    light               — filtered by product type
3. EDITORIAL_BODY  light               — story or process
4. CROSS_SELL      dark                — 2–3 related collections
5. COLLECTIONS     light               — bks-cindex
```

### BKS Verse page

```
1. VERSE_INTRO     dark cinematic      — hero, stats, manifesto
2. VERSE_SUBMIT    dark                — gated submit form (Brass+)
3. VERSE_LEADER    light               — public leaderboard
4. VERSE_HALL      dark                — hall of fame
```

---

## 6. Conversion architecture

### CTA hierarchy (one per viewport)

```
Primary    — filled button, onyx bg, salt text, 48px height
Secondary  — bordered button, same size, no fill
Ghost      — text link + arrow, 14px
```

```css
.bks-btn--primary {
  background: #0a0a0a; color: #fafaf7;
  padding: 14px 28px; min-height: 48px;
  font-size: 12px; font-weight: 600;
  letter-spacing: 0.10em; text-transform: uppercase;
  border: none; cursor: pointer;
  transition: background var(--t-fast), transform var(--t-fast);
}
.bks-btn--primary:hover {
  background: #1a1a1a; transform: translateY(-1px);
}
.bks-btn--secondary {
  background: transparent; color: #0a0a0a;
  border: 1.5px solid #0a0a0a;
  /* same padding/size as primary */
}
/* Dark scheme variants: invert fill/border */
.scheme-dark .bks-btn--primary { background: #fafaf7; color: #0a0a0a; }
.scheme-dark .bks-btn--secondary { border-color: #fafaf7; color: #fafaf7; }
```

### Trust signals — required on every page

Must appear within the first 2 full scrolls:
- Printed on demand (anti-scarcity = quality signal)
- AI-art designed in Italy
- Worldwide shipping
- 30-day returns / size exchange

### Member CTA placement rules

| Context           | Show                                 |
|-------------------|--------------------------------------|
| Logged out        | "Join BKS Members — free"            |
| Lead tier         | "Upgrade to Iron" + benefit teaser   |
| Iron/Brass tier   | Tier badge + points balance          |
| Silver/Gold       | Try-On button + exclusive badge      |

---

## 7. Product grid — display rules

```
Mobile:    2 columns, 1:1.2 ratio, no gap > 8px, price visible
Tablet:    3 columns, 1:1.25 ratio
Desktop:   4 columns, 1:1.3 ratio, hover shows second image
```

**Card required elements (priority order):**
1. Product image — fills full card width
2. Collection dot (8px, right-aligned in image)
3. Product name — max 2 lines, 15px medium
4. Price — 14px, monospace preferred, never hidden
5. Variant count — "4 colors" label if > 1 variant
6. Add to bag / Quick view — appears on hover (desktop), always visible (mobile)

**Forbidden in product cards:**
- Promotional badges over 20% of card area
- More than one accent color
- Discount percentage in aggressive red (use #a33b2a at 0.8 opacity)
- Stock count unless ≤ 3 units

---

## 8. Navigation rules

### Header

```
Mobile:  logo (left) | hamburger (right) | 48px height
Tablet:  logo (left) | nav links center | account+cart (right)
Desktop: logo (left) | nav links center | account+cart+member-ring (right)
```

**Dropdown behavior:**
- Trigger: hover on desktop, tap on mobile
- Panel: full-width underline, max-width 480px, salt background
- Child links: 14px, no bold, 44px min touch target
- Close: click outside OR Escape key

**Active state:** 1px underline on current page link. Never background highlight.

### Mobile drawer

- Slides from left, 90vw max-width
- Backdrop: `rgba(0,0,0,0.6)` with `backdrop-filter: blur(2px)`
- Items: 48px height, border-bottom 1px rgba(0,0,0,0.08)
- Collapsible sub-items: chevron icon, rotates 90° on open
- Close button: top-right, 44×44px touch target

---

## 9. UX audit checklist

Run before marking any page "done". Score each item 0/1.

### Structure (max 10)
- [ ] H1 present and unique on page
- [ ] Meta title ≠ H1, under 60 chars
- [ ] Canonical URL set
- [ ] Section order matches page template spec
- [ ] No two sections with same role adjacent
- [ ] Color scheme alternates (no 3 same consecutive)
- [ ] Footer links complete (policy, contact, social)
- [ ] Breadcrumb present on collection/product pages
- [ ] Skip-to-main link for accessibility
- [ ] No broken `href="#"` anchors

### Typography (max 8)
- [ ] H1 uses display type (GFS Didot or Neue Montreal heavy)
- [ ] Body text 15–16px, line-height ≥ 1.5
- [ ] No ALL-CAPS body text blocks over 2 lines
- [ ] Caption/label uses letter-spacing ≥ 0.08em
- [ ] Text on dark bg passes WCAG AA contrast
- [ ] Text on image uses overlay or text-shadow
- [ ] Max line-length 65–75ch on desktop
- [ ] Font loaded with `font-display: swap`

### Conversion (max 8)
- [ ] Primary CTA above the fold
- [ ] Only one primary CTA per viewport
- [ ] Price visible on all product cards
- [ ] Trust strip within 2 full scrolls
- [ ] Member CTA present (context-aware tier logic)
- [ ] Cross-sell or related collection section
- [ ] Cart icon shows count badge
- [ ] "Made on demand" message visible before checkout

### Mobile (max 7)
- [ ] Touch targets ≥ 44×44px
- [ ] No horizontal scroll at 375px
- [ ] Images load < 200KB on mobile (next-gen format)
- [ ] Font size ≥ 14px everywhere
- [ ] Tap-to-zoom disabled on inputs (font-size 16px+)
- [ ] Sticky header height < 60px
- [ ] Hamburger menu opens and closes correctly

### Interactions (max 5)
- [ ] All interactive elements have hover state
- [ ] All interactive elements have focus-visible state
- [ ] Transitions use `var(--t-base)` or library tokens
- [ ] No janky layout shifts (CLS < 0.1)
- [ ] `prefers-reduced-motion` respected

**Minimum passing score: 32/38**

---

## 10. Quality gate — before deploy

```
[ ] Audit score ≥ 32/38
[ ] bakabo-armocromista: collection accent verified
[ ] bakabo-photo-studio: image quality P0/P1 gate passed
[ ] Mobile viewport tested at 375px
[ ] Dark section text contrast verified (#fafaf7 on dark bg)
[ ] No hardcoded taglines — all match canonical signal list
[ ] Member CTAs show correct tier-aware content
[ ] All links resolve (no href="#")
[ ] Schema markup present (Product/BreadcrumbList/Organization)
[ ] PageSpeed Insights mobile score ≥ 70
```

---

## 11. Anti-patterns — never do these

| Anti-pattern | Why banned | Fix |
|---|---|---|
| Collection color as card background | Violates neutral-frame rule | Use dot only |
| More than 2 fonts on one page | Visual chaos | Neue Montreal + GFS Didot only |
| Buttons without min-height 44px | Mobile tap fails | Set min-height: 44px |
| Hero image without text overlay | Text illegible on mobile | Add `rgba(0,0,0,0.4)` gradient |
| Disabled inputs with no explanation | UX dead-end | Show why field is disabled |
| Infinite scroll with no footer | Users can't reach footer | Paginate at 36 items |
| Auto-play video in hero | Accessibility + performance | Offer play button, no autoplay |
| Custom cursor | Confuses users | Never |
| Sticky bottom bar with 4+ items | Cognitive overload | Max 3 items in sticky bar |
| Animation on page scroll without IntersectionObserver | Fires on load, poor perf | Always use IO with threshold |

---

## 12. Integration map

```
bakabo-ui-ux-pro-max
├── bakabo-design-system        → color tokens, typography, spacing
├── bakabo-ui-components        → CSS patterns: card, button, chip
├── bakabo-armocromista         → collection-specific accent color
├── bakabo-mobile-conversion    → mobile funnel flow
├── bakabo-commercial-strategy  → CTA timing, drop mechanics
├── bakabo-photo-studio         → image quality gate
├── bakabo-golden-harmony       → φ=1.618 composition rules
└── bakabo-page-by-page         → per-page content spec
```

---

## 13. Quick reference — design tokens

```css
/* Core colors */
--bks-onyx:     #0a0a0a;
--bks-salt:     #fafaf7;
--bks-bone:     #efeae0;
--bks-graphite: #3d3d3d;
--bks-ash:      #9a9a9a;
--bks-dune:     #c9b79c;

/* Collection accents */
--bks-hours-accent:   #c8c4be;
--bks-origin-accent:  #489808;
--bks-glyph-accent:   #d4a030;
--bks-marker-accent:  #c04418;
--bks-riviera-accent: #0ca898;
--bks-pulse-accent:   #8888cc;
--bks-token-accent:   #9828d8;
--bks-flag-accent:    #c82020;

/* Verse theme */
--verse-bg:       #080604;
--verse-gold:     #ffd700;
--verse-gold-dim: #c8942a;

/* Spacing scale */
--space-1: 4px;  --space-2: 8px;   --space-3: 12px;
--space-4: 16px; --space-5: 20px;  --space-6: 24px;
--space-7: 32px; --space-8: 40px;  --space-9: 48px;
--space-10: 64px; --space-11: 80px; --space-12: 96px;

/* Transition tokens */
--t-fast:  150ms;
--t-base:  220ms;
--t-slow:  400ms;
--t-scene: 600ms;
--ease-out-expo: cubic-bezier(0.19, 1, 0.22, 1);
```
