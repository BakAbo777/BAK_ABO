# BakAbo Armocromista Skill
> Sistema di armonia cromatica BKS — mappa collezione → stagione colorimetrica → DNA visivo
> Usato dal Worker per selezionare il DNA artistico dinamico di ogni opera generata.

---

## SISTEMA STAGIONI COLORIMETRIA

Il sistema BKS usa 4 stagioni × 2 varianti = 8 profili cromatici, uno per ogni collezione.

| Stagione | Caratteristica | Temperatura | Contrasto |
|----------|---------------|-------------|-----------|
| Winter Neutral | cool-neutral, argento-caldo | fredda | medio-basso |
| Autumn Vivid | ambra dominante, void profondo | calda | alto |
| Autumn Deep | ruggine-arancio terroso | calda | alto |
| Spring Warm | oro-teal caldo Mediterraneo | tiepida | medio |
| Summer Cool | lavanda-blu elettrico | fredda | alto |
| Winter Vivid | viola profondo + neon | fredda | massimo |
| Spring Vivid | rosso bold flat | vibrante | massimo |
| Autumn Natural | verde foresta caldo-naturale | tiepida | basso-medio |

---

## MAPPA COLLEZIONE → STAGIONE → DNA ARTISTICO

### Hours — Winter Neutral `#c8c4be`
- **Stagione**: Winter Neutral (cool-neutral, undertone silver-warm)
- **Palette**: argento caldo, grigio-beige, nero quasi-totale con accento oro singolo
- **DNA artistico**: Gordon Willis chiaroscuro depth — Hopper late-night solitudine architettonica, Klimt ornamento oro come accento strutturale, De Chirico dramma metafisico vuoto
- **Tecnica tessile**: brocato architettonico, griglia dorata su nero, frammenti di scena contemplativa
- **Anti-pattern**: NO calore ambrato diffuso, NO saturazione, NO folklore

### Glyph — Autumn Vivid `#d4a030`
- **Stagione**: Autumn Vivid (ambra dominante, contrasto void profondo)
- **Palette**: ambra-oro dominante, neri profondi, chiarore surreale
- **DNA artistico**: Magritte precisione surrealista impossibile — Dalì dreamscape su griglia Mondrian, linea tecnica Leonardo da Vinci nascosta nella composizione
- **Tecnica tessile**: micro-trama simboli greci, oggetti impossibili in ripetizione, tile surrealista piatto
- **Anti-pattern**: NO calore organico, NO figure pop, NO folkloristico

### Marker — Autumn Deep `#c04418`
- **Stagione**: Autumn Deep (ruggine-arancio caldo, terroso profondo)
- **Palette**: ruggine-arancio dominante, highlights polvere di gesso, campo strutturato sotto il gesto
- **DNA artistico**: Storaro calore Rembrandt — Basquiat corona grezza, Pollock urgenza gestuale su fondo old-master ambrato, Banksy ironia stencil in superficie
- **Tecnica tessile**: brushstroke gestuale in repeat, tag urbano overlay, drip pattern seamless
- **Anti-pattern**: NO geometria fredda, NO kawaii, NO pop flat

### Riviera — Spring Warm `#0ca898`
- **Stagione**: Spring Warm (teal-oro caldo Mediterraneo)
- **Palette**: teal caldo come accento, oro dorato, luce sea-bounce dal basso
- **DNA artistico**: naturalismo dorato Mediterraneo — Seurat vibrazione puntinista ocean-light, Matisse flat color cutout decorativo, Gauguin calore tropicale polinesiano
- **Tecnica tessile**: pattern spiaggia puntinista, tile Mediterraneo flat color, repeat onda oceanica, flora e fauna tropicali
- **Anti-pattern**: NO ombre architettoniche, NO geometria rigida, NO neon

### Pulse — Summer Cool `#8888cc`
- **Stagione**: Summer Cool (lavanda-blu elettrico, contrasto chiaro)
- **Palette**: lavanda e blu elettrico dominanti, ombre ambrate profonde, energia ottica
- **DNA artistico**: precisione elettrica Deakins fredda — geometria primaria Mondrian come logica strutturale, astrazione colore-suono Kandinski, linea figura cinetica neon Keith Haring
- **Tecnica tessile**: griglia geometrica in interferenza, repeat figura cinetica, pattern ottico a onde, overlay de Stijl
- **Anti-pattern**: NO calore terroso, NO organico, NO melanconico

### Token — Winter Vivid `#9828d8`
- **Stagione**: Winter Vivid (viola profondo + neon, contrasto massimo)
- **Palette**: viola profondo dominante, alone neon rim, vibrazione retro-grid di fondo
- **DNA artistico**: precisione manga JoJo Araki — superflat kawaii×darkness Murakami, pop giapponese robot-samurai-fenicottero Kaneko Ryuichi, luce wonder retrowave Dean Cundey
- **Tecnica tessile**: griglia pixel art, tile panel manga, kawaii icon repeat, all-over personaggio cartoon
- **Anti-pattern**: NO naturalismo, NO chiaroscuro classico, NO caldo terroso

### Flag — Spring Vivid `#c82020`
- **Stagione**: Spring Vivid (rosso bold flat, massima vibrazione)
- **Palette**: rosso dominante, blocchi flat pop, stratificazione screen-print su fondo pulito
- **DNA artistico**: dichiarazione flat pop Warhol screen-print — stencil Banksy su superficie pubblica, grafica propaganda bold Shepard Fairey, potere tipografico rosso-nero-bianco Barbara Kruger
- **Tecnica tessile**: blocco colore flat bold, screen-print repeat, tile icona pop, overlay stencil pattern
- **Anti-pattern**: NO sfumature, NO texture tessile fine, NO organico

### Folklore — Autumn Natural `#489808`
- **Stagione**: Autumn Natural (verde foresta caldo-naturale, antico)
- **Palette**: verde foresta accento, riempimento arancio-candela caldo, profondità terra antica
- **DNA artistico**: calore chiaroscuro fiamma-candela Delli Colli — chaos micro-figura organica medievale Bosch in ogni angolo, simboli primari biomorfi Mirò su campo antico, forza narrativa lussureggiante Gauguin polinesiana
- **Tecnica tessile**: trama micro-figura organica, tile biomorfo, scene narrative in repeat, pattern botanico lussureggiante
- **Anti-pattern**: NO geometria fredda, NO pop flat, NO neon

---

## REGOLE DI SELEZIONE DNA (Worker)

```
1. Il Worker legge collection dalla richiesta
2. Chiama pickBaseDNA(collection) → restituisce { season, armocromia, base }
3. Il DNA base è dinamico — NON è mai German Expressionism fisso
4. Il DNA si combina con:
   - artist_map da KV (style:bakabo:artist_map)
   - product_affinity da KV (style:bakabo:product_affinity)
   - material_context estratto dalla descrizione prodotto
   - ad_voice da KV (style:bakabo:ad_voice)
5. Il prompt finale è: Collection DNA + Artist reference + Product affinity + Material + Ad voice
```

---

## REGOLE ANTI-INQUINAMENTO CROMATICO

- **Mai mescolare stagioni opposte**: Pulse (fredda) + Marker (calda) = incoerenza
- **Il DNA della collezione è dominante** — gli artisti secondari non devono ribaltare la temperatura
- **Il materiale prodotto può ammorbidire** (es. cotone morbido attiva texture più organiche anche su Pulse)
- **L'accent color è sacro** — ogni prompt deve terminare con `Collection accent: {hex}`

---

## REGOLA BKS 21/25 — QUALITY GATE

Ogni opera generata (artwork, design pezza, scatto AI) deve superare questo gate prima della pubblicazione:

| Asse | Descrizione | Max |
|------|-------------|-----|
| Immagine | Potenza visiva, leggibilità del design | 5 |
| Voce | Coerenza con la voce BKS Studio | 5 |
| Tensione | Tensione estetica, non-ovvio | 5 |
| BKS | Fedeltà alla collezione e al DNA cromatico | 5 |
| Corpo | Adattabilità al capo reale, drape, tiling | 5 |
| **Totale** | **Gate ≥ 21/25 per procedere** | **25** |

- Score < 21 → rigenera o scarta (DB: `rejected`)
- Score 21–23 → approva con nota revisione
- Score 24–25 → pubblica direttamente

---

## AGGIORNAMENTO DNA (come aggiornare)

Per aggiornare il DNA di una collezione senza rideploy del Worker:
1. Modifica questa SKILL.md
2. Aggiorna `pickBaseDNA()` in `cloudflare/bks-ai-worker.js`
3. Rideploy Worker con `python scripts/_deploy_bks_worker.py`

Per aggiornare solo il tono pubblicitario (no rideploy):
```bash
python scripts/_update_ad_voice.py --year 2026 --tone "quiet maximalism, craft over spectacle"
```
