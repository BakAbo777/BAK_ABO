# BKS TM04 Theme Skill
**Tema attivo su Shopify store bakabo.club**
**Theme ID live:** `202392961362` — "BKS TM04 MEMBER TIER + SHOPPER 17JUN2026"
**Source locale:** `04_TEMA_SHOPIFY/_merged_tm04/`
**Script push:** `scripts/push_magazine_update.py`, `scripts/push_collection_templates.py`, `scripts/push_section_and_retry.py`

---

## Architettura pagina magazine (flusso colore)

```
┌─────────────────────────────────┐
│  HEADER  white #fafaf7          │  bakabo-header.liquid (snippet)
│  sticky · logo centrato         │  render da layout/theme.liquid
├─────────────────────────────────┤
│  COLLECTION SIGNAL  #0A0A0A     │  bks-collection-signal.liquid
│  hero dark + radial accent glow │  accent per collezione (var CSS)
│  ████ gradient accent bar ████  │  .bks-collection-signal__accent
├─────────────────────────────────┤
│  PRODUCT GRID  magazine flow    │  main-collection-product-grid.liquid
│  top: #0A0A0A                   │  gradient 0%→dark
│  9%:  dark + accent tint        │
│  18%: tinted paper              │  → prodotti su sfondo chiaro
│  44%+: #FAFAF7 neutro           │
├─────────────────────────────────┤
│  FOOTER  dark #0A0A0A           │  footer.liquid (color_scheme: accent-1)
│  bookend chiusura pagina        │  footer-group.json
└─────────────────────────────────┘
```

---

## Sistema colori per collezione

| Handle           | Accent        | Foreground |
|------------------|---------------|------------|
| bks-hours        | `#c8c4be`     | `#0A0A0A`  |
| bks-origin       | `#489808`     | `#0A0A0A`  |
| bks-glyph        | `#d4a030`     | `#0A0A0A`  |
| bks-marker       | `#c04418`     | `#FAFAF7`  |
| bks-riviera      | `#0ca898`     | `#0A0A0A`  |
| bks-pulse        | `#8888cc`     | `#0A0A0A`  |
| bks-token        | `#9828d8`     | `#FAFAF7`  |
| bks-flag         | `#c82020`     | `#FAFAF7`  |
| puffer-jacket    | `#c8c4be`     | `#0A0A0A`  |
| windbreaker      | `#0ca898`     | `#0A0A0A`  |
| pullover-hoodie  | `#8888cc`     | `#0A0A0A`  |
| lounge-pants     | `#9828d8`     | `#FAFAF7`  |
| sneakers         | `#d4a030`     | `#0A0A0A`  |
| backpack         | `#489808`     | `#0A0A0A`  |
| flip-flop        | `#c04418`     | `#FAFAF7`  |
| athletic-shorts  | `#c82020`     | `#FAFAF7`  |
| swim-trunks      | `#0ca898`     | `#0A0A0A`  |
| beach-towel      | `#0ca898`     | `#0A0A0A`  |
| swimwear         | `#0ca898`     | `#0A0A0A`  |
| one-piece-swimsuit | `#9828d8`   | `#FAFAF7`  |
| racerback-dress  | `#d4a030`     | `#0A0A0A`  |
| womens-tee       | `#d4a030`     | `#0A0A0A`  |
| duffle-bag       | `#9828d8`     | `#FAFAF7`  |
| cozy-slipper     | `#9828d8`     | `#FAFAF7`  |
| travel-bag       | `#c8c4be`     | `#0A0A0A`  |
| cut-dress        | `#d4a030`     | `#0A0A0A`  |

Le variabili CSS sono iniettate in `main-collection-product-grid.liquid` via `case collection.handle`.

---

## Color Schemes Shopify (settings_data.json)

| ID           | Background  | Uso                        |
|--------------|-------------|----------------------------|
| background-1 | `#fafaf7`   | header, product grid, pages |
| background-2 | `#efeae0`   | bone/ivory (non usato live) |
| inverse      | `#242833`   | sezioni scure medie         |
| accent-1     | `#0a0a0a`   | **footer** · hero sections  |
| accent-2     | `#c9b79c`   | badge, accenti caldi        |

---

## Sezioni chiave

### `snippets/bakabo-header.liquid`
- Menu: `linklists['main-menu-1']` → fallback `linklists['main-menu']`
- Layout: grid 3 colonne (nav | logo | actions)
- Mobile: hamburger + drawer overlay
- Sticky + hide-on-scroll-down (> 200px, desktop only)

### `sections/bks-collection-signal.liquid`
- Hero dark per ogni collezione BKS
- Accetta `max_blocks: 16` subnav links
- CSS accent via `--bks-accent` CSS var per-collection
- Termina con gradient bar `.bks-collection-signal__accent`

### `sections/main-collection-product-grid.liquid`
- **Magazine gradient**: dark→tinted (0%→18%→44%→100%)
- Editorial layout: 12 colonne, span asimmetrico (5-4-3-3 pattern per 8 prodotti)
- Tablet: 6 colonne, mobile: 2 colonne
- Setting chiave: `bks_editorial_grid: true` (default) — abilitato da schema
- Intro block (kicker + title + glass panel) su sfondo scuro → testo bianco

### `sections/footer.liquid`
- Custom BKS footer (override Dawn footer)
- 4 colonne: Brand + Collections + Support + Newsletter
- `color_scheme: "accent-1"` → dark #0A0A0A

---

## Menu principale (main-menu-1)

Struttura attiva (aggiornata 2026-06-17):

```
Home
BKS Man
BKS Woman
Collections
  ├─ BKS Hours → /collections/bks-hours
  ├─ BKS Origin → /collections/bks-origin
  ├─ BKS Glyph → /collections/bks-glyph
  ├─ BKS Marker → /collections/bks-marker
  ├─ BKS Riviera → /collections/bks-riviera
  ├─ BKS Pulse → /collections/bks-pulse
  ├─ BKS Token → /collections/bks-token
  ├─ BKS Flag → /collections/bks-flag
  └─ All collections → /collections
Product Types
  ├─ BKS Puffer Jackets → /pages/bks-puffer-jackets
  ├─ BKS Windbreakers → /pages/bks-windbreakers
  ├─ BKS Pullover Hoodies → /pages/bks-pullover-hoodie
  ├─ BKS Lounge Pants → /pages/bks-lounge-pants
  ├─ BKS Sneakers → /pages/bks-sneakers
  ├─ BKS Backpacks → /pages/bks-backpack
  ├─ BKS Travel Bags → /pages/bks-travel-bag
  ├─ BKS Swimwear → /pages/bks-swimwear
  ├─ BKS Flip Flops → /pages/bks-flip-flop
  ├─ BKS Athletic Shorts → /pages/bks-athletic-shorts
  ├─ BKS One-Piece Swimsuits → /pages/bks-one-piece-swimsuits
  ├─ BKS Racerback Dresses → /pages/bks-racerback-dresses
  ├─ BKS Swim Trunks → /pages/bks-swim-trunks
  ├─ BKS Hawaiian Shirts → /pages/bks-hawaiian-shirt
  ├─ BKS Beach Towels → /pages/bks-beach-towel
  ├─ BKS Duffel Bags → /pages/bks-duffel-bag
  └─ All products → /collections/all
BKS Members
  ├─ Wishlist
  ├─ Mobile Try-On
  ├─ Account
  └─ Cart
About
```

Script per ricostruire menu: `scripts/fix_menu_and_colors.py`
Script per ispezionare menu: `scripts/inspect_menus.py`

---

## Template collection (29 totali)

Ogni template ha:
- `bks_signal` section (type: `bks-collection-signal`) con subnav specifici
- `product-grid` section (type: `main-collection-product-grid`) con `color_scheme: background-1`

Pusho con: `scripts/push_collection_templates.py` + `scripts/push_section_and_retry.py`

**Nota:** `bks-collection-signal.liquid` deve avere `max_blocks: 16` (non 6) altrimenti i template BKS con 7+ subnav falliscono con 422.

---

## Regole push tema

1. Modificare file locali in `04_TEMA_SHOPIFY/_merged_tm04/`
2. Pushare via REST API: `PUT /themes/202392961362/assets.json`
3. Ordine sicuro: sections → templates
4. Rate limit: `time.sleep(0.4)` tra ogni asset

**Non modificare il .env** — l'ID shop Printify nel .env è stale, viene risolto dinamicamente.

---

## Sistema Responsive + Contrasto (armocromista pass 2026-06-18)

### File: `assets/bks-responsive.css`

Caricato in `theme.liquid` come ultimo CSS (massima specificità).
Struttura in 4 sezioni:

1. **Mobile patch** — product page a ≤989px e ≤749px; NO override `.page-width`
2. **Section tokens** — `.bks-section--dark` (con `color-scheme: dark`) e `.bks-section--light`
3. **Armocromista pass** — testo forzato per ogni tipo di pagina:
   - Sezioni dark (collection-signal, impact, timed-offer) → `color: #FAFAF7`
   - Product system panels → `color: #0A0A0A`; kicker/label → `#5a5450` + bordo accent
   - Collections index light → `color: #0A0A0A`
   - Member dashboard inputs → `background: #1e1e1e; color: #f0ece4`
   - Related products (background-2) → `color: #0A0A0A`
   - Footer (accent-1) → `color: #FAFAF7`
4. **Metal tier badge vars** — `--bks-tier-lead/iron/brass/silver/gold`

### Regola armocromista accent

Accenti su sfondo **chiaro** (`#FAFAF7`) — usare solo come decorazione, MAI come testo:

- Hours `#c8c4be` — contrasto 1.6:1, invisibile
- Glyph `#d4a030` — contrasto 2.6:1, insufficiente
- Riviera `#0ca898` — contrasto 3.3:1, insufficiente
- Pulse `#8888cc` — contrasto 3.0:1, insufficiente

Accenti su sfondo **scuro** (`#0A0A0A`) — usabili come testo decorativo:

- Marker `#c04418` — contrasto 4.2:1 su scuro (AA large)
- Token `#9828d8` — contrasto 4.6:1 su scuro (AA)
- Flag `#c82020` — contrasto 3.7:1 su scuro (AA large)
- Origin `#489808` — contrasto 3.3:1 su scuro (AA large)

Regola operativa: gli accent color BKS sono sempre DECORATIVI (bordi, punti, chip, glow). Per testo su panel chiaro usare `#0A0A0A` o `#5a5450` (muted). Per testo su sfondo scuro usare `#FAFAF7`.

### Fix `bks-product-system.liquid`

- `.bks-product-system__kicker`: era `color-mix(accent 80%, #0A0A0A)` → ora `color: #5a5450` + `border-bottom: 2px solid accent`
- `.bks-product-system__label`: era `color-mix(accent 84%, #0A0A0A)` → ora `color: #0A0A0A` + `border-left: 3px solid accent`
- Motivo: per Hours/Riviera/Pulse (accenti chiari) il color-mix produceva contrasto <2:1 su panel bianco

### Fix product templates (15 file)

Tutti i template `product*.json` in `_merged_tm04/templates/` avevano `bks_cindex` block c8:
- `"name": "BKS Folklore"` → `"BKS Origin"`
- `"collection_handle": "bks-folklore"` → `"bks-origin"`
- `"tagline": "Narrative warmth"` → `"Natural materials"`

---

## Armocromista pass 2 — tutte le 8 collezioni (2026-06-18)

Audit completo: 47/47 elementi PASS, zero fail.

### Fix `bks-collection-signal.liquid`

- `.bks-signal-tag__accent`: era `color: var(--bks-accent)` → ora `color: color-mix(in srgb, var(--bks-accent) 60%, #FAFAF7)` — porta Token/Marker/Flag da 3.4–3.8:1 a 6.5–7.4:1 su dark bg
- `.bks-collection-signal__typologies-label`: stessa fix — da `var(--bks-accent)` a mix 60% con `#FAFAF7`

### Fix `bks-responsive.css` (bordi accent su white)

- `.bks-product-system__kicker border-bottom-color`: `color-mix(in srgb, var(--bks-product-accent) 60%, #0A0A0A)` — Hours 1.7→4.3:1, Glyph 2.4→5.5:1 (non-text 3:1)
- `.bks-product-system__label border-left-color`: stessa formula

### Fix `main-collection-product-grid.liquid`

- Origin `bks_grid_foreground`: `#FAFAF7` → `#0A0A0A` (verde #489808 con bianco = 3.5:1 FAIL, con nero = 5.4:1 PASS)
- backpack: stessa fix (stesso accent #489808)
- Made-to-order stamp `::after`: opacity 74% → 85% (su white 3.4→5.2:1)

### Foreground tabella corretta (aggiornata)

Nota: nella tabella "Sistema colori per collezione" sopra, `bks-origin` e `backpack` usano `#0A0A0A` come foreground (non `#FAFAF7`).

---

## Script di manutenzione

| Script | Funzione |
| --- | --- |
| `scripts/push_magazine_update.py` | Push: product-grid, footer, **bks-product-system.liquid**, **theme.liquid**, **bks-responsive.css** |
| `scripts/push_section_and_retry.py` | Push `bks-collection-signal.liquid` (max_blocks 16) + retry template falliti |
| `scripts/push_collection_templates.py` | Push **collection + product templates** da `_merged_tm04/templates/` |
| `scripts/deploy_theme_section.py` | Push sezioni `04_TEMA_SHOPIFY/` + **bks-responsive.css** |
| `scripts/inspect_menus.py` | Ispeziona menu live Shopify |
| `scripts/fix_menu_and_colors.py` | Ricostruisce menu `main-menu-1` con struttura BKS |
| `scripts/_read_store.py` | Lista collezioni e pagine reali dello store (per handle corretti) |
| `scripts/archive_products_no_image.py` | Archivia prodotti Shopify senza immagine |

### Procedura: archivia prodotti senza immagine

```bash
# Anteprima (dry run, non archivia)
python scripts/archive_products_no_image.py

# Archiviazione reale
python scripts/archive_products_no_image.py --execute
```

La card CSS `:has()` nel product grid nasconde già le card vuote visivamente.
L'archivio le rimuove definitivamente dal catalogo Shopify.

### Procedura: rimuovere selettore lingua dal footer

In `sections/footer-group.json`, sezione `footer.settings`:

```json
"enable_country_selector": false,
"enable_language_selector": false
```

Poi pushare con `push_magazine_update.py`.
Riabilitare solo se il sito viene multilingua.

---

## Aggiornamenti fatti il 2026-06-17

- Menu `main-menu-1` ricostruito con struttura corretta (handle reali dallo store)
- 29 collection templates pushati con subnav specifici e link corretti
- `bks-collection-signal.liquid` aggiornato con `max_blocks: 16`
- `main-collection-product-grid.liquid`: magazine gradient dark→tinted, mobile ottimizzato
- `footer-group.json`: `color_scheme` cambiato a `accent-1` (dark footer)
- Contrasto testo ottimizzato WCAG AA: kicker 0.48→0.70, panel text 0.66→0.84, footer opacità +20-30%
- `footer-group.json`: `enable_language_selector/country_selector` → false (widget floating rimosso)
- `main-collection-product-grid.liquid`: CSS `:has()` nasconde card senza immagine prodotto
- `footer.liquid`: schema default `color_scheme` → `accent-1`; gradient warm-dark background
- `footer.liquid`: schema default `color_scheme` corretto da `scheme-1` a `accent-1`
