# BakAbo — Popup & Overlay AI (Autonomous)

`bakabo-popup-ai` — Autonomous execution skill for creating, configuring, and deploying all popup/overlay/panel elements in the BakAbo Shopify theme.

## Popup archetypes

| Type | Mode | File | Trigger |
|---|---|---|---|
| Piano Collection Panel | cinema / editorial | bks-piano-hero.* | key press |
| Product Pop-out Card | editorial | bks-product-popout | scroll reveal |
| Promotional Overlay | cinema | bks-timed-offer.liquid | timed / exit |
| Member Modal | dark minimal | bks-members-login.liquid | tier gate |

Mode decision:
- Collection/magazine context → `editorial` (`style_mode: editorial`)
- Offer/urgency/sales → `cinema` (default)
- On collection page → inherit `--bks-active-accent` automatically

## Image selection for panels

Image rules for `image_url` field (Piano Hero per-block):
- Portrait 2:3 ratio (400×600px minimum)
- Dark background (`#0A0A0A`) or deep accent wash
- Subject: editorial silhouette / abstract ink / clothing shape
- DM Mono label at bottom allowed
- NO: light/white backgrounds, faces, busy compositions

Image decision:
1. `col.image_url` set → use it, nothing needed
2. Empty + major collection (Glyph, Origin, Riviera, Pulse) → generate via Canva, upload, assign
3. Empty + minor → CSS gradient fallback is acceptable

Canva generation prompt template: `Editorial fashion illustration, {name} collection. Dark background #{bg}. Color accent {color}. Abstract ink silhouette, minimal, architectural. DM Mono label bottom-left. Wallpaper*/System aesthetic. Portrait 2:3.`

## CSS/JS panel architecture

```javascript
// Injected on openCollection()
pianoEl.style.setProperty('--bks-coll-initial', '"' + col.name[0] + '"');
pianoEl.style.setProperty('--bks-coll-accent', col.color);
```

- `--bks-coll-initial` → watermark letter in `::before` (editorial mode left panel)
- `--bks-coll-accent` → pull-quote border, pill borders, CTA hover colour

Editorial panel animation: `translateY(18px)` → `translateY(0)` + opacity 0→1 at 0.52s (slide from page surface).

Newspaper typography: `#bks-coll-name` headline (font-weight 800, border-top 1.5px), `#bks-coll-quote` pull-quote (italic, border-left 2px solid accent), `.bks-prod-pill` square (border-radius 0).

## Autonomous action checklist

1. Identify context: which page? which collections?
2. Decide mode: editorial (collection page) / cinema (homepage, offer)
3. Check `image_url` fields: empty for major collections → generate Canva
4. Edit `bks-piano-hero.liquid` schema blocks
5. Deploy: `python scripts/deploy_theme_section.py sections/bks-piano-hero.liquid assets/bks-piano-hero.js assets/bks-piano-hero.css`
6. Sync to `04_TEMA_SHOPIFY/_merged_tm04/`
7. Confirm HTTP 200

## Product pop-out (future section)

```html
<div class="bks-popout-card" data-product-url="/products/{handle}">
  <div class="bks-popout-image"></div>
  <div class="bks-popout-body">
    <p class="bks-popout-type">{type}</p>
    <h3 class="bks-popout-name">{name}</h3>
    <p class="bks-popout-price">{price}</p>
  </div>
</div>
```

CSS: `transform: translateY(calc(-1 * var(--lift, 0px)))` + `box-shadow` driven by `IntersectionObserver`. `--bks-active-accent` from page context for borders.

AI trigger: collection has 3+ products AND no `bks-product-popout` section → suggest building it.

## Editorial rules (always)

- No emoji, no urgency language in editorial mode
- DM Mono for labels, masthead, key text
- `#0A0A0A` / `#fafaf7` as the only background poles
- Accent colours only from 8-collection palette
- White space is intentional — never fill for the sake of it

Related: `bakabo-theme-build`, `bakabo-shopify-ops`, `bakabo-market-intelligence`
