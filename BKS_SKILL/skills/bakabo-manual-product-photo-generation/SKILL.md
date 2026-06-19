---
name: bakabo-manual-product-photo-generation
description: Use this skill when manually creating a complete Shopify image set from BKS Studio / BakAbo product mockups. Trigger when the user uploads front/back/side product images and asks to create editorial, catalog, Shopify-ready, hero, product-detail, or missing product photos manually. Also triggers for single-image prompt requests, photo direction briefs, or when evaluating an AI-generated product image for quality and brand compliance. Works alongside bakabo-image-production (collection-level hero and naming), bakabo-armocromia (model palette), bakabo-brand (voice and positioning). Do not use for theme code or product copy.
---

# BKS Studio — Manual Product Photo Generation
## Skill v1 — Giugno 2026

Workflow manuale per creare un set completo di immagini prodotto BKS Studio partendo dai mockup caricati. Output pronto per Shopify PDP, collection grid, homepage hero, advertising, lookbook.

---

## 1. Input richiesto

L'utente carica sempre le immagini prodotto come riferimento. Questa skill non inventa mai:

| Asset input | Obbligatorio | Note |
|---|---|---|
| Front product | ✅ | Mockup frontale completo |
| Back product | Raccomandato | Se disponibile |
| Side product | Opzionale | Utile per sneakers e bag |
| Detail | Opzionale | Fabric texture, logo, zip, hardware |
| Logo originale | Solo se presente sul prodotto | Non aggiungere logo BKS a prodotti che non ce l'hanno |

**Regole assolute:**
- Mai inventare un pattern — il print viene dall'immagine caricata
- Mai cambiare i colori dominanti del prodotto
- Mai sostituire o aggiungere loghi non presenti nell'originale
- Mai generare contenuto che non parta dal mockup reale

---

## 2. Set immagini minimo per ogni prodotto

Per ogni prodotto generare o proporre questo set:

```
01_front_product.jpg          — mockup frontale su sfondo pulito
02_back_product.jpg           — mockup posteriore su sfondo pulito
03_side_product.jpg           — mockup laterale o 3/4
04_editorial_front.jpg        — still-life o on-model, front
05_editorial_back.jpg         — still-life o on-model, back
06_detail_fabric.jpg          — close-up texture/print/hardware
07_hero_banner.jpg            — formato 16:7 wide per banner Shopify
```

**Set esteso (quando richiesto):**
```
08_lifestyle_front.jpg        — on-model lifestyle, ambiente reale
09_lifestyle_back.jpg         — on-model lifestyle, back
10_flat_lay.jpg               — overhead flat-lay, sfondo neutro
11_size_comparison.jpg        — prodotto vicino a oggetto di scala nota
12_packaging.jpg              — solo se il packaging è rilevante
```

---

## 3. Specifiche tecniche per formato

| Slot | Uso Shopify | Formato | Dimensione min | Aspect ratio |
|---|---|---|---|---|
| 01–03 | Immagini prodotto PDP (galeria) | JPG | 2000×2000px | 1:1 |
| 04–05 | Immagini editoriali PDP | JPG | 1600×2000px | 4:5 |
| 06 | Detail PDP | JPG | 1500×1500px | 1:1 |
| 07 | Hero banner collection/home | JPG | 2400×1050px | 16:7 |
| 08–09 | Lifestyle PDP / social | JPG | 1600×2000px | 4:5 |
| 10 | Flat-lay griglia / card | JPG | 2000×2000px | 1:1 |

**Tutti i file:** RGB, sRGB color space, qualità JPG 85–92%, nessun watermark, nessun testo visibile nell'immagine.

---

## 4. Prompt master per ogni slot

### Slot 01–03 — Product clean (sfondo)

```
Product photography for e-commerce. Exact [product_type] from the uploaded 
reference image, placed on a clean [background_color] background. 
No model, no props, no shadows. Perfect centering. 
All-over print fully visible, fabric texture realistic. 
No text, no logo overlay. Photorealistic.
[format: square 1:1, 2000×2000px]
```

Background consigliato per slot 01–03:
- Sfondo bianco `#FFFFFF` per lightbox standard Shopify
- Sfondo `--bks-salt` `#FAFAF7` per coerenza brand
- Sfondo `--bks-onyx` `#0A0A0A` per prodotti chiari (es. Flag, Folklore)

---

### Slot 04–05 — Editorial (still-life o on-model)

**Still-life:**
```
Editorial still-life fashion photography, vertical 4:5.
Exact [product_type] from uploaded reference, arranged on 
[surface: matte concrete / travertine / linen / black matte].
[Light: golden hour lateral / studio diffused / single hard source].
No model, no props beyond the surface.
All-over print clearly legible. No text, no logo.
[Mood coerente con la collezione]
```

**On-model:**
```
Editorial fashion photography, vertical 4:5.
Adult [man/woman] model wearing the exact [product_type] from the 
uploaded reference. [Postura]. [Sfondo]. 
[Luce]. All-over print clearly visible. 
No celebrity resemblance. No text, no logo.
[Mood coerente con la collezione]
```

Scegliere still-life o on-model in base alla decisione curatoriale della skill `bakabo-image-production` §2.

---

### Slot 06 — Detail fabric

```
Close-up macro photography of the fabric surface of the exact product 
from the uploaded reference. Shallow depth of field, sharp on the pattern.
No background — just the fabric filling the frame edge to edge.
Realistic fiber texture, stitching visible if present.
No text, no logo.
[Square 1:1]
```

---

### Slot 07 — Hero banner wide

```
Wide hero banner, horizontal format 16:7, 2400×1050px.
[still-life group OR on-model editorial scene].
Featuring the exact [product_type] from the uploaded reference, 
[positioned left / centered / right of frame].
[Background matching collection palette].
[Light direction and mood].
Generous negative space on [left/right] for text overlay.
No text, no logo in the image.
```

---

## 5. Superficie e luce per collezione

Da applicare ai slot editoriali (04–07):

| Collezione | Superficie still-life | Luce | Mood |
|---|---|---|---|
| Hours | Cemento grezzo scuro | Laterale dura singola | Urban, contemplativo |
| Glyph | Piano nero matte | Studio flat ring light | Grafico, coded |
| Marker | Carta grezza / ferro | Laterale dura, ombra netta | Gestuale, urbano |
| Riviera | Travertino / lino | Golden hour laterale destra | Resort, mediterraneo |
| Pulse | Piano scuro / piastrelle | Ring light frontale | Ottico, kinetic |
| Token | Superficie riflettente / plexiglass | Low-key, neon accent | Arcade, digitale |
| Flag | Bianco studio | Luce piatta uniforme | Pop, grafico |
| Folklore | Pietra chiara / linen / terra | Overcast morbida | Narrativo, naif |

---

## 6. Workflow operativo — step by step

**Step 1 — Ricezione mockup**
L'utente carica 1+ immagini prodotto. Identificare:
- Tipo prodotto (sneakers, puffer, swim trunks, lounge pants, etc.)
- Collezione di appartenenza (da handle o tag)
- Colori dominanti del print (estrarre palette 3–5 hex)
- Presenza di logo/branding nel prodotto

**Step 2 — Conferma set da produrre**
Proporre all'utente quali slot produrre tra i 12 disponibili. Default: slot 01, 04, 07 (clean front + editorial + hero).

**Step 3 — Scelta modalità editoriale**
Consultare `bakabo-image-production` §2 per la decisione curatoriale. Comunicare all'utente: *"Per questa collezione la modalità approvata è [still-life / on-model]."*

**Step 4 — Generazione prompt**
Compilare il prompt master del §4 con:
- Tipo prodotto
- Superficie e luce della collezione (§5)
- Formato e dimensione dello slot
- Riferimento al mockup caricato come source

**Step 5 — QA visivo**
Valutare ogni immagine generata contro checklist §7.

**Step 6 — Naming e consegna**
Rinominare secondo convention §8 prima di qualsiasi upload.

---

## 7. Checklist QA per ogni immagine generata

Tutti i punti devono passare prima dell'upload in Shopify:

- [ ] **Print fedele** — il pattern corrisponde al mockup originale (no pattern inventati)
- [ ] **Colori corretti** — palette dominante coerente con il prodotto originale
- [ ] **Formato e risoluzione** — rispetta le specifiche dello slot (§3)
- [ ] **Nessun testo / logo aggiunto** — l'immagine è pulita
- [ ] **Nessun artefatto AI** — no dita malformate, no testi corrotti, no proporzioni sbagliate
- [ ] **Prodotto protagonista** — occupa almeno 60% del frame per i slot 01–06
- [ ] **Sfondo coerente con collezione** — palette corretta per lo slot
- [ ] **Naming corretto** — file rinominato prima dell'upload

---

## 8. Naming convention per questo workflow

Formato: `bks-[collection]-[design]-[product_type]-[slot]-[variant].jpg`

| Componente | Esempi |
|---|---|
| `[collection]` | hours · glyph · marker · riviera · pulse · token · flag · folklore |
| `[design]` | terra · argyle · citadel · quilt · fracture (slug del design) |
| `[product_type]` | lounge-pants · sneakers · puffer · swim-trunks · travel-bag |
| `[slot]` | front · back · side · editorial · detail · hero · lifestyle · flat |
| `[variant]` | 01 · 02 · 03 |

**Esempi corretti:**
```
bks-folklore-terra-lounge-pants-front-01.jpg
bks-folklore-terra-lounge-pants-editorial-01.jpg
bks-folklore-terra-lounge-pants-hero-01.jpg
bks-riviera-argyle-swim-trunks-editorial-01.jpg
bks-glyph-fracture-sneakers-detail-01.jpg
bks-hours-cloud-puffer-hero-01.jpg
```

**Mai:**
- Spazi, caratteri speciali, parentesi
- Nomi Printify originali (`AOP_Mock_v3_FRONT_BKS...`)
- Nomi con data generica (`IMG_20260610_001.jpg`)
- "BakAbo" nel filename
- Maiuscole

---

## 9. Integrazione con Shopify — ordine immagini PDP

L'ordine di upload in Shopify determina l'ordine di visualizzazione nella galleria prodotto. Caricare in questo ordine:

```
1. 01_front_product       ← immagine principale (thumbnail)
2. 04_editorial_front     ← seconda immagine (hover su desktop)
3. 06_detail_fabric       ← terza (texture, print detail)
4. 02_back_product        ← quarta
5. 05_editorial_back      ← quinta
6. 03_side_product        ← sesta (se disponibile)
7. 10_flat_lay            ← settima (se disponibile)
8. 08_lifestyle_front     ← ottava (se disponibile)
```

**Immagine hero collection page:** `07_hero_banner` — va impostata come collection image in Admin → Collections → [nome] → Collection image.

---

## 10. Prompt rapidi per i casi più comuni

### Sneakers — editorial 4:5
```
Editorial fashion photography, vertical 4:5. Pair of sneakers from 
the uploaded reference, unlaced, placed on matte concrete surface. 
Hard lateral light from the left, sharp shadow. All-over print fully 
visible on upper. No model, no props. No text, no logo.
```

### Swim trunks — editorial on-model
```
Editorial men's swimwear, vertical 4:5. Adult male model, seated on 
travertine pool ledge, wearing exact swim trunks from uploaded reference. 
Mediterranean golden hour, waistband and drawstring visible. 
All-over print clearly legible. No text, no logo. No celebrity resemblance.
```

### Puffer jacket — editorial still-life
```
Editorial fashion still-life, vertical 4:5. Puffer jacket from the 
uploaded reference, laid flat on matte black surface, front panel up. 
All-over print edge to edge fully visible. Studio overhead diffused light. 
No model, no props. No text, no logo.
```

### Travel bag / backpack — editorial still-life
```
Editorial product photography, vertical 4:5. [Travel bag / backpack] from 
uploaded reference, placed upright on concrete surface, main compartment 
facing camera. Golden hour warm light from the right. All-over print 
clearly legible. No model. No text, no logo.
```

### Racerback dress — on-model
```
Editorial fashion photography, vertical 4:5. Adult woman, standing pose, 
wearing exact racerback dress from uploaded reference. Contemporary 
architecture background, soft overcast light. Front panel and all-over 
print fully visible. No text, no logo. No celebrity resemblance.
```

### Lounge pants — on-model resort
```
Editorial resort fashion photography, vertical 4:5. Adult woman, seated 
on travertine terrace, wearing exact wide-leg lounge pants from uploaded 
reference. Mediterranean golden hour light from the right. Print visible 
from waist to ankle. Neutral ribbed top. No text, no logo.
```

---

## 11. Integrazione con le altre skill

| Skill | Come si collega |
|---|---|
| `bakabo-image-production` | Consultare §2 per la decisione still-life/on-model; usare §6 per i naming convention di collection hero |
| `bakabo-armocromia` | Per shoot on-model, consultare la stagione cromatica consigliata per la collezione |
| `bakabo-brand` | Il tono editoriale vale anche per le direzioni fotografiche: mai "luxury", mai urgency |
| `bakabo-product-copy` | Il copy della PDP usa le stesse immagini — coerenza tra testo e visual |

---

## 12. Limiti della skill

- Non genera immagini direttamente — produce prompt e direzione per tool AI (ChatGPT Image, Midjourney, Firefly, DALL-E 3, gpt-image-1)
- Non può verificare se il pattern dell'immagine generata corrisponde all'originale — questo è un controllo umano obbligatorio nel §7
- Non produce codice Liquid o HTML
- La fedeltà del print dipende dal modello generativo usato — i modelli AI non garantiscono la riproduzione esatta del pattern originale senza reference image in input (usa sempre images.edit, non text-to-image puro)
