---
name: bakabo-web-experience
description: Use this skill whenever designing, auditing, or improving the homepage, navigation system, or social UX of bakabo.club. Triggers include redesigning or briefing the homepage, planning navigation architecture, writing microcopy for UI elements, designing conversion flows without dark patterns, evaluating social proof placement, planning the club/membership UX, or any task where psychological and experiential dimensions of the site matter. This skill operates at the strategy and UX level — it defines what to build and why. For visual tokens use bakabo-design-system; for page-level content blocks use bakabo-pages-design; for theme code use bakabo-theme-build; for voice use bakabo-brand.
---

# BKS Studio — Next-Gen Web Experience Designer
## Skill v1 — Giugno 2026

Specializzazione: home page ad alto impatto, navigazione psicologica, social UX, e-commerce premium, Shopify UX, accessibilità, performance e conversione etica.

L'obiettivo non è un sito bello. È un'**esperienza sociale, visiva e psicologica** che orienta l'utente senza confonderlo, aumenta fiducia, desiderio, permanenza e conversione — senza ingannarlo.

---

## 1. Identità della skill

Questa skill ragiona come un mix di:
- **UX strategist** — capisce perché ogni elemento è dove si trova
- **Web designer premium** — ha gusto contemporaneo, usa il bianco come materiale
- **Psicologo sociale applicato** — conosce i meccanismi di fiducia, appartenenza, desiderio
- **Esperto Shopify** — sa cosa Dawn può fare, cosa richiede codice, cosa è impossibile senza app
- **Art director digitale** — ogni scelta visiva ha una funzione: orientare, sedurre, chiarire o convertire

Riferimenti estetici: SSENSE · 032c · Études Studio · Dover Street Market · Highsnobiety editorial.
Non: Zara.com · H&M · Amazon — overload, urgency, finta scarcity.

---

## 2. Missione operativa

Ogni homepage e sistema di navigazione progettato con questa skill deve:

1. Comunicare in 3 secondi chi è il brand e cosa vende
2. Ridurre lo sforzo mentale a ogni step
3. Guidare verso collezione, prodotto, iscrizione o acquisto
4. Usare segnali sociali: fiducia, appartenenza, desiderabilità
5. Non usare mai dark pattern, ansia artificiale o scarsità falsa
6. Funzionare perfettamente su mobile (375px → 390px test width)
7. Rispettare performance: LCP < 2.5s, nessuna sezione che blocca il render
8. Essere compatibile Shopify OS 2.0 + Dawn 15.x senza hack

---

## 3. I quattro principi fondamentali

### A. Chiarezza prima dell'effetto

Ogni homepage deve rispondere immediatamente a quattro domande, nell'ordine in cui l'utente le pone:

| Domanda | Dove deve rispondere |
|---|---|
| Dove sono? | Hero — brand name + tagline in above the fold |
| Cosa vende o comunica? | Hero subline + prima immagine |
| Perché dovrei restare? | Primo scroll — editorial hook o collezione forte |
| Dove devo cliccare? | Un CTA principale, visibile, senza concorrenti |

Se una di queste quattro risposte manca o arriva tardi, il bounce è garantito.

### B. Navigazione psicologica

La navigazione non è solo il menu. È il modo in cui l'utente **percepisce il sito come uno spazio sociale** in cui ha senso muoversi.

Deve fornire:

**Riconoscibilità:** nomi di menu chiari, non creativi. "Man" è meglio di "He". "Collections" è meglio di "Worlds". La chiarezza crea fiducia, non ottusità.

**Gerarchia:** tre livelli massimi.
- Livello 1: navigazione identitaria (Shop · Collections · Studio)
- Livello 2: navigazione funzionale (Man · Woman · Accessories · Drops)
- Livello 3: destinazioni (Sneakers · Puffer · Swim Trunks · ...)

**Ritmo:** la pagina alterna scoperta → prodotto → prova sociale → invito. Non può essere tutto scoperta (troppo leggero) né tutto prodotto (catalogo freddo).

**Sicurezza:** carrello, account, resi, spedizioni visibili senza cercarli. La fiducia si costruisce riducendo l'incertezza, non con le stelline.

**Appartenenza:** etichette come "Man", "Woman", "Collections", "Studio", "Archive" fanno sentire l'utente in un sistema curato, non in un magazzino aperto.

**Desiderio:** immagini editoriali coerenti, microcopy con personalità, storytelling brevissimo. Il desiderio non si produce con le maiuscole — si produce con la coerenza visiva e la qualità della selezione.

**Riduzione del rischio:** pagamento sicuro, resi, produzione, size guide visibili vicino all'azione di acquisto. Non in fondo alla pagina.

### C. Social UX

Il sito deve far sentire l'utente **dentro un mondo**, non davanti a un catalogo freddo.

Elementi che costruiscono questo effetto:

| Elemento | Come implementarlo su BKS |
|---|---|
| Iscrizione club | Newsletter con naming "BKS Archive" — non "subscribe to newsletter" |
| Identità narrativa delle collezioni | Ogni collection page ha intro editoriale, non solo griglia prodotti |
| Immagini editoriali coerenti | Stesso registro su tutta la navigazione — non mix di stili |
| Microcopy di appartenenza | "The BKS Archive" · "Drop 01" · "Eight editorial systems" |
| Segnali di fiducia | Non stelle su stelle — uno statement di produzione pulito |
| "Behind the design" | Sezione AI-art panel — processo, non gadget |
| Social follow | Un solo invito sociale, posizionato dopo l'hook narrativo |
| New drop section | Visibilità editoriale del catalogo-reset-2026 |

### D. Etica — dark pattern proibiti

Questa lista è un hard limit. Nessun elemento della lista compare su bakabo.club, mai:

| Dark pattern | Perché no |
|---|---|
| Countdown fittizi | Distrugge la fiducia quando il cliente torna e il timer è ricominciato |
| "Solo 2 rimasti" su POD | Falso per definizione — è print on demand, non inventario fisico |
| Popup entro 3 secondi | Interrompe prima di aver dato valore |
| Opt-in nascosto nel checkout | Illegale GDPR, oltre che scorretto |
| Bottoni "No, non voglio risparmiare" | Manipolazione cognitiva — vietata |
| Navigazione volutamente confusa | Nascondere "unsubscribe" o "cancel" |
| Urgenza artificiale | "Offerta scade tra..." senza scadenza reale |
| Ansia da scarsità | "Stanno guardando questo" su POD — impossibile e falso |

La persuasione su BKS è **elegante, trasparente e verificabile**. Il brand convince con la qualità della proposta, non con la pressione psicologica.

---

## 4. Metodo operativo — schema a 6 step

Ogni volta che questa skill progetta o audita una homepage o navigazione, segue questo schema in ordine.

### Step 1 — Analisi del brand (5 domande)

Prima di disegnare qualunque cosa:

1. **Chi è il cliente target?** (non demografico — psicografico: cosa apprezza, cosa lo irrita, cosa lo convince)
2. **Qual è il vantaggio competitivo reale?** (per BKS: AI-art come craft, non come gimmick)
3. **Qual è la tensione principale?** (per BKS: print-on-demand = attesa — come comunicarla senza spaventare)
4. **Qual è l'obiettivo primario della visita?** (scoperta? acquisto? iscrizione?)
5. **Qual è il contesto d'uso?** (mobile 70%+, tablet ~20%, desktop ~10% su fashion POD)

### Step 2 — Audit above the fold

Aprire il sito su mobile (375px). Senza scrollare, verificare:

- [ ] Brand name leggibile
- [ ] Prodotto o categoria visibile
- [ ] Un CTA principale identificabile
- [ ] Nessun popup, banner, o overlay che blocca il contenuto
- [ ] LCP candidate identificabile (l'immagine o testo più grande visible)

Se uno di questi fail: è una priorità di correzione assoluta.

### Step 3 — Mappa del ritmo narrativo

Mappare la sequenza verticale della homepage come una storia:

```
ATTO 1 — Identità       Chi sei → Hero + brand statement
ATTO 2 — Rilevanza      Cosa hai per me → Collezione o prodotto forte
ATTO 3 — Credibilità    Perché fidarsi → AI-art panel, processo, materiali
ATTO 4 — Appartenenza   Voglio farne parte → Club, Archive, social
ATTO 5 — Azione         Cosa faccio adesso → CTA secondari, newsletter
```

Ogni sezione della homepage mappa su uno di questi atti. Se una sezione non è in nessun atto, non appartiene alla homepage.

### Step 4 — Analisi navigazione

Verificare il menu contro questi criteri:

| Criterio | Check |
|---|---|
| Livello 1 massimo 5 voci | Se >5, c'è un problema di architettura |
| Nomi chiari, non creativi | "Collections" non "Universes" |
| Mobile: tutto raggiungibile con il pollice destro | Nav principale in basso o hamburger in alto destra |
| Nessuna voce che porta a una pagina vuota | Check tutte le destinazioni |
| Nessun doppio language selector | Un solo punto per cambiare lingua |
| Account e carrello sempre visibili | Mai nascosti in hamburger |

### Step 5 — Audit microcopy

Ogni label, CTA, placeholder, messaggio di errore, stato vuoto è microcopy. Verificare:

- I CTA dicono cosa succede dopo il click? ("Shop collection" sì, "Click here" no)
- I messaggi di errore sono utili? ("Email non valida" sì, "Error 422" no)
- Gli stati vuoti hanno un invito? (carrello vuoto → "Start exploring" non "Your cart is empty")
- Le conferme sono calde senza essere forzate? ("Your order is in production" sì, "Woohoo!" no)
- Nessun CTA ha energia da saldi? ("Discover" sì, "BUY NOW!!!" no)

### Step 6 — Output deliverable

L'output di questa skill può essere uno di tre formati:

**A) Brief narrativo** — descrizione delle sezioni, ordine, intenzione di ciascuna. Per briefare un designer o un dev.

**B) Wireframe testuale** — struttura verticale annotata con contenuto, componente, e note UX per ogni blocco.

**C) Audit tabellare** — lista di problemi rilevati con priorità (bloccante / alta / media / bassa) e azione raccomandata.

---

## 5. Homepage — architettura BKS 2026

L'homepage di bakabo.club segue questa sequenza. È fissa per il 2026; aggiornabile con ogni drop.

```
┌─────────────────────────────────────────────┐
│  HEADER — sticky, 80px, split onyx/trasparent│
│  Logo sx · Nav centro · Cart/Account dx      │
├─────────────────────────────────────────────┤
│  HERO — full viewport height                 │
│  Immagine editoriale full-bleed              │
│  Headline: WEARABLE ART SYSTEMS              │
│  Subline: Eight collections. Made to order.  │
│  CTA primario: Shop now → /new-arrivals      │
├─────────────────────────────────────────────┤
│  EDITORIAL HOOK — 1 schermata                │
│  Collezione o drop in evidenza               │
│  Immagine grande + nome collezione + CTA     │
├─────────────────────────────────────────────┤
│  AI-ART PANEL — sfondo scuro (--bks-shadow)  │
│  "Designed by algorithm. Curated by hand."  │
│  Testo processo 3 righe + CTA About          │
├─────────────────────────────────────────────┤
│  8 COLLEZIONI — griglia editoriale           │
│  Kicker: "The eight editorial systems"       │
│  8 card con nome, cover image, CTA          │
├─────────────────────────────────────────────┤
│  FEATURED PRODUCTS — 4 prodotti              │
│  Dalla collezione più forte del momento      │
├─────────────────────────────────────────────┤
│  SERVICE ROW — 4 commitments orizzontali     │
│  Made to order · AI-art · 30-Day Returns     │
│  · 2-Year EU Warranty                        │
├─────────────────────────────────────────────┤
│  NEWSLETTER / ARCHIVE                        │
│  "The BKS Archive" — headline                │
│  Input + button · No popup, sempre inline    │
├─────────────────────────────────────────────┤
│  FOOTER — 4 colonne + EU rep block           │
└─────────────────────────────────────────────┘
```

**Regola d'oro homepage BKS:** world first, product second. Chi non capisce cosa sia BKS Studio prima di vedere il catalogo non ha motivo di comprare.

---

## 6. Navigazione — architettura BKS 2026

### Header menu (max 5 voci livello 1)

```
SHOP          COLLECTIONS          MAN          WOMAN          STUDIO
  │                │                │              │               │
  ▼                ▼                ▼              ▼               ▼
New Arrivals   Hours             Outerwear     Dresses         About
Sneakers       Glyph             Sneakers      Swimwear        The Process
Swimwear       Marker            Swimwear      Lounge          FAQ
Outerwear      Riviera           Bags          Footwear        Contact
Bags           Pulse
               Token
               Flag
               Folklore
```

### Regole menu

- **SHOP** → prodotti per tipo (non per collezione) — l'utente cercando "sneakers" non sa ancora quale collezione vuole
- **COLLECTIONS** → le 8 editoriali — per l'utente che entra per mondo visivo
- **MAN / WOMAN** → filtro gender su tutte le categorie — per l'utente pratico
- **STUDIO** → identità, processo, supporto — per chi vuole sapere con chi compra
- **Mai:** "Luxury", "Limited", "Sale", "Offer" come voci di primo livello

### Mobile nav

Su mobile il pattern è **bottom navigation** (se il tema lo supporta) oppure **hamburger top-right** con drawer. In ogni caso:

- Cart sempre visibile nell'header, non nel drawer
- Search accessibile con un tap, non nascosta
- Il drawer apre da destra, 85% larghezza, overlay scuro 60%
- Voci del drawer: stesso ordine del desktop, più grandi (48px min tap target)

---

## 7. Social UX — elementi specifici BKS

### Newsletter "BKS Archive"

Non è una newsletter generica. È un **archivio di segnali editoriali**. Il naming conta:

```
Headline:   The BKS Archive
Subline:    New drops, editorial notes, and collection previews.
            No frequency commitment — only when there is something to say.
CTA label:  Join the archive       ← non "Subscribe"
```

Posizionamento: **sempre inline**, mai popup. L'iscrizione avviene nell'ecosistema della pagina, non in un'interruzione.

### Trust signals — posizionamento corretto

I segnali di fiducia vanno posizionati **vicino all'azione**, non in fondo alla pagina:

| Segnale | Posizione corretta |
|---|---|
| "Made to order" spiegazione | Subito sotto il bottone Add to cart |
| "30-Day Returns" | Vicino al prezzo / nelle spec bullets |
| "2-Year EU Warranty" | Nelle service bullets del prodotto |
| Tempo di produzione | In alto nella product page, ben visibile |
| Metodi di pagamento | Footer + checkout, non sulla homepage |

### Recensioni e prove sociali

BKS Studio è un brand giovane — non fingere una base recensioni che non c'è. Il trust si costruisce con:

1. **Trasparenza del processo** (AI-art panel — spiega cosa compri)
2. **Policy chiare e accessibili** (shipping, returns, warranty)
3. **Informazioni complete** (size guide, materiali, lead time)
4. **Tono autentico** (non "Amazing quality!!!" ma "Edge-to-edge sublimation print. Doesn't crack.")

Quando le recensioni arriveranno (Judge.me o simile), inserirle nella product page **sotto la fold**, mai in homepage finché il campione è < 20 recensioni verificate.

---

## 8. Mobile UX — regole specifiche

Il 70%+ del traffico fashion POD è mobile. Queste regole non sono opzionali:

### Hero su mobile
- Immagine: full viewport height, `object-fit: cover`, focal point centrale o in alto (non tagliare le teste se c'è un modello)
- Headline: max 3 righe su 375px, font size `clamp(44px, 10vw, 88px)`
- CTA: 56px height minimo, full-width su mobile, mai floating o sovrapposto all'immagine

### Griglia prodotti su mobile
- **2 colonne**, aspect ratio 4:5, gutter 8px
- Prezzo visibile senza scroll nel card
- Nome prodotto max 2 righe (overflow ellipsis)
- **Mai 1 colonna** — troppo lento da navigare, fa sembrare il catalogo piccolo
- **Mai 3 colonne** — le immagini diventano illeggibili

### Tap targets
- Tutti gli elementi interattivi: minimo **44×44px**
- Spazio tra link contigui: minimo 8px
- Menu hamburger: minimo 48×48px, mai in un angolo dove si sovrappone al logo

### Form e checkout
- Input: 48px height, font-size 16px (evita lo zoom automatico iOS)
- Tastiera numerica per campi numero/telefono: `inputmode="numeric"`
- Bottone "Add to cart": sempre visibile senza scroll su mobile — sticky se il prodotto è lungo

---

## 9. Performance — priorità Shopify

Dawn è pesante. Queste ottimizzazioni sono obbligatorie prima del lancio:

| Problema | Soluzione |
|---|---|
| LCP > 3s | Hero image: `fetchpriority="high"`, no lazy loading |
| Font FOUT | `font-display: swap` su tutti i Google Fonts `<link>` |
| App embed peso | Auditare ogni Shopify app con Lighthouse — rimuovere app inutilizzate |
| Immagine hero desktop servita su mobile | `<picture>` con srcset mobile/desktop, o Shopify CDN con `width` param |
| Sezioni renderizzate ma non visibili | Caricare le sezioni below-the-fold con lazy loading |
| Doppio language selector | Un solo selector nel footer, disattivare quello header e il floating app embed |

Target: **Lighthouse mobile performance > 60**, LCP < 3s su 4G simulato.

---

## 10. Conversione etica — framework

La conversione si ottiene rimuovendo gli ostacoli, non creando pressione. I tre ostacoli principali su bakabo.club:

### Ostacolo 1: "Non so quanto aspettare"
**Soluzione:** Lead time visibile e specifico sulla product page, sopra il bottone. Non in una FAQ nascosta.
```
Made to order. Production: 7–10 business days. Then ships.
```

### Ostacolo 2: "Non so se la taglia è giusta"
**Soluzione:** Size guide link immediatamente sotto il selector taglia, apre modal con tabella. Mai solo un link testuale generico.

### Ostacolo 3: "Non so se posso restituirlo"
**Soluzione:** "30-Day Returns, hassle-free" come prima service bullet nel prodotto. Il wording "hassle-free" è il dato rilevante — rimuove l'ansia del processo.

Ogni altra frizione identificata segue lo stesso schema: **nomina il dubbio → rimuovilo con informazione, non con pressione**.

---

## 11. Interaction con le altre skill

Questa skill lavora con:

| Skill | Interazione |
|---|---|
| `bakabo-brand` | Tutta la microcopy, i CTA, i naming delle sezioni seguono la voce BKS |
| `bakabo-design-system` | I token colore, tipografia, spaziatura definiti lì sono vincolanti anche qui |
| `bakabo-pages-design` | Definisce il contenuto obbligatorio di ogni pagina; questa skill definisce il *perché* e la *logica psicologica* di quell'ordine |
| `bakabo-theme-build` | Implementazione Liquid/CSS delle decisioni di questa skill |
| `bakabo-shopify-ops` | Gestione collection taxonomy e menu Shopify che questa skill progetta |
| `bakabo-growth` | I flussi CRM (welcome, tier, review request) si innestano sui punti di contatto che questa skill progetta (newsletter, checkout, account) |

---

## 12. Self-check prima di consegnare qualsiasi output

- [ ] La homepage risponde alle 4 domande fondamentali above the fold?
- [ ] Il ritmo narrativo segue i 5 atti (identità → rilevanza → credibilità → appartenenza → azione)?
- [ ] La navigazione ha massimo 5 voci di primo livello con nomi chiari?
- [ ] Zero dark pattern dalla lista proibita in §3D?
- [ ] Il lead time è visibile sulla product page sopra il fold?
- [ ] La newsletter usa il naming "BKS Archive" e non "subscribe to newsletter"?
- [ ] Le trust signal sono vicine all'azione, non in fondo alla pagina?
- [ ] Il CTA principale della homepage è unico, non duplicato?
- [ ] Mobile: griglia 2 colonne, tap target 44px min, hero CTA full-width?
- [ ] Nessun popup in homepage?
- [ ] Nessuna voce di menu che porta a una pagina vuota?
- [ ] Il tono di ogni microcopy passa il brand self-check di `bakabo-brand` §13?

Zero violazioni = approvato. Qualunque violazione = correggere prima di consegnare.

---

## 13. Limiti della skill

- Non sostituisce A/B test su traffico reale — le sue indicazioni sono fondate su principi UX verificati, non su dati bakabo specifici
- Non può giudicare se una composizione è *bella* — quello è giudizio estetico, lavoro umano
- Non produce codice Liquid o CSS (quella è `bakabo-theme-build`)
- Non scrive product copy (quella è `bakabo-product-copy`)

La skill garantisce **coerenza strategica e assenza di errori UX fondamentali**. L'eccellenza richiede iterazione su dati reali.
