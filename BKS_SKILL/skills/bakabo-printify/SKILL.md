---
name: bakabo-printify
description: >
  Esperto sistema Printify BKS. Gestisce upload design, sostituzione layer,
  protezione logo, selezione stile per collezione via Worker.
  Trigger: "printify", "aggiorna design", "nuova pezza", "sostituisci artwork",
  "layer", "print area", "scarica immagini", "libreria Printify", "worker stile".
metadata:
  type: skill
  version: "2.0"
  created: "2026-06-23"
  updated: "2026-06-23"
---

# SKILL — BKS PRINTIFY SYSTEM

## Costanti sistema

| Variabile | Valore |
|---|---|
| SHOP_ID | `12030061` |
| API BASE | `https://api.printify.com/v1` |
| Token | `env: PRINTIFY_API_TOKEN` |
| Prodotti totali | 674 |
| Source images locale | `BAKABO_IMAGE_FACTORY_v1.1/output/source/` (680 file) |

---

## Architettura layer — Regola unica

```
SOSTITUISCI → qualsiasi immagine NON logo
PRESERVA    → solo file logo BKS (vedi tabella sotto)
```

### Logo BKS protetti (MAI toccare)

| ID Printify | Nome file | Prodotti |
|---|---|---|
| `6a217ca23d24179e1f1eaf5f` | `bks.png` | shorts, apparel |
| `660d81c6209c2958d2f0bb75` | `LG 002.png` | sneakers, hoodie waistband |

Pattern riconoscimento logo: `^(lg\s*\d+|bks[\s_-]*(logo|label|tag)).*\.(png|svg)$`

---

## Struttura print_areas per tipo prodotto

### Athletic Shorts (blueprint 1084)
```
back_pocket_right  → design (wonder_*.jpg) + possibile extra
inside_label       → bks.png [LOGO — PRESERVA]
left_leg           → design x2
pocket             → design
right_leg          → design x2 + possibile AI artwork
```

### Puffer Jacket (blueprint 934)
```
front              → design (k24.png o wonder_*.jpg)
back               → design
front/back sleeves → design x2 ciascuna
Collar             → design x2 + possibile AI badge (piccolo, scale ~0.07)
```
> Nota: nessun logo su molti puffer — solo design layers

### Sneakers Low-Top (blueprint 291)
```
body_outside_left  → design (wonder_*.jpg) + LG002 x2-3 [LOGO]
body_outside_right → design + LG002 x2-3 [LOGO]
body_inside_left   → design + LG002 x2-3 [LOGO]
body_inside_right  → design + LG002 x2-3 [LOGO]
```

### Pullover Hoodie (blueprint 450)
```
front              → design x2
back               → design + possibile artwork terzi (Marla SneakerArt. ecc.) → SOSTITUISCI
left/right_sleeve  → design
left/right_hood    → design
pocket             → design
waistband          → LG 002.png [LOGO — PRESERVA]
```

---

## File e moduli Python

| File | Funzione |
|---|---|
| `ecommerce_automation/services/printify_client.py` | Client API: `get_product`, `update_product`, `upload_image_from_bytes`, `upload_image_from_url`, `iter_products` |
| `ecommerce_automation/printify_design_updater.py` | Core: `update_product_design()` — identifica design vs logo, sostituisce layer |
| `scripts/_update_printify_design.py` | CLI: `--product-id --image [--dry-run]` |
| `scripts/_probe_product_layers.py` | Ispeziona struttura print_areas di un prodotto |
| `scripts/_download_missing_images.py` | Scarica source mockup da Printify (680 scaricati) |
| `scripts/_audit_images.py` | Stato source/cutout per collezione |

---

## Pipeline design update

```
1. OpenAI genera pezza (PNG high-res, pattern texture)
      ↓
2. upload_image_from_bytes(file_name, png_bytes)
      → Printify risponde con new_image_id
      ↓
3. get_product(shop_id, product_id)
      → legge print_areas correnti
      ↓
4. _find_design_image_ids(print_areas)
      → tutti gli ID non-logo
      ↓
5. _replace_design_in_areas(areas, old_ids, new_image_id)
      → sostituisce ID, preserva x/y/scale/angle
      ↓
6. update_product(shop_id, product_id, {"print_areas": new_areas})
      ✓ Design aggiornato, logo intatto
```

### Uso CLI
```bash
# Dry run (sicuro, non modifica nulla)
python scripts/_update_printify_design.py \
  --product-id 6a2544f48ca667581803f49b \
  --image output/generated/nuova_pezza.png \
  --dry-run

# Aggiornamento reale
python scripts/_update_printify_design.py \
  --product-id 6a2544f48ca667581803f49b \
  --image output/generated/nuova_pezza.png
```

---

## Sistema artworkPrompt — BKS Sala Disegno (v2)

Da 23/06/2026 il Worker costruisce il prompt artwork esclusivamente tramite `BKS_SALA_DISEGNO`.

### Regole assolute prompt
- **MAI** nomi di artisti esterni (no Basquiat, Haring, Warhol, Bosch, Hockney, Gauguin, ecc.)
- **MAI** figure umane, animali, volti, personaggi
- **SEMPRE** superficie proprietaria BKS originale
- **SEMPRE** tile seamless all-over
- **SEMPRE** qualità minima 21/25 BKS Artwork Quality Index

### Struttura prompt
```
1. BakAbo Sala Disegno — original all-over print surface...
2. BKS [Collection] collection — [mood]
3. Weekly trend direction: [weeklyBrief] (opzionale, da KV)
4. Execution technique: [sala.tecnica]
5. Surface: [baseDesc]
6. Tools in use: [toolsDesc]
7. Garment fabric: [materialCtx] (opzionale)
8. Creative direction: [design_description] (opzionale)
9. Color system: [col.keywords]. Accent: [col.accent]
10. Visual DNA: [dnaArtwork.base]
11. CRITICAL: NO human figures, NO faces, NO animals...
12. Seamless all-over tile pattern...
13. QUALITY MANDATE: score 21-25/25...
```

### Endpoint generate
```
POST https://bks-agent.bakabo.workers.dev/design-generate
{
  "product_id": "...",
  "collection": "origin",   ← usa "origin" non "folklore"
  "dry_run": true
}
```

---

## Integrazione Worker — Selezione stile BKS

Il Cloudflare Worker (`bks-agent.bakabo.workers.dev`) può attivare il design update via comando testuale. Il Worker riconosce l'intent e chiama il Python backend.

### Comandi Worker riconosciuti
```
"aggiorna design [collezione] [prodotto]"
"nuova pezza per [handle prodotto]"
"applica stile [collezione] a [handle]"
"sostituisci artwork [product_id]"
```

### Selezione stile per collezione (Worker → Python)

Ogni collezione ha colori, mood e pattern di riferimento:

| Collezione | BG | Accent | Mood design | Pattern keywords |
|---|---|---|---|---|
| **hours** | `#1A1A1A` | `#C9B79C` | dark-warm, brocade, floral | floral, botanical, gold |
| **glyph** | `#0A0A0A` | `#C9B79C` | dark, geometric, coded | symbol, glyph, grid, hex |
| **marker** | `#F5F0E8` | `#0A0A0A` | light, gestural, brush | stroke, drip, urban, painted |
| **riviera** | `#E8DCC8` | `#2A8B85` | warm, coastal, resort | wave, palm, terracotta, teal |
| **pulse** | `#0E1420` | `#C9B79C` | navy-dark, kinetic, optical | hex, grid, optical, wave |
| **token** | `#080810` | `#C9B79C` | darkest, pixel, arcade | pixel, maze, circuit, neon |
| **flag** | `#FAFAF7` | `#0A0A0A` | pure-pop, flat, stencil | colorblock, banner, primary |
| **origin** | `#EDE5D0` | `#489808` | warm-organic, botanical abstraction | earth-tone, resist-dye, botanical mark, linen |

### Endpoint Worker (da implementare)
```javascript
// POST /printify-update
{
  "product_id": "651f3b7691a9771a560ac91d",
  "collection": "pulse",
  "design_url": "https://cdn.bakabo.club/designs/new_hex_v2.png",
  "dry_run": false
}
// → chiama Python master_agent → printify_design_updater
```

---

## Libreria Printify uploaded files

URL: `https://printify.com/app/account/uploaded-files`
API: `GET /v1/uploads.json?page=1&limit=50`

I file `wonder_*.jpg` sono i design originali ad alta risoluzione (8533×8533px).  
**REGOLA:** non usare mai mockup JPG (product source) come design — usare solo:
- File `wonder_*.jpg` dalla libreria Printify (artwork originali)
- PNG generati da OpenAI (nuovi design)

### Recupero file dalla libreria
```python
uploads = client.iter_uploads(max_pages=50)
# filtra per nome o dimensione per trovare il design corretto
design = next(u for u in uploads if "wonder_" in u["file_name"])
```

---

## Prodotti testati (dry-run + update reale)

| Prodotto | ID | Tipo | Design ID | Logo protetto |
|---|---|---|---|---|
| BKS Hours Brocade Shorts | `6a2544f48ca667581803f49b` | Shorts | `wonder_1710849852306.jpg` | `bks.png` |
| BKS Fawn Puffer | `6587f8cf11b3fd24380aac8a` | Puffer | `k24.png` | — |
| BKS Pulse Hex Sneakers | `651f3b7691a9771a560ac91d` | Sneakers | `wonder_1710848635576.jpg` | `LG 002.png` |
| BKS Glyph Drift Hoodie | `65650cc13d1ec0d32b03cc06` | Hoodie | `wonder_1705789511366.png` | `LG 002.png` |

---

## Note critiche

- **MAI** usare mockup source JPG come design — è la foto del prodotto, non l'artwork
- **MAI** modificare `bks.png` o `LG 002.png` — brand identity invariabile
- Sempre fare `--dry-run` prima di aggiornare in produzione
- Il Collar dei puffer può avere AI badges a scala molto piccola (0.07) — vengono sostituiti (comportamento corretto)
- `Marla SneakerArt.` e altri artwork di terzi su back/retro vanno sostituiti (opzione B confermata da Roberto)
- PRINTIFY_SHOP_ID = `12030061` — NON cambiare mai
