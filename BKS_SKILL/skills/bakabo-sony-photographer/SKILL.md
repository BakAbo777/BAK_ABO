---
name: bakabo-sony-photographer
description: >
  BKS Professional Sony Photographer Kit — reference camera body + lens per ogni tipo di prodotto/scena BKS.
  Usa questa skill quando: generi immagini AI prodotto, scrivi prompt fotografici, pianifichi uno shooting,
  scegli la camera e la lente per un tipo di capo specifico, vuoi coerenza tra set/luce/formato e collezione.
  Trigger: "foto prodotto", "scatto campagna", "prompt fotografico", "set sneakers", "hero collection",
  "video BKS", "macro tessuto", qualunque richiesta di immagine che richieda scelte tecniche fotografiche.
  Lavora con bakabo-photo-studio (stage gates Shopify), bakabo-catalog-images (pipeline mockup), 
  bakabo-fashion-editorial (mood campagna), bakabo-collection-guide (coerenza collezione).
metadata:
  type: skill
  version: "1.0"
  created: "2026-06-20"
---

# SKILL — BAKABO / BKS PROFESSIONAL SONY PHOTOGRAPHER KIT

## Ruolo

Fotografo ufficiale BAKABO/BKS. Progetta set fotografici professionali per catalogo, collezioni, prodotto, social, hero banner, video e dettagli tessuto. Ogni immagine deve sembrare scattata con una vera fotocamera Sony professionale — lente coerente, luce realistica, profondità di campo controllata, prodotto sempre leggibile.

---

## ⬛ BLOCCO OBBLIGATORIO — REGOLA FOTO BAKABO / BKS

> Queste regole hanno precedenza su qualsiasi altro criterio. Ogni immagine generata deve rispettarle integralmente prima di essere approvata.

### Principio fondamentale
Ogni foto BAKABO/BKS deve essere costruita come una fotografia professionale reale, non come un'immagine generica AI. Il prodotto è sempre il protagonista assoluto.

### La foto deve mostrare
- Forma reale del prodotto con proporzioni corrette
- Pattern leggibile e non deformato
- Materiale credibile
- Cuciture, zip, suola, manici o dettagli tecnici quando presenti
- Nessun testo inventato
- Nessun logo aggiunto o modificato
- Nessuna deformazione del capo o dell'accessorio

### Camera obbligatoria per contesto
| Contesto | Camera | Lente |
|---|---|---|
| Editoriale / campagna / modelli | Sony Alpha 1 II | 85mm f/1.4 GM |
| Catalogo / prodotto / texture | Sony A7R V | 90mm Macro G |
| Movimento / azione / dinamico | Sony Alpha 9 III | 70–200mm f/2.8 GM |
| Video / reel / spot | Sony FX3 | 35mm f/1.4 GM |

### Luce obbligatoria
**Luxury/campagna:** golden hour, luce laterale calda, ombre lunghe, contrasto morbido, bokeh naturale
**Catalogo:** softbox grande laterale, fondo neutro, ombra morbida, prodotto nitido — mai luce piatta

### Ambienti ufficiali BKS
| Ambiente | Prodotti / Collezioni |
|---|---|
| Travertino chiaro | Sneakers, backpack, travel bag, puffer, accessori |
| Architettura contemporanea | Hero collection, moda uomo/donna, campagne luxury |
| Città nordica moderna | BKS Hours, Marker, Pulse — windbreaker, sneakers |
| Costa mediterranea | BKS Riviera — swimwear, beach towel, flip flops, travel summer |
| Studio neutro premium | Catalogo, prodotto singolo, macro dettagli, Shopify |

---

## Drone Photography — BKS Post-Approval Pipeline

Dopo approvazione design, il generatore drone produce 3 slot automatici via OpenAI.

**Camera drone:** Sony FX3 su DJI, Zeiss 35mm f/1.4 GM, RAW+Log, 4K still frame

| Slot | Angolo | Formato | Uso |
|---|---|---|---|
| `overhead_flatlay` | 90° straight down | 1024×1024 | Shopify product image principale |
| `drone_angle_45` | 45° prospettiva | 1792×1024 | Hero banner collezione |
| `collection_scene` | 60° editoriale, 2-3 prodotti | 1792×1024 | Social, campagna, newsletter |

**Superfici drone per collezione:**
| Collezione | Superficie | Luce |
|---|---|---|
| hours | dark brushed concrete | hard single lateral |
| glyph | matte black polished stone | flat ring light |
| marker | aged industrial iron sheet | harsh lateral |
| riviera | white travertine + sea traces | golden hour overhead |
| pulse | dark checkerboard resin | uniform ring light |
| token | reflective plexiglass dark | low-key neon accent |
| flag | pure white studio seamless | flat uniform frontal |
| folklore | linen on light stone garden | soft overcast golden |

**CLI:**
```bash
python scripts/_generate_drone_shots.py \
  --handle bks-pulse-hex-sneakers \
  --collection pulse \
  --type sneakers \
  --title "BKS Pulse Hex Sneakers" \
  --design "orange hexagonal grid on charcoal grey" \
  [--dry-run]
```

**Output:** `BAKABO_IMAGE_FACTORY_v1.1/output/generated/{collection}/{handle}/`

---

### Divieti assoluti
Non generare mai: testo sull'immagine · loghi inventati · mani/piedi/gambe deformate · prodotto tagliato male · pattern alterato · colori cambiati senza richiesta · sfondi confusi · posa volgare · prodotto troppo piccolo · set più importante del capo.

### Formula prompt obbligatoria
```
Professional BAKABO / BKS [tipo prodotto] photography shot on [Sony camera], [lens], [settings].
[Product] as the main subject, [collection mood], [environment], [lighting], realistic materials,
correct proportions, sharp product detail, readable all-over print pattern,
premium luxury editorial style, no text, no extra logos, no distortion.
```

### Checklist approvazione (10 punti)
1. Il prodotto si capisce subito?
2. Il pattern è leggibile e non deformato?
3. Le proporzioni del capo sono realistiche?
4. La luce sembra professionale e fotografica?
5. Il set è coerente con la collezione?
6. L'immagine funziona su cellulare (1:1)?
7. Nessun testo inventato?
8. Nessun logo errato?
9. Il prodotto è vendibile su Shopify?
10. La foto sembra parte di una campagna BKS coerente?

**Se anche una sola risposta è NO → rigenerare o correggere prima di procedere.**

---

## 1. Obiettivo immagine BKS

Ogni scatto deve avere:
- Resa luxury editoriale
- Prodotto sempre leggibile e proporzionato
- Pattern non deformato
- Materiali credibili
- Luce professionale coerente con la collezione
- Nessun testo inventato
- Nessun logo aggiunto se non richiesto
- Nessuna alterazione del design del prodotto

---

## 2. Kit Sony principale

### Camera 1 — Sony Alpha 1 II
**Uso:** campaign hero · lookbook · immagini premium collezione · modelli · puffer · windbreaker · travel bag · backpack · sneakers

| Setting | Valore |
|---|---|
| Sensore | Full-frame stacked 50,1 MP |
| Lente principale | 85mm f/1.4 GM |
| ISO | 100–400 |
| Apertura | f/1.8–f/2.8 |
| Tempo | 1/500–1/1000s |
| White balance | 5200–6000K |
| AF | Volto/prodotto |

> "Usa Sony Alpha 1 II quando serve immagine finale da campagna luxury — alta qualità, bokeh elegante, resa editoriale premium."

---

### Camera 2 — Sony A7R V
**Uso:** foto prodotto · catalogo · macro tessuto · texture AOP · dettagli cuciture · zip · colletti · suole · patch · etichette

| Setting | Valore |
|---|---|
| Sensore | Full-frame 61 MP |
| Lente principale | 90mm Macro G |
| ISO | 100–200 |
| Apertura | f/5.6–f/8 |
| Tempo | 1/160–1/250s (cavalletto) |
| Luce | Diffusa laterale |

> "Usa Sony A7R V quando serve massima definizione del prodotto, dettaglio tessuto e controllo tecnico assoluto."

---

### Camera 3 — Sony Alpha 9 III
**Uso:** movimento · modelli in camminata · sneakers in azione · swimwear dinamico · windbreaker con vento · campagne outdoor

| Setting | Valore |
|---|---|
| Sensore | Full-frame global shutter |
| Lente principale | 70–200mm f/2.8 GM |
| ISO | 100–800 |
| Apertura | f/2.8–f/4 |
| Tempo | 1/1000–1/4000s |
| AF | Continuo, congelamento movimento |

> "Usa Sony Alpha 9 III quando il prodotto deve essere fotografato in movimento senza perdere nitidezza."

---

### Camera 4 — Sony FX3
**Uso:** video BKS · campagne verticali social · backstage · mini spot prodotto · clip cinematiche Shopify/Instagram/TikTok/YouTube Shorts

| Setting | Valore |
|---|---|
| Tipo | Cinema Line full-frame |
| Lente principale | 35mm f/1.4 GM o 50mm f/1.2 GM |
| Risoluzione | 4K 120fps |
| Movimento | Gimbal o handheld stabilizzato |
| Atmosfera | Luce naturale golden hour |

> "Usa Sony FX3 quando il risultato deve sembrare un video moda cinematico, non una semplice ripresa prodotto."

---

## 3. Lenti ufficiali BKS

| Lente | Uso principale | Effetto |
|---|---|---|
| **24mm f/1.4 GM** | Architettura, set ampio, hero banner, modella in ambiente | Scena ampia, geometria forte |
| **35mm f/1.4 GM** | Lifestyle, social vertical, mezzo busto, outfit completo | Naturale, editoriale — ottimo per Instagram e Shopify |
| **50mm f/1.2 GM** | Ritratto moda, dettaglio capo indossato, immagine ravvicinata | Bokeh elegante, volto nitido, prodotto leggibile |
| **85mm f/1.4 GM** | Campagna luxury, modella/modello, hero collection | Compressione elegante, sfondo sfocato, resa fashion premium |
| **90mm Macro G** | Tessuto, texture, patch, logo, zip, suola, cuciture, pattern AOP | Dettaglio estremo, texture reale |
| **70–200mm f/2.8 GM** | Movimento, strada, camminata, campagna outdoor, lookbook dinamico | Compressione professionale, isolamento soggetto |

---

## 4. Matrice camera + lente per tipo di prodotto

| Prodotto | Camera prodotto | Camera campagna | Camera movimento | Lente principale |
|---|---|---|---|---|
| **Sneakers** | A7R V | Alpha 1 II | Alpha 9 III | 85mm hero / 90mm macro / 70–200 azione |
| **Puffer Jacket** | — | Alpha 1 II | — | 85mm f/1.4 |
| **Windbreaker** | — | Alpha 1 II | Alpha 9 III | 50mm o 70–200 |
| **Backpack** | A7R V | Alpha 1 II | — | 85mm hero / 90mm macro / 50mm lifestyle |
| **Travel / Duffel Bag** | A7R V | Alpha 1 II | — | 85mm hero / 50mm lifestyle / 90mm dettagli |
| **Swimwear** | — | Alpha 1 II | — | 85mm figura / 50mm mezza figura / 90mm tessuto |
| **Dresses** | — | Alpha 1 II | — | 85mm o 50mm |
| **T-Shirt / Hoodie** | — | Alpha 1 II | — | 50mm o 85mm |
| **Beach Towel** | A7R V | — | — | 35mm scena / 90mm macro tessuto |
| **Video qualsiasi** | — | FX3 | FX3 | 35mm f/1.4 GM o 50mm f/1.2 GM |

---

## 5. Schemi luce BKS

### Golden hour luxury
**Per:** campaign, hero, moda, prodotti premium
```
Prompt: "golden hour natural light, warm side light, long clean shadows, premium fashion editorial lighting"
```
Toni: beige, nero, travertino, cemento caldo. Ombre lunghe, contrasto morbido, bokeh naturale.

---

### Studio softbox
**Per:** catalogo, prodotto singolo, e-commerce, dettaglio materiali
```
Prompt: "professional studio softbox lighting, neutral background, soft controlled shadows, high-end product photography"
```
Setup: softbox grande a 45° + pannello riflettente opposto + fondo neutro.

---

### Travertine architecture
**Per:** sneakers, bags, puffer, windbreaker, accessori luxury
```
Prompt: "minimal travertine architecture, contemporary concrete geometry, warm neutral palette, luxury editorial product set"
```

---

### Northern city light
**Per:** collezioni urbane — BKS Marker, BKS Hours, BKS Pulse
```
Prompt: "northern city light, modern architecture, cool soft daylight, clean urban luxury atmosphere"
```

---

## 6. Formati ufficiali

| Formato | Dimensioni | Uso | Regola |
|---|---|---|---|
| **Catalogo prodotto** | 1:1 | Shopify product image, griglia | Prodotto grande, pulito, senza testo |
| **Collection page** | 1600×900 / 16:9 | Hero collezione, banner, landing | Atmosfera forte, prodotto protagonista |
| **Mobile hero** | 720×1280 / 9:16 | Homepage mobile, story, reel | Soggetto verticale, prodotto centrale |
| **Social square** | 1080×1080 / 1:1 | Instagram feed, carousel | Leggibile anche da cellulare |
| **Editorial wide** | 2.3:1 | Homepage luxury, campagna premium | Composizione larga, architettura |

---

## 7. Regole specifiche per prodotto

### Sneakers
- Non deformare la forma della scarpa
- Pattern originale non alterato
- Suola proporzionata
- Set classico: 1 profilo laterale + 1 coppia 3/4 + 1 macro dettaglio

### Puffer Jacket
- Non modificare taglio
- Non deformare maniche
- Non aggiungere cappucci se non presenti
- Volume realistico

### Windbreaker
- Tessuto leggero con movimento credibile
- Zip e colletto realistici
- Nessun effetto plastico eccessivo

### Backpack
- Spallacci credibili
- Zip visibili
- Pattern non stirato
- Tasche e cuciture proporzionate

### Swimwear
- Soggetti adulti
- Posa elegante, non provocante
- Texture costume leggibile

### Beach Towel
- Telo ben steso o piegato con eleganza
- Pattern leggibile
- Texture spugna realistica

---

## 8. Struttura prompt master

```
Professional BAKABO / BKS [tipo prodotto] photography shot on [Sony camera], [lente], 
[impostazioni ISO/apertura/tempo], [prodotto], [mood collezione], [ambiente], [luce], 
[composizione], realistic materials, premium luxury editorial style, sharp product detail, 
natural proportions, controlled depth of field, no text, no extra logos, no distortion.
```

### Prompt esempio — Backpack
```
Professional BAKABO / BKS backpack photography shot on Sony Alpha 1 II, 85mm f/1.4 GM lens, 
ISO 200, f/2.2, 1/800s. Adult model walking through contemporary travertine architecture, 
golden hour warm side light, soft background bokeh, backpack clearly visible and correctly 
proportioned, realistic straps, zippers and fabric texture, BKS luxury editorial style, 
no text, no extra logos, no distortion.
```

### Prompt esempio — Sneakers
```
Professional BKS sneaker product photography shot on Sony A7R V, 90mm macro G lens, 
ISO 100, f/7.1, 1/200s. Single sneaker side profile perfectly parallel to camera, minimal 
travertine platform, soft studio-golden light, sharp pattern detail, realistic stitching, 
eyelets, sole and fabric texture, sneaker occupies 75% of frame width, 
no text, no extra logos, no deformation.
```

### Prompt esempio — Hero collection
```
Luxury BAKABO / BKS collection hero campaign shot on Sony Alpha 1 II, 85mm f/1.4 GM lens, 
ISO 200, f/2.0, 1/1000s. Adult model in premium editorial pose, contemporary architecture 
in background, warm golden hour light, strong product visibility, cinematic depth of field, 
realistic proportions, elegant non-provocative fashion styling, no text, no extra logos.
```

### Prompt esempio — Macro tessuto
```
High-resolution BKS fabric macro shot on Sony A7R V, 90mm macro G lens, ISO 100, f/8, 
1/160s on tripod. Extreme detail of all-over print fabric, visible weave texture, realistic 
stitching, controlled softbox lighting, neutral background, no distortion, no text.
```

### Prompt esempio — Video FX3
```
Cinematic BAKABO / BKS fashion video shot on Sony FX3, 35mm f/1.4 GM lens, 4K, slow 
stabilized camera movement. Adult model wearing BKS product in contemporary architecture, 
golden hour natural light, soft cinematic contrast, premium fashion campaign atmosphere, 
product always visible, realistic movement, no text, no extra logos.
```

---

## 9. Checklist qualità obbligatoria

Prima di approvare ogni immagine BKS:

- [ ] Il prodotto è il protagonista?
- [ ] Il pattern è leggibile e non deformato?
- [ ] Le proporzioni del capo sono realistiche?
- [ ] Mani, gambe, piedi e volto sono anatomicamente corretti?
- [ ] La luce sembra fotografica, non artificiale o plastificata?
- [ ] Il set è coerente con la collezione?
- [ ] Nessun testo inventato presente?
- [ ] Nessun logo errato o aggiunto?
- [ ] L'immagine funziona in formato quadrato su mobile?
- [ ] Adatta a Shopify product image (1:1, fondo pulito)?

Se una risposta è **No** → rigenerare o correggere prima di procedere.

---

## 10. Selezione automatica camera per trigger

Quando l'AI riceve una richiesta di immagine, sceglie automaticamente:

| Trigger | Camera | Lente | Set | Formato |
|---|---|---|---|---|
| `backpack` | Alpha 1 II | 85mm | travertino / golden hour | 1:1 |
| `sneakers` (prodotto) | A7R V | 90mm macro | studio neutro | 1:1 |
| `sneakers` (campagna) | Alpha 1 II | 85mm | architettura + golden hour | 1:1 |
| `sneakers` (azione) | Alpha 9 III | 70–200 | strada urbana | 4:5 |
| `puffer` | Alpha 1 II | 85mm | architettura / golden hour | 16:9 o 4:5 |
| `windbreaker` | Alpha 1 II | 50mm | città moderna | 4:5 |
| `swimwear` | Alpha 1 II | 85mm | costa / piscina | 4:5 |
| `beach towel` | A7R V | 90mm macro | spiaggia / poolside | 1:1 |
| `tessuto / macro` | A7R V | 90mm macro | studio diffuso | 1:1 |
| `hero collection` | Alpha 1 II | 85mm | architettura | 16:9 |
| `social vertical` | Alpha 1 II | 35mm | lifestyle urbano | 9:16 |
| `video` | FX3 | 35mm o 50mm | architettura / golden hour | 16:9 |

---

## 11. Skill correlate

- [[bakabo-photo-studio]] — stage gates Shopify, priority P0/P1/P2, media mapping
- [[bakabo-catalog-images]] — pipeline mockup Printify AS-IS, no AI su mockup originali
- [[bakabo-fashion-editorial]] — mood campagna, arc narrativo, caption magazine
- [[bakabo-collection-guide]] — coerenza collezione → ambiente fotografico
- [[bakabo-armocromia]] — palette prodotto, selezione skin tone modello
