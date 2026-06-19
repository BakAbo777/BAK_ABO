---
name: bakabo-openai-image
description: Use this skill when generating product images for BKS Studio using the OpenAI Images API (gpt-image-1 or dall-e-3). Triggers include: creating editorial sneaker shots, building collection visual schemes, generating modernized product reference images, producing window display / vetrina prompts, or any request to build an image prompt for OpenAI that uses an existing BKS product as reference. Works alongside bakabo-manual-product-photo-generation (workflow), bakabo-armocromia (model palette), bakabo-window-display (vetrina staging), and bakabo-brand (voice). Do not use for Midjourney or Firefly — this skill is OpenAI-specific.
---

# BKS Studio — OpenAI Image Generation Skill
## Skill v1 — Giugno 2026

Workflow completo per generare immagini prodotto BKS Studio tramite OpenAI Image API (`gpt-image-1`). Copre sneakers, bag, apparel, ancora collection hero e vetrine editoriali.

---

## 1. Modello e modalità corrette

| Caso | Modello | Modalità | Note |
|---|---|---|---|
| Prodotto con reference image caricata | `gpt-image-1` | **images.edit** | Preserva il pattern originale — mai text-to-image puro |
| Schema prodotto (modernizzazione) | `gpt-image-1` | **images.edit** | Input = mockup originale, output = scena editoriale |
| Nuovo prompt senza reference | `gpt-image-1` | **images.generate** | Solo se il pattern è descritto verbalmente con precisione |
| Vetrina / window display | `gpt-image-1` | **images.generate** | Scena allestita senza prodotto fisso come reference |
| Varianti colore | `gpt-image-1` | **images.edit** | Input = immagine base, prompt descrive solo il cambio |

**Regola critica:** quando l'utente carica un'immagine prodotto, usare sempre `images.edit` — non `images.generate`. La fedeltà al print originale è garantita solo con reference image in input.

---

## 2. Struttura API call

### images.edit (prodotto con reference)

```python
import openai, base64, pathlib

client = openai.OpenAI()

image_bytes = pathlib.Path("product_mockup.png").read_bytes()

result = client.images.edit(
    model="gpt-image-1",
    image=image_bytes,
    prompt=PROMPT,           # vedi §4
    size="1024x1536",        # 2:3 per editoriale 4:5 (più vicino)
    quality="high",          # sempre high per BKS
    n=1
)

# Salva output
image_data = base64.b64decode(result.data[0].b64_json)
pathlib.Path("output.png").write_bytes(image_data)
```

### images.generate (vetrina / scena senza prodotto fisso)

```python
result = client.images.generate(
    model="gpt-image-1",
    prompt=PROMPT,
    size="1536x1024",        # wide 16:9 per hero banner
    quality="high",
    n=1
)
```

### Taglie disponibili gpt-image-1

| Size | Ratio | Uso BKS |
|---|---|---|
| `1024x1024` | 1:1 | Clean product, flat-lay, detail |
| `1024x1536` | 2:3 | Editoriale PDP, on-model, still-life |
| `1536x1024` | 3:2 | Hero banner, vetrina wide, lookbook |

---

## 3. Sneakers — schema di modernizzazione

Quando l'utente carica un'immagine sneaker BKS e chiede di "renderla più moderna" o di usarla come schema, applicare questo workflow:

### 3a. Analisi prodotto (da fare prima del prompt)

Identificare dal mockup:
1. **Silhouette** — low-top / high-top / runner / platform
2. **Pattern dominante** — nome e descrizione visiva (es. "leopard gold/black + hexagonal chrome mesh")
3. **Palette** — 3–5 hex dominanti
4. **Label** — posizione e forma del logo (BAK|ABO sul lato, BKS sul tallone, etc.)
5. **Suola** — colore e tipo (rubber nera, bianca, gum)

### 3b. Prompt modernizzazione sneakers — template

```
Editorial product photography, 4:5 vertical.
Pair of low-top canvas sneakers with all-over print: 
[DESCRIZIONE PATTERN ESATTA DAL MOCKUP].
Suola in rubber [colore]. Lacci [colore].

Placement: shot at a slight 3/4 angle, unlaced, 
heel slightly raised — one shoe behind the other.
Surface: [superficie da §5 della collezione].
Light: [luce da §5 della collezione].

The print pattern must be exactly preserved from the reference image.
No model. No added text. No logo beyond what is visible on the shoe.
Ultra-sharp focus on the toe box and pattern. 
Contemporary editorial aesthetic — no commercial catalog feel.
Photorealistic, no CGI look.
```

### 3c. Varianti scena per sneakers

| Variante | Superficie | Luce | Mood |
|---|---|---|---|
| **Urban studio** | Cemento levigato grigio scuro | Hard lateral from left, sharp shadow | Contemporaneo, grafico |
| **Travertino** | Lastre travertino chiaro | Golden hour da destra | Mediterraneo, resort |
| **Floating** | Sfondo `#0A0A0A` puro, no surface | Ring light frontale | Collectible, digitale |
| **Brutalist** | Gradino calcestruzzo grezzo | Overcast, ombra morbida | Urban, architettonico |
| **Editorial pair** | Piano bianco `#FAFAF7` | Studio diffuso overhead | Clean, e-commerce hero |

---

## 4. Prompt master per prodotto BKS (sneakers Image 1)

### Prodotto identificato: Marker/Glyph Hybrid Sneakers
Pattern: leopard gold + hexagonal chrome mesh overlay, black toe cap, black sole, BAK|ABO label on side panel.

**Prompt — Urban Studio (modernizzazione)**:
```
Editorial product photography, vertical 2:3.
Pair of low-top canvas sneakers. All-over print featuring two overlapping 
patterns: a golden amber leopard/animal spot pattern and a silver hexagonal 
chrome mesh overlay — the two textures bleed into each other diagonally 
across the upper. Black rubber toe cap. Black rubber sole. Black laces. 
Small white label reading "BAK ABO" on the side panel near the sole.

Shoes arranged at a 3/4 angle, one heel slightly elevated, laces loosely 
draped. Placed on polished dark concrete surface.
Hard single light source from the left, sharp directional shadow to the right.
Ultra-sharp focus on the pattern detail. 
Photorealistic — no CGI feel. No model. No added text. No decorative props.
Contemporary editorial sneaker photography. 
```

**Prompt — Floating dark (collectible)**:
```
Product photography, square 1:1.
Single sneaker, left shoe, side profile.
Low-top canvas sneaker with all-over print: golden amber leopard spots 
transitioning into chrome hexagonal mesh across the upper.
Black toe cap, black sole, black laces.
Pure black background #0A0A0A. No surface — shoe appears to float.
Soft studio ring light, even illumination, subtle specular on the chrome mesh.
Ultra-sharp focus across entire shoe. No shadow. No model. No text.
Photorealistic.
```

---

## 5. Prompt master per collezioni (Image 2 — vetrina editoriale)

Immagine 2 mostra una scena-vetrina con tre prodotti su piedistalli travertino sotto luce calda architetturale. Questo è il layout di riferimento per le vetrine BKS.

### Prompt — Vetrina Glyph (duffle + windbreaker + backpack)
```
Luxury editorial product still-life photography, horizontal 3:2.
Three BKS Studio products arranged on stepped travertine pedestals in 
a warm-toned architectural setting — stone columns, arched alcoves, 
diffused warm afternoon light from above-right.

Left foreground: large duffle bag with gold/ochre all-over print 
featuring abstract glyph-like symbols and coded fragments. 
Tan leather handles. White outlined human figure motif on front panel.

Center background: full-zip windbreaker jacket hanging on a minimal 
gold mannequin stand — all-over print of irregular white grid lines 
on deep black ground. Mock neck collar.

Right foreground: compact backpack — all-over diamond/grid mesh pattern 
in navy/charcoal tones with ivory lines. 
White fabric label strip with "BAK ABO" text in black.

No models. No text beyond the visible product labels.
Warm travertine and sand palette environment.
Photorealistic, editorial fashion photography.
```

---

## 6. Parametri qualità e output

### Quality settings

Usare sempre `quality="high"` — è la qualità massima di gpt-image-1.

### Post-processing obbligatorio

Dopo ogni generazione OpenAI:
1. **Verificare il print** — confrontare con il mockup originale. Se il pattern è alterato, rigenerare con prompt più specifico.
2. **Crop e resize** — portare all'aspect ratio corretto per lo slot Shopify (§3 della skill `bakabo-manual-product-photo-generation`).
3. **Color check** — palette dominante coerente con il prodotto.
4. **Naming** — applicare convention `bks-[collection]-[design]-[product_type]-[slot]-[variant].png`.

### Prompt engineering tips per gpt-image-1

- **Descrivere il pattern in modo fisico**, non artistico: "gold spots averaging 8–12mm diameter on white ground" è più fedele di "leopard print".
- **Specificare la luce prima della scena**: gpt-image-1 risponde meglio a descrizioni light-first.
- **Evitare riferimenti a brand reali** nella descrizione del pattern — "leopard" sì, "Versace-style" no.
- **Non usare "luxury", "premium"** nel prompt — il modello tende a generare prodotti falsi e dorati. Usare invece "editorial", "contemporary", "craft".
- **Per la fedeltà al print**, chiudere sempre con: *"The all-over print pattern from the reference image must be preserved exactly — do not invent or alter the pattern."*

---

## 7. Integrazione con le skill BKS

| Skill | Quando consultare |
|---|---|
| `bakabo-manual-product-photo-generation` | Per la lista completa degli slot (01–12) e i prompt base per tipo prodotto |
| `bakabo-armocromia` | Per scegliere il tono pelle del modello (se on-model) coerente con la palette della collezione |
| `bakabo-window-display` | Per costruire scene vetrina multi-prodotto con staging, piedistalli, allestimento |
| `bakabo-brand` | Per controllare che il mood del prompt non cada in "luxury" o "fast-fashion" |
| `bakabo-design-system` | Per scegliere i colori di sfondo (tokens: `--bks-onyx`, `--bks-salt`, `--bks-bone`) |

---

## 8. Limiti e workaround

| Limite | Workaround |
|---|---|
| gpt-image-1 altera il pattern | Aggiungere al prompt: "preserve the exact print from the reference image" + usare images.edit |
| Logo BAK\|ABO non leggibile | Non generare il logo nel prompt — aggiungere in post con overlay grafico |
| Sfondo non neutro per clean product | Aggiungere al prompt: "flat [color] background, no texture, no shadow, no environment" |
| Suola non realistica | Descrivere la suola separatamente: "thick rubber sole, flat profile, black, no branding" |
| Modello troppo stilizzato (CGI) | Chiudere il prompt con: "photorealistic photography, Canon lens, not CGI, not illustration" |
