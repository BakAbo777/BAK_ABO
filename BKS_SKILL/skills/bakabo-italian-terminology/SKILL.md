---
name: bakabo-italian-terminology
description: >
  BKS Bilingual Terminology & Synonym Lexicon — mappings between customer language
  (Italian + US English) and official BKS product/collection names. Used to train the
  Cloudflare Worker AI agents (BKS_SYNONYMS constant) and Shopify Search & Discovery.
  Covers: product types (IT/EN→BKS), collection keywords, intent signals, size/fit
  vocabulary, US market voice, and tone-of-voice guidelines for both markets.
metadata:
  type: skill
  version: "1.1"
  created: "2026-06-21"
  updated: "2026-06-21"
---

# BKS Bilingual Terminology — Skill Lexicon (IT + US EN)

> Usato da: Worker AI (BKS_SYNONYMS), Shopify Search & Discovery (19 sinonimi configurati),
> Catalog Agent, Navigation Agent, Support Agent.

---

## 1. Prodotti — Sinonimi IT → Nome BKS ufficiale

| Termini italiani del cliente | Nome prodotto BKS | Handle tipo |
|---|---|---|
| giacca, piumino, giubbotto, giaccone, parka, piumone | **Puffer Jacket** | `puffer-jacket` |
| felpa, felpa con cappuccio, cappuccio, hoodie | **Pullover Hoodie** | `pullover-hoodie` |
| pantaloncini, shorts, short sportivo, bermuda | **Athletic Shorts** | `athletic-shorts` |
| costume, costumino, costume intero, body da bagno | **Swimwear / One-Piece** | `swimwear` |
| boxer mare, boxer da bagno, costume uomo, bermuda mare | **Swim Trunks** | `swim-trunks` |
| vestito, abito, dress, abitino, abito sportivo | **Racerback Dress** | `racerback-dress` |
| scarpe, scarpe da ginnastica, sneaker, tennis | **Sneakers** | `sneakers` |
| borsa viaggio, borsone, borsa, trolley soft | **Travel Bag** | `travel-bag` |
| zaino, zainetto, backpack | **Backpack** | `backpack` |
| pantalone, pantalone morbido, pantalone tuta, jogger | **Lounge Pants** | `lounge-pants` |
| infradito, ciabatte, sandali | **Flip Flops** | `flip-flops` |
| t-shirt, maglietta, maglia, top | **T-Shirt** | `t-shirt` |
| k-way, giacca vento, impermeabile, giacca tecnica | **Windbreaker** | `windbreaker` |

---

## 2. Collezioni — Parole chiave IT → Handle BKS

| Keyword italiane | Collezione BKS | Handle | Colore accent |
|---|---|---|---|
| ore, orologio, tempo, città, notte, urbano, grigio, silenzio, contemplazione | **BKS Hours** | `bks-hours` | `#c8c4be` |
| glifi, simboli, alfabeto, segni, rune, geroglifici, marchi, grafica brand | **BKS Glyph** | `bks-glyph` | `#d4a030` |
| pennarello, graffiti, marker, muro, vernice, gesto, pennello, stroke, urban | **BKS Marker** | `bks-marker` | `#c04418` |
| riviera, mare, estate, mediterraneo, turchese, vacanza, resort, sole, spiaggia | **BKS Riviera** | `bks-riviera` | `#0ca898` |
| pulse, pulsazione, ottico, geometrico, viola, vibrazione, ritmo, kinetic, op-art | **BKS Pulse** | `bks-pulse` | `#8888cc` |
| token, gettone, pixel, arcade, videogioco, retro, bit, digitale, viola scuro | **BKS Token** | `bks-token` | `#9828d8` |
| bandiera, flag, rosso, pop, collage, blocchi, dada, rosso forte | **BKS Flag** | `bks-flag` | `#c82020` |
| origine, origin, folklore, naif, illustrazione, fiaba, memoria, storia, verde, disegno | **BKS Origin** | `bks-origin` | `#489808` |

---

## 3. Intent — Segnali linguistici italiani → Routing agent

| Frasi/keyword italiane | Intent → Agent |
|---|---|
| reso, cambio, rimborso, restituire, non va bene, rotto | `support` |
| spedizione, consegna, quando arriva, tracking, ritardo, pacco | `support` |
| ordine, il mio ordine, numero ordine, stato ordine, acquisto | `support` |
| taglia, misura, come scelgo, tabella taglie, va bene per me | `catalog` + size guide |
| personalizzare, nome sopra, testo, iniziali, custom, scritto | `customization` |
| prova, prova virtuale, camerino, indossarlo virtualmente, try-on | `tryon` |
| tier, livello, membro, abbonamento, punti, sblocco, metal | `tier` |
| dove, come accedo, link, pagina, sito, trovo, navigazione | `navigation` |
| ciao, salve, buongiorno, buonasera, aiuto generico | `greeting` |
| prodotto, collezione, prezzo, disponibile, colore, taglia disponibile | `catalog` |

---

## 4. Taglia — Vocabolario IT

| Termine cliente | Interpretazione |
|---|---|
| piccola / piccolo | S |
| media / medio | M |
| grande / largo | L o XL |
| taglia unica | One size |
| come veste / va grande | → suggerisci size down |
| taglio largo / oversize | → è il fit BKS standard su puffer e hoodie |
| vestibilità slim | → athletic shorts e swim trunks hanno fit slim |

---

## 5. Tono BKS in italiano

- **Non usare**: "bellissimo", "fantastico", "stupendo" — tono BKS è editoriale, non entusiasta
- **Usare**: "essenziale", "costruito su", "sistema", "identità", "gesto", "segno"
- **Prodotto** → sempre "capo" o nome specifico, mai "articolo" o "item"
- **Collezione** → sempre con nome BKS (es. "BKS Riviera"), mai solo "la riviera"
- **Tier** → sempre abbreviazione con simbolo: "Brass ◈", "Gold ✦", "Silver ◇"
- **Contatto umano** → sempre "crew@bakabo.club", mai generica "assistenza clienti"

---

---

## 5b. US English — Product Synonyms (EN → BKS name)

| US English customer terms | BKS product name |
|---|---|
| puffer, puffer jacket, quilted jacket, down jacket, bubble jacket | **Puffer Jacket** |
| hoodie, sweatshirt, pullover, hooded sweatshirt, crewneck | **Pullover Hoodie** |
| shorts, athletic shorts, gym shorts, running shorts, workout shorts | **Athletic Shorts** |
| swimsuit, one-piece, bathing suit, one piece swimsuit | **Swimwear / One-Piece** |
| swim trunks, board shorts, swim shorts, surf shorts | **Swim Trunks** |
| dress, racerback dress, sporty dress, athletic dress | **Racerback Dress** |
| sneakers, shoes, kicks, low-tops, graphic shoes | **Sneakers** |
| duffel, duffel bag, carry-on, weekender bag, travel bag | **Travel Bag** |
| backpack, bag, bookbag, pack, rucksack | **Backpack** |
| joggers, sweatpants, lounge pants, track pants, comfy pants | **Lounge Pants** |
| flip flops, sandals, slides, thongs | **Flip Flops** |
| tee, t-shirt, graphic tee, shirt | **T-Shirt** |
| windbreaker, wind jacket, rain jacket, shell jacket, track jacket | **Windbreaker** |

---

## 5c. US English — Collection Keywords (EN → BKS handle)

| US English keywords / mood | Collection | Handle |
|---|---|---|
| monochrome, urban, grayscale, minimalist, city, contemplation, black & white | **BKS Hours** | `bks-hours` |
| graphic, typographic, symbol print, abstract marks, glyphs, visual alphabet | **BKS Glyph** | `bks-glyph` |
| brushstroke, graffiti, street art, gestural, drip, urban paint | **BKS Marker** | `bks-marker` |
| coastal, resort wear, Mediterranean, vacation, tropical, summer, teal | **BKS Riviera** | `bks-riviera` |
| optical, geometric, hypnotic, kinetic, psychedelic, op-art, vibration, violet | **BKS Pulse** | `bks-pulse` |
| pixel art, retro gaming, digital, 8-bit, arcade, tech, sci-fi | **BKS Token** | `bks-token` |
| bold color, pop art, color block, graphic fields, red, dada | **BKS Flag** | `bks-flag` |
| folk art, illustrated, naive art, storybook, earthy, organic, green | **BKS Origin** | `bks-origin` |

---

## 5d. US Market — Key Signals & Tone

**What US customers say vs what they mean:**
- "all-over print" / "AOP" / "sublimation" / "full print" → standard BKS production method
- "made to order" / "MTO" / "print on demand" → confirm: 7–14 days production + 3–5 shipping
- "runs big?" / "TTS?" → BKS puffers and hoodies have an intentional oversized fit; dresses and shorts are slim-cut
- "limited?" / "sold out?" → all items are made to order — no sell-outs, but styles may be retired
- "wearable art" / "artist-designed" → yes, every BKS piece is an original graphic system by Roberto Picchioni
- "collab?" / "who designed this?" → BKS Studio, independent brand by Roberto Picchioni
- "sustainable?" → made to order = zero overproduction; no dead stock

**US Tone — BKS voice in English:**
- Do NOT use: "amazing", "awesome", "gorgeous", "love it" — too retail-casual
- DO use: "sharp", "built around", "graphic system", "precise", "intentional", "constructed"
- Products are "garments" or their specific name, never "items" or "products"
- Collections always "BKS [Name]", never just the name alone
- Tiers always with symbol: "Brass ◈", "Gold ✦", "Silver ◇", "Iron ⬡", "Lead ◎"
- Contact: always "crew@bakabo.club", never "customer service" or "support team"

**US shipping expectations (set correctly):**
- NOT fast fashion. Made to order. Say: "Each piece is made for your order — production takes 7–14 days, then 3–5 days shipping."
- Returns: 30 days from delivery
- No GTIN / no barcode on packaging (custom art product)

---

## 6. Shopify Search & Discovery — Sinonimi configurati (19)

Questi sinonimi sono attivi nel pannello Shopify per il motore di ricerca nativo:

```
piumino → puffer jacket
felpa → hoodie
giacca vento → windbreaker
costume → swimwear
shorts → athletic shorts
borsa → travel bag
zaino → backpack
scarpe → sneakers
vestito → dress
pantalone → lounge pants
infradito → flip flops
maglietta → t-shirt
ore → hours
glifi → glyph
riviera → riviera
origine → origin
origine → folklore
marker → glyph
pulse → pulse
```

> Nota: i sinonimi Shopify sono monodirezionali (IT→EN per ricerca). Il Worker AI usa
> la lista completa di questa skill (§1–4) per comprensione bidirezionale.

---

## 7. Come usare questa Skill nel Worker

Nel file `cloudflare/bks-ai-worker.js`, la costante `BKS_SYNONYMS` contiene la versione
compatta di §1–3 iniettata nel system prompt del `catalogAgent`. Aggiorna entrambi
quando si aggiunge un nuovo tipo di prodotto o una nuova collezione.

**Regola di aggiornamento**: ogni nuovo prodotto Printify aggiunto al catalogo deve avere
almeno 3 keyword italiane nella mappa §1 e almeno 5 keyword nella mappa §2 per la
sua collezione.
