---
name: bakabo-business
description: Use this skill for all economic, pricing, margin, and business decision-making for BKS Studio. Triggers include: setting or reviewing a product price, calculating margins, evaluating profitability of a new product category, deciding minimum viable price, planning a promotion or discount, analyzing Printify cost structure, comparing fulfillment options by cost, evaluating break-even on a new category, forecasting revenue from a drop, or any question about the financial health of the brand. Also use when auditing the Cozy Slipper pricing anomaly (retail below cost+shipping) or deciding whether a product is commercially viable beyond the aesthetic scoring. Works alongside bakabo-product-copy (copy output), bakabo-printify-sync (cost inputs), bakabo-shopify-ops (markets/shipping). Never price a product without consulting this skill first.
---

# BKS Studio — Business, Pricing & Margin Skill
## Skill v1 — Giugno 2026

Sistema economico completo per BKS Studio / bakabo.club. Copre: struttura costi Printify, calcolo margini, pricing strategy, psicologia del prezzo, break-even, valutazione commerciale prodotti, analisi per drop, KPI economici.

---

## 1. Modello di business — struttura

BKS Studio opera come **AI-art atelier print-on-demand**. Ogni prodotto viene stampato solo dopo l'ordine (made-to-order). Non c'è magazzino, non c'è overstock, non c'è capitale immobilizzato in scorte.

### Catena del valore

```
Roberto (design + cura) → Printify (produzione + spedizione) → Cliente finale
```

### Conseguenze economiche del modello MTO

| Fattore | Impatto |
|---|---|
| Nessuna scorta | Zero rischio invenduto |
| Produzione post-ordine | Costo variabile puro — nessun costo fisso di produzione |
| Lead time 7-14 gg | Accettabile nel segmento accessible designer |
| Resi | Ogni reso è un costo pieno — il pezzo stampato non si rivende |
| Scalabilità | Infinita in teoria — il limite è il sell-through, non la capacità produttiva |

---

## 2. Struttura dei costi — Printify

### Costo totale per prodotto = Base Cost + Shipping Cost

**Base Cost** = costo di stampa e produzione comunicato da Printify per prodotto e provider.

**Shipping Cost** = varia per:
- Provider (MWW On Demand, Smart Printee, ecc.)
- Destinazione (EU, US, resto del mondo)
- Peso/dimensione prodotto

### Costi indicativi per categoria (valori di riferimento — verificare sempre in Printify prima del pricing)

| Categoria | Base Cost indicativo | Note |
|---|---|---|
| Sneakers | €18–26 | Provider: Smart Printee |
| Backpack | €22–30 | Provider: MWW |
| Swim Trunks | €14–20 | Provider: MWW |
| Puffer Jacket | €38–55 | Costo più alto — margine sensibile |
| Windbreaker | €28–38 | Provider: MWW |
| Travel Bag/Duffle | €30–42 | Provider: MWW |
| One-Piece Swimsuit | €18–24 | Provider: MWW |
| Hawaiian Shirt | €20–28 | Provider: MWW |
| Lounge Pants (W) | €16–22 | Provider: MWW |
| Pullover Hoodie | €24–32 | Provider: MWW |
| Racerback Dress | €20–28 | Provider: MWW |
| Cozy Slipper | €12–18 | **ALERT: verificare vs retail** |
| Cut & Sew Tee | €16–22 | Provider: MWW |
| Athletic Shorts | €14–20 | Provider: MWW |
| Flip Flops | €10–16 | Provider: MWW |

### Shipping indicativo EU (aggiungere al base cost)

| Peso prodotto | Costo spedizione EU indicativo |
|---|---|
| Leggero (<500g): tee, shorts, slipper | €4–7 |
| Medio (500g–1kg): hoodie, swimwear | €6–10 |
| Pesante (>1kg): sneakers, bag, puffer | €8–14 |

**REGOLA CRITICA:** Costo totale reale = Base Cost + Shipping EU. Il pricing deve coprire entrambi con margine.

---

## 3. Target di margine BKS Studio

### Margine lordo target

| Livello | Margine % su prezzo vendita | Quando applicare |
|---|---|---|
| **Minimo assoluto** | 45% | Prodotti con alta concorrenza di prezzo o bassa ASP |
| **Target standard** | 55–65% | La maggior parte dei prodotti BKS |
| **Target premium** | 65–75% | Prodotti con forte identità BKS, bassa sostituibilità |
| **Non pubblicare** | <40% | Il prodotto non è economicamente sostenibile |

### Formula margine

```
Margine % = (Prezzo Vendita - Costo Totale) / Prezzo Vendita × 100

Costo Totale = Base Cost Printify + Shipping Cost (media EU)
```

### Esempio calcolo

```
Sneakers:
Base Cost: €22
Shipping EU: €10
Costo Totale: €32

Target margine 60%:
Prezzo Vendita = €32 / (1 - 0.60) = €80

Check: (€80 - €32) / €80 = 60% ✓
```

---

## 4. Pricing strategy BKS Studio

### Principi

**1. Prezzi round numbers o .95** — Mai .99 (scadente per posizionamento editoriale). Mai cifre dispari come €73 o €88.

Formato approvato: €45 · €55 · €65 · €75 · €85 · €95 · €105 · €115 · €125 · €135

**2. Price anchoring per collezione** — All'interno di una collezione, lo stesso design su categorie diverse deve mantenere coerenza di posizionamento. Un cliente che compra la sneaker non deve trovare la hoodie dello stesso design a un prezzo incoerente.

**3. No sconti permanenti** — I saldi cronici distruggono il posizionamento accessible designer. Promozioni solo per drop launch (max 15% per 48h) o per liquidazione end-of-season.

**4. Free shipping threshold** — Impostato per ogni mercato in Shopify Markets. Non hardcodato in copy. Target: soglia che spinge AOV senza essere irraggiungibile.

### Price ladder BKS per categoria

| Categoria | Prezzo minimo | Prezzo target | Prezzo premium |
|---|---|---|---|
| Flip Flops | €35 | €45 | €55 |
| Cozy Slipper | €35 | €45 | €55 |
| Swim Trunks | €45 | €55 | €65 |
| Athletic Shorts | €45 | €55 | €65 |
| Cut & Sew Tee | €45 | €55 | €65 |
| One-Piece Swimsuit | €55 | €65 | €75 |
| Racerback Dress | €55 | €65 | €75 |
| Lounge Pants | €55 | €65 | €75 |
| Hawaiian Shirt | €65 | €75 | €85 |
| Pullover Hoodie | €65 | €75 | €85 |
| Backpack | €75 | €85 | €95 |
| Sneakers | €75 | €89 | €105 |
| Duffle/Travel Bag | €85 | €99 | €115 |
| Windbreaker | €95 | €109 | €125 |
| Puffer Jacket | €109 | €125 | €139 |

---

## 5. Alert pricing — Cozy Slipper

**PROBLEMA IDENTIFICATO IN SESSIONE:** Il prezzo di default Printify per Cozy Slipper era $16.16 — sotto il costo totale inclusa spedizione.

**Azione richiesta su ogni nuovo prodotto Cozy Slipper:**
1. Verificare base cost attuale in Printify
2. Aggiungere shipping cost EU medio (€5-7)
3. Applicare target margine 55%
4. Arrivare a prezzo pubblicato ≥€35

**Formula rapida slipper:**
```
Se base cost = €12, shipping = €6 → costo totale = €18
Margine 55%: prezzo = €18 / 0.45 = €40 → arrotondare a €39 o €45
```

---

## 6. Valutazione commerciale prodotto (business layer)

Il scoring estetico (21-25/25) è necessario ma non sufficiente. Ogni prodotto approvato esteticamente deve superare anche il business check.

### Business check — 4 domande

**Q1: Il margine regge?**
Calcola costo totale → applica target margine → il prezzo risultante è compatibile con la price ladder della categoria? Se il prezzo necessario è sopra il massimo della categoria, il prodotto è fuori range.

**Q2: C'è un mercato sufficiente?**
La categoria ha già prodotti simili su Etsy, Redbubble, competitor diretti? BKS compete su identità visiva forte, non su prezzo. Se il pattern è generico (beachwear standard, stripe, floral), la competizione abbassa il prezzo praticabile.

**Q3: Il costo di reso erode il margine?**
Prodotti con alta probabilità di reso (taglie difficili, prodotti indossabili con fit critico) devono avere margine ≥60%. Ogni reso su MTO è un costo pieno non recuperabile.

**Q4: Il volume potenziale giustifica l'energia?**
Categorie con mercato piccolo (es. Cozy Slipper) richiedono meno prodotti, non di più. Meglio 2 prodotti forti che 10 mediocri.

### Schema decisione finale prodotto

```
Scoring estetico ≥ soglia?
  NO → DRAFT
  SÌ ↓

Business check OK (Q1-Q4)?
  NO → DRAFT con nota "business fail"
  SÌ ↓

APPROVATO → procedere con scheda Printify + Shopify
```

---

## 7. Analisi break-even per drop

Prima di ogni drop, calcolare:

```
Break-even unità = Costi fissi drop / Margine unitario medio

Costi fissi drop:
- Ore lavoro Roberto (valorizzare)
- Eventuale costo foto (OpenAI API, shoot)
- Costo Suno tracce audio (se generato per il drop)
- Costo app e abbonamenti mensili (pro-rata)

Margine unitario medio = media margini assoluti sui prodotti del drop

Es:
Costi fissi drop: €200 (API + lavoro valorizzato)
Margine unitario medio: €35
Break-even: €200 / €35 = 6 ordini per coprire i costi del drop
```

---

## 8. KPI economici — monitoraggio

### Mensile

| KPI | Target | Alert |
|---|---|---|
| **AOV (Average Order Value)** | >€75 | <€60 |
| **Margine lordo medio** | >58% | <50% |
| **Return rate** | <8% | >15% |
| **Revenue per sessione** | >€1.5 | <€0.8 |

### Per prodotto (dopo 30 gg live)

| KPI | Target | Azione se sotto |
|---|---|---|
| **Conversion rate prodotto** | >2% | Audit prezzo, foto, copy |
| **Add-to-cart rate** | >8% | Audit prezzo, prima immagine |
| **Return rate** | <10% | Audit fit guide, taglia |

---

## 9. Strategie di crescita ricavi — priorità

**1. AOV uplift via bundle** — "Completa il look": sneaker + backpack della stessa collezione. Cross-sell automatico in cart e post-purchase email. Target: +20% AOV.

**2. Free shipping threshold** — Impostare la soglia a AOV attuale + 20% per creare pressione all'aggiunta. Es. AOV €75 → soglia €89.

**3. Member area come leva margine** — bks-archive ha accesso early. L'early access riduce la competizione su prezzo (il cliente compra prima che altri vedano). Preserva margine pieno.

**4. Drop scarcity pricing** — I primi 48h del drop possono avere prezzo pieno. Dopo 30 gg, eventuale -10% su prodotti lenti. Mai -20% o più.

**5. Capsule capsule dual-product** — Stesso pattern su due categorie (es. Glyph Quill: swim trunk + puffer). L'acquirente del trunk può tornare per il puffer. Costo acquisizione zero.

---

## 10. Struttura commissioni e costi fissi operativi

### Ricorrenti mensili (verificare sempre prezzi aggiornati)

| Voce | Costo indicativo/mese | Note |
|---|---|---|
| Shopify Basic/Grow | €29–79 | Verificare piano attivo |
| Printify Premium | €24 | Riduce base cost ~20% — quasi sempre conveniente |
| ParcelPanel | €9–19 | Piano traffico-based |
| Judge.me / Tydal | €0–15 | **ALERT: entrambi attivi — audit pendente** |
| Google Fonts | €0 | Incluso |
| OpenAI API | variabile | ~$0.08 per foto verifica, $0.04–0.20 per generazione |
| Suno | variabile | Verificare piano attivo per commercial rights |
| Claude Pro | €20 | Piano Roberto |

### Printify Premium — convenienza

**Printify Premium riduce il base cost di ~20%.** A €24/mese:
```
Break-even Premium:
Se margine medio per prodotto = €35, risparmio Premium = €4-5 per prodotto
Break-even: €24 / €4.5 = ~5-6 ordini/mese
Con 10+ ordini/mese Premium è obbligatorio.
```

---

## 11. Posizionamento prezzo vs competitor

| Brand competitor | Fascia | Note |
|---|---|---|
| Redbubble / Teepublic | €20–45 | Commodità totale — non competiamo qui |
| ASOS Print labels | €35–60 | Fast fashion — non competiamo qui |
| Études Studio | €80–200 | Aspirazionale — riferimento visivo |
| Daily Paper | €60–150 | Segmento target — siamo allineati |
| Drôle de Monsieur | €70–180 | Leggermente sopra BKS — buon benchmark |
| Carhartt WIP | €50–130 | Benchmark per accessori |

**Posizione BKS:** fascia €45–140, con identità AI-art come differenziatore primario (non il prezzo).

---

## 12. Regola d'oro BKS Business

> **Mai pubblicare un prodotto senza aver calcolato il margine.**
> Se il margine non è ≥45%, o si rinegozia il prezzo (rialzo) o il prodotto va in draft.
> Il brand si costruisce sulla qualità editoriale, non sul volume a basso margine.

---

## 13. Integrazione con le altre skill

| Skill | Come si collega |
|---|---|
| `bakabo-printify-sync` | Fornisce il base cost — input primario per calcolo margine |
| `bakabo-product-copy` | Riceve il prezzo approvato e lo include nel data table Shopify |
| `bakabo-shopify-ops` | Gestisce free shipping threshold per mercato |
| `bakabo-growth` | Usa i KPI economici per segmentare i clienti (AOV, ordini, LTV) |
| `bakabo-brand` | Il pricing non deve mai comunicare urgency o scarsità falsa |
