---
name: bakabo-growth
description: Use this skill for all CRM, email marketing, customer segmentation, member area design, loyalty/referral mechanics, and conversion funnel work for bakabo.club. Triggers include writing email flows (welcome, post-purchase, re-engagement, VIP), designing the member area pages and tier system (bks-subscriber / bks-drop / bks-archive), planning the UGC gallery, reviews strategy, wishlist, referral program, or any question about converting the existing 32 Shopify customers. Also use when analyzing customer segments, planning the loyalty tier strategy, or deciding what to send to which segment. Works alongside bakabo-brand (voice — no exclamation marks, no urgency tactics), bakabo-shopify-ops (Flow automation, Shopify mechanics), and bakabo-pages-design (page structure). Always apply bakabo-brand voice to all copy produced.
---

# BakAbo — Growth, CRM & Member Area

This skill covers everything between "someone created an account" and "they become a loyal BKS Archive customer": email flows, segmentation, member area pages, social proof mechanics, wishlist, referral, and loyalty tier logic.

Two constraints shape every decision here:
1. **Brand voice from `bakabo-brand`** — editorial, cool, no urgency, no exclamation marks, no emoji in body copy. These rules apply to email subject lines too.
2. **Scale honesty** — BakAbo has 32 customers in June 2026. Don't over-engineer. Manual gestures beat automations at this scale. Build for 200 customers, not 2000.

---

## 1. Customer base — stato reale (giugno 2026)

Reference data from Shopify. Always use this before making any CRM recommendation.

| Segmento Shopify | N | % | Azione prioritaria |
|---|---|---|---|
| Email subscriber | 12 | 38% | Welcome flow — P1 immediata |
| 1+ acquisti | 2 | 6% | Post-purchase flow + VIP treatment |
| 2+ acquisti | 1 | 3% | Renato Tedeschi — BKS Archive manuale |
| Abandoned checkout (30gg) | 0 | 0% | Drop pre-checkout → fix PDP, non email |
| Mai acquistato | 30 | 94% | Prima conversione è il problema |

**Insight core:** zero abandoned checkout non è un segnale positivo — significa che il drop avviene sulla product page prima che il cliente arrivi al checkout. Il problema è la PDP e la chiarezza del made-to-order, non il recovery email.

**Clienti con nome e valore:**
- **Renato Tedeschi** (ES) — 2 ordini, €246, subscriber → BKS Archive, il primo superfan
- **Marita Sheshaberidze** (US) — 1 ordine, €94, non subscriber → BKS Drop, warm target per secondo acquisto

---

## 2. Segmenti operativi

Quattro segmenti da gestire. Non inventarne altri finché la base non supera i 200 clienti.

### Segmento A — BKS Archive (tag: bks-archive)
Attualmente: 1 cliente (Renato). Chi ha 2+ ordini.
**Trattamento:** gesto umano > automazione. Email personale dal fondatore. Accesso BKS Studio Archivio. Free shipping permanente.

### Segmento B — BKS Drop (tag: bks-drop)
Attualmente: 1 cliente (Marita). Chi ha 1 ordine.
**Trattamento:** post-purchase flow automatico. Focus sul secondo acquisto.

### Segmento C — BKS Subscriber (tag: bks-subscriber)
Attualmente: ~12 clienti. Newsletter iscritti, 0 ordini.
**Trattamento:** welcome flow 3 email in 7 giorni. Priorità assoluta.

### Segmento D — Dormant (senza tag)
Attualmente: ~20 account. Zero email di marketing, zero acquisti.
**Trattamento:** 1 sola email di re-engagement. Se nessuna apertura in 30 giorni → suppression list. Non offrire sconti.

---

## 3. Email flows — struttura e copy

### Regole voce per tutte le email
- Soggetto: sotto 50 caratteri, nessun punto esclamativo
- Corpo: sotto 150 parole per email automatiche
- Nessuna emoji nel body
- Nessuna urgency ("ultimi pezzi", "offerta scade") — mai per BakAbo
- Firma: "— BKS Studio" o "— [nome fondatore], BKS Studio"
- Nessun coupon nelle prime 3 email del welcome flow — non svalutare il brand

### 3.1 Welcome flow (Segmento C — subscriber, 0 ordini)

**Email 1 — immediata — "BKS Studio — di cosa si tratta"**
```
Soggetto: BKS Studio — di cosa si tratta

Ciao,

BKS Studio è un atelier digitale che produce arte indossabile.

Ogni stampa nasce da un processo AI guidato da una libreria di riferimenti
artistici — Neo-Espressionismo, Optical, Brut, e altri. Progettiamo, curiamo,
selezioniamo. Poi stampiamo dopo il tuo ordine: nessun magazzino, nessun invenduto.

Questo è il modello. Non è un brand di moda. È uno studio grafico che ha imparato
a fare capi.

Le collezioni sono qui →

— BKS Studio
```

**Email 2 — giorno 3 (se orders_count = 0) — processo AI**
```
Soggetto: Come nasce un pattern BKS

Ogni stampa inizia da un prompt.

Lo studio mantiene una libreria di riferimenti artistici — movimenti, autori,
tecniche. Da quella libreria nascono le istruzioni per il modello AI. Il risultato
viene selezionato a mano: la maggior parte non passa.

Quello che vedi sul sito è ciò che ha superato la selezione.

Vedi le collection →

— BKS Studio
```

**Email 3 — giorno 7 (se orders_count = 0) — le collection**
```
Soggetto: Tre collection da conoscere

BKS Hours — città, luce, silhouette. La collection più adulta.
BKS Glyph — simboli, codici, alfabeto visivo del brand.
BKS Riviera — resort mediterraneo, estate permanente.

Tutte e otto le collection →

— BKS Studio
```

### 3.2 Post-purchase flow (Segmento B — bks-drop)

**Email 1 — giorno 7 post-consegna — "Come ti veste?"**
```
Soggetto: Come ti veste?

Ciao,

Il tuo ordine è arrivato da qualche giorno.

Se ti va, ci piacerebbe vederlo. Una foto, un tag su Instagram (@bksstudio) —
lo condividiamo nella nostra gallery clienti.

E se vuoi lasciare una recensione, ci aiuta più di qualsiasi campagna.

— BKS Studio
```

**Email 2 — giorno 14 — cross-sell (1 prodotto stessa collection)**
```
Soggetto: Dalla stessa collection

Hai acquistato da [nome collection]. Questo va con quello che hai scelto.

[Nome prodotto] →

— BKS Studio
```

### 3.3 VIP — email manuale per BKS Archive

Questa email non è automatizzata. Va scritta e inviata a mano per ogni nuovo BKS Archive.

```
Soggetto: Sei il primo BKS Archive.

[Nome],

Hai acquistato due volte. Sei il primo cliente ad arrivare a questo livello.

Da adesso hai accesso permanente alla sezione BKS Studio — il processo AI,
i pattern scartati, la libreria prompt. Non è ancora completa, ma cresce
con ogni drop.

Free shipping permanente è già attivo sul tuo account.

Grazie — sul serio.

— [nome fondatore], BKS Studio
```

### 3.4 Re-engagement dormant

```
Soggetto: Ci sei ancora?

Qualche tempo fa hai creato un account su bakabo.club.

Se non hai trovato quello che cercavi, siamo curiosi di sapere perché.
Se invece hai voglia di guardare cosa c'è di nuovo:

Le collection →

— BKS Studio
```

---

## 4. Member area — pagine e struttura

La member area è un layer di contenuto accessibile dopo login. Non è un portale separato — è il tema Shopify con sezioni condizionali via tag Liquid.

### Pagine della member area

**Dashboard account** (`/account/`)
- Saluto con nome + tier attuale ("Sei BKS Drop")
- Banner upgrade tier se applicabile ("Ancora 1 ordine per diventare BKS Archive")
- Shortcut contestuali: Traccia ordine · Wishlist · Early access
- Nessun feed promozionale inline

**I miei ordini** (`/account/orders`)
- Lista ordini con thumbnail + stato MTO: In produzione · Stampato · Spedito · Consegnato
- Tracker timeline visivo per ordini in corso
- Link ParcelPanel per ordini spediti
- CTA "Riacquista" su ordini consegnati
- CTA "Scrivi recensione" (solo bks-drop e bks-archive, via Judge.me) — appare 7 giorni dopo consegna

**Wishlist** (disponibile da bks-subscriber)
- Grid prodotti salvati con add-to-cart diretto
- Condivisione wishlist via link (uso gifting)
- Se vuota: 3 suggerimenti da Hours o Glyph

**Early access drops** (disponibile da bks-subscriber)
- Pagina `/pages/early-access` con controllo Liquid sul tag
- Teaser drop successivo: nome · visual · data
- Per bks-archive: accesso +24h prima del lancio pubblico
- Archivio drops passati con link a collection

**BKS Studio Archivio** (solo bks-archive)
- Pagina `/pages/bks-studio` con controllo Liquid `bks-archive`
- Prompt library parziale (non l'intera library — abbastanza da mostrare il processo)
- Galleria pattern generati non usati in produzione ("gli scarti che ci piacciono")
- Process notes: 1 nota per ogni drop su come è stato costruito
- Download wallpaper: pattern AI in alta risoluzione per uso personale

**Referral** (disponibile da bks-subscriber)
- Link referral personale
- Meccanica: €10 credito per chi porta + €10 per chi arriva al primo ordine
- Dashboard: link cliccati · conversioni · crediti

**Profilo** (`/account/`)
- Nome · email · password
- Indirizzi con etichette
- Preferenze newsletter IT/EN
- Export dati (GDPR art. 20) + cancellazione account (GDPR art. 17)
- Tier attuale con progress bar verso il prossimo

---

## 5. Social proof — strategia

### Reviews (Judge.me — già installato)
- Non configurare il widget "richiesta automatica" di Judge.me — usare il Flow post-purchase per controllare timing e tono
- Target review rate: >8% degli ordini
- Risposta brand obbligatoria entro 48h — voce editoriale BKS, mai difensiva
- Stelle medie + conteggio visibile sulla PDP come anchor al reviews widget
- Non filtrare le recensioni basse — trasparenza = fiducia

### UGC gallery ("As worn")
- Trigger: hashtag #BKSStudio su Instagram o upload diretto
- Tag prodotto su ogni foto → link diretto al PDP
- CTA nell'email post-purchase: "Condividi il tuo look"
- Trasparenza: "Foto condivise dai nostri clienti con il loro consenso"

---

## 6. Loyalty / Referral — meccanica

Regola brand: nessun countdown, nessuna urgenza, nessun "offerta scade alle 23:59".

**Punti:** 1€ speso = 1 punto. 100 punti = €5 di credito. Punti extra per: recensione con foto (+5 punti), primo acquisto (+20 punti), referral convertito (+50 punti).

**Referral:** link personale generato automaticamente per ogni bks-subscriber. €10 credito per chi porta, €10 per chi arriva. Crediti non scadono entro 12 mesi.

**Implementazione ora:** tutto manuale via metafield cliente Shopify. Scalare a LoyaltyLion o Smile.io quando si superano i 50 acquirenti.

---

## 7. Conversion diagnostics — cosa guardare prima delle email

Prima di investire in email flows, verificare che questi elementi siano a posto sulla PDP:

1. **Made-to-order lead time visibile PRIMA del add-to-cart** — non come sorpresa al checkout
2. **Stelle medie visibili** sulla collection page (card hover) e sulla PDP (anchor alle recensioni)
3. **Size guide accessibile** — link prominente vicino al selettore taglia
4. **Gallery con 5+ immagini** — il cliente non compra senza vedere il prodotto indosso
5. **Descrizione chiara** — il brand voice deve essere riconoscibile, non generica

Il fatto che ci siano 0 abandoned checkout (vs 30 clienti che non hanno mai comprato) indica che il problema è pre-checkout. Fix la PDP prima di costruire email di recupero carrello.

---

## 8. Metriche da monitorare (CRM)

| Metrica | Target | Come misurare |
|---|---|---|
| Welcome flow open rate | >40% | Shopify Email / Klaviyo |
| Welcome flow conversion | >2 ordini / 30gg | Shopify Orders |
| Post-purchase review rate | >8% ordini | Judge.me dashboard |
| Wishlist-to-cart conversion | >15% | Shopify Analytics |
| Referral conversion rate | >10% link cliccati | metafield manuale |
| Repeat purchase rate | >30% entro 90gg | Shopify Segments |

---

## 9. Stack attuale (giugno 2026)

| Tool | Ruolo | Note |
|---|---|---|
| Shopify Flow | Automazioni tier + email trigger | Nativo, zero costo |
| Shopify Email | Invio email (incluso nel piano) | OK fino a ~500 subscriber |
| Judge.me | Raccolta e display recensioni | Già installato |
| ParcelPanel | Order tracking | Core per MTO |
| Printify | Produzione on-demand | Vedi bakabo-printify-sync |

Non aggiungere app finché la base clienti non giustifica il costo. Ogni app è: costo mensile + performance hit + nuovo data processor da dichiarare in Privacy policy.
