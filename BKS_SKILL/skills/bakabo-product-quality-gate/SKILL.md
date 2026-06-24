---
name: bakabo-product-quality-gate
description: Use this skill BEFORE publishing any product on bakabo.club. BKS Product Score ≥ 21/25 required to publish. Two-level system: primary BKS Product Score (9 factors × weights) + detailed 5-dimension deep-dive. Minimum 21/25 to publish, 23/25 for strategic product, 25 for capsule candidate. Triggers: "valuta il prodotto", "score", "quality check", "possiamo pubblicarlo?", "è pronto?", REJECT / REWORK / PRODUCT READY / STRATEGIC PRODUCT / CAPSULE CANDIDATE.
---

# BKS Studio — Product Quality Gate
## BKS Product Score ≥ 21/25 — minimo obbligatorio per pubblicare

Nessun prodotto BakAbo viene pubblicato senza superare questo gate.
Meglio 8 prodotti da 22/25 che 80 da 14/25. BakAbo è sistema visivo curato, non catalogo di massa.

---

## LIVELLO 1 — BKS Product Score (formula principale)

```
BKS Product Score =
  (BKS Identity Fit      × 0.15)   ← è riconoscibile come BakAbo / BKS?
+ (Visual Surface Strength × 0.15) ← il pattern/superficie è forte?
+ (Product Truth          × 0.15)  ← credibile rispetto a Printify / made-on-demand?
+ (Commercial Clarity     × 0.15)  ← il cliente capisce subito cosa compra?
+ (Garment Fit            × 0.10)  ← il capo è adatto a trend / età / collezione?
+ (Color Fit              × 0.10)  ← i colori sono attuali, armonici, coerenti col target?
+ (Mobile Impact          × 0.10)  ← funziona in 3 secondi da cellulare?
+ (Image Potential        × 0.05)  ← si può fotografare bene in studio neutro + architettura BKS?
+ (Risk Safety            × 0.05)  ← evita falso lusso, confusione, promesse non verificabili?
```

**Decisione finale (usa solo queste):**

| Score | Decisione |
|---|---|
| 1–18 | REJECT |
| 19–20 | REWORK — correggere naming / colori / capo / immagine / descrizione |
| 21–22 | PRODUCT READY |
| 23–24 | STRATEGIC PRODUCT |
| 25 | CAPSULE CANDIDATE |

**Regola No-Luxury:** se il prodotto "sembra luxury finto" → automaticamente ≤ 15 (REJECT).

---

## LIVELLO 2 — Analisi 5 dimensioni (dettaglio per redesign)

Usa il Livello 2 quando il prodotto è REWORK — fornisce il feedback specifico su quale dimensione correggere.

### Dimensione 1 — BLANK SUITABILITY (moda dominant) — /5
La qualità della base Printify è la fondazione su cui poggia tutto. Un print eccellente su un blank sbagliato vale zero.

### Dimensione 1 — BLANK SUITABILITY (moda dominant) — /5
La qualità della base Printify è la fondazione su cui poggia tutto. Un print eccellente su un blank sbagliato vale zero.

| Punteggio | Criterio |
| --- | --- |
| 5 | Blank premium: peso corretto per la categoria, silhouette definita, provider con buona reputazione qualità. Hoodie ≥ 400g, tee ≥ 185g, cut fashion (non boxy sportswear) |
| 4 | Blank buono, piccole limitazioni (peso leggermente basso, silhouette standard) |
| 3 | Blank accettabile ma generico — non si distingue dalla concorrenza mass-market |
| 2 | Blank di qualità discutibile — rischio resi per delusione sul ricevuto |
| 1 | Blank sbagliato per la categoria o per il prezzo richiesto |
| 0 | Blank rifiutato / problemi Printify / prodotto non stampabile correttamente |

**Blockers automatici (score = 0 indipendente):**
- Blank noto per scarsa resa stampa
- Provider con tasso resi > 10% nella categoria
- Peso o composizione non comunicati chiaramente

---

### Dimensione 2 — PRINT×GARMENT DIALOGUE (moda+arte) — /5
Il grafico e il capo devono parlare. La stampa non è un adesivo — è una decisione compositiva sul corpo.

| Punteggio | Criterio |
| --- | --- |
| 5 | Il print rispetta (o deliberatamente contesta) le linee costruttive del capo. Scala corretta per il corpo. Placement intenzionale: center chest, full-front, sleeve, all-over — mai casuale |
| 4 | Placement buono, piccola imprecisione di scala o posizione |
| 3 | Placement standard (center chest generico) — funziona ma non sceglie |
| 2 | Print troppo grande/piccolo per il capo o mal centrato |
| 1 | Print sembra applicato senza considerare il garment come superficie compositiva |
| 0 | Print incompatibile col capo (es. print complesso su garment strutturato che lo distorce) |

---

### Dimensione 3 — VISUAL CONCEPT STRENGTH (arte dominant) — /5
La forza del sistema visivo. Usa la skill `bakabo-art-critic` per questo punteggio.

| Punteggio | Criterio |
| --- | --- |
| 5 | Il print ha un sistema visivo coerente e leggibile. La connessione collection concept → mark visivo è chiara anche senza leggere il nome. L'originale è riconoscibile come BKS. |
| 4 | Buona coerenza visiva, piccola ambiguità nel concept encoding |
| 3 | Il print è grafico e curato ma il legame col concept musicale/culturale è debole o assente |
| 2 | Il print è decorativo ma non concettuale — potrebbe essere di qualsiasi brand |
| 1 | Il print è generico o imita referenze esistenti senza elaborazione |
| 0 | Stock imagery, clip art, o contenuto senza identità visiva propria |

**Blockers automatici:**
- Immagini stock usate senza trasformazione
- Print che replica visivamente un brand esistente
- Contenuto che non parte dal mockup reale del prodotto

---

### Dimensione 4 — CHROMATIC INTEGRITY (arte+moda) — /5
Il colore deve funzionare come identità artistica (BKS collection) E come posizionamento di mercato (moda contemporanea).

| Punteggio | Criterio |
| --- | --- |
| 5 | La palette del prodotto (garment color + print colors) appartiene inequivocabilmente alla collection di riferimento. La combo è market-viable: non troppo safe, non troppo divisiva. |
| 4 | Buona coerenza collection, piccola deviazione di palette |
| 3 | Palette accettabile ma non distintiva — potrebbe essere di qualsiasi marca |
| 2 | Il colore del garment e il print entrano in conflitto cromatico non intenzionale |
| 1 | Palette cromaticamente sbagliata per la collection (es. teal su un prodotto Flag rosso) |
| 0 | Combinazione cromatica che distrugge la leggibilità del print |

---

### Dimensione 5 — EDITORIAL CREDIBILITY (moda+arte) — /5
Il test finale: questo prodotto comparirebbe su SSENSE, System, Wallpaper*? Roberto lo porterebbe a un buyer di un concept store?

| Punteggio | Criterio |
| --- | --- |
| 5 | Sì, senza esitazione. Il prodotto ha la statura di un pezzo da concept store indipendente. |
| 4 | Sì, con piccole riserve. Potrebbe avere bisogno di una minor edit per arrivare al livello |
| 3 | Forse — è un prodotto onesto ma non ambizioso. Non verrebbe selezionato da un buyer esigente. |
| 2 | Probabilmente no. Manca la scintilla che lo rende selezionabile da chi sceglie con occhio critico. |
| 1 | No. Ha gli attributi tecnici del fashion ma non la voce artistica. |
| 0 | No. È un prodotto generico con un print sopra — non è BKS. |

---

## Matrice decisionale unificata

```
BKS Product Score    Decisione finale           Tag Shopify
──────────────────────────────────────────────────────────────
25                  CAPSULE CANDIDATE           bakabo-hero-product
23–24               STRATEGIC PRODUCT           bakabo-hero-product
21–22               PRODUCT READY               bakabo-enriched
19–20               REWORK (non pubblicare)     bakabo-needs-review
< 19                REJECT                      bakabo-ai-failed / bakabo-needs-redesign
```

---

## Come si esegue il gate — workflow AI

1. **Input:** nome prodotto + BKS collection di riferimento + URL/immagine mockup Printify
2. **Score D1:** consulta metadati Printify (blank name, provider, weight)
3. **Score D2:** analizza immagine mockup — print placement, scala sul corpo
4. **Score D3:** applica `bakabo-art-critic` — leggi il graphic, valuta concept strength
5. **Score D4:** confronta palette con `BKS_COLLECTION_PALETTE` (Hours `#c8c4be`, Glyph `#d4a030`, ecc.)
6. **Score D5:** editorial judgment — test mentale: SSENSE? System? Concept store TL?
7. **Output:** tabella score + totale + decisione + feedback specifico per ogni dimensione < 4

---

## Feedback per redesign — come si scrive

Non scrivere "migliorare il design." Scrivi la correzione specifica:

```
D3 = 2 → "Il print è un pattern geometrico senza connessione leggibile
           con BKS Pulse (frequenza elettronica, violet). Soluzione:
           il motivo dovrebbe incorporare un riferimento alla forma
           d'onda o alla nota musicale in scala, con palette violet
           che spinga verso #8888cc."

D5 = 1 → "Il prodotto non ha statura editoriale: il print è decorativo
           ma non concettuale. Confronta con BKS Glyph hoodie (score 23)
           — la differenza è nel rigore del sistema visivo."
```

---

## Integrazione nel workflow catalogo

```
Prodotto creato su Printify
         ↓
Sync automatico → Shopify (draft, not published)
         ↓
Quality Gate (questo skill) — score 0–25
         ↓
Score ≥ 21 → bakabo-printify-sync (enrichment: title, copy, SEO, metafields)
           → bakabo-product-copy (descrizione HTML + meta)
           → publish + tag bakabo-enriched / bakabo-hero-product
         ↓
Score 19–20 → REWORK — feedback preciso → NON pubblicare
           → Roberto riceve briefing di redesign specifico
         ↓
Score < 19  → REJECT — rimuovere da Printify / non creare
```

---

## Prodotti di riferimento BKS (benchmark score noto)

Quando in dubbio sul calibro, confronta con questi:

| Prodotto | Score stimato | Note |
| --- | --- | --- |
| BKS Glyph Hoodie — ochre chromatic field | 23/25 | Benchmark di eccellenza |
| BKS Origin Pullover — botanical mark | 21/25 | Solido, pubblicabile |
| BKS Pulse Tee — violet frequency | 21/25 | Minimo pubblicabile |
| BKS Token Oversized — purple depth | 22/25 | Alto valore editoriale |

---

## BKS Collection palette (per D4)

| Collection | Accent hex | Temperatura | Stagione |
| --- | --- | --- | --- |
| Hours | `#c8c4be` | Neutra/fredda | Inverno/Estate |
| Glyph | `#d4a030` | Calda/ambra | Autunno/Primavera |
| Marker | `#c04418` | Calda/bruciata | Autunno |
| Riviera | `#0ca898` | Fredda/teal | Primavera/Estate |
| Pulse | `#8888cc` | Fredda/viola | Estate/Inverno |
| Token | `#9828d8` | Fredda/profonda | Inverno |
| Flag | `#c82020` | Calda/forte | Autunno/Inverno |
| Origin | `#489808` | Calda/botanica | Primavera |
