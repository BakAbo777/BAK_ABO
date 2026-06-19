---
name: bakabo-popup-ai
description: Use this skill whenever you need to create, configure, deploy, or choose assets for any popup/overlay/panel in the BakAbo theme — including the Piano Hero collection panels, promotional overlays, editorial product pop-outs, and image selection. Triggers include: "crea popup", "aggiorna pannello", "scegli immagine per", "deploy popup", "configura pannello editoria", "newspaper effect", "tasto pianoforte", or any time a section opens an overlay/panel. This skill makes the AI autonomous on popup work — it decides mode, chooses images, deploys, and trains on outcomes. Works with bakabo-theme-build (deploy), bakabo-shopify-ops (section placement), bakabo-brand (voice), bks-newspaper-popout-skill (lift mechanics).
---

# BakAbo — Popup / Overlay AI Skill

This skill makes the BakAbo internal AI **autonomous** on popup and overlay work. It covers: when to act, how to choose the right popup type, how to select/generate images, how to configure and deploy, and how to evaluate outcomes.

---

## 1. Popup archetypes in BakAbo

| Type | Trigger | Mode | File |
|---|---|---|---|
| **Piano Collection Panel** | Key press → `openCollection()` | Cinema or Editorial | `bks-piano-hero.*` |
| **Product Pop-out Card** | Scroll reveal / hover | Editorial only | `bks-product-popout` (future) |
| **Promotional Overlay** | Timed (3s) / Exit-intent | Cinema dark | `bks-timed-offer.liquid` |
| **Member Area Modal** | Login gate / tier check | Dark minimal | `bks-members-login.liquid` |

**Decision rule:**
- Collection/editorial context → **editorial mode** (`style_mode: editorial`)
- Offer/urgency/sales context → **cinema mode** (`style_mode: cinema`)
- Anywhere on a collection page → inherit `--bks-active-accent` automatically

---

## 2. Cinema vs editorial — when to choose which

```
Is this about a specific BakAbo collection?  → editorial
Is this a time-limited offer / drop alert?   → cinema
Is this on the homepage?                     → cinema (default dark brand)
Is this on a collection-specific page?       → editorial (paper/ink)
Is the user a BKS Archive tier (gold)?       → cinema (luxury feel)
Is the user exploring / browsing?            → editorial (magazine feel)
```

---

## 3. Image selection for panel artwork

### When to use Canva images
- Panel `image_url` field is empty AND the collection has editorial visual potential
- Scheduled collection drops (new season, Origin, Glyph, etc.)
- When `--bks-active-accent` is strong enough to build an editorial composition

### What makes a good panel image for Piano Hero
- **Format:** Portrait, 400×600px minimum, 2:3 ratio
- **Background:** Dark (`#0A0A0A`) or deep collection-accent wash
- **Subject:** Editorial mannequin / clothing silhouette / abstract ink marks
- **Typography overlay allowed:** small DM Mono label at bottom — collection name in light ink
- **What to AVOID:** photos with light/white backgrounds (destroys cinema mode); busy compositions; faces
- **Style reference:** Wallpaper*, System magazine, SSENSE editorial — cold, architectural, minimal

### AI image decision tree
```
Has col.image_url?
  YES → use it, nothing needed
  NO  → is this a major collection (Glyph, Origin, Riviera, Pulse)?
        YES → generate via Canva using editorial template, upload, set image_url
        NO  → let CSS gradient handle it (acceptable fallback)
```

### Canva generation prompt template
When generating a panel image for collection `{name}` with accent `{color}`:
```
Editorial fashion illustration, {name} collection.
Dark background #{background}.
Color accent {color}.
Abstract ink silhouette, minimal, architectural.
DM Mono font label "{BKS — {name}}" bottom-left, small.
Wallpaper* / System magazine aesthetic.
Portrait 2:3 ratio.
NO faces. NO photography. Graphic art only.
```

---

## 4. Configuring the Piano Hero panel

### Shopify admin path
`Themes → Customize → (page with Piano Hero section) → Piano Hero section → Settings`

### Key settings
| Setting | Values | When to change |
|---|---|---|
| `style_mode` | `cinema` / `editorial` | Default cinema for homepage, editorial for collection pages |
| `fallboard_label` | string | BKS Studio usually; can be collection name for special drops |
| Per block: `image_url` | URL | Set after Canva export |
| Per block: `audio_url` | Suno CDN URL | When new ambient track generated |

### Editing collection blocks in piano
Each block = one key = one collection. Block order = left-to-right key order.
Block fields: `name`, `slug`, `key_label`, `freq_hz`, `color`, `gradient`, `quote`, `products`, `url`, `arm_season`, `arm_desc`, `image_url`, `audio_url`

---

## 5. Deploy commands (autonomous)

Run from `i:\BAK ABO\` root:

```python
# Single file deploy
python scripts/deploy_theme_section.py sections/bks-piano-hero.liquid

# Multi-asset deploy
python scripts/deploy_theme_section.py sections/bks-piano-hero.liquid assets/bks-piano-hero.js assets/bks-piano-hero.css
```

Also sync to `_merged_tm04/`:
```
04_TEMA_SHOPIFY/sections/bks-piano-hero.liquid → 04_TEMA_SHOPIFY/_merged_tm04/sections/
04_TEMA_SHOPIFY/assets/bks-piano-hero.js       → 04_TEMA_SHOPIFY/_merged_tm04/assets/
04_TEMA_SHOPIFY/assets/bks-piano-hero.css      → 04_TEMA_SHOPIFY/_merged_tm04/assets/
```

Theme ID: `202392961362` (TM04 draft — always deploy here)

---

## 6. How the editorial panel is built (CSS/JS architecture)

### CSS variables injected per collection open
```javascript
pianoEl.style.setProperty('--bks-coll-initial', '"' + col.name[0] + '"');
pianoEl.style.setProperty('--bks-coll-accent', col.color);
```

- `--bks-coll-initial` → large watermark letter in `#bks-model-panel::before`
- `--bks-coll-accent` → pull-quote left border color, pill borders, CTA hover

### Slide-up entry animation (editorial)
`.bks-paper #bks-coll-screen` starts at `translateY(18px)` + `opacity:0`, animates to `translateY(0)` + `opacity:1` at 0.52s ease — simulates paper page lifting from the surface.

### Newspaper typography
- `#bks-coll-name`: headline `font-size: clamp(26px, 4.4vw, 52px)`, `font-weight: 800`, `border-top: 1.5px solid #0A0A0A`
- `#bks-coll-quote`: italic, `border-left: 2px solid --bks-coll-accent`
- `.bks-prod-pill`: `border-radius: 0` (square — newspaper classification style)
- All text: `color: rgba(20,14,6,*)` ink tones

### Page color adaptation
On collection pages `bks-dynamic-ux.js` sets `--bks-active-accent` on `<html>`. Piano reads it in `getPageAccent()`. This means:
- Piano on Hours page → warm neutral `#c8c4be` tinting on keys and masthead
- Piano on Glyph page → amber `#d4a030`
- Piano on homepage → falls back to each collection's own color

---

## 7. Autonomous action checklist

When the AI is asked to "add piano to [page]" or "aggiorna popup":

1. **Identify context** — what page? which collection(s)?
2. **Choose mode** — editorial (collection page) or cinema (homepage/offer)
3. **Check image_url** — is Canva artwork needed?
4. **Edit liquid schema** — set `style_mode`, update block fields
5. **Deploy** — `python scripts/deploy_theme_section.py ...`
6. **Sync** — copy to `_merged_tm04/`
7. **Verify** — confirm deploy response HTTP 200
8. **Update memory** — note changes in `theme_ai_assistant.py` BKS_SYSTEM_PROMPT if architectural

---

## 8. Future: product pop-out section

Pattern: same newspaper lift, applied to product cards.

```html
<!-- bks-product-popout block -->
<div class="bks-popout-card" data-product-url="/products/{handle}">
  <div class="bks-popout-image">...</div>
  <div class="bks-popout-body">
    <p class="bks-popout-type">{type}</p>
    <h3 class="bks-popout-name">{name}</h3>
    <p class="bks-popout-price">{price}</p>
  </div>
</div>
```

CSS: `transform: translateY(var(--lift,0)) box-shadow: 0 var(--lift) 40px rgba(20,14,6,0.12)` — driven by `IntersectionObserver` on scroll entry. Accent border from `--bks-active-accent`.

**AI trigger:** When any collection has 3+ products AND the page has no `bks-product-popout` section → suggest adding it. Generate the section file based on this skill.

---

## 9. Editorial rules (always)

- No emoji in any popup/panel copy
- DM Mono for labels, key text, masthead
- `#0A0A0A` and `#fafaf7` are the only background poles
- Accent colors only from the 8-collection palette — never approximate
- The panel must BREATHE — white space is intentional, not empty
- No urgency language in editorial mode ("Limited!" "Only 3 left!" → not in editorial)
