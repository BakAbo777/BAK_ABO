# BKS Newspaper Pop-out Skill
**Section:** `bks-piano-hero.liquid` / `bks-piano-hero.js`
**Pattern:** Editorial newspaper aesthetic with physical key-lift press effect
**Status:** Live — theme ID `202392961362`

---

## Concept

Two rendering modes for the BKS Piano Hero section, switchable via Shopify admin:

| Mode | Background | Press effect | Panel |
|---|---|---|---|
| `cinema` | `#0A0A0A` dark luxury | `shadowBlur` glow, accent fills key | Dark — white text |
| `editorial` | `#fafaf7` paper newsprint | Drop shadow lift, key expands from page | Light — dark ink text |

The editorial mode simulates a **newspaper/magazine page** where the piano keys are illustrated/printed on paper and seem to physically emerge when touched. The overall aesthetic is inspired by high-fashion editorial publications (Wallpaper*, System, SSENSE editorial).

---

## How the lift effect works (editorial mode)

When a key's `KS[idx].anim` interpolates toward 1 (pressed state), `pd` = 0→1:

```
lift    = pd * 16         // white keys: 16px vertical lift
expand  = lift * 0.4      // horizontal expansion
shadow_d = lift * 0.38 + 2  // drop shadow offset
```

1. **Drop shadow drawn first** — offset trapezoid at `+sd, +sd*0.25` — simulates paper lifting
2. **Key body drawn** — expanded by `expand` on each side, translated up by `lift`
3. **Accent wash** — `col.color + '28'` overlay at 40% opacity when active
4. **Ink border** — switches from `rgba(20,14,6,0.42)` to `accent + 'cc'` when active
5. **DM Mono label** — switches from ink grey to full `accent` color when active

---

## Page colour adaptation

The editorial mode reads `--bks-active-accent` from `document.documentElement` (injected by `bks-dynamic-ux.js` per collection page context).

```javascript
pageAccent = getComputedStyle(document.documentElement)
  .getPropertyValue('--bks-active-accent').trim() || '';
```

- On Hours page → `#c8c4be` tint on key borders, masthead rule, labels
- On Glyph page → `#d4a030` amber tint
- On any other page → falls back to `col.color` (per-key collection color)

This means placing the piano section on a collection page gives it that collection's identity automatically — no per-instance configuration needed.

---

## Cinema mode highlights

- Background: `#0A0A0A` brand dark + active collection accent radial wash
- Lacquered fallboard: wood grain (24 sinusoidal lines), horizontal sheen, gold trim
- Shadow cascade from fallboard edge onto keys
- White key press: `shadowBlur = 28`, `shadowColor = col.color` — full glow
- Black key press: `shadowBlur = 22`, same
- Ripples: bloom ring + inner radial fill
- Sound: 3-oscillator pad (root + +0.38% detuned + sub-octave), per-note 1400Hz LPF, 100ms attack, reverb feedback 0.18

---

## Model panel artwork (Canva)

Each collection block has an `image_url` field. When set:
- `modelBg.style.backgroundImage = 'url(' + col.image_url + ')'`
- Overrides the CSS gradient fallback
- Portrait format recommended (width ~400px, height ~600px)
- Dark background + accent gradient + collection name (Canva editorial template)

8 Canva designs created June 2026 — awaiting export confirmation and URL assignment.

---

## Product pop-out (special, future)

The same newspaper lift principle can be applied to product cards:
- Section type: `bks-product-popout`
- Each product card appears as a newspaper clipping
- On hover/scroll-reveal: card lifts with drop shadow
- Implementation: CSS `transform: translateY(-lift) + box-shadow` + CSS `@keyframes` — no canvas needed
- Colour context: adapts via `--bks-active-accent` CSS variable already present on all collection pages
- Recommended trigger: `IntersectionObserver` — card enters viewport → lift animation plays once

---

## Schema settings

| ID | Type | Description |
|---|---|---|
| `style_mode` | select | `cinema` or `editorial` — default `cinema` |
| `fallboard_label` | text | Brand label on fallboard/masthead |
| `hint_text` | text | Bottom hint |
| `cta_label` | text | CTA button label |
| `back_label` | text | Back button label |
| `use_webaudio_fallback` | checkbox | Enable Web Audio synthesis |
| Per block: `image_url` | text | Canva artwork URL for model panel |
| Per block: `audio_url` | text | Suno MP3 CDN URL |

---

## Deploy

```bash
python scripts/deploy_theme_section.py sections/bks-piano-hero.liquid assets/bks-piano-hero.js assets/bks-piano-hero.css
```

Files to sync:
- `04_TEMA_SHOPIFY/sections/bks-piano-hero.liquid` → `_merged_tm04/sections/`
- `04_TEMA_SHOPIFY/assets/bks-piano-hero.js` → `_merged_tm04/assets/`
- `04_TEMA_SHOPIFY/assets/bks-piano-hero.css` → `_merged_tm04/assets/`

---

## Editorial rules (always respect)

- No emoji anywhere in the section
- DM Mono font for all key labels and masthead text
- BakAbo brand paper `#fafaf7` and brand dark `#0A0A0A` as the two poles
- Accent colors strictly from the 8-collection palette (no approximations)
- Style adapts to page context — do not hard-code accent colors in CSS
