---
name: bakabo-window-display
description: Use this skill when designing or generating a BKS Studio editorial product display — either a physical window display brief, an AI-generated still-life scene with multiple products, a lookbook setting, or a collection hero with staged environment. Triggers include: "vetrina", "allestimento", "window display", "staging", "collection scene", "interior design brief for shoot", "hero con più prodotti". Integrates bakabo-armocromia (model/mannequin palette), bakabo-openai-image (prompt engineering), bakabo-brand (voice), bakabo-design-system (color tokens). Do not use for single-product clean shots — use bakabo-manual-product-photo-generation instead.
---

# BKS Studio — Window Display & Editorial Staging
## Skill v1 — Giugno 2026

Sistema per costruire allestimenti editoriali multi-prodotto BKS Studio. Output: brief per interior design di un allestimento fisico, oppure prompt per generazione AI di scene-vetrina (still-life con più pezzi, collection hero, lookbook environment).

---

## 1. Principio editoriale

La vetrina BKS non è una vetrina commerciale. È una **scena curatoriale** — il prodotto è esposto come un oggetto culturale, non come merce da acquistare. 

Riferimento mentale: **galleria d'arte con oggetti da indossare**, non centrocommerciale.

Tre valori che guidano ogni allestimento:
1. **Gerarchia chiara** — un prodotto protagonista, gli altri in supporto
2. **Luce come materiale** — la luce crea l'atmosfera prima degli oggetti
3. **Spazio negativo intenzionale** — il vuoto è parte della composizione

---

## 2. Vocabolario materiale BKS

### Superfici ammesse (in ordine di preferenza editoriale)

| Superficie | Temperatura | Uso consigliato |
|---|---|---|
| Travertino chiaro | Calda/neutro | Hours, Riviera, Glyph, Folklore |
| Calcestruzzo levigato grigio scuro | Fredda | Marker, Pulse, Flag, Token |
| Cemento grezzo naturale | Neutro-freddo | Marker, Hours |
| Marmo bianco Carrara | Fredda/lusso sobrio | Flag, Pulse |
| Lino grezzo cammello | Calda | Folklore, Riviera |
| Ferro ossidato nero | Fredda/industriale | Marker, Token |
| Pietra lavica nera | Fredda | Glyph, Token, Pulse |

### Superfici vietate
- Legno di pino chiaro (cheap feel)
- Plastica visibile
- Carta da regalo o carta velina
- Superfici lucide specchianti (troppo commercial-glamour)

### Piedistalli e supporti

La vetrina BKS usa **piedistalli minimali**. I tipi approvati:

| Tipo | Materiale | Altezze | Uso |
|---|---|---|---|
| Blocco cubico | Travertino o calcestruzzo | 10/20/30 cm | Accessori, sneakers |
| Cilindro | Cemento levigato | 15/25 cm | Bag, accessori |
| Stand mannequin | Oro spazzolato / cromo | Standard | Outerwear |
| Piano inclinato | Acciaio satinato | 5–15° inclinazione | Sneakers, flat-lay |

**Regola altezze:** nella stessa scena, usare 3 altezze diverse (bassa / media / alta) per creare ritmo. Mai tutti allo stesso livello.

---

## 3. Lighting design per vetrina

### Luce calda editoriale (standard BKS)
Temperatura: 2700–3200K. Direzione: laterale-alta destra o sinistra. Effetto: ombre morbide direzionali, superfici travertino che cantano.

### Luce fredda architetturale (collezioni urban)
Temperatura: 4000–5000K. Direzione: frontale diffusa o dall'alto. Effetto: grafico, piatto, pattern leggibile.

### Luce naturale filtrata (Riviera / Folklore)
Simula overcast mediterraneo. Diffusa, senza ombre nette. Warm white. Effetto: materiale, autentico.

### Per prompt AI — formula luce
```
Warm architectural lighting, temperature 2800K, 
single directional source from upper-right at 45 degrees.
Soft diffused fill from the left. 
No harsh reflections. Travertine surfaces catch warm tone.
```

---

## 4. Layout vetrina — regole compositive

### Layout a 3 prodotti (standard — come Image 2)

```
SFONDO         [Prodotto C — outerwear su stand — alto]
               
PIANO BASSO    [Prodotto A — bag — basso sinistra] [Prodotto B — backpack — medio destra]
```

Regole:
- Prodotto più alto sempre al centro-fondo
- Prodotto più voluminoso (duffle/travel bag) in basso a sinistra
- Prodotto più compatto (backpack/sneaker) in basso a destra
- Gap tra i prodotti: almeno il 15% della larghezza frame

### Layout a 2 prodotti

```
[Prodotto A — grande, primo piano sinistra]   [Prodotto B — più piccolo, fondo destra]
```

### Layout a 1 prodotto (hero singolo)

Prodotto centrato o a regola dei terzi, spazio negativo a sinistra per eventuale testo overlay. Sempre su piedistallo o superficie caratterizzante.

---

## 5. Ambiente architetturale di riferimento

### Tipo A — Colonnato mediterraneo (come Image 2)
```
Warm-toned Mediterranean architectural setting.
Tall stone or travertine columns in the background.
Arched alcoves. Soft afternoon diffused light entering from upper right.
Sand and bone color palette — #EFEAE0 to #C9B79C range.
No people, no greenery, no props beyond the display pedestals.
```

### Tipo B — Studio industriale urbano
```
Minimal industrial studio setting.
Raw concrete walls, dark cement floor.
Hard single-source light from left, sharp shadows.
Color palette: near-black #0A0A0A to mid-gray #3D3D3D.
No windows, no texture beyond concrete.
```

### Tipo C — Galleria bianca
```
Contemporary white gallery space.
Neutral white walls, light terrazzo or polished concrete floor.
Even diffused lighting, no directionality.
Clean, museum-like atmosphere.
Palette: pure white to off-white #FAFAF7.
```

### Tipo D — Esterno architetturale (sneakers — come Image 1)
```
Exterior architectural setting — travertine steps, stone walls.
Mediterranean daylight, slightly overcast but warm.
Natural shadows from above. No cars, no people, no vegetation close.
Stone palette: #D4C5A9 to #A8927A.
```

---

## 6. Abbinamento collezione → ambiente

| Collezione | Ambiente consigliato | Superficie pedistallo | Luce |
|---|---|---|---|
| **Hours** | Tipo B (industriale) o Tipo C (galleria) | Cemento grigio | Fredda laterale dura |
| **Glyph** | Tipo A (colonnato) | Travertino | Calda laterale |
| **Marker** | Tipo B (industriale) | Ferro ossidato | Dura laterale |
| **Riviera** | Tipo A o Tipo D | Travertino / pietra | Golden hour |
| **Pulse** | Tipo C (galleria) o Tipo B | Calcestruzzo levigato | Fredda frontale |
| **Token** | Tipo B con accento luce | Ferro / plexiglass | Low-key, accent |
| **Flag** | Tipo C (galleria) | Marmo bianco | Piatta uniforme |
| **Folklore** | Tipo A o Tipo D | Pietra chiara / lino | Overcast morbida |

---

## 7. Prompt master vetrina — template completo

```
Editorial product still-life photography, horizontal 3:2 format.
[N] BKS Studio products arranged as a curated display in 
[AMBIENTE — da §5].

[PRODOTTO A]: [descrizione fedele al mockup]. 
Placed on a [pedistallo A] at [altezza A].

[PRODOTTO B]: [descrizione fedele al mockup].
Positioned on a [pedistallo B] at [altezza B], [posizione nel frame].

[PRODOTTO C se presente]: [descrizione].
[MANNEQUIN se outerwear: Minimal brushed gold headless mannequin stand, 
abstract form, garment hanging naturally.]

[LIGHTING da §3].
[COMPOSIZIONE LAYOUT da §4].

No people. No text beyond visible product labels. 
No added props (flowers, books, plants, decorative objects).
All product prints must be clearly legible.
Photorealistic editorial fashion photography.
```

---

## 8. Prompt specifico — scena Image 2 modernizzata

Partendo dall'Image 2 (colonnato, tre prodotti Glyph/Pulse), versione potenziata:

```
Editorial product still-life photography, horizontal 3:2.
Three BKS Studio products displayed in a warm Mediterranean 
architectural setting — tall travertine columns, arched stone alcoves,
warm directional light from upper right at 2800K.

Left foreground (low, on travertine block 20cm): oversized duffle bag, 
all-over print of golden ochre ground covered in densely packed 
abstract glyph-like symbols — coded fragments, geometric signs, 
stylized human outlines in white. Tan leather handles. 
Matte canvas body. Placed at slight angle, handles upright.

Center background (elevated, on minimal brushed-gold headless 
mannequin stand): full-zip windbreaker jacket — deep black ground 
with dense irregular white grid lines across entire surface, 
mock neck collar. BKS label at collar.

Right foreground (low-mid, on cement cylinder 15cm): compact backpack, 
all-over diamond/lattice mesh pattern in deep navy with ivory lines. 
White horizontal label strip across front pocket: "BAK ABO" in black.

Composition: pyramid structure — jacket highest at center, 
bag lowest-left, backpack mid-right. 
15% negative space between products.
No people. No decorative objects beyond pedestals.
All prints fully legible.
Photorealistic, editorial fashion still-life.
```

---

## 9. Brief per interior designer / scenografo (allestimento fisico)

Se l'output non è un prompt AI ma un brief per un allestimento fisico:

### Struttura brief standard

```
BKS STUDIO — WINDOW DISPLAY BRIEF
Collezione: [nome]
Stagione: [anno / drop]

CONCEPT
[2–3 frasi che descrivono il mood editoriale della scena]

PRODOTTI DA ESPORRE
1. [Prodotto — colore — taglia espositiva]
2. [...]

AMBIENTE
Tipo: [A/B/C/D da §5]
Dimensioni pedistallo: [lista altezze]
Materiale pedistallo: [da §2]
Superficie piano: [da §2]

LUCE
Temperatura: [Kelvin]
Direzione: [laterale / frontale / overhead]
Numero sorgenti: [1 principale + 1 fill / overhead diffuso]

PALETTE AMBIENTE
Sfondo: [hex o descrizione]
Suolo: [hex o descrizione]
Accenti: nessuno (regola BKS — un accento al massimo)

VIETATO
- Fiori, piante, vegetazione decorativa
- Oggetti d'arredo (libri, candele, vasi)
- Carta da regalo o tissue paper
- Qualsiasi elemento che non sia il prodotto o il supporto
- Font o testi al di fuori dell'etichetta prodotto

KPI VISIVO
Il prodotto deve occupare almeno il 40% dell'area visiva utile della vetrina.
Il pattern all-over deve essere leggibile dalla distanza di 2 metri.
```

---

## 10. Integrazione skill

| Skill | Connessione |
|---|---|
| `bakabo-openai-image` | I prompt di §7–8 vanno in `images.generate` di gpt-image-1 |
| `bakabo-armocromia` | Se la vetrina include un modello umano, applicare §4–6 di armocromia |
| `bakabo-manual-product-photo-generation` | Slot 07 (hero banner) e slot 04 (editorial) si costruiscono con questa skill |
| `bakabo-brand` | Verificare che l'ambiente non evochi "luxury" (no candele, no fur, no champagne) |
| `bakabo-design-system` | Colori superficie: usare i token BKS (`--bks-bone`, `--bks-onyx`, `--bks-salt`) |
