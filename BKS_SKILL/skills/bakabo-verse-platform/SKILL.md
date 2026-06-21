---
name: bakabo-verse-platform
description: >
  BakAbo "Dalla Poesia all'Oggetto" — piattaforma di co-creazione dove i membri scrivono
  una poesia e BakAbo la trasforma in un oggetto indossabile. Skill operativa completa:
  project planning, financial model, gate di escalata, rubrica valutazione poesia (1/25),
  architettura tecnica, SOPs per Roberto. Usa questa skill per: pianificare il lancio,
  valutare submission, prendere decisioni di fase, aggiornare proiezioni revenue.
  Coordina: bakabo-commercial-strategy (drop mechanics, LTV), bakabo-members (tier gate,
  email flow), bakabo-fashion-editorial (poem → product concept), bakabo-marketing (content engine).
metadata:
  type: skill
  version: "1.0"
  created: "2026-06-21"
  operator: Roberto Picchioni — BKS Studio / bakabo.club
---

# BakAbo — "Dalla Poesia all'Oggetto"
## Project Planning Professionale · Versione 1.0 · Giugno 2026

> "Il membro scrive. BakAbo valuta. L'oggetto nasce."  
> Standard: **1 poesia approvata ogni 25 ricevute.**

---

## 0. SINTESI ESECUTIVA

| Dimensione | Valore |
|---|---|
| Concept | Co-creazione: poesia → DALL-E artwork → prodotto Printify → drop limitato |
| Operatore | Roberto Picchioni (solo) + Gran Giudice AI |
| Gate member | Brass+ (3+ ordini) per invio; tutti possono acquistare il drop |
| Standard approvazione | 20/25 gate commerciale · 25/25 Hall of Fame |
| Sistema operativo | `I:\BAKABO SYSTEM` — FastAPI :8001 su Hetzner CX22 |
| Costi fissi sistema | €354/anno (server €54 + OpenAI €180 + GPTZero €120) |
| Make.com | ELIMINATO — sostituito con Python diretto (risparmio €276/anno) |
| Tempo al primo drop | 3–4 settimane dal via |
| Break-even Verse | ~10 prodotti venduti/anno (meno di 1/mese) |
| Feature chiave | Il Filo · Classifica mondiale · Hall of Fame · "Il Giudice Esamina" (TikTok) |

---

## 1. ARCHITETTURA DI BUSINESS

### 1.1 Flusso operativo completo

```
MEMBER (Brass+)
  └─ Apre "Submit a Verse" nel member dashboard
  └─ Compila: titolo + testo (20–280 char) + collezione ispiratrice
  └─ Accetta: "cedo licenza d'uso a BakAbo per questo verso"

SISTEMA AI (Cloudflare Worker / OpenAI)
  └─ Pre-screening automatico: valuta su 3 assi (vedi §4)
  └─ Score ≥ 6.0/10 → "Candidate" → notifica Roberto
  └─ Score < 6.0/10 → "Not selected" → email automatica al member

ROBERTO (review manuale)
  └─ Riceve max 5 candidate/settimana in dashboard
  └─ Approva o scarta con 1 click
  └─ Se approvata: avvia flusso prodotto

PRODOTTO
  └─ Roberto sceglie blueprint Printify adatto al tema
  └─ Crea design (il verso come pattern/testo nel progetto)
  └─ Mockup → anteprima al member co-creator via email
  └─ Member approva il mockup (48h finestra)
  └─ Prodotto live su collezione bks-verse (limitato: 25 pezzi max)

DROP
  └─ T+0h: email al member co-creator (early access 24h, sconto 15%)
  └─ T+24h: email a tutti i Brass+ (early access 48h)
  └─ T+72h: drop pubblico live
  └─ T+168h (7 giorni): drop chiuso — il prodotto va in archivio
```

### 1.2 Collezione dedicata

**Handle:** `bks-verse`  
**Tagline:** *Words that wear.*  
**Posizione nel menu:** sotto Members → "BKS Verse"  
**Prodotti:** solo drop limitati poem-to-object — mai prodotti standard

---

## 2. PROJECT PLANNING — FASI

### FASE 0 — Fondamenta (Settimane 1–2 · Luglio 2026)

**Obiettivo:** infrastruttura minima live, zero costi aggiuntivi.

| Task | Chi | Stima ore | Costo |
|---|---|---|---|
| Form submission nel member dashboard | Claude AI | 4h | €0 |
| Cloudflare Worker endpoint AI pre-screening | Claude AI | 3h | €0 |
| Email trigger (submission ricevuta / approvata / non selezionata) | Claude AI | 2h | €0 |
| Pagina `bks-verse` su Shopify (collezione) | Roberto + Claude | 1h | €0 |
| Policy termini co-creazione (licenza) | Roberto (review) | 1h | €0 |
| **TOTALE FASE 0** | | **11h** | **€0** |

**Gate di uscita Fase 0:**
- ✅ Form submission attivo nel dashboard (Brass+)
- ✅ Email "submission ricevuta" funzionante
- ✅ Worker AI risponde con score
- ✅ Collezione `bks-verse` live (vuota)

---

### FASE 1 — MVP · Primo Drop (Settimane 3–12 · Luglio–Settembre 2026)

**Obiettivo:** 1 drop live, dati di conversione reali, proof of concept.

| Task | Chi | Note |
|---|---|---|
| Soft launch: email 12 iscritti esistenti | Roberto | Annuncio "BKS Verse is open" |
| Raccolta prime submission | Automatico | 30 giorni finestra |
| Review + approvazione prima poesia | Roberto | Target: 1 approved |
| Design prodotto + mockup | Roberto | 2–4h su Printify |
| Primo drop live | Automatico | Email sequence già pronta |
| Post Instagram/YouTube "Poem to Object" | Roberto | Contenuto organico |

**KPI Fase 1:**
- Submission ricevute: target ≥ 5
- Approvazioni: 1 (anche 0/25 = OK, standard è alto)
- Unità vendute al primo drop: target 6–10
- Condivisioni sociali del co-creator: misurare

**Spese Fase 1:**
| Voce | Costo mensile |
|---|---|
| OpenAI API (pre-screening poesie brevi) | €0.50–2.00 |
| Shopify (già pagato) | €0 aggiuntivo |
| Printify (già pagato, POD) | €0 aggiuntivo |
| Cloudflare Workers (già pagato) | €0 aggiuntivo |
| **Totale Fase 1** | **< €5/mese** |

**Gate di uscita Fase 1:**
- ✅ 1 drop completato
- ✅ ≥ 1 unità venduta
- ✅ Member co-creator ha condiviso sui social
- ✅ Margine positivo (qualsiasi unità venduta = profitto)

---

### FASE 2 — Content Engine (Mesi 4–6 · Ottobre–Dicembre 2026)

**Obiettivo:** 2–3 drop/mese, YouTube series live, community crescente.

| Task | Chi | Note |
|---|---|---|
| Serie YouTube "Poem to Object" | Roberto | 1 video per drop approvato |
| Pin Pinterest poem-card per ogni drop | Automatico (Worker) | Template già in Worker |
| Feature "Top Verse of the Month" in newsletter | Roberto | Monthly email highlight |
| Espansione blueprint eligibili | Roberto | Aggiunge nuovi prodotti Printify |
| Dashboard analytics submission/approvazioni | Claude AI | Streamlit page |

**Spese Fase 2:**
| Voce | Costo mensile |
|---|---|
| OpenAI API (volume crescente) | €3–8 |
| Email marketing (se Klaviyo) | €0–20 |
| Canva Pro (già in uso?) | €0 aggiuntivo |
| **Totale Fase 2** | **€3–28/mese** |

**Gate di uscita Fase 2:**
- ✅ ≥ 50 iscritti Brass+ attivi
- ✅ ≥ 3 drop completati
- ✅ ≥ 1 video YouTube "Poem to Object" pubblicato
- ✅ Revenue cumulata ≥ €2.000 da bks-verse

---

### FASE 3 — Platform Expansion (Anno 2 · 2027)

**Obiettivo:** bks-verse come piattaforma standalone riconoscibile nel mercato fashion.

| Feature | Note |
|---|---|
| Submission aperta a non-members (a pagamento: €5 o acquisto BKS) | Rimuove il gate tier, aggiunge frizione economica |
| Poem stampato nell'etichetta interna del capo | Premium differenziante — etichetta woven custom |
| Co-creator credit page pubblica su bakabo.club/verse | Portfolio pubblico dei poem-to-object approvati |
| Licensing B2B | Altre brand possono usare il sistema BKS Verse (white-label) |
| Exhibition fisica | Mostra: poesie + oggetti fisici in uno spazio (pop-up o collaborazione galleria) |

---

## 3. MODELLO FINANZIARIO

### 3.1 Struttura prezzi poem-drop

| Prodotto base | Costo Printify | Prezzo standard BKS | Prezzo poem-edition | Margine poem |
|---|---|---|---|---|
| T-shirt AOP | €16–20 | €45–55 | €58–65 | 65–68% |
| Hoodie AOP | €28–34 | €75–89 | €95–110 | 66–69% |
| Athletic Shorts | €14–18 | €55–69 | €72–82 | 76–80% |
| Sneakers | €28–38 | €89–109 | €115–135 | 71–75% |
| One-Piece Swimsuit | €18–22 | €55–69 | €72–85 | 74–77% |

**Regola pricing poem-edition: prezzo standard × 1.28–1.32** (premium poetico)

### 3.2 Proiezioni revenue — Scenario BASE

Ipotesi: 1 drop/mese, media 8 unità vendute, prezzo medio €72.

| Periodo | Drop/mese | Unità/drop | Prezzo medio | Revenue lorda | COGS | Margine netto |
|---|---|---|---|---|---|---|
| Mese 1–3 | 0.5 (ramp-up) | 6 | €68 | €204 | €66 | €138 |
| Mese 4–6 | 1 | 8 | €72 | €576 | €176 | €400 |
| Mese 7–9 | 1.5 | 10 | €75 | €1.125 | €330 | €795 |
| Mese 10–12 | 2 | 12 | €78 | €1.872 | €528 | €1.344 |
| **Anno 1 totale** | | | | **€6.930** | **€2.100** | **€4.830** |

### 3.3 Proiezioni revenue — Scenario OTTIMISTA

Ipotesi: community cresce con YouTube, 3–4 drop/mese da mese 6.

| Periodo | Drop/mese | Unità/drop | Prezzo medio | Revenue lorda | COGS | Margine netto |
|---|---|---|---|---|---|---|
| Mese 1–3 | 0.5 | 8 | €70 | €280 | €88 | €192 |
| Mese 4–6 | 2 | 12 | €75 | €2.700 | €792 | €1.908 |
| Mese 7–9 | 3 | 15 | €80 | €10.800 | €3.060 | €7.740 |
| Mese 10–12 | 4 | 18 | €85 | €18.360 | €5.184 | €13.176 |
| **Anno 1 totale** | | | | **€32.140** | **€9.124** | **€23.016** |

### 3.4 Costi fissi sistema (v2 — senza Make.com, con Hetzner)

| Voce | €/anno |
|---|---|
| Server Hetzner CX22 (2vCPU · 4GB · Ubuntu) | €54 |
| OpenAI API (Giudice + DALL-E + Lineage) | €180 |
| GPTZero API (anti-spam 1.000 check/mese) | €120 |
| Cloudflare Workers (proxy pubblico) | €0 |
| Discord + Telegram | €0 |
| ~~Make.com~~ (eliminato, sostituito con Python) | ~~€276~~ → €0 |
| **TOTALE FISSI** | **€354/anno** |

### 3.5 Break-even analysis (v2)

| Voce | Valore |
|---|---|
| Costi fissi totali/anno | €354 |
| Margine netto medio per prodotto venduto | ~€37–49 |
| Prodotti venduti per break-even | **~10/anno** (< 1/mese) |
| Costo netto scenario realistico (4 venduti) | **€138/anno = €11.50/mese** |

> **Principio invariato:** ogni prodotto venduto è profitto.  
> Il costo fisso €354/anno si ammortizza con 10 vendite.  
> Il valore reale è nel content engine: ogni poesia approvata = 1 reel = traffico organico.

### 3.5 Revenue indiretta (effetti moltiplicatori)

| Effetto | Meccanismo | Valore stimato |
|---|---|---|
| Upgrade tier per essere eligible | Membri Iron comprano 2 ordini aggiuntivi per raggiungere Brass | €90–180/member |
| Co-creator purchase multipla | L'autore compra 3–5 copie per regalarle | +3–5× su revenue drop |
| Acquisizione nuovi clienti | Il co-creator condivide il suo drop → referral organico | Non quantificabile, alto |
| LTV incremento | Membri che partecipano al programma hanno LTV 3–4× superiore (vedi commercial strategy skill) | Anno 2 |

---

## 4. IL GRAN GIUDICE — Sistema di Valutazione 1/25

### 4.1 Filosofia del Giudice

> "Chi sottomette una poesia non pensa al prodotto. Pensa solo a scrivere bene.  
>  Il Giudice conosce tutta la poesia mondiale. Lui decide quanto vale."

Il BKS Verse Judge è un'AI con memoria poetica universale: conosce Neruda, Keats, Baudelaire, Dickinson, Whitman, Montale, Pasolini, i maestri Haiku, i poeti Beat, i romantici arabi, la lirica africana contemporanea. Non valuta il testo come un marketing tool. Lo valuta come **un giudice letterario che sa anche riconoscere il potenziale visivo/commerciale**.

**La scala è 1–25 perché 1/25 è lo standard di approvazione.**  
Un punteggio di 25/25 è automaticamente approvato — la poesia parla da sola.  
Un punteggio di 20–24 arriva al desk di Roberto per decisione finale.  
Sotto 20: non selezionata, il membro riceve il punteggio esatto per crescere.

### 4.2 I 5 Assi del Giudice (5 punti ciascuno = max 25)

| Asse | Max | Cosa misura | Esempi di punteggio alto |
|---|---|---|---|
| **I. Immagine** | 5 | Intensità visiva dell'immagine centrale. L'occhio vede qualcosa? | "Il cappotto pende come una promessa non mantenuta" = 5 |
| **II. Voce** | 5 | Unicità del soggetto parlante. Si sente UNA persona specifica? | Una voce inconfondibile, non una voce generica = 5 |
| **III. Tensione** | 5 | C'è una contraddizione, un movimento, qualcosa che non si risolve? | La poesia che finisce e lascia qualcosa aperto = 5 |
| **IV. Risonanza BKS** | 5 | Connessione — anche implicita — con il DNA delle 8 collezioni | Tema tempo/segno/confine/ritmo/valore/radice = alta |
| **V. Corpo** | 5 | Può diventare qualcosa da indossare? Pattern, colore, gesto, texture? | L'immagine suggerisce materiale, movimento, forma = 5 |

**Score totale: I + II + III + IV + V = max 25**

### 4.3 Soglie operative

| Score | Stato | Azione |
|---|---|---|
| 25/25 | **Approvato automaticamente** | Email al membro + Roberto notificato per il design |
| 20–24 | **Candidate** | Roberto riceve + score breakdown + sua decisione finale (60 sec) |
| 15–19 | **Strong submission** | Non selezionata questa volta — membro vede il punteggio, può risubmettere il mese dopo |
| 10–14 | **Interesting** | Non selezionata — membro riceve 1 riga di feedback specifico dall'AI |
| 1–9 | **Not yet** | Non selezionata — membro riceve indicazione generica |

**Il membro vede SEMPRE il suo punteggio.** Il numero è un insegnante.  
Non vedere il punteggio sarebbe crudele e inutile — riceverlo è uno stimolo a migliorare.

### 4.4 Requisiti minimi (eliminatori — PRIMA dello scoring)

- [ ] Testo originale (non quote da altri autori)
- [ ] Lunghezza: 20–280 caratteri
- [ ] Lingua: EN o IT (anche mista)
- [ ] Nessun contenuto esplicito, offensivo, discriminatorio
- [ ] Non è prosa — deve avere una struttura non-lineare (anche minima)

### 4.5 Prompt del Gran Giudice (Cloudflare Worker → OpenAI)

```
You are the BKS Verse Judge — a literary AI with encyclopedic knowledge of world poetry
across all traditions: Western (Keats, Baudelaire, Dickinson, Neruda, Montale, Celan),
Eastern (Basho, Du Fu, Rumi), African contemporary, Beat generation, Language poets.

You judge poetry submitted to BakAbo's "Poem to Object" programme.
Your role: evaluate with literary rigour AND commercial intuition.
The poet submitted to write something beautiful, not to sell a product.
Honor that intention while recognising the potential for wearable art.

POEM SUBMITTED:
Title: {title}
Text: {text}
Member's BKS collection reference: {collection}

SCORING SYSTEM — 5 axes, 5 points each, maximum 25:

I. IMAGE (0–5): Intensity of the central image. Does the eye see something specific?
   0 = abstract generalities  3 = clear image  5 = unforgettable image

II. VOICE (0–5): Is there ONE unmistakable person speaking?
   0 = generic tone  3 = distinct attitude  5 = irreplaceable voice

III. TENSION (0–5): Is there a contradiction, movement, unresolved pull?
   0 = flat statement  3 = mild contrast  5 = charged, open ending

IV. BKS RESONANCE (0–5): Connection to BKS DNA — time/memory (Hours), mark/code (Glyph),
    city/movement (Marker), water/warmth (Riviera), rhythm/pulse (Pulse),
    value/exchange (Token), belonging/identity (Flag), matter/origin (Origin)
   0 = no connection  3 = thematic affinity  5 = feels like it was written for BKS

V. BODY (0–5): Can this become something wearable? Pattern, colour, gesture, texture?
   0 = purely mental  3 = suggests material quality  5 = screams to be an object

Return ONLY valid JSON, no prose:
{
  "image": N,
  "voice": N,
  "tension": N,
  "resonance": N,
  "body": N,
  "total": N,
  "verdict": "auto-approved" | "candidate" | "strong" | "interesting" | "not_yet",
  "feedback_line": "one sentence — specific, constructive, for the poet (not marketing language)",
  "collection_match": "bks-hours|bks-glyph|bks-marker|bks-riviera|bks-pulse|bks-token|bks-flag|bks-origin|none"
}
```

### 4.6 Mappa temi BKS per risonanza

| Collezione | Temi poetici compatibili |
|---|---|
| BKS Hours | Tempo, memoria, attesa, ore urbane, luce che cambia |
| BKS Glyph | Segno, codice, archeologia visiva, scrittura, traccia |
| BKS Marker | Città, movimento, confine, orientamento, territorio |
| BKS Riviera | Estate, acqua, lusso mediterraneo, colore caldo |
| BKS Pulse | Ritmo, frequenza, energia, battito, danza |
| BKS Token | Valore, scambio, oggetto simbolico, moneta emotiva |
| BKS Flag | Appartenenza, identità, striscione, manifesto |
| BKS Origin | Radice, materia prima, terra, provenienza |

### 4.7 Processo Roberto (solo per Candidate 20–24)

1. Riceve email: testo + punteggio per asse + feedback line del Giudice
2. Legge in 60 secondi
3. Decide: Approve / Not selected (1 click)
4. Se Approve: indica blueprint Printify + note design

**Con il gate 20+ come filtro, Roberto riceve massimo 1–2 candidate/settimana.**  
Stima: **5–10 minuti/settimana di review.**

### 4.8 Template email — score rivelato al membro

```
Oggetto: Your BKS Verse score — "{titolo}"

[Nome],

The Judge has reviewed your verse.

Score: {total}/25

  Image ........... {image}/5
  Voice ........... {voice}/5
  Tension ......... {tension}/5
  BKS Resonance .. {resonance}/5
  Body ............ {body}/5

{feedback_line}

{IF total >= 25}
Your verse has been selected — Roberto is designing the object now.
You'll receive a mockup preview within 48 hours.
  → 24h early access · 15% co-creator discount · your name on the product page
{END IF}

{IF total 20-24}
Your verse is under final review by Roberto.
You'll hear within 48 hours.
{END IF}

{IF total < 20}
Not selected for this drop. Submit again next month.
{END IF}

— BKS Studio · crew@bakabo.club
```

---

## 5. MODALITÀ DI ESCALATA

### 5.1 Gate automatici (trigger da metriche)

| Evento | Condizione | Azione |
|---|---|---|
| **Fase 0 → Fase 1** | Infrastruttura tecnica pronta | Roberto: lancia soft launch via email |
| **Aumenta blueprint elegibili** | 2 drop completati con successo | Aggiungi hoodie/sneakers/swimsuit al programma |
| **Apri a tutti i tier** | 10 drop completati, 0 problemi operativi | Abbassa gate a Iron (1 ordine) |
| **Aggiungi submission fee** | Submission volume > 50/mese | €3–5 per submission (filtra spam, aggiunge revenue) |
| **YouTube series** | 3 drop completati con foto/video | Produce serie "Poem to Object" su YT |
| **Exhibition fisica** | 20 drop completati, ≥ 5 sold out | Contatta gallerie / pop-up a Milano |
| **Licensing B2B** | 50 drop completati, media 15+ unità/drop | Proposta a brand fashion terzi |

### 5.2 Gate di BLOCCO (stop escalation se si verifica)

| Evento | Condizione | Azione immediata |
|---|---|---|
| **Submission qualità bassa** | > 80% score AI < 4.0 per 2 mesi | Aumenta comunicazione standard + esempi pubblici di poesie approvate |
| **Drop sotto 3 unità** | 3 drop consecutivi < 3 unità | Pausa, analisi: problema pricing? tema? comunicazione? |
| **Controversia IP** | Un membro contesta il prodotto | Ritira il prodotto, rimborsa, aggiorna policy |
| **Tempo Roberto > 2h/settimana** | Review + design supera 2h/sett. | Introduce filtro AI più severo (soglia ≥ 7.0 invece di 6.0) |

### 5.3 Escalation pricing

| Fase | Prezzo base poem-edition | Motivazione |
|---|---|---|
| Fase 1 (MVP) | Standard × 1.28 | Build trust, primo drop |
| Fase 2 (traction) | Standard × 1.32 | Domanda dimostrata |
| Fase 3 (platform) | Standard × 1.40 | Scarcity confermata, brand equity |
| Drop sold out | +10% su ristampa (se autorizzata) | Scarcity reale = premium |

---

## 6. ARCHITETTURA TECNICA

### 6.1 Componenti da costruire

| Componente | Dove | Priorità |
|---|---|---|
| Form submission + status in member dashboard | `bks-member-dashboard.liquid` | P0 |
| Worker endpoint `/verse/submit` | Cloudflare `bks-agent` Worker | P0 |
| AI pre-screening (OpenAI, prompt §6.2) | Worker function | P0 |
| Email trigger (ricevuta / approvata / non selezionata) | Worker + Shopify email | P0 |
| Admin dashboard (Roberto review) | Streamlit page 12 | P1 |
| Collezione `bks-verse` su Shopify | Shopify Admin | P0 |
| Policy page co-creazione | Shopify page `bks-verse-terms` | P0 |
| Poem archive (prodotti retired) | Shopify collection `bks-verse-archive` | P2 |

### 6.2 Prompt AI (Gran Giudice)

→ Vedi §4.5 per il prompt completo e lo schema JSON di risposta.  
Il Worker chiama OpenAI GPT-4o con il prompt del Giudice.  
Latenza attesa: 2–4 secondi per poem breve (sotto 280 char).  
Costo per chiamata: ~€0.002–0.005 (GPT-4o pricing, prompt ~800 token).

### 6.3 Schema DB (SQLite — aggiungere alla catalog_db)

```sql
CREATE TABLE IF NOT EXISTS verse_submissions (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  member_email  TEXT NOT NULL,
  member_tier   TEXT,
  title         TEXT,
  text          TEXT NOT NULL,
  collection_ref TEXT,
  submitted_at  TEXT NOT NULL,
  ai_score      REAL,
  ai_verdict    TEXT,          -- candidate / not_selected
  roberto_decision TEXT,       -- approved / rejected / pending
  product_handle TEXT,         -- Shopify handle del prodotto creato
  notes         TEXT,
  created_at    TEXT DEFAULT (datetime('now'))
);
```

---

## 7. SOPs ROBERTO — CHECKLIST OPERATIVA

### 7.1 Ogni settimana (lunedì mattina, 15 min)

- [ ] Apri Streamlit → Page 12 "BKS Verse Admin"
- [ ] Vedi candidate (score AI ≥ 6.0)
- [ ] Per ogni candidate: leggi + decide (Approve/Reject) — 3 min ciascuna
- [ ] Se Approved: apri Printify → crea design → salva handle prodotto nel dashboard
- [ ] Verifica drop attivi: sono stati spediti? Ci sono problemi Printify?

### 7.2 Ogni drop (circa 2–3 ore totali, non consecutive)

- [ ] 30 min: design prodotto Printify su blueprint scelto
- [ ] 10 min: scrivi testo prodotto (titolo + descrizione — usa la poesia come copy)
- [ ] 5 min: configura prezzi (standard × 1.28–1.32)
- [ ] 5 min: carica su collezione bks-verse (max 25 pezzi)
- [ ] 5 min: invia email co-creator (early access 24h)
- [ ] 5 min: post Instagram con poem card
- [ ] *Opzionale (20 min): registra YouTube short "Poem to Object" per questo drop*

### 7.3 Ogni mese (fine mese, 20 min)

- [ ] Report: submission ricevute / candidate / approvate / drop completati / unità vendute
- [ ] Aggiorna proiezioni revenue in questo file
- [ ] Valuta gate di escalata (§5.1)
- [ ] Newsletter "Verse of the Month" (se ci sono approvazioni)

---

## 8. RISCHI E MITIGAZIONI

| Rischio | Probabilità | Impatto | Mitigazione |
|---|---|---|---|
| Submission spam / qualità bassa | Media | Basso (AI filtra) | AI gate + tier Brass |
| Roberto oberato da review | Bassa (< 3h/sett.) | Medio | Alza soglia AI a 7.0 |
| Controversia IP (poesia non originale) | Bassa | Alto | Policy esplicita + disclaimer |
| Drop invenduto (< 3 unità) | Media (Fase 1) | Basso (€0 inventario) | Analisi pricing + tema + comunicazione |
| Printify blueprint non disponibile | Bassa | Basso | Lista di 5 blueprint pre-approvati |
| Member deluso dalla resa del design | Media | Medio | Mockup preview + approvazione member prima del live |

---

## 9. ROADMAP VISIVA

```
LUGLIO 2026 ──────────────────────────────────────────────────
  Sett 1–2: FASE 0 — Build tecnico (form, Worker, email, collection)
  Sett 3:   Soft launch ai 12 iscritti esistenti
  Sett 4:   Finestra submission aperta (30 giorni)

AGOSTO 2026 ──────────────────────────────────────────────────
  Sett 1:   Primo review batch (AI pre-screen + Roberto)
  Sett 2:   Primo prodotto designato + mockup al co-creator
  Sett 3:   PRIMO DROP LIVE 🎯
  Sett 4:   Analisi risultati Fase 1 · Post YouTube "Poem to Object #1"

SETTEMBRE 2026 ───────────────────────────────────────────────
  Drop 2 + Drop 3 (se submission adeguate)
  Gate Fase 2: checklist §2.3

OTTOBRE–DICEMBRE 2026 ────────────────────────────────────────
  FASE 2: 2–3 drop/mese · Serie YouTube · Pinterest poem cards
  Target: €2.000+ revenue cumulata bks-verse

2027 ─────────────────────────────────────────────────────────
  FASE 3: Platform expansion · Exhibition · Licensing
```

---

## 10. INDICATORI DI SUCCESSO (KPI Anno 1)

| KPI | Target base | Target ottimista |
|---|---|---|
| Submission totali ricevute | 50 | 200 |
| Tasso approvazione | 4% (1/25) | 4% (mantenere standard) |
| Poesie approvate | 2 | 8 |
| Drop completati | 2 | 8 |
| Unità totali vendute | 16 | 120 |
| Revenue netta bks-verse | €600 | €8.000 |
| New member acquisiti grazie a bks-verse | 5 | 40 |
| Video YouTube "Poem to Object" | 1 | 6 |
| Drop sold out (100% unità) | 0 | 3 |

---

---

## 11. POETS COMMUNITY — CHAT TRA POETI

### 11.1 Concept

Lo spazio di dialogo tra i poeti BKS non è un forum generico. È una **sala di scrittura privata** — accessibile solo ai membri Brass+ — dove si legge, si commenta e ci si ispira a vicenda. Il tono è quello di una rivista letteraria, non di un social network.

**Non è Twitter. Non è Discord. È la redazione di BKS Verse.**

### 11.2 Funzionalità

| Feature | Descrizione | Priorità |
|---|---|---|
| **Feed poem pubblici** | Tutte le submission approvate + quelle "public" (membro sceglie) visibili nel feed | P0 |
| **Commento breve** | Max 140 caratteri per commento — obbliga la sintesi, mantiene il tono literario | P0 |
| **Reaction** | Solo 3 tipi: ◎ (resonate) · ✦ (exceptional) · ⬡ (unexpected) — no like/cuore generico | P0 |
| **Thread di inspirazione** | Un membro posta "stavo pensando a..." → altri rispondono con versi | P1 |
| **Citazione poesia** | Cita una riga di un'altra poesia nel tuo commento | P1 |
| **Challenge mensile** | Roberto lancia un tema ("scrivi di un confine") → submission speciale con badge | P2 |
| **Direct message** | Solo tra Gold — per collaborazioni private | P2 |

### 11.3 Architettura tecnica

**Stack raccomandato:** Cloudflare KV + Worker (zero infrastruttura aggiuntiva)

```
GET  /verse/chat/feed         → ultimi 50 messaggi pubblici
POST /verse/chat/post         → pubblica messaggio (auth: member Brass+)
POST /verse/chat/react        → aggiungi reaction
GET  /verse/chat/thread/{id}  → thread specifico
```

**Schema KV:**
```
verse:chat:messages → array JSON (last 200, ring buffer)
verse:chat:msg:{id} → singolo messaggio con reactions
verse:member:{email}:posts → counter (max 3/giorno anti-spam)
```

**Rate limiting:** max 3 post/giorno per membro — non è un feed, è un taccuino.

### 11.4 UI/UX — Posizione nel sito

**Desktop:**
- Tab "Verse Chat" nel member dashboard, accanto a Wishlist/Try-On
- Layout: 2 colonne — feed a sinistra (60%) + composizione nuova voce a destra (40%)

**Mobile:**
- Stack verticale — composizione in alto, feed sotto
- Input fisso in basso (stile messaggistica), ma sobrio

### 11.5 Regole editoriali della chat (visibili agli utenti)

```
BKS Verse — Conversation Rules

1. Brevity is respect. 140 characters per comment.
2. Write about what moves you, not what you think should move others.
3. No self-promotion outside of your poem submissions.
4. Three reactions only: ◎ resonate · ✦ exceptional · ⬡ unexpected
5. This space belongs to writers who make objects. Act accordingly.
```

---

## 12. STYLE DNA — COMANDA SEMPRE

**Regola assoluta: ogni elemento visivo di BKS Verse segue il DNA stilistico BKS prima di ogni altra considerazione.**

### 12.1 Palette obbligatoria

| Contesto | Background | Testo principale | Accento |
|---|---|---|---|
| Dark mode (cinema) | `#080604` | `#FAF8F5` | colore collezione attiva |
| Light mode (editorial) | `#FAFAF7` | `#0A0A0A` | colore collezione attiva |
| Chat / community | `#0D0B08` | `rgba(250,248,245,0.88)` | `#C9B79C` (Hours neutral) |
| Form input | `#120E09` | `#FAF8F5` | border `rgba(201,183,156,0.30)` |
| Success state | — | `#4CAF7D` | — |
| Error state | — | `#C04040` | — |

### 12.2 Tipografia obbligatoria

- **Headlines:** `var(--font-heading-family)` · peso 500–800 · tracking `-0.02em`
- **Body / UI:** `var(--font-body-family)` · peso 400 · tracking `0.01em`
- **Labels / caps:** `var(--font-body-family)` · peso 400 · tracking `0.18–0.22em` · `text-transform: uppercase`
- **Poesia / quote:** `font-style: italic` · `line-height: 1.65–1.80` · peso 400
- **MAI:** font esterni non dichiarati nel tema Shopify TM04

### 12.3 Componenti UI BKS standard

| Componente | Regola |
|---|---|
| Button primario | `background: colore-collezione; color: #0A0A0A; border-radius: 2px; letter-spacing: 0.14em` |
| Button secondario | `background: transparent; border: 0.5px solid rgba(255,255,255,0.24); color: rgba(255,255,255,0.70)` |
| Input text | `background: rgba(255,255,255,0.04); border: 0.5px solid rgba(255,255,255,0.14); border-radius: 2px; padding: 10px 14px` |
| Card | `border: 0.5px solid rgba(255,255,255,0.08); border-radius: 4px; background: rgba(255,255,255,0.02)` |
| Divider | `0.5px solid rgba(255,255,255,0.07)` |
| Badge / pill | `border-radius: 2px; font-size: 9px; letter-spacing: 0.18em; text-transform: uppercase` |

### 12.4 Tone of voice per la piattaforma Verse

| Cosa comunicare | Tone |
|---|---|
| Submission ricevuta | Sobrio, rispettoso: "We have your verse." |
| Approvazione | Riconoscente, non enfatico: "Your verse has been selected." |
| Rifiuto | Onesto, mai apologetico: "Not selected. The standard is high." |
| Chat | Diretto, letterario. Niente emoji. Punteggiatura esatta. |
| Drop announcement | Editoriale. La poesia parla prima del prodotto. |

### 12.5 Gate stile prima di ogni deploy

Prima di deployare qualsiasi UI legata a BKS Verse, verificare:
- [ ] Palette rispettata (§12.1)
- [ ] Tipografia da tema TM04 (§12.2)
- [ ] Componenti UI standard (§12.3)
- [ ] Tono editoriale (§12.4)
- [ ] Mobile-first: touch target min 48px, input leggibile su 375px

---

---

## 13. IL FILO — POESIA ATTRAVERSO IL TEMPO

### Concept

Quando una poesia supera il gate (≥20/25), il Gran Giudice identifica l'**antenato poetico** tra i 21 poeti storici nell'archivio. Il poeta storico "ringrazia" il membro attraverso il tempo. Inversione della prospettiva tradizionale: non il membro si ispira al maestro, ma il maestro riconosce il membro.

### Meccanismo operativo

1. Il Giudice approva il verso
2. `lineage.py` → OpenAI identifica il poeta dell'archivio più affine
3. Viene generata la **Lineage Card** (mostrata nel dashboard membro)
4. Viene generato lo **Storyboard reel** via `/reel/storyboard/{id}`

### Lineage Card (formato)

```text
[NOME POETA · ERA · CITTÀ]
"estratto poesia storica"
  ↓  [N anni dopo]
"verso del member BKS"

Il Giudice: "[il poeta storico] avrebbe riconosciuto questo sguardo."
```

### I 21 poeti nell'archivio (con score BKS)

| Poeta | Paese | Anno | Score |
|---|---|---|---|
| e.e. cummings | US | 1894–1962 | **25/25** |
| Ungaretti "M'illumino" | IT | 1888–1970 | **25/25** |
| Celan | DE | 1920–1970 | 24/25 |
| Rilke | AT | 1875–1926 | 24/25 |
| Rimbaud | FR | 1854–1891 | 24/25 |
| Ungaretti "Soldati" | IT | 1888–1970 | 24/25 |
| Lorca | ES | 1898–1936 | 23/25 |
| Basho | JP | 1644–1694 | 23/25 |
| Plath | US | 1932–1963 | 22/25 |
| Ginsberg | US | 1926–1997 | 21/25 |
| Dickinson | US | 1830–1886 | 21/25 |
| Montale | IT | 1896–1981 | 20/25 |
| Neruda | CL | 1904–1973 | 20/25 |
| Szymborska | PL | 1923–2012 | 20/25 |
| Leopardi | IT | 1798–1837 | 19/25 |
| Bukowski | US | 1920–1994 | 19/25 |
| Rumi | IR | 1207–1273 | 19/25 |
| Whitman | US | 1819–1892 | 18/25 |
| Cavafy | GR | 1863–1933 | 18/25 |
| Saffo | GR | 630–570 a.C. | 23/25 |
| Pasolini | IT | 1922–1975 | 22/25 |

---

## 14. CLASSIFICA MONDIALE — LEADERBOARD

### Concept

Una singola classifica che mette sullo stesso piano i poeti storici e i members BKS, usando **la stessa rubrica del Gran Giudice**. Un member Gold può battere Leopardi (19/25) se ottiene 20+. Non è irriverente — è la logica del sistema applicata con coerenza.

### Endpoint API

- `GET /leaderboard/global` → classifica unificata poeti + members
- `GET /leaderboard/hall` → solo 25/25 storici + members Hall

### UI Shopify

- **Pagina:** `bakabo.club/verse` → sezione leaderboard sotto il form di submit
- **Template:** `page.bks-verse.json` → include `bks-verse-leaderboard.liquid`
- **Colori:** storico = oro scuro, member = bianco/argento, hall = oro brillante

### Valore commerciale

La classifica è un motore di engagement che:
- Genera dibattito ("Leopardi 19/25 — corretto?")
- Motiva i members a superare i propri score precedenti
- È condivisibile su social (screenshot personale con la propria posizione)
- Attira letterati e accademici che trovano il progetto stimolante

---

## 15. TIKTOK — SERIE "IL GIUDICE ESAMINA"

### Concept

Una poesia storica famosa viene analizzata dal Gran Giudice in 60 secondi. Il Giudice dà il punteggio. Il dibattito esplode.

### 5 episodi pilota

| Ep | Poeta | Hook | Score | Perché |
|---|---|---|---|---|
| 1 | Ungaretti | "2 parole. Il Giudice le analizza." | 25/25 | Impatto max, zero controversia |
| 2 | Saffo | "2.600 anni fa. Sopravvissuto su papiro." | 23/25 | Distanza temporale massima |
| 3 | Celan | "In tedesco. Da un sopravvissuto." | 24/25 | Oscurità BKS, alta emotività |
| 4 | Rimbaud | "A 19 anni scrisse questo. Poi smise." | 24/25 | Narrativa forte |
| 5 | **Leopardi** | "19/25. Leopardi non passa il gate." | 19/25 | **Massimo dibattito in Italia** |

L'episodio Leopardi è il più controverso. Non moderare. Il Giudice ha ragione: scriveva per l'eternità, non per un tessuto. L'asse Body = 2/5. Spiegarlo crea engagement organico.

### Format reel (60 secondi)

```text
[0-8s]   Luogo e anno del poeta — foto archivio b/n
[8-22s]  Il verso appare parola per parola (typewriter)
[22-26s] "↓ N anni dopo"
[26-40s] BKS aesthetic — eventuale verso member
[40-52s] Score reveal — 5 assi uno a uno (suono macchina da scrivere)
[52-60s] Verdict del Giudice + CTA bakabo.club/verse
```

### Identità del Giudice (voce AI)

Timbro: maschile, lento, asciutto. Spirito di Pasolini — non perdona la banalità, non concede nulla alla moda del momento. Il contrario di un influencer.

---

## 16. SISTEMA OPERATIVO — I:\BAKABO SYSTEM

### Directory

Il motore BKS Verse vive in `I:\BAKABO SYSTEM\` (separato da BAK ABO, il motore principale resta lì).

### File chiave

| File | Funzione |
|---|---|
| `00_START_VERSE.bat` | Avvia API locale :8001 (sviluppo) |
| `01_ADMIN_PANEL.bat` | Pannello approvazione Roberto → localhost:8099 |
| `verse_engine/giudice.py` | Gran Giudice OpenAI |
| `verse_engine/artwork.py` | DALL-E → Printify → Shopify draft (no Make.com) |
| `verse_engine/lineage.py` | Il Filo — antenato poetico |
| `verse_engine/notifications.py` | Discord + Telegram + Email |
| `scripts/init_db.py` | Crea DB SQLite + carica 21 poeti |
| `scripts/deploy_shopify.py` | Deploy sezioni liquid → TM04 |
| `scripts/server_setup.sh` | Setup Hetzner CX22 (bash) |
| `cloudflare/worker.js` | Proxy pubblico CORS + rate-limit |

### Avvio sistema completo

```text
Sviluppo locale:  00_START_VERSE.bat → :8001
Produzione:       server Hetzner → verse.bakabo.club → Cloudflare Worker → :8001
Admin:            01_ADMIN_PANEL.bat → localhost:8099
Deploy Shopify:   python scripts/deploy_shopify.py
```

### Costi (definitivi)

€354/anno = €29.50/mese. Nessun Make.com. Controllo totale.

---

*Skill aggiornata dopo ogni drop completato. Fonte di verità operativa per il programma BKS Verse.*
*Architettura v2 — Luglio 2026: senza Make.com, server Hetzner, Il Filo, Leaderboard, TikTok.*
