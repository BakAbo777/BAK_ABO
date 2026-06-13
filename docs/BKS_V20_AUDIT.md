# BKS_V20_TEXTS_COLOR_READY — Audit Report
## Dawn 15.4.1 · Giugno 2026

22 check totali. Riepilogo: **6 critici · 5 warning · 11 OK**.

---

## 🔴 CRITICI (6) — bloccare prima del publish

---

### 🔴 C1 — `series` visibile sulla product page

**File:** `sections/bks-product-meta.liquid` righe 127–128

```liquid
<span>Series</span>
<strong>{{ bks_series | default: '—' }}</strong>
```

Il metafield `bks.series` (valori: `neo-expressionism`, `hyperrealism`, `brut`, ecc.) viene mostrato al cliente. Questo viola il principio fondamentale: i metadata interni non sono mai customer-facing.

**Fix:**
```liquid
{{- comment -}} Series row rimosso — internal metadata, never customer-facing {{- endcomment -}}
```
Rimuovere l'intero `<div class="bks-product-meta__cell">` che contiene `<span>Series</span>`.

---

### 🔴 C2 — Google Fonts non caricati via `<link>` tag

**File:** `layout/theme.liquid`

Le variabili CSS `--bks-font-display: 'Bebas Neue'` e `--bks-font-body: 'DM Sans'` sono definite ma **nessun `<link>` verso fonts.googleapis.com** è presente. I font vengono caricati solo via Shopify font API (che serve i font scelti nel Customizer), non Bebas Neue e DM Sans da Google.

Risultato: Bebas Neue e DM Sans **non rendereranno** a meno che siano anche i font selezionati nel Customizer. Se il Customizer usa altri font, le variabili puntano a font non caricati.

**Fix — aggiungere in `layout/theme.liquid` subito dopo `<meta name="viewport">`:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,400&family=DM+Mono:wght@400;500&display=swap">
```

---

### 🔴 C3 — `BAKABO` unspaced in testo visibile / default copy

**File:** multipli — impatto su sezioni attivamente in uso dall'homepage

Occorrenze in copy visibile o schema defaults che il Customizer mostra:

| File | Riga | Contenuto |
|---|---|---|
| `bks-impact-home.liquid` | 892 | `default: "BAKABO container / Creator: BKS Studio"` |
| `bks-product-meta.liquid` | 103–106 | `BAKABO container` in testo fisso hardcoded |
| `bks-trust-reviews.liquid` | 345, 407 | `BAKABO trust layer` / `same BAKABO trust system` |
| `BKS_WOMAN.liquid` | 29, 286, 290 | `BAKABO container / Creator: BKS Studio` · `BAKABO Woman Collection` |
| `bks-hero-video-image.liquid` | 416–419 | defaults con `BAKABO container` |

**Fix per `bks-product-meta.liquid` righe 103–106 (hardcoded, priorità massima):**
```html
<!-- prima -->
<div class="bks-kicker">BAKABO container / Creator: BKS Studio</div>
<p>Every BKS Studio piece lives inside the BAKABO container...</p>

<!-- dopo -->
<div class="bks-kicker">BKS Studio · AI-Art Atelier</div>
<p>Every BKS piece is designed by the studio, printed on demand after purchase.</p>
```

Per i `"default"` negli schema JSON: cambiarli in Customizer o via str_replace nei file.

---

### 🔴 C4 — `Luxury` / `Premium` in copy defaults di sezioni attive

**File:** `bks-sneakers-panel.liquid` (multipli) · `Bks-Neo-Classic-C.liquid` · sezioni split hero

Occorrenze:
- `"Luxury contemporary sneakers blending coastal geometry..."` × 6 defaults
- `"Premium Quality"` come label feature × 6 defaults
- `"editorial premium identity"` nei split hero text defaults

Queste sono `"default"` values nello schema JSON — se non sovrascritte nel Customizer, appaiono al cliente.

**Fix globale per `bks-sneakers-panel.liquid`** — sostituire tutti i `"Premium Quality"` con `"AI-Generated Print"` e tutte le tagline `"Luxury contemporary sneakers..."` con varianti coerenti:
```
"Sneakers from the BKS [Collection] collection. AI-generated all-over print, made to order."
```

---

### 🔴 C5 — Footer mancante del blocco EU Representative (HONSON VENTURES)

**File:** `sections/footer.liquid`

Nessuna occorrenza di `HONSON`, `Limassol`, `gpsr`, `EU Representative` nel footer. Il blocco legale obbligatorio per GPSR compliance è assente.

**Fix — aggiungere alla fine del footer, prima del tag `</footer>` o nel blocco legale:**
```html
<div class="bks-footer__eu-rep">
  <p><small>EU Representative (GPSR): HONSON VENTURES LIMITED, Gnaftis House flat 102, Limassol, Mesa Geitonia, 4003, Cyprus — <a href="mailto:gpsr@honsonventures.com">gpsr@honsonventures.com</a></small></p>
</div>
```

---

### 🔴 C6 — 13 collection templates 2026 mancanti

Le Shopify smart collection appena create hanno handle che non trovano template dedicato — useranno `collection.json` (default) che può non caricare la sezione corretta.

**Templates mancanti:**
```
collection.sneakers.json
collection.swim-trunks.json
collection.one-piece-swimsuit.json
collection.windbreaker.json
collection.athletic-shorts.json
collection.lounge-pants.json
collection.pullover-hoodie.json
collection.racerback-dress.json
collection.travel-bag.json
collection.backpack.json
collection.flip-flop.json
collection.cozy-slipper.json
collection.womens-tee.json
collection.swimwear.json
```
`collection.puffer-jacket.json` e `collection.outerwear.json` esistono già ✅

**Fix — creare tutti come copie del default:**
```bash
cd templates
for h in sneakers swim-trunks one-piece-swimsuit windbreaker athletic-shorts lounge-pants pullover-hoodie racerback-dress travel-bag backpack flip-flop cozy-slipper womens-tee swimwear; do
  cp collection.json collection.${h}.json
done
```
Poi personalizzare ciascuno se si vuole una sezione hero/intro specifica.

---

## ⚠️ WARNING (5) — correggere prima del lancio

---

### ⚠️ W1 — Doppio Google Tag Manager

**File:** `layout/theme.liquid` righe 18–23 + 305–306

Due container GTM attivi simultaneamente: `GTM-M4ND7QL` (WEB container, principale) e `GT-TWMGQB9`. Il codice stesso contiene un commento che dice *"GA4 e Google Ads gestiti via GTM-M4ND7QL — aggiungere in GTM per evitare doppio firing"*.

**Azione:** verificare se `GT-TWMGQB9` è ancora necessario. Se GA4 è già gestito dentro `GTM-M4ND7QL`, rimuovere `GT-TWMGQB9` per evitare doppio firing degli eventi di acquisto.

---

### ⚠️ W2 — Token CSS mancanti: `--bks-shadow`, `--bks-ink`, `--bks-mocha`

**File:** `layout/theme.liquid`

Solo 7 variabili BKS definite (`--bks-font-display/body/mono`, `--bks-onyx/salt/bone/graphite/ash/dune/accent`). Mancano:
- `--bks-shadow: #242833` — usato nell'AI-art panel e sezioni dark
- `--bks-ink: #0F2240` — accent Riviera/BKS Pulse
- `--bks-mocha: #443C3C` — warm dark alternative

Se le sezioni li usano inline, renderizzano correttamente. Se li ereditano dal `:root`, fallback a non-definito.

**Fix — aggiungere al blocco CSS vars in theme.liquid:**
```css
--bks-shadow: #242833;
--bks-ink:    #0F2240;
--bks-mocha:  #443C3C;
```

---

### ⚠️ W3 — 43 template legacy nel repository

Templates per collezioni dismesse (`canvas`, `circus`, `dog`, `mondello`, `neo-dada`, `collezione-*`, `island-sneakers`, `japan-sneakers`, ecc.) — 43 file. Non causano errori sul live ma aumentano il peso del repository, creano confusione, e alcuni (`collection.neo-dada.json`, `page.bks-tribal-signals.json`) violano le guardrail di collection naming.

**Azione:** eliminare tutti i 43 dal file system prima del deploy finale. Non impattano URL live se le collection Shopify corrispondenti non esistono più.

---

### ⚠️ W4 — 11 file sezioni con naming uppercase/underscore

```
BKS_WOMAN.liquid
Banner_Accessories.liquid
Bks-Neo-Classic-C.liquid
Bks-hero-video-image-template.liquid
Bks-meta-split-header.liquid
Bks-split-hero-man-woman-meta.liquid
Bks-split-hero-man-woman-optimized.liquid
Bks-visual-language-collection-keyboards.liquid
Bks-visual-language-selectors.liquid
Bks-visual-panel.liquid
bks_collection_grid.liquid
```

Causa problemi su deploy via Shopify CLI in ambienti case-sensitive (Linux). Convenzione corretta: `lowercase-hyphen-separated`.

**Azione:** rinominare con `git mv` (preserva storia) e aggiornare i riferimenti nei template JSON che li invocano per `"type"`.

---

### ⚠️ W5 — AVADA SEO Suite attiva + metafield `bks.series` esposto

Due sub-issue correlati:
1. AVADA SEO inserisce `{% include 'avada-seo' %}` nell'head — app separata da verificare: se il negozio non ha più la licenza attiva, genera errori Liquid silenti.
2. Il metafield `bks.series` è letto in `bks-product-meta.liquid` (già segnalato in C1) ma anche potenzialmente esposto nei meta-tag SEO se AVADA li legge. Verificare che AVADA non indicizzi il valore `series` come keyword pubblica.

---

## ✅ OK (11)

| # | Check | Risultato |
|---|---|---|
| 1 | Dawn 15.4.1 confermato | ✅ |
| 2 | CSS vars BKS core presenti in `:root` | ✅ `--bks-onyx/salt/bone/graphite/ash/dune` |
| 3 | Homepage section order logico | ✅ Impact → Matrix → Slogan → Split → Grids → Trust |
| 4 | 8 template editoriali presenti | ✅ `bks-hours/glyph/marker/riviera/pulse/token/flag/folklore` |
| 5 | `collection.puffer-jacket.json` presente | ✅ |
| 6 | `collection.outerwear.json` presente | ✅ |
| 7 | Series metadata terms non in navigazione/copy principale | ✅ Solo in product-meta (C1) |
| 8 | Hero copy corretto | ✅ "Wearable Art Systems" · "Eight editorial collections. 189 AI-generated pieces..." |
| 9 | Editorial matrix copy corretto | ✅ "The eight editorial systems" · "Eight signals" · nomi collezioni corretti |
| 10 | Logo header: `BAK\|ABO` con separatore | ✅ `aria-label="BAK\|ABO"` in header.liquid r.665 |
| 11 | 2 product templates (`product.bks-men.json`, `product.bks-woman.json`) presenti | ✅ |

---

## Riepilogo priorità intervento

| Priorità | Item | File | Effort |
|---|---|---|---|
| **P1** | C1 — Rimuovi Series row product page | `bks-product-meta.liquid` | 5 min |
| **P1** | C2 — Aggiungi Google Fonts link tag | `layout/theme.liquid` | 5 min |
| **P1** | C5 — Aggiungi EU Rep footer | `sections/footer.liquid` | 10 min |
| **P1** | C3 — Fix BAKABO hardcoded in product-meta | `bks-product-meta.liquid` | 10 min |
| **P2** | C6 — Crea 13 template mancanti | `templates/` | 5 min (bash loop) |
| **P2** | C4 — Fix Luxury/Premium defaults | `bks-sneakers-panel.liquid` | 20 min |
| **P3** | W2 — Aggiungi token shadow/ink/mocha | `layout/theme.liquid` | 5 min |
| **P3** | W1 — Verifica doppio GTM | `layout/theme.liquid` | 15 min |
| **P4** | W3 — Rimuovi 43 template legacy | `templates/` | 5 min (bash) |
| **P4** | W4 — Rinomina 11 sezioni uppercase | `sections/` | 30 min |
| **P5** | W5 — Verifica AVADA licenza + series in SEO | Admin + AVADA | 15 min |

**P1 = bloccante pre-publish · P2 = correggere prima del lancio · P3-P5 = post-lancio**

---

*Audit: BKS_V20_TEXTS_COLOR_READY.zip — Giugno 2026*
