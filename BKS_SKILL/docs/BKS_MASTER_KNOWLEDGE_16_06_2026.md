# BKS Studio — Master Knowledge Document
## skill-bks_al_16_06_2026 · Aggiornato 16 Giugno 2026

Documento di riferimento completo per l'agente Gaetano (Claude). Contiene tutta la conoscenza maturata nelle sessioni di lavoro con Roberto Picchioni su BKS Studio / bakabo.club.

---

## 1. IDENTITÀ OPERATORE

| Campo | Valore |
|---|---|
| Nome | Roberto Picchioni |
| Alias agente | Bakabo |
| Professione | Architetto, Terni (TR), Italia |
| Età | 57 anni |
| Esperienza professionale | 25 anni |
| Brand | BKS Studio / BAK\|ABO / bakabo.club |
| Email | bakabofirm@gmail.com |
| Store contact | crew@bakabo.club |
| Telefono | +393486950017 |
| Shopify domain | 11628e-2.myshopify.com |
| Piano Claude | Pro |

---

## 2. BRAND ARCHITECTURE

### Nomi pubblici ammessi

| Forma | Uso | Mai |
|---|---|---|
| **BKS Studio** | Nome pubblico primario — sito, prodotti, social, email | — |
| **BAK\|ABO** | Hangtag, packaging, footer, wordmark visivo | Superfici prodotto, copy pubblico |
| **bakabo.club** | Dominio tecnico, URL, email tecnica | Copy customer-facing |
| **BAKABO** (unspaced) | **VIETATO PERMANENTEMENTE** | Qualsiasi uso pubblico (SEO risk + AQMI) |
| **BAK ABO** (con spazio) | Errore legacy — correggere ovunque | — |
| **BKS** | Etichetta cucita — black on white / white on black | — |

### Posizionamento

- Segmento: **Accessible designer** — non luxury, non fast fashion
- Produzione: Print-on-demand via Printify (MWW On Demand / Smart Printee)
- Claim ammesso: "AI-art atelier" · "Wearable art, on demand" · "Designed in Italy"
- **NON ammesso**: "luxury" · "premium" · "handcrafted" · "Made in Italy" · "limited edition" (salvo drop numerati chiusi)
- Prezzi: €40–140
- Mercati: EU + US
- Riferimenti editoriali: Études, Daily Paper, Drôle de Monsieur, Tealer, Carne Bollente

### Label e hangtag

- **Etichetta cucita**: BKS ONLY — nero su bianco o bianco su nero. Mai BAK|ABO, mai logo esteso
- **Hangtag**: BAK|ABO + BKS + categoria prodotto
- **Icone categoria**: 🦈 = swimwear · ⛰ = outerwear · 🌊 = footwear

---

## 3. LE 8 COLLEZIONI PERMANENTI

| Collezione | Series (interno) | Mood | Colore | Nota jazz |
|---|---|---|---|---|
| **BKS Hours** | hyperrealism | Contemplativo urbano, Hopper energy | #c8c4be grigio caldo | Do (261 Hz) |
| **BKS Glyph** | brut | Simbolico codificato, alfabeto visivo BKS | #d4a030 oro | Re♭ (277 Hz) |
| **BKS Marker** | neo-expressionism | Gestuale urbano, Basquiat energy | #c04418 terracotta | Re (293 Hz) |
| **BKS Riviera** | islands | Resort mediterraneo, luce calda | #0ca898 acqua | Mi♭ (311 Hz) |
| **BKS Pulse** | optical | Geometrico kinetic, optical art | #8888cc viola | Mi (329 Hz) |
| **BKS Token** | arcade | Digitale pixel, Herbie Hancock register | #9828d8 viola elettrico | Fa (349 Hz) |
| **BKS Flag** | neo-dada | Pop collage, campi grafici astratti | #c82020 rosso | Sol♭ (369 Hz) |
| **BKS Origin** | naif | Figurativo narrativo, natura e mitologia privata | #489808 verde | Sol (392 Hz) |

**NOTA**: I nomi series: sono metadati interni — il cliente vede solo il nome collezione.

### Guardrail critici per collezione

| Collezione | Vietato |
|---|---|
| Glyph | "tribal" · "etnico" · "primitivo" · "antico" · riferimenti culturali reali |
| Flag | Bandiere nazionali · simboli politici · territoriali |
| Origin | Nessun riferimento a culture reali o tradizioni territoriali specifiche |
| Token | Crypto · NFT · web3 (Token = oggetto fisico, gettone) |

---

## 4. CATALOGO LIVE — STATO AL 16 GIUGNO 2026

### Master catalog: BKS_COLLEZIONE_26_v5.csv — 189 prodotti totali

| Categoria | Count | Stato |
|---|---|---|
| Sneakers | 20 | Chiuso |
| Backpack | 12 | Chiuso |
| Swim Trunks | 25 | Chiuso |
| Puffer Jackets | 28 | Chiuso |
| Windbreaker | 12 | Chiuso |
| Travel Bag/Duffle | 15 | Chiuso |
| Lounge Pants (W) | 15 | Chiuso |
| Pullover Hoodie | 16 | Chiuso |
| Racerback Dress | 19 | Chiuso |
| Flip Flops | Chiuso | — |
| One-Piece Swimsuit | 10 | Live |
| Hawaiian Shirt | 4/10 | 6 prodotti mancanti |
| Athletic Long Shorts | 9 | Live |
| Women's Cut & Sew Tee | 3 | Live |
| Cozy Slipper | 2 | Live |

### Anomalie handle da correggere

- `bks-glyph-cross-puffer` → `marker-scrawl-puffer`
- `glyph-script-swim-trunks` → `glyph-quill-swim-trunks`
- Marker Drip: `series:arcade` → `series:neo-expressionism`

---

## 5. SHOPIFY INFRASTRUCTURE

### Store

- **Tema live**: Dawn 15.4.1 (OS 2.0 JSON templates)
- **Ultimo ZIP tema**: BKS_V24_HEADER_FIX.zip
- **25 collezioni live**: 8 editorial + 14 product type + 3 navigation
- **Metafield pipeline**: `create_metafields.py` → `create_metaobjects.py` → `populate_metafields.py` (eseguiti, 193 righe aggiornate)

### Tipografia

Stack Google Fonts via `<link>` in theme.liquid (MAI @import):
- **Display**: Bebas Neue
- **Body/Nav**: DM Sans
- **Prezzi/Tecnico**: DM Mono

### Colori brand

```
Onyx:  #0A0A0A
Salt:  #FAFAF7
Dune:  #C9B79C
Bone:  #E8E4DC
```

### Shopify Inbox

Configurato con:
- 7 instant answers
- Store name: "BKS Studio"
- Label: "BKS Studio"
- Colori: onyx/salt/dune
- Icona: hand wave
- Marketing opt-in: OFF
- Email: crew@bakabo.club

### CSV standards (obbligatori su tutti gli export)

- Handles: mai ™ symbol
- SEO meta description: max 160 caratteri
- EU Representative: HONSON VENTURES LIMITED, gpsr@honsonventures.com, Gnaftis House flat 102, Limassol, Mesa Geitonia, 4003, CY
- Warranty: Directive 1999/44/EC
- Care instructions: obbligatorie
- Free Shipping bullet: rimosso da tutti i body HTML
- Italian text: rimosso da tutti i body
- Color metafield: `Color (product.metafields.shopify.color-pattern)`
- GPC metafield: `Google Product Category (product.metafields.custom.google_product_category)`
- Shoe size: `Shoe size (product.metafields.shopify.shoe-size)` — US only, semicolon-separated

---

## 6. SISTEMA MEMBER AREA — METAL TIER (aggiornato 17/06/2026)

5 tier automatici basati su `customer.orders_count` — nessun tag manuale richiesto.

| Tier | Simbolo | Colore | Acquisti | Benefici chiave |
| --- | --- | --- | --- | --- |
| **Lead** | ◎ | `#8c8c8c` | 0 | Wishlist, newsletter, account base |
| **Iron** | ⬡ | `#607080` | 1–2 | Size history, raccomandazioni base |
| **Brass** | ◈ | `#d4a030` | 3–5 | AI Personal Shopper attivo, Try-On Camerino, preview (+48h) |
| **Silver** | ◇ | `#b0b8c4` | 6–10 | Drop anticipati (+24h), BKS Archive completo |
| **Gold** | ✦ | `#c8a820` | 11+ | Private drops VIP, white-glove curation, co-creation |

### Rilevamento tier — pura Liquid

```liquid
{%- assign bks_order_count = customer.orders_count | default: 0 -%}
{%- if bks_order_count >= 11 -%}{%- assign bks_tier = "gold" -%}
{%- elsif bks_order_count >= 6 -%}{%- assign bks_tier = "silver" -%}
{%- elsif bks_order_count >= 3 -%}{%- assign bks_tier = "brass" -%}
{%- elsif bks_order_count >= 1 -%}{%- assign bks_tier = "iron" -%}
{%- else -%}{%- assign bks_tier = "lead" -%}{%- endif -%}
```

### AI Personal Shopper (Brass+)

- Attivato da `bks-ai-assistant.liquid` via `data-member-tier`, `data-member-name`, `data-member-orders`
- Tono calibrato per tier — vedi `BKS_SKILL/members/bks-member-marketing.json`
- Dashboard member: `sections/bks-member-dashboard.liquid`
- Header account dropdown con tier dot: `snippets/bakabo-header.liquid`

### Try-On Camerino

- Accessibile da Brass in su
- Browser mobile nativo (`getUserMedia`) — nessuna app
- Desktop: QR code via `api.qrserver.com` → rimanda al mobile

---

## 7. STANDARD DI VALUTAZIONE PRODOTTI

- **Soglia default**: ≥21/25 su 5 criteri
- **Soglia elevata**: Women's Cut & Sew Tee, Cozy Slipper, Racerback Dress = 22/25
- **Eccezioni**: assoluta unicità o prodotto già venduto

### Criteri di scoring (5 × 5 = 25)

1. Coerenza visiva / identità BKS
2. Riconoscibilità brand
3. Qualità print
4. Forza commerciale
5. Assegnazione collezione

### Pattern che penalizzano per categoria

- Puffer: strisce orizzontali (interagiscono male con cuciture trapuntate)
- Windbreaker: richiede struttura ibrida solid/AOP (colorblock-only fallisce)
- Swim trunks: richiedono identità BKS forte oltre il beachwear generico

---

## 8. NAMING PRODOTTI

Formula: `BKS [Collection] [Design]™ [Product Type]`

- Design names verificati contro catalogo completo (conflict check CSVs)
- Stesso design name può apparire in più categorie (es. "Quill" su swim trunk + futuro puffer)
- Capsule dual-product: stesso pattern in due categorie sotto stesso nome

---

## 9. ARMOCROMIA — SISTEMA MODELLI

| Collezione | Stagione | Tipo modello |
|---|---|---|
| Hours | Inverno | Pelle porcellanata/ebano, massimo contrasto |
| Glyph | Autunno | Pelle bronzo caldo, capelli scuri caldi |
| Marker | Autunno | Pelle terracotta media, capelli castano scuro |
| Riviera | Primavera | Pelle dorata luminosa, capelli biondi ramati |
| Pulse | Inverno | Freddo contrastato, platino o nero assoluto |
| Token | Inverno | Saturazione alta, ebano o porcellana |
| Flag | Inverno | Contrasto estremo, nessuna via di mezzo |
| Folklore | Autunno | Pelle olivastra calda, capelli castano caldo |

- **Folklore/Riviera** → Autunno Caldo (on-model)
- **Pulse/Token** → Inverno Brillante (on-model)
- **Hours/Glyph/Marker/Flag** → still-life editoriale

---

## 10. IMAGE PRODUCTION

### Naming convention
`bks-[collection]-[product]-[modalità]-[numero].jpg`

### Tipo per collezione
- **Still-life**: Hours, Glyph, Marker, Flag, New Arrivals
- **On-model**: Folklore, Riviera, Pulse, Token

### OpenAI gpt-image-1
- Con reference image: `images.edit`
- Senza reference: `images.generate`
- Qualità: sempre `high`
- Size editoriale: `1024x1536` (2:3)
- Size hero/banner: `1536x1024` (3:2)
- Size clean product: `1024x1024` (1:1)

### Regole prompt
- Mai "luxury" o "premium" nei prompt
- Descrivere il pattern fisicamente (dimensioni, colori esatti), non artisticamente
- Chiudere sempre con: "The all-over print pattern from the reference image must be preserved exactly"
- Ambiente sneakers: Tipo D (esterno architetturale, travertino)

---

## 11. VETRINA / WINDOW DISPLAY

### 4 ambienti architetturali

| Tipo | Descrizione | Collezioni |
|---|---|---|
| A | Colonnato mediterraneo, travertino, luce calda | Glyph, Riviera, Folklore |
| B | Studio industriale, cemento, luce dura laterale | Hours, Marker, Token |
| C | Galleria bianca, luce uniforme | Flag, Pulse |
| D | Esterno architetturale, gradini pietra | Sneakers, Riviera |

### Regole compositive
- 3 prodotti: piramide (alto al centro-fondo, voluminoso basso sinistra, compatto basso destra)
- Gap minimo 15% tra prodotti
- Nessun prop decorativo (no fiori, piante, candele, libri)

---

## 12. PIANO INTERATTIVO — SISTEMA COMPLETO

### Concept
8 tasti di pianoforte (5 bianchi + 3 neri) = 8 collezioni. Click → tasto scende → suona nota → pannello collezione con manichino + armocromia + prodotti + jazz ambient. Click di nuovo → torna al piano.

### File pronti
- `bks-piano-hero-shopify.zip` (section liquid + css + js + README)

### Mapping note
| Collezione | Tasto | Nota | Hz |
|---|---|---|---|
| Hours | Bianco | Do | 261 |
| Glyph | Nero | Re♭ | 277 |
| Marker | Bianco | Re | 293 |
| Riviera | Nero | Mi♭ | 311 |
| Pulse | Bianco | Mi | 329 |
| Token | Bianco | Fa | 349 |
| Flag | Nero | Sol♭ | 369 |
| Folklore | Bianco | Sol | 392 |

---

## 13. AUDIO — SUNO PROMPTS

8 tracce ambient piano minimal + fiati jazz (stile Miles Davis / Chet Baker / Brian Eno).
File: `bks-suno-prompts.md`

Naming output: `BKS-Concept-Ambient-[001-008].mp3`
Cartella: `06_Concept` → `07_Approved_Master`

Stile generale: lentissimo (36-52 BPM), poche note, molto silenzio, lungo decay, riverbero.

---

## 14. CANALE YOUTUBE

- **Handle**: @BakAboClub
- **Nome**: Art in transfiguration (BKS)
- **Keywords**: Tarsiocromia, AI, BAKABO, Arte Moderna, Trasfigurazione, impressionismo rapido
- **Video chiave**: BAKABO_SMONTA.mp4 — scultura modulare in legno, smontaggio rituale, identità brand autentica

### Avatar BKS Studio (Roberto)
- Maglione a collo alto nero fine knit, no logo
- Capelli corti sale e pepe, no cappello
- Mani sulla scultura modulare BAK|ABO
- Sfondo: parete grigia, quadro BAK|ABO, opera Glyph
- Stile: fotorealistico editoriale, Willy Vanderperre for Dior Homme
- Script generazione: `bks_avatar_generator.py` + `best_35s.jpg`

---

## 15. VOCE BKS STUDIO

### 4 dial

| Dial | Valore |
|---|---|
| Register | Editoriale — frasi brevi, dichiarative |
| Calore | Cool ma accessibile — no punti esclamativi, no emoji nel corpo |
| Densità | Minimale — taglia ogni aggettivo |
| Postura | Curatore — condivide il lavoro, non vende il prodotto |

### Lessico ammesso
series · prompt · pattern · field · on-demand · drop · studio · archive · fragment · composition · digital craft · index

### Lessico vietato
luxury · premium · amazing · stunning · must-have · exclusive · iconic · game-changer · handcrafted · made in Italy · limited edition* · wear your story

### Self-check 6 punti
1. Potrebbe averla scritta un brand POD generico? → riscrivere
2. Potrebbe usarla Acne o Bottega senza mentire? → smorzare
3. Ci sono punti esclamativi o emoji nel corpo? → rimuovere
4. Compaiono parole dalla lista "Banditi"? → sostituire
5. Si citano termini series: al cliente? → usare solo nome collezione
6. La natura AI-art è dichiarata dove pertinente? → aggiungere senza scusarsi

---

## 16. TOOL E RISORSE TECNICHE

| Tool | Uso |
|---|---|
| Shopify (Dawn 15.4.1) | Store principale |
| Printify (MWW On Demand) | Produzione POD |
| Python + pandas | CSV processing (dtype=str sempre) |
| OpenAI gpt-image-1 | Image generation/edit |
| Suno | Generazione tracce audio brand |
| HyperFrames by HeyGen | Video motion graphics |
| bakabo_collection_photo_generator_v2 | Python image factory |

### Path importanti (locale Roberto)
- `.env`: `E:\BAKSITO\BAKABO\BAK ABO\bakabo_collection_photo_generator_v2\fixed_generator\.env`
- `run_verifica_1foto.bat`: verifica API OpenAI (~$0.08)
- Archivio immagini: `E:\IMMAGINI AI`
- NFT archive: `E:\NFT`
- Repository principale: `I:\BAK ABO`

### Python CSV pattern affidabili
```python
df = pd.read_csv(file, dtype=str)  # sempre dtype=str
df.at[first_idx, col] = value      # single-row write
df.loc[mask, col] = value          # multi-row/variant write
```

---

## 17. PROSSIMI STEP (priorità)

1. Completare Hawaiian Shirt collection (6 prodotti mancanti)
2. Correggere 3 handle anomalies
3. Shopify theme navigation + homepage structure build
4. Member area Liquid implementation
5. Generare 8 tracce Suno + caricare in bks-piano-hero section
6. Generare avatar Roberto con OpenAI (script pronto: `bks_avatar_generator.py`)
7. Analizzare e riorganizzare `E:\NFT` e `E:\IMMAGINI AI` con Claude Code
8. Trasferire tutto in `I:\BAK ABO`

---

## 18. ISSUES APERTI

- Review app audit: Judge.me + Tydal running simultaneously — non risolto
- Potential duplicate announcement bar — non risolto
- Lounge pants images shooting → assegnate a Folklore (primary) / Riviera (mood)
- Homepage redesign brief (`BKS_Studio_Shopify_Theme_Brief_v1.docx`) + developer handoff (`bks-studio-handoff.docx`) prodotti — designer implementation pending
- API key OpenAI esposta in chat → REVOCARE IMMEDIATAMENTE e generare nuova

---

## 19. SKILL INSTALLATE (14 + 1 pending)

| Skill | Dominio |
|---|---|
| bakabo-brand | Voce, lessico, posizionamento |
| bakabo-identity | Naming, label, wordmark |
| bakabo-design-system | Token, colori, tipografia, componenti |
| bakabo-product-copy | Titoli, descrizioni, meta, tag |
| bakabo-printify-sync | Enrichment post-sync Printify→Shopify |
| bakabo-shopify-ops | Operazioni store, drop, navigation |
| bakabo-pages-design | Brief e audit per-page |
| bakabo-growth | CRM, email, loyalty, conversione |
| bakabo-theme-build | Liquid, CSS, JSON template Shopify |
| bakabo-armocromia | Palette modelli per shoot on-model |
| bakabo-manual-product-photo-generation | Workflow immagini prodotto |
| bakabo-openai-image | Prompt engineering OpenAI gpt-image-1 |
| bakabo-window-display | Staging editoriale multi-prodotto |
| bakabo-sound | Libreria audio BKS |
| bakabo-editorial | (pending verifica) |

---

*Documento generato da Gaetano (Claude Sonnet 4.6) · 16 Giugno 2026*
*Tutte le sessioni precedenti lette e integrate*
