---
name: bakabo-master
description: Use this skill FIRST before any other BKS Studio skill. It is the master index of all active resources, tools, skills, files, scripts, and integrations for BKS Studio / bakabo.club. Triggers include: starting a new session, not knowing which skill to use, needing an overview of the current project state, asking what tools are available, or planning multi-step work across several domains. This skill does not produce output on its own — it routes to the correct skill and resource for each task. Always read this skill first, then the specific skill for the task.
---

# BKS Studio — Master Resource Map
## Skill v2 — 18 Giugno 2026
## Agente: Gaetano (Claude Sonnet 4.6)

Mappa completa di tutte le risorse attive, skill, file, script, integrazioni e connessioni per BKS Studio / bakabo.club. Questo documento è il punto di ingresso per ogni sessione di lavoro.

---

## 1. CHI È BKS STUDIO

| Campo | Valore |
|---|---|
| Brand pubblico | **BKS Studio** |
| Wordmark | **BAK\|ABO** (hangtag/packaging only) |
| Dominio | **bakabo.club** |
| Operatore | Roberto Picchioni, architetto, Terni (TR), 57 anni |
| Agente AI | Gaetano (Claude Sonnet 4.6) |
| Modello business | AI-art atelier, print-on-demand MTO via Printify |
| Mercati | EU (primario) + US |
| Prezzi | €69–€249 (ladder: entry €69–89, core €109–149, collection €159–199, archive €199–249) |
| Prodotti live | 189 (BKS_COLLEZIONE_26_v5.csv) |
| Email operativa | crew@bakabo.club · bakabofirm@gmail.com |
| Telefono | +393486950017 |
| Shopify ID | 11628e-2.myshopify.com |

---

## 2. LE SKILL ATTIVE — MAPPA E ROUTING

### Skill di dominio — core

| Skill | Dominio | Usa quando |
|---|---|---|
| **bakabo-brand** | Voce, lessico, tono, posizionamento | Qualsiasi output testuale pubblico |
| **bakabo-identity** | Naming, label, wordmark, icone categoria | Decisioni sul nome, etichette, logo |
| **bakabo-design-system** | Token colori, tipografia, componenti UI | Design, layout, frontend |
| **bakabo-business** | Pricing, margini, break-even, KPI economici | Ogni decisione di prezzo o valutazione commerciale |
| **bakabo-product-copy** | Titoli, descrizioni HTML, meta, tag Shopify | Scheda prodotto completa |
| **bakabo-printify-sync** | Enrichment post-sync Printify→Shopify | Prodotto appena arrivato da Printify |
| **bakabo-shopify-ops** | Store ops, drop launch, navigation, policy | Operazioni Shopify non-prodotto |
| **bakabo-pages-design** | Brief e audit per ogni pagina del sito | Redesign o audit pagine |
| **bakabo-growth** | CRM, email, loyalty, member area, conversione | Email flows, segmentazione, retention |
| **bakabo-theme-build** | Liquid, CSS, JSON template, sezioni Shopify | Sviluppo tema, codice Shopify |
| **bakabo-armocromia** | Palette modelli, stagioni cromatiche | Selezione modello per shoot on-model |
| **bakabo-manual-product-photo-generation** | Workflow immagini prodotto, slot 01-12 | Produzione foto editoriale |
| **bakabo-openai-image** | Prompt engineering OpenAI gpt-image-1 | Generazione immagini via API OpenAI |
| **bakabo-window-display** | Staging vetrina multi-prodotto | Scene editoriali, lookbook, vetrina |
| **bakabo-sound** | Libreria audio BKS, tracce Suno | Musica brand, selezione tracce |

### Skill di qualità e direzione creativa — ⭐ NUOVE

| Skill | Dominio | Usa quando |
|---|---|---|
| **bakabo-product-quality-gate** | Gate 20/25 moda+arte prima pubblicazione | Ogni prodotto prima di publish su Shopify |
| **bakabo-market-antagonist** | Osservatore competitivo, testa e sfida i concept | Prima di sviluppare una nuova collezione |
| **bakabo-art-critic** | Legge il grafico come opera — mark, field, concetto | Gallery text, recensione grafica, lookbook caption |
| **bakabo-editorial-typographer** | Composizione prodotto+tipografia su 5 schemi | Placement immagine su pagine, hero, panel |
| **bakabo-popup-ai** | Popup/overlay autonomi — scelta immagine, deploy | Configurazione Piano Hero, product pop-out |
| **bakabo-market-intelligence** | Strategia commerciale, timing drop, crescita | Quando e come agire sul mercato |
| **bakabo-members** | Lifecycle member, tier Metal, comunicazioni | Tier upgrade, email member, AI Shopper, Try-On gate |
| **bakabo-avatar-resident** | Avatar video 15s per collezione, workspace HeyGen | Produzione avatar senza Streamlit, registra video in DB |

### Routing rapido per task comune

| Task | Skill primaria | Skill secondaria |
|---|---|---|
| Scrivere una scheda prodotto | bakabo-product-copy | bakabo-brand |
| **Valutare se un prodotto è pubblicabile** | **bakabo-product-quality-gate** | bakabo-art-critic |
| **Sfidare una direzione creativa** | **bakabo-market-antagonist** | bakabo-market-intelligence |
| **Scrivere la critica grafica di un print** | **bakabo-art-critic** | bakabo-brand |
| Calcolare il prezzo giusto | bakabo-business | bakabo-printify-sync |
| Generare un'immagine prodotto | bakabo-openai-image | bakabo-armocromia |
| Costruire una sezione Shopify | bakabo-theme-build | bakabo-design-system |
| Scrivere un'email | bakabo-growth | bakabo-brand |
| **Comunicare con un member** | **bakabo-members** | bakabo-brand |
| **Tier upgrade di un member** | **bakabo-members** | — |
| **Produrre un avatar video** | **bakabo-avatar-resident** | bakabo-market-intelligence |
| Scegliere il modello per uno shoot | bakabo-armocromia | bakabo-manual-product-photo-generation |
| Costruire una vetrina | bakabo-window-display | bakabo-armocromia |
| Lanciare un drop | bakabo-shopify-ops | bakabo-product-copy |
| Aggiustare prezzi catalogo | bakabo-business | bakabo-printify-sync |
| Redesign di una pagina | bakabo-pages-design | bakabo-design-system |
| **Pianificare una nuova collezione** | **bakabo-market-antagonist** | bakabo-business |

---

## 3. RISORSE TECNICHE ATTIVE

### Stack e-commerce

| Risorsa | Stato | Note |
|---|---|---|
| **Shopify** Dawn 15.4.1 OS 2.0 | ✅ Live | Tema TM04 ID 202392961362 — BKS_TM04_FULL_LINKS_PAGES_UPDATE_16JUN2026.zip |
| **Printify** MWW On Demand | ✅ Live | Provider primario produzione |
| **Shopify Inbox** | ✅ Configurato | 7 instant answers, colori BKS, label "BKS Studio" |
| **ParcelPanel** | ✅ Attivo | Order tracking MTO |
| **Judge.me** | ⚠️ Attivo | Audit pendente: Tydal attivo simultaneamente |
| **Tydal** | ⚠️ Attivo | Duplicato con Judge.me — risolvere |
| **Shopify Flow** | ✅ Attivo | Automazioni tier tagging |
| **Shopify Email** | ✅ Attivo | Email marketing nativo |

### Tool AI e produzione

| Risorsa | Stato | Uso |
|---|---|---|
| **OpenAI gpt-image-1** | ✅ Attivo | Image generation/edit prodotti e avatar |
| **Suno** | ✅ Attivo | Generazione tracce audio 8 collezioni |
| **HyperFrames by HeyGen** | ✅ Connesso | Motion graphics, video brand |
| **Claude Sonnet 4.6** | ✅ Pro | Agente principale (Gaetano) |
| **Claude Code** | ✅ Disponibile | Automazioni file system, script Python |

### Canali brand attivi

| Canale | Handle/URL | Stato |
|---|---|---|
| **Sito** | bakabo.club | ✅ Live |
| **YouTube** | @BakAboClub | ✅ Attivo — "Art in transfiguration (BKS)" |
| **Email** | crew@bakabo.club | ✅ Operativa |

---

## 4. FILE E SCRIPT CHIAVE

### File di catalogo (locale Roberto)

| File | Percorso | Contenuto |
|---|---|---|
| `BKS_COLLEZIONE_26_v5.csv` | `I:\BAK ABO\` | Master catalog 189 prodotti, clean |
| `collezione_backpack_v04.zip` | Archive | Conflict check nomi design |
| `collezione_puffer_v04.zip` | Archive | Conflict check nomi design |
| `collezione_sneakers_v04.zip` | Archive | Conflict check nomi design |
| `collezione_swim_trunks_final.zip` | Archive | Conflict check nomi design |
| `collezione_travel_bag_final.zip` | Archive | Conflict check nomi design |
| `collezione_windbreaker_v04.zip` | Archive | Conflict check nomi design |
| `Collezione_One-Piece_Swimsuit_v2.csv` | Archive | One-piece swimsuit live |

### Script Python

| Script | Percorso | Funzione |
|---|---|---|
| `bakabo_collection_photo_generator_v2` | `E:\BAKSITO\BAKABO\BAK ABO\bakabo_collection_photo_generator_v2\fixed_generator\` | Factory immagini prodotto OpenAI |
| `run_verifica_1foto.bat` | Stessa cartella | Test API OpenAI (~$0.08) |
| `.env` | `fixed_generator\.env` | OPENAI_API_KEY + config |
| `create_metafields.py` | Archive sessione | Metafield definitions Shopify |
| `create_metaobjects.py` | Archive sessione | 8 metaobject collezioni |
| `populate_metafields.py` | Archive sessione | Scrivi metafield su 189 prodotti |
| `bks_avatar_generator.py` | `skill-bks_al_16_06_2026\components\` | Genera avatar Roberto via OpenAI |

### File tema Shopify (TM04 — `04_TEMA_SHOPIFY/sections/`)

Deploy: `scripts/deploy_theme_section.py` — 38 file, `python deploy_theme_section.py`
CSS accent regola: **SEMPRE** `var(--bks-active-accent, [fallback])` — mai hardcoded per-collezione

| File | Contenuto |
|---|---|
| `bks-piano-hero.liquid` + `.css` + `.js` | Pianoforte interattivo 8 collezioni, audio Web Audio |
| `bks-impact-home.liquid` | Hero homepage editoriale |
| `bks-member-dashboard.liquid` | Area member + Camerino Try-On |
| `bks-members-login.liquid` | Login gate member area |
| `bks-ai-assistant.liquid` | AI Personal Shopper in-page |
| `bks-trust-strip.liquid` | 4 colonne fiducia Google Merchant, accent animato |
| `bks-store-reviews.liquid` | Google Customer Reviews badge + heading DM Mono |
| `bks-timed-offer.liquid` | Offerta con countdown |
| `bks-planet-collections-orbit.liquid` | Orbit 8 collezioni |
| `bks-accessories-panel.liquid` | Griglia accessori con filtro categorie client-side |
| `main-collection-product-grid-bks.liquid` | Collection grid con newspaper lift + accent |
| `bks-product-editorial-care.liquid` | Scheda prodotto editoriale |
| `bks-collection-signal.liquid` | Banner segnale collezione |

### Archivio media BKS

| Risorsa | Path | Contenuto |
|---|---|---|
| **BKS Database** | `I:\BKS database` | 14,421 file media indicizzati in SQLite `assets` table |
| `sync_bks_database.py` | `scripts/` | Indicizza `I:\BKS database` → `catalog_db` assets table, incrementale |
| `bks_assets.py` | radice | `bks_media_root()` — priorità: json config → env → `I:\BKS database` |
| `catalog_db.py` | `ecommerce_automation/` | Schema `assets`: handle, type, collection, path, url, dimensions |

### Documenti strategici

| File | Contenuto |
|---|---|
| `BKS_Studio_Shopify_Theme_Brief_v1.docx` | Brief redesign sito per designer |
| `bks-studio-handoff.docx` | Developer handoff completo |
| `BKS_MASTER_KNOWLEDGE_16_06_2026.md` | Knowledge base completa (questo progetto) |
| `bks-suno-prompts.md` | 8 prompt audio per generazione Suno |
| `best_35s.jpg` | Frame video BAKABO_SMONTA — reference avatar |

---

## 5. LE 8 COLLEZIONI — QUICK REFERENCE

| # | Collezione | Series | Colore | Nota | Tasto |
|---|---|---|---|---|---|
| 1 | **Hours** | hyperrealism | #c8c4be | Do 261Hz | Bianco |
| 2 | **Glyph** | brut | #d4a030 | Re♭ 277Hz | Nero |
| 3 | **Marker** | neo-expressionism | #c04418 | Re 293Hz | Bianco |
| 4 | **Riviera** | islands | #0ca898 | Mi♭ 311Hz | Nero |
| 5 | **Pulse** | optical | #8888cc | Mi 329Hz | Bianco |
| 6 | **Token** | arcade | #9828d8 | Fa 349Hz | Bianco |
| 7 | **Flag** | neo-dada | #c82020 | Sol♭ 369Hz | Nero |
| 8 | **Origin** | naif | #489808 | Sol 392Hz | Bianco |

---

## 6. STATO CATALOGO AL 16 GIUGNO 2026

| Categoria | Prodotti | Stato |
|---|---|---|
| Sneakers | 20 | ✅ Chiuso |
| Backpack | 12 | ✅ Chiuso |
| Swim Trunks | 25 | ✅ Chiuso |
| Puffer Jackets | 28 | ✅ Chiuso |
| Windbreaker | 12 | ✅ Chiuso |
| Travel Bag/Duffle | 15 | ✅ Chiuso |
| Lounge Pants (W) | 15 | ✅ Chiuso |
| Pullover Hoodie | 16 | ✅ Chiuso |
| Racerback Dress | 19 | ✅ Chiuso |
| Flip Flops | — | ✅ Chiuso |
| One-Piece Swimsuit | 10 | ✅ Live |
| Hawaiian Shirt | 4/10 | ⚠️ 6 prodotti mancanti |
| Athletic Long Shorts | 9 | ✅ Live |
| Women's Cut & Sew Tee | 3 | ✅ Live |
| Cozy Slipper | 2 | ✅ Live — ⚠️ verificare prezzi |
| **TOTALE** | **189** | BKS_COLLEZIONE_26_v5.csv |

---

## 7. INFRASTRUTTURA SHOPIFY

### Configurazione attiva

```
Tema:          Dawn 15.4.1 (OS 2.0 JSON templates)
Collezioni:    25 live (8 editorial + 14 product type + 3 navigation)
Tipografia:    Bebas Neue / DM Sans / DM Mono (Google Fonts via <link>)
Colori:        Onyx #0A0A0A · Salt #FAFAF7 · Dune #C9B79C · Bone #E8E4DC
Metafield:     bks.collection / bks.design / bks.series / bks.drop (su 189 prodotti)
Tag standard:  drop:catalog-reset-2026 · bakabo-enriched · collection: · series:
```

### Standard CSV obbligatori

```
- Handle: mai ™ symbol
- SEO meta: max 160 caratteri
- EU Rep: HONSON VENTURES LIMITED, gpsr@honsonventures.com, Limassol CY 4003
- Warranty: Directive 1999/44/EC
- Care: obbligatorie
- Free Shipping bullet: RIMOSSO da tutti i body
- Lingua: ENGLISH ONLY in tutti i body
- Color metafield: Color (product.metafields.shopify.color-pattern)
- GPC: Google Product Category (product.metafields.custom.google_product_category)
- Shoe size: Shoe size (product.metafields.shopify.shoe-size) — US only, semicolon
```

---

## 8. MEMBER AREA — METAL TIER SYSTEM

| Tag Shopify | Tier | Simbolo | Orders | Unlock chiave |
|---|---|---|---|---|
| `bks-tier-lead` | **Lead** | ◎ | 0 | Wishlist, newsletter |
| `bks-tier-iron` | **Iron** | ⬡ | 1–2 | Size history, AI recs base |
| `bks-tier-brass` | **Brass** | ◈ | 3–5 | AI Personal Shopper, Try-On Camerino, +48h drops |
| `bks-tier-silver` | **Silver** | ◇ | 6–10 | Curated drops +24h, archivio completo |
| `bks-tier-gold` | **Gold** | ✦ | 11+ | VIP private drops, co-creation, Roberto personale |

- Calcolo tier: `customer.orders_count` — Liquid in `sections/bks-member-dashboard.liquid`
- Try-On gate: `orders_count >= 3` (Brass+)
- Gold: Roberto scrive personalmente — mai automatizzato
- Skill completa: **bakabo-members** — template email, AI Shopper logic, CRM segments
- Comunicazioni: `crew@bakabo.club` — Roberto approva ogni invio reale

---

## 9. PRICING — REGOLE OPERATIVE

### Margine target

| Livello | Margine % | Quando |
|---|---|---|
| Minimo assoluto | 45% | Non scendere mai sotto |
| Standard | 55–65% | La maggior parte dei prodotti |
| Premium | 65–75% | Forte identità BKS, bassa sostituibilità |
| Non pubblicare | <40% | Draft obbligatorio |

### Formula

```
Costo Totale = Base Cost Printify + Shipping EU
Prezzo = Costo Totale / (1 - margine target)
Arrotondare a: €X5 o €X9 o numero tondo
```

### Alert attivi

- ⚠️ Cozy Slipper: verificare prezzo ≥ €69 (minimo price ladder)
- ⚠️ Tutti i prodotti: audit margine con CSV Printify + CSV Shopify pendente
- ⚠️ Price ladder update: portare tutti i prodotti nella fascia €69–€249

---

## 10. WORKFLOW CATALOGO — CON QUALITY GATE

**Regola assoluta: nessun prodotto viene pubblicato senza score ≥ 20/25.**

```
1. Prodotto creato su Printify
          ↓
2. Sync Printify → Shopify (draft, non published)
          ↓
3. bakabo-market-antagonist — il concept è originale? Passa il 24-month test?
   (Solo per nuovi concept / nuove collezioni — non per varianti)
          ↓
4. bakabo-product-quality-gate — score 0-25 su 5 dimensioni
   D1 Blank suitability + D2 Print×garment + D3 Visual concept
   + D4 Chromatic integrity + D5 Editorial credibility
          ↓
   Score ≥ 20 → continua
   Score 17-19 → HOLD + feedback → redesign specifico
   Score < 17  → RIMUOVI da Printify

5. bakabo-printify-sync — enrichment: title clean, metafields, tags
          ↓
6. bakabo-product-copy — descrizione HTML + SEO title + meta
          ↓
7. bakabo-art-critic — gallery text per il print (50-120 parole)
          ↓
8. bakabo-business — verifica margine ≥ 45%, prezzo nel price ladder
          ↓
9. Publish + tag bakabo-enriched
```

**Tag di stato prodotto:**
- `bakabo-enriched` → pronto, pubblicato
- `bakabo-needs-review` → quality gate 17-19, in attesa feedback
- `bakabo-needs-redesign` → quality gate < 17, redesign richiesto
- `bakabo-ai-failed` → blocco automatico (stock art, copia brand, ecc.)
- `bakabo-hero-product` → score 22-25, prodotto di riferimento

---

## 10b. IMAGE PIPELINE — PRINTIFY → CUTOUT → OVERLAY

**Script:** `BAKABO_IMAGE_FACTORY_v1.1/scripts/printify_cutout_pipeline.py`

```bash
python scripts/printify_cutout_pipeline.py           # tutti i prodotti
python scripts/printify_cutout_pipeline.py --max 5   # test 5 prodotti
python scripts/printify_cutout_pipeline.py --force   # rigenera cache
```

Output per prodotto:
- `{slug}_cutout_safe.png` — PNG trasparente (RGBA, Shopify-ready)
- `{slug}_salt_overlay.jpg` — su #FAFAF7 paper
- `{slug}_onyx_overlay.jpg` — su #0A0A0A cinema
- `{slug}_{collection}_overlay.jpg` × 8 — uno per collezione BKS
- `cutout_manifest.csv` — path completo di tutti gli output

**Regola:** il cutout PNG si usa su tutte le pagine collection tramite CSS `--bks-active-accent` — stesso asset, 8 colori automatici.

---

## 11. IMAGE PRODUCTION — QUICK REFERENCE

| Tipo | Collezioni | Ambiente |
|---|---|---|
| Still-life | Hours · Glyph · Marker · Flag · New Arrivals | Studio industriale o galleria |
| On-model | Origin · Riviera · Pulse · Token | Travertino / Resort / Urban |

| Stagione | Collezioni | Modello |
|---|---|---|
| Inverno | Hours · Pulse · Flag · Token | Massimo contrasto pelle |
| Autunno | Glyph · Marker · Origin | Toni caldi bronzo/terracotta |
| Primavera | Riviera | Luminoso dorato |

**Naming:** `bks-[collection]-[product]-[modalità]-[numero].jpg`
**API:** gpt-image-1 · `images.edit` con reference · `quality="high"`
**Sizes:** 1024×1536 (editoriale) · 1536×1024 (hero) · 1024×1024 (clean)

---

## 11. PIANO INTERATTIVO — SISTEMA COMPLETO

Sezione Shopify che sostituisce l'hero standard con un pianoforte prospettico interattivo.

**File pronti:** `bks-piano-hero-shopify.zip` (liquid + css + js + README)

**Funzionamento:** Click tasto → tasto scende → suona nota (Web Audio o MP3 Suno) → pannello collezione con manichino + armocromia + prodotti + CTA → click di nuovo per tornare.

**Audio:** 8 tracce Suno da generare con prompt in `bks-suno-prompts.md`
**Naming audio:** `BKS-Concept-Ambient-001.mp3` … `008.mp3`
**Installazione:** Theme → Sections + Assets → Customize → Add section → "BKS Piano Hero"

---

## 12. YOUTUBE / AVATAR / BRAND VIDEO

**Canale:** @BakAboClub · "Art in transfiguration (BKS)"

**Avatar Roberto:**
- Maglione a collo alto nero fine knit · capelli corti sale e pepe · no cappello
- Mani sulla scultura modulare BAK|ABO in legno naturale
- Sfondo: parete grigia · quadro BAK|ABO · opera Glyph
- Script: `bks_avatar_generator.py` · Reference: `best_35s.jpg`
- Prompt: già pronto nella skill `bakabo-openai-image`

**Video BAKABO_SMONTA:**
- Documento fondativo del brand — Roberto smonta la scultura modulare
- Va embeddato in homepage o About page
- È il video più autentico disponibile — usarlo come hero YouTube

---

## 13. ISSUES APERTI — PRIORITÀ

| # | Issue | Priorità | Azione |
|---|---|---|---|
| 1 | **API key OpenAI esposta in chat** | 🔴 URGENTE | Revocare su platform.openai.com/api-keys |
| 2 | **Judge.me + Tydal duplicati** | 🔴 Alta | Audit e disinstallare uno dei due |
| 3 | **Hawaiian Shirt 6 prodotti mancanti** | 🟡 Media | Completare categoria |
| 4 | **Audit prezzi 189 prodotti** | 🟡 Media | Script Python margine check |
| 5 | **3 handle anomalies** | 🟡 Media | bks-glyph-cross-puffer · glyph-script-swim-trunks · Marker Drip series |
| 6 | **Duplicate announcement bar** | 🟢 Bassa | Verifica tema |
| 7 | **Generare 8 tracce Suno** | 🟢 Bassa | Prompt pronti in bks-suno-prompts.md |
| 8 | **Avatar Roberto** | 🟢 Bassa | Script pronto · serve nuova API key |
| 9 | **Analisi E:\NFT e E:\IMMAGINI AI** | 🟢 Bassa | Usare Claude Code |
| 10 | **Homepage redesign implementazione** | 🟢 Bassa | Brief pronto · designer pendente |

---

## 14. REGOLE OPERATIVE AGENTE

### Lingua
- Roberto scrive in italiano → Gaetano risponde in italiano
- Tutto il copy customer-facing → English only
- Prompt OpenAI → English only

### Stile risposte
- Risposte dirette, tecniche, concise
- Nessun preambolo sentimentale
- Deliverable concreti, non discussioni astratte
- "ok" / "si" / "procedi" = conferma → avanzare

### Prima di ogni task
1. Leggere questa skill (bakabo-master) per orientamento
2. Leggere la skill specifica del dominio
3. Verificare che il task non violi le brand rules (bakabo-brand + bakabo-identity)
4. Produrre il deliverable in un unico blocco di risposta

### Regole brand non negoziabili
- **BAKABO** unspaced → mai in pubblico
- **"luxury"** → mai in copy o prompt immagini
- **Glyph** → mai "tribale" / "etnico"
- **Origin** (ex-Folklore) → naif, mitologia inventata, mai riferimenti culturali reali
- **Flag** → mai bandiere nazionali
- **™** → mai negli handle Shopify
- **Free Shipping bullet** → rimosso da tutti i body prodotto
- **Italiano** → rimosso da tutti i body prodotto
- **`bakabo-enriched` tag** → presenza = non rielaborare

### Scoring prodotti
- Default: ≥21/25 per procedere
- Elevato (Tee, Slipper, Dress): ≥22/25
- Sempre: business check margine prima di approvare

---

## 15. PATH LOCALI ROBERTO

```
Store Shopify:    11628e-2.myshopify.com
Email:            crew@bakabo.club
Telefono:         +393486950017

Archivio locale:
E:\IMMAGINI AI        → archivio immagini AI (da analizzare)
E:\NFT                → archivio NFT (da analizzare con criteri BKS)
I:\BAK ABO            → repository principale — qui vanno tutti i file

Script foto:
E:\BAKSITO\BAKABO\BAK ABO\bakabo_collection_photo_generator_v2\fixed_generator\
  .env                → OPENAI_API_KEY (⚠️ aggiornare con nuova key)
  run_verifica_1foto.bat → test API OpenAI

EU Representative:
HONSON VENTURES LIMITED
gpsr@honsonventures.com
Gnaftis House flat 102, Limassol, Mesa Geitonia, 4003, CY
```

---

*Aggiornato: 18 Giugno 2026 · Gaetano (Claude Sonnet 4.6) — module BKS upgrade pass completo*
*Prossimo aggiornamento: dopo ogni sessione che produce deliverable o decisioni nuove*
