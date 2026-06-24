---
name: bakabo-trend-index
description: BKS Trend Index (BKSTI) 1–25 + Age×Color×Garment Selector — sistema completo analisi trend settimanali, fascia età, palette colori, capo consigliato, score prodotto e decisione operativa
metadata:
  type: skill
  version: 2.0
  created: 2026-06-23
---

# BKS Trend Index — BKSTI

## Nome e abbreviazione

**BKS Trend Index** | Abbreviazione: **BKSTI**

### Versioni temporali
| Codice | Finestra |
|---|---|
| BKSTI-W | variazione settimanale |
| BKSTI-3M | potenziale a 3 mesi |
| BKSTI-6M | potenziale a 6 mesi |
| BKSTI-9M | potenziale a 9 mesi |
| BKSTI-12M | potenziale a 12 mesi |

---

## Scala punteggio 1–25

| Range | Lettura |
|---|---|
| 1–5 | Rumore — non rilevante |
| 6–10 | Segnale debole |
| 11–15 | Trend osservabile |
| 16–19 | Trend utile per test |
| 20–22 | Trend forte per campagna |
| 23–25 | Trend strategico per collezione |

---

## 7 Fattori dell'indice (ciascuno 1–25)

1. **Search Momentum** — crescita ricerche Google, Pinterest, marketplace, AI search, motori visuali
2. **Social Velocity** — crescita TikTok, Instagram, Pinterest, YouTube Shorts, creator, hashtag
3. **Media & Advertising Signal** — campagne, editoriali, magazine, competitor, investimenti adv, contenuti sponsorizzati
4. **Retail & Product Fit** — compatibilità ecommerce, Printify, categorie prodotto, margine, vendibilità, fattibilità
5. **Cultural Depth** — forza culturale: arte, cinema, architettura, musica, subculture, tecnologia, design
6. **BKS Visual Compatibility** — compatibilità con Hours, Origin, Glyph, Marker, Riviera, Pulse, Token, Flag
7. **Risk Filter** — rischio estetico, legale, etico, reputazionale, saturazione, associazione negativa
   - **Nota**: punteggio alto = rischio basso (25 = rischio minimo, 1 = rischio molto alto)

---

## Formula

```
BKSTI = (Search Momentum × 0.15)
      + (Social Velocity × 0.15)
      + (Media & Advertising Signal × 0.15)
      + (Retail & Product Fit × 0.15)
      + (Cultural Depth × 0.15)
      + (BKS Visual Compatibility × 0.15)
      + (Risk Filter × 0.10)
```

Risultato arrotondato su scala **1–25**.

---

## Variazione settimanale

```
BKSTI-W (%) = ((BKSTI_attuale - BKSTI_precedente) / BKSTI_precedente) × 100
```

| Range variazione | Classificazione |
|---|---|
| oltre +25% | Accelerazione forte |
| +10% → +25% | Crescita interessante |
| -5% → +10% | Stabile |
| -5% → -20% | Rallentamento |
| sotto -20% | Trend in uscita / saturo |

---

## Decisione operativa

| BKSTI | Decisione |
|---|---|
| 1–5 | IGNORE |
| 6–10 | WATCH |
| 11–15 | TEST |
| 16–19 | PUSH LIGHT |
| 20–22 | PUSH |
| 23–25 | BUILD COLLECTION |

---

## Lettura strategica

**1–5** — Trend troppo debole, confuso o non utile per BakAbo.

**6–10** — Segnale da osservare, ma non ancora da usare in campagna.

**11–15** — Trend visibile. Testare con immagini, Pinterest, caption, micro contenuti.

**16–19** — Trend interessante. Usare in immagini prodotto, mini drop, board Pinterest o test ads.

**20–22** — Trend forte. Adatto a campagna, prodotto, landing, shooting editoriale o nuova direzione visuale.

**23–25** — Trend strategico. Può diventare capsule, linguaggio stabile o evoluzione di una collezione BKS.

---

## Output settimanale

Produce tabella con:

| Campo | Descrizione |
|---|---|
| Trend | Nome del trend |
| Categoria | Macro-area tematica |
| BKSTI attuale | Punteggio 1–25 questa settimana |
| BKSTI precedente | Punteggio settimana prima |
| Variazione % | BKSTI-W |
| 3M | Previsione azione 3 mesi |
| 6M | Previsione 6 mesi |
| 9M | Previsione 9 mesi |
| 12M | Previsione 12 mesi |
| Collezione BKS | Hours / Origin / Glyph / Marker / Riviera / Pulse / Token / Flag |
| Prodotti consigliati | Tipo prodotto Printify suggerito |
| Azione consigliata | Content, ads, Pinterest, Sala Disegno, batch |
| Rischio | Breve nota rischio |
| Decisione finale | IGNORE → BUILD COLLECTION |

---

## Integrazione Worker

### Endpoint
- `GET /trend-index` — legge tabella BKSTI corrente da KV
- `POST /trend-index` — invia nuova analisi, aggiorna KV + weekly_brief automaticamente
- `DELETE /trend-index` — reset tabella settimana

### KV keys
- `bakabo:trend_index:current` — array trend settimana corrente
- `bakabo:trend_index:previous` — snapshot settimana precedente per variazione
- `bakabo:weekly_brief` — brief auto-generato dai trend ≥ 20 → iniettato nel prompt Sala Disegno

### Connessione Sala Disegno
I trend con BKSTI ≥ 20 (decisione PUSH / BUILD COLLECTION) vengono automaticamente
trascritti nel `weekly_brief` della Sala Disegno, aggiornando il prompt artwork di ogni
prodotto generato nella settimana corrente.

---

## BKS Score 1/25 — formula valutazione proposta

```
BKS Score = (BKS Identity Fit    × 0.15)
          + (Visual Strength      × 0.15)
          + (Product Truth        × 0.15)
          + (Commercial Clarity   × 0.15)
          + (Mobile Impact        × 0.10)
          + (Trend Compatibility  × 0.15)
          + (Color/Garment Fit    × 0.10)
          + (Risk Safety          × 0.05)
```

Scala e decisione identica al BKSTI (1–25, IGNORE→BUILD COLLECTION).
Soglie operative: **≥16** per test · **≥20** per campagna · **≥23** per collezione.
Regola No-Luxury: se la proposta "sembra luxury finto" → automaticamente < 15.

---

## Prompt operativo settimanale

> Analizza i trend della settimana e calcola il BKS Trend Index per BakAbo / BKS Studio su scala 1–25.
> Classifica ogni trend, misura la variazione settimanale, valuta potenziale a 3, 6, 9 e 12 mesi,
> collega ogni trend alle collezioni BKS e proponi azioni pratiche per prodotto, immagine, ads,
> Pinterest, AI search e catalogo.

---

## Esempio output tabella

| Trend | BKSTI | 3M | 6M | 9M | 12M | Decisione |
|---|---:|---|---|---|---|---|
| Hardware Style | 21 | sneakers / patch | accessori | Token capsule | stabile BKS | PUSH |
| German Expressionism | 18 | hero images | pattern scuri | Glyph / Hours | archivio visivo | PUSH LIGHT |
| AI Product Photography | 24 | catalogo | automazione | workflow stabile | asset centrale | BUILD COLLECTION |
| Mediterranean Futurism | 20 | Riviera content | summer campaign | travel bags | identità stagionale | PUSH |
| Weapon Aesthetic | 8 | solo filtro formale | evitare simboli | no prodotto | rischio alto | WATCH |

---

# MODULO 2 — BKS Age × Color × Garment Selector

Integra il BKSTI con analisi fascia d'età, palette colori e selezione automatica capo.

## Fasce d'età

### 16–24 — Gen Z / Visual Youth
Pubblico visivo, rapido, social-first, identità forti, colori accesi, simboli, contenuti brevi.
- **Colori**: nero profondo, bianco ottico, blu elettrico, viola digitale, verde acido, argento/chrome, rosso segnale
- **Prodotti**: sneakers, hoodie, backpack, T-shirt, windbreaker, flip flops, accessori grafici
- **Collezioni BKS**: Pulse, Token, Marker, Flag
- **Canali**: TikTok, Instagram Reels, Pinterest verticale, short video

### 25–34 — Young Creative Adults
Urbano, creativo, design, AI, tecnologia, moda indipendente.
- **Colori**: nero, grigio cemento, avorio, blu petrolio, verde digitale scuro, terracotta moderna, sabbia urbana
- **Prodotti**: sneakers, backpack, windbreaker, travel bag, hoodie, athletic shorts, T-shirt
- **Collezioni BKS**: Glyph, Token, Marker, Riviera
- **Canali**: Instagram, Pinterest, Google Shopping, AI Search, Meta Ads

### 35–44 — Design Conscious Buyers
Selettivo, qualità percepita, stile riconoscibile, comfort, architettura, viaggi.
- **Colori**: nero caldo, travertino, beige architettonico, grigio pietra, blu notte, verde oliva spento, ocra controllato
- **Prodotti**: puffer jacket, windbreaker, lounge pants, travel bag, backpack, sneakers sobrie, Hawaiian shirt (solo editoriale)
- **Collezioni BKS**: Hours, Glyph, Riviera, Origin
- **Canali**: Pinterest, Google Search, Meta Ads, email/newsletter, AI assistant

### 45–54 — Premium Functional Aesthetic
Funzionale, colori controllati, non rumoroso.
- **Colori**: nero, avorio, sabbia, cemento caldo, blu navy, marrone cuoio, verde salvia scuro
- **Prodotti**: windbreaker, puffer jacket, travel bag, backpack, beach towel, sneakers minimal, lounge pants
- **Collezioni BKS**: Hours, Riviera, Origin, Glyph
- **Canali**: Google Shopping, Pinterest, Facebook/Meta, newsletter, ricerca organica

### 55+ — Refined Comfort / Cultural Buyer
Estetica raffinata, culturale, leggibile, comfort, palette eleganti.
- **Colori**: avorio, sabbia, grigio caldo, blu profondo, nero morbido, terracotta elegante, verde bosco spento
- **Prodotti**: travel bag, beach towel, windbreaker, lounge pants, puffer jacket, accessori, T-shirt sobrie
- **Collezioni BKS**: Origin, Hours, Riviera, Glyph
- **Canali**: Google Search, Pinterest, Facebook, contenuti editoriali, guide prodotto

---

## Regola colori per fascia

Per ogni fascia d'età, tre livelli:
- **Base color** = dominante, 60% / 61.8%
- **Support color** = secondario, 30% / 38.2%
- **Accent color** = spinta, 10%

---

## Logica automatica selezione capo

| Tipo trend | Prodotti preferiti | Collezioni |
|---|---|---|
| Giovane, veloce, digitale, pop, cromatico | sneakers, hoodie, backpack, T-shirt, windbreaker | Pulse, Token, Marker, Flag |
| Urbano, tecnico, architettonico | windbreaker, puffer, backpack, sneakers, travel bag | Marker, Token, Hours, Glyph |
| Culturale, artistico, simbolico | T-shirt, lounge pants, travel bag, puffer, sneakers, beach towel | Glyph, Hours, Origin, Flag |
| Mediterraneo, viaggio, estate, lifestyle | swim trunks, bikini, beach towel, flip flops, travel bag, Hawaiian shirt | Riviera, Origin, Flag |
| Premium, comfort, adulto, sobrio | puffer jacket, windbreaker, lounge pants, travel bag, backpack | Hours, Riviera, Origin, Glyph |

---

## Formula BKS Age Product Score (1–25)

```
BKS_APS = (Age Fit × 0.20)
         + (Color Fit × 0.15)
         + (Garment Fit × 0.20)
         + (BKS Collection Fit × 0.15)
         + (Commercial Fit × 0.15)
         + (Visual Impact × 0.10)
         + (Risk Safety × 0.05)
```

### Decisione APS

| Range | Azione |
|---|---|
| 1–5 | Non usare |
| 6–10 | Osservare |
| 11–15 | Test immagine / Pinterest |
| 16–19 | Test prodotto / mini campagna |
| 20–22 | Spingere in advertising |
| 23–25 | Sviluppare capsule o collezione |

---

## Output Age × Color × Garment

| Trend | Età target | Colori (base/support/accent) | Capo | Collezione | APS | Azione |
|---|---|---|---|---|---:|---|

**Esempio:**

| Trend | Età target | Colori | Capo | Collezione | APS | Azione |
|---|---|---|---|---|---:|---|
| Hardware Style | 25–34 / 35–44 | nero, cemento, chrome | sneakers, backpack, windbreaker | Token / Marker | 21 | PUSH |
| German Expressionism | 35–44 / 45–54 | nero, avorio, grigio pietra, rosso spento | puffer, lounge pants, T-shirt | Glyph / Hours | 18 | PUSH LIGHT |
| Mediterranean Futurism | 25–34 / 35–44 / 45–54 | sabbia, azzurro, terracotta, blu petrolio | swim trunks, beach towel, travel bag | Riviera / Origin | 22 | PUSH |

---

## Regola finale

Il trend viene scelto solo se:
- è adatto a una fascia d'età reale
- ha colori coerenti con quella fascia
- si traduce in un capo vendibile su Printify
- rafforza una collezione BKS
- funziona su mobile e Pinterest / AI Search
- non crea rischio reputazionale
- non trasforma BakAbo in fast fashion o falso luxury
