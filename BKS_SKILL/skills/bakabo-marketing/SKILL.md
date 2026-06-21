---
name: bakabo-marketing
description: >
  BKS Studio Master Marketing Skill — strategia integrata per bakabo.club.
  Copre: GMC/Google Shopping (priorità revenue immediata), YouTube restart, Instagram,
  Pinterest, Worker AI content generation (/social endpoint), SEO organico,
  mercato US, calendario contenuti, analytics, CRM segmenti e growth.
  Usa questa skill per qualsiasi decisione di marketing, canale, contenuto o crescita.
  Coordina: bakabo-social (formati), bakabo-growth (CRM email), bakabo-social-campaigns (campagne),
  bakabo-italian-terminology (sinonimi IT/EN), bakabo-collection-guide (identità collezione).
metadata:
  type: skill
  version: "1.0"
  created: "2026-06-21"
  updated: "2026-06-21"
---

# BKS Studio — Master Marketing Skill

> Il Worker `bks-agent` è il motore di contenuto. Non scrivere copy manualmente
> quando il Worker può generarlo in IT+EN, per prodotto, per collezione, per piattaforma.

---

## 0. Stato di verità — Giugno 2026

| Metrica | Valore | Note |
|---|---|---|
| Clienti Shopify totali | 32 | 2 acquisti, 12 iscritti, 1 superfan |
| Prodotti attivi | 202 | 8 collezioni, 13 tipi prodotto |
| Revenue | Early stage | Renato Tedeschi (ES, €246), Marita (US, €94) |
| GMC | 35.1K bloccati "numero limitato" | Blocco revenue principale |
| YouTube | 11 video 2023, fermo 18 mesi | Canale ancora "Art in transfiguration" |
| Instagram | Handle da verificare | Non operativo |
| Pinterest | Sospeso | Appeal inviato 20/06, 24–48h |
| TikTok | Non collegato | Admin → TikTok → reconnect |
| Facebook | 141 video archivio FB_VID_* | Da deduplicare e ritaggare |
| Cloudflare Worker | `bks-agent.bakabo.workers.dev` | Allenato IT+EN, 8 collezioni, live |

---

## 1. Priorità marketing — stack per impatto

```
PRIORITÀ 1 — Revenue immediata
  └─ GMC fix: 35.1K prodotti "numero limitato" → sblocco → Google Shopping live

PRIORITÀ 2 — Reach organica
  └─ YouTube restart: rinomina canale → 8 video editoriali → serie Pattern Reveal

PRIORITÀ 3 — Social proof
  └─ Instagram: stabilire handle → contenuto prodotto settimanale → link-in-bio

PRIORITÀ 4 — Recupero canale visuale
  └─ Pinterest: attesa appeal → board per collezione → feed automatico da Shopify

PRIORITÀ 5 — CRM
  └─ Email welcome flow: 12 iscritti in attesa → 3 email in 7 giorni → prima conversione
```

---

## 2. GMC — Fix priorità 1

### Problema
Google Merchant Center mostra 35.1K prodotti con "numero limitato" (limited quantity).
Questo blocca la visualizzazione negli annunci Shopping e riduce il ranking organico.

### Causa
I prodotti made-to-order non hanno stock fisico → GMC interpreta `quantity=0` come
"esaurito" → flag "numero limitato".

### Fix
```
Attributo da aggiungere al feed GMC:
  availability: in_stock
  quantity_to_sell_on_google: 0   → o rimuovere questo campo
  custom_label_0: made-to-order

Oppure nel feed Shopify → GMC:
  inventory_policy: continue      (permettere acquisti senza stock)
  inventory_quantity: 999         (stock "virtuale" per GMC)
```

### Script
`tools/enrich_shopify_catalog.py` — aggiungi campo `inventory_quantity: 999` per tutti
i prodotti con `inventory_policy: continue`.

### Timeline
- Wixpa re-submitted 20/06 → verifica indice GMC entro 22/06/2026

---

## 3. YouTube — Restart completo

### Azioni immediate (ordine)
1. **Rinomina canale**: "Art in transfiguration (BKS)" → **"BKS Studio"**
2. **Aggiorna descrizione canale** (testo da `bakabo-social` §2)
3. **Aggiorna keyword canale**: rimuovi "BAKABO" unspaced, aggiungi lista da `bakabo-social` §2
4. **11 video 2023**: rendi privati → verifica copyright audio → ripubblica selettivamente
5. **Carica 8 video nuovi**: uno per collezione, tipo "Pattern Reveal" (30–60s, no parlato)

### Generazione titoli e descrizioni via Worker
```
POST bks-agent.bakabo.workers.dev/social
{
  "collection": "bks-marker",
  "product_type": "puffer-jacket",
  "platform": "youtube",
  "language": "en"
}
→ { "title": "...", "description": "...", "tags": [...] }
```

### Serie editoriali per collezione (8 episodi × 4 tipi = 32 video piano annuale)

| Tipo | Durata | Formato | Priorità |
|---|---|---|---|
| Pattern Reveal | 30–60s | Short 9:16 | P0 — lancia subito |
| Product Editorial | 1–2 min | 16:9 | P1 |
| AI Process | 2–4 min | 16:9 | P1 |
| Collection Overview | 3–5 min | 16:9 | P2 |

### Titolo format
`[Nome Collezione] — BKS Studio` (max 70 char, no emoji, no ALL CAPS)

---

## 4. Instagram — Setup e piano contenuti

### Setup iniziale
1. Verificare handle attivo (da controllare in Admin)
2. Bio: `BKS Studio — Wearable AI Art. Made to order. bakabo.club`
3. Link in bio: `bakabo.club`
4. Avatar: logo BakAbo ufficiale
5. Highlights: Hours · Glyph · Marker · Riviera · Pulse · Token · Flag · Origin

### Frequenza contenuti raccomandata
- **3 post/settimana** — prodotto + caption editoriale
- **1 Reel/settimana** — Pattern Reveal 15–30s (stesso file YouTube Short)
- **5 Stories/settimana** — archivio prodotti, BTS, collage collezione

### Caption via Worker
```
POST bks-agent.bakabo.workers.dev/social
{
  "collection": "bks-riviera",
  "product_type": "swimwear",
  "platform": "instagram",
  "language": "en"
}
→ { "caption": "...", "hashtags": [...] }
```

### Hashtag fissi (sempre)
```
#BKSStudio #AIArtFashion #WearableArt #PrintOnDemand #AIFashion #ItalianDesign
```

### Hashtag per collezione — aggiornati con nome corretto (Origin, non Folklore)
| Collezione | Hashtag |
|---|---|
| Hours | #BKSHours #UrbanArt #CityWear #MonochromeFashion |
| Glyph | #BKSGlyph #GraphicArt #SignSystem #VisualAlphabet |
| Marker | #BKSMarker #UrbanExpressionism #BrutalistFashion #BrushstrokeFashion |
| Riviera | #BKSRiviera #MediterraneanStyle #ResortWear #CoastalFashion |
| Pulse | #BKSPulse #OpticalArt #DigitalFashion #OpArt |
| Token | #BKSToken #PixelFashion #ArcadeAesthetic #RetroGaming |
| Flag | #BKSFlag #GlobalSignal #PopArt #ColorBlock |
| Origin | #BKSOrigin #FolkArt #IllustratedFashion #NaifArt |

---

## 5. Pinterest — Ripristino post-appeal

### Stato
- Account `bakabofirm` sospeso — appeal inviato 20/06/2026
- Attesa: 24–48h → risposta entro 22/06/2026

### Piano post-ripristino
1. Crea 8 board — una per collezione (nome: "BKS [Nome]")
2. 5 pin per board per settimana — immagini prodotto da Shopify CDN
3. Attiva il feed catalogo Shopify → Pinterest automatico
4. Pin description: generata via Worker `/social` con `platform: "pinterest"`

### SEO Pinterest per collezioni
- Board name: `BKS Riviera — Mediterranean Resort Wear`
- Pin title format: `[Prodotto] — BKS [Collezione] | bakabo.club`
- Description: 150–300 char, keyword naturale, no spam hashtag

---

## 6. Worker `/social` — Endpoint content generation

### Aggiungere al `bks-ai-worker.js`

```javascript
if (request.method === "POST" && url.pathname === "/social") {
  const { collection, product_type, platform, language = "en", product_title } = await request.json();
  // Calls catalogAgent with social generation context
  // Returns: { title, caption, description, hashtags, tags }
}
```

### Output per piattaforma

| Platform | Output campi |
|---|---|
| `youtube` | `title` (max 70), `description` (struttura 3 paragrafi), `tags` (array 15) |
| `instagram` | `caption` (max 2200), `hashtags` (array 25) |
| `facebook` | `caption` (più descrittivo di IG), `hashtags` (array 10) |
| `pinterest` | `title` (max 100), `description` (max 300), `hashtags` (array 5) |
| `tiktok` | `caption` (max 150), `hashtags` (array 8) |

---

## 7. Mercato US — Priorità strategica

Il cliente Marita Sheshaberidze (US, €94, 1 ordine) è il segnale che il mercato US funziona.
Le collezioni BKS hanno forte appeal US per:
- Streetwear / wearable art (mercato maturo)
- Made-to-order / print-on-demand (normalizzato)
- AI-designed fashion (trend in ascesa)

### Azioni US
1. Google Shopping: assicurare che i prodotti appaiano su google.com/shopping (USD)
2. Instagram: contenuto in inglese, hashtag US: `#AIFashion #StreetStyle #WearableArt`
3. YouTube: titoli in inglese (già standard)
4. Copy prodotto: inglese master (già configurato)
5. Spedizione US: comunicare chiaramente 7–14 + 3–5 giorni (il Worker già lo gestisce in EN)

### Sinonimi US da `bakabo-italian-terminology` §5b–5d
Già caricati nel Worker. Il catalog agent risponde correttamente a:
- "puffer", "board shorts", "duffel", "tee", "joggers" → prodotti BKS corretti
- "wearable art", "AOP", "made to order" → spiega il modello correttamente
- "runs big?" → risponde con note fit BKS

---

## 8. Email marketing — CRM flow immediati

### Segmenti attivi (da `bakabo-growth`)
- **BKS Archive** (1 cliente — Renato): email personale dal fondatore
- **BKS Drop** (1 cliente — Marita): post-purchase flow → secondo acquisto
- **BKS Subscriber** (12): welcome flow 3 email / 7 giorni — **attivare subito**
- **Dormant** (~20): 1 email re-engagement → suppression se 0 aperture

### Welcome flow — 3 email in 7 giorni
```
Email 1 (giorno 0): "8 collections, one system."
  → presenta le 8 collezioni, link al catalogo, tono editoriale
Email 2 (giorno 3): "How BKS is made."
  → processo made-to-order, AI art, stampa Printify, 7–14 giorni
Email 3 (giorno 7): "Your first BKS piece."
  → CTA soft: "Start with the collection that fits you." + link collezione consigliata
```

### Trigger Shopify Flow da attivare
- Birthday coupon `BKS-BIRTHDAY` → creare e attivare
- Cart abandonment → fix preview text → attivare
- Post-purchase Brass tier → Try-On unlock notification

---

## 9. SEO organico — bakabo.club

### Keyword primarie (IT+EN)
```
EN: AI art fashion, wearable art print on demand, AOP clothing, AI designed streetwear
IT: moda AI, arte indossabile, stampa su richiesta, abbigliamento AI
```

### Ottimizzazioni Shopify SEO
1. Meta title format: `[Prodotto] — BKS [Collezione] | BKS Studio`
2. Meta description: generare via Worker per tutti i 202 prodotti
3. Alt text immagini: `[prodotto] BKS [collezione] - wearable AI art`
4. URL handle: già corretti (`/products/bks-marker-fawn-puffer-jacket`)
5. Blog: creare "BKS Journal" — 1 articolo per collezione (generato via Worker)

---

## 10. Analytics — Setup minimo

### Google Analytics 4
- Evento da tracciare: `ask_bks_open` (quando si clicca Ask BKS nel menu)
- Evento: `tryon_start`, `tryon_complete`, `tryon_crew_request`
- Funnel: PDP → Add to Cart → Checkout Started → Purchase

### Cloudflare Analytics
- Disponibile gratis nella dashboard
- Metriche: Web traffic 1.61K/24h → traccia crescita post-YouTube launch
- Workers invocations: 12/24h → obiettivo 100/giorno entro 30 giorni

### KPI mensili da monitorare
| KPI | Attuale | Target 30gg | Target 90gg |
|---|---|---|---|
| Clienti totali | 32 | 50 | 100 |
| Worker invocations/day | 12 | 100 | 500 |
| YouTube subscribers | ? | 50 | 200 |
| Instagram followers | 0 | 200 | 1000 |
| GMC prodotti approvati | ~0 | 200 | 202 |

---

## 11. Regole di voce — applicabili a tutto il marketing

Da `bakabo-brand` + `bakabo-social` — **mai derogare:**

**Non usare mai:**
- Punti esclamativi
- "Limited edition", "Drop now", "Hurry", "Don't miss"
- "Luxury", "Premium", "High-end"
- "BAKABO" unspaced
- Emoji in eccesso (max 1–2 per caption)
- CTA aggressivi ("Buy now", "Shop before it's gone")

**Usare sempre:**
- Tono osservativo, non persuasivo
- Frasi brevi, spazi bianchi
- Nome collezione completo: "BKS Marker", mai "il marker"
- CTA neutri: "bakabo.club", "link in bio", "in the catalog"
- Contatto: sempre `crew@bakabo.club`

---

## 12. Azioni immediate — checklist operativa

### Questa settimana
- [ ] GMC: verificare re-index dopo Wixpa re-submit (22/06)
- [ ] YouTube: rinomina canale → "BKS Studio"
- [ ] YouTube: carica 1 Pattern Reveal per BKS Origin (collezione più ampia)
- [ ] Email: attiva welcome flow per 12 subscriber
- [ ] Pinterest: verifica stato appeal (22/06)
- [ ] TikTok: Admin → reconnect

### Prossime 2 settimane
- [ ] Worker: aggiungi endpoint `/social` per generazione copy automatica
- [ ] Instagram: stabilisci handle, carica prime 9 immagini (grid iniziale)
- [ ] YouTube: 7 video rimanenti (1 per collezione)
- [ ] GMC: se feed OK → attiva campagna Performance Max Budget minimo

### Entro fine mese
- [ ] Blog BKS Journal: 8 articoli (1 per collezione, generati via Worker)
- [ ] Email Marita: offerta secondo acquisto (manuale, personale)
- [ ] Email Renato: aggiornamento "sei BKS Gold" + accesso anticipato prossimo drop

---

## 13. Collegamento con sistema tecnico

| Asset tecnico | Uso marketing |
|---|---|
| `bks-agent.bakabo.workers.dev/chat` | AI assistant sul sito → conversione |
| `bks-agent.bakabo.workers.dev/social` (da costruire) | Generazione copy per tutti i canali |
| `bks-agent.bakabo.workers.dev/tryon` (in costruzione) | Try-On Camerino → retention membri |
| `bakabo-italian-terminology` SKILL | Sinonimi IT+EN per copy e SEO |
| `bakabo-collection-guide` SKILL | Hook editoriale per ogni collezione |
| Cloudflare Analytics | Dashboard traffico gratuita |
| Shopify Flow | Email automation trigger |
| Google Merchant Center | Shopping feed → revenue diretta |
