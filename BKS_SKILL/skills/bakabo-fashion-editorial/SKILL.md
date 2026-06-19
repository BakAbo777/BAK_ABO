---
name: bakabo-fashion-editorial
description: >
  BKS fashion editorial direction — stagione/collezione storytelling, look composition,
  prompt AI per scatti editoriali, direzione narrativa per campagne e drops.
  Usa questa skill per: scrivere il concept editoriale di una collezione, comporre un look AI,
  strutturare una shooting list con mood e location, scrivere caption magazine, pianificare un drop.
  Lavora con bakabo-armocromia (colore), bakabo-photo-studio (fotografia), bakabo-commercial-strategy (timing).
metadata:
  type: skill
  version: "1.0"
  created: "2026-06-19"
---

# BKS Fashion Editorial Skill v1
## La collezione ha una storia. Ogni storia ha un'immagine.

---

## 1. Principio editoriale BKS

> "Non vendiamo capi. Vendiamo il momento in cui li indossi."

Il fashion editorial di BKS non è lookbook. È **narrativa breve** — 3–7 immagini che
raccontano un frammento di vita urbana, con il prodotto come protagonista silenzioso.

**Due errori da non fare mai:**
- Mostrare il capo senza contesto (foto catalogo nuda) — risultato: anonimo
- Costruire una storia così elaborata che il capo scompare — risultato: arte, non commercio

**Il bilanciamento BKS:** 60% prodotto, 40% atmosfera.

---

## 2. Architettura di una campagna editoriale

Ogni drop/collezione richiede:

| Layer | Cosa produce | Formato |
|---|---|---|
| **Cover** | 1 hero image — il momento iconico | 1:1 o 4:5 |
| **Story arc** | 3–5 immagini narrative | 4:5 (mobile-first) |
| **Detail** | 2–3 close-up su tessuto/logo/fit | 1:1 quadrato |
| **Manifesto** | 1 testo editoriale — max 80 parole | Copy |
| **Caption set** | 5–7 caption per i singoli post | 1–3 righe ciascuna |

---

## 3. Mappa collezione → direzione editoriale

### BKS Hours `#c8c4be`
- **Mood:** Urbano notturno, contemplativo, solitudine scelta
- **Stagione:** Autunno/Inverno
- **Location AI:** Stazione metro vuota alle 23:00 / Cemento con ombra dura laterale / Scaffalatura industriale
- **Model direction:** Persona che aspetta, guarda lontano, non posa — vissuta, non studiata
- **Manifesto template:** "Sono le [ORA]. La città non dorme mai del tutto. Nemmeno tu."

### BKS Glyph `#d4a030`
- **Mood:** Grafico, codificato, archivio personale
- **Stagione:** Tutto l'anno (evergreen)
- **Location AI:** Studio matte black / Tavolo con carte e penne marker / Muro con segnaletica grafica
- **Model direction:** Movimento preciso, gesto tecnico — come chi lavora con le mani
- **Manifesto template:** "Ogni segno ha un significato. Scegli il tuo codice."

### BKS Marker `#c04418`
- **Mood:** Gestuale, urbano, espressivo — street art come linguaggio
- **Stagione:** Primavera/Estate / tutto anno
- **Location AI:** Muro con tag / Carta kraft macchiata di inchiostro / Cantiere con colori
- **Model direction:** In movimento, braccio teso, gesto aperto — energia non posata
- **Manifesto template:** "Segni che restano. Su carta, su muro, su tessuto."

### BKS Riviera `#0ca898`
- **Mood:** Resort mediterraneo, luce dorata, lusso discreto
- **Stagione:** Primavera/Estate
- **Location AI:** Travertino a bordo piscina / Lenzuola lino bianco / Porto al tramonto
- **Model direction:** Rilassato, naturale, sguardo verso il sole — non costruito
- **Manifesto template:** "La costa non si affretta. Il tempo si dilata. Il colore rimane."

### BKS Pulse `#8888cc`
- **Mood:** Ottico, cinetico, ritmo urbano
- **Stagione:** Tutto l'anno
- **Location AI:** Pavimento piastrelle bianche e nere / Neon riflesso / Vetrina notturna
- **Model direction:** Freeze-frame di un movimento — come catturato in un frame
- **Manifesto template:** "Il ritmo non si vede. Si sente. Poi si porta addosso."

### BKS Token `#9828d8`
- **Mood:** Arcade digitale, neon basso, oggetto collezionabile
- **Stagione:** Autunno/Inverno
- **Location AI:** Superficie plexiglass riflettente / Cabinet arcade / Luce viola bassa
- **Model direction:** Postura controllata, guarda diretto in camera — presenza, non sorriso
- **Manifesto template:** "Ogni pezzo è un token. Ogni token è un accesso."

### BKS Flag `#c82020`
- **Mood:** Pop grafico, dichiarazione, energia positiva
- **Stagione:** Primavera/Estate / tutto anno
- **Location AI:** Studio bianco / Muro bianco con un elemento rosso / Sfondo monocromo
- **Model direction:** Frontale, diretto, postura aperta — una dichiarazione, non un'ambiguità
- **Manifesto template:** "Scegli la tua bandiera. Poi indossala."

### BKS Origin `#489808`
- **Mood:** Narrativo, naif, terra, origine personale
- **Stagione:** Tutto l'anno (primavera come peak)
- **Location AI:** Lino e pietra chiara / Terra battuta / Tavolo di legno con oggetti personali
- **Model direction:** Gesto caldo, naturale — come chi racconta qualcosa a un amico
- **Manifesto template:** "Ogni cosa ha un punto di partenza. Questo è il tuo."

---

## 4. Struttura del prompt AI per scatto editoriale

```
[TIPO DI SCATTO] + [SOGGETTO] + [LOCATION/SFONDO] + [LUCE] + [MOOD] + [GUARDRAIL ANATOMIA]

Esempio Riviera:
"Editorial fashion photograph, adult model wearing [PRODUCT DESCRIPTION], 
travertine poolside with golden hour light from the right, 
mediterranean resort atmosphere, confident relaxed posture, natural gaze, 
full body shot, 4:5 format, no distortion of limbs or hands, 
anatomically correct, photorealistic, Vogue editorial quality"
```

### Guardrail anatomia (SEMPRE inclusi):
- `anatomically correct, no extra limbs, no distorted hands`
- `realistic proportions, natural posture`
- Per close-up mani: `natural hand position, five fingers visible`
- Per full body: `full body visible, no cropping at joints`

### Pattern di illuminazione per collezione:
| Collezione | Light direction | Key source |
|---|---|---|
| Hours | Hard lateral from left | Single tungsten or LED |
| Glyph | Flat front ring | Studio ring light |
| Marker | Hard lateral with sharp shadow | Hard box, no diffusion |
| Riviera | Soft golden from right | Golden hour / large window |
| Pulse | Front centre with neon rim | Ring + neon accent |
| Token | Low-key neon from below | Neon strip, under-table |
| Flag | Flat uniform | Soft box, all sides |
| Origin | Soft overcast | Large window, no direct sun |

---

## 5. Look composition rules

**Regola dei tre pesi:**
Ogni look deve avere: un elemento FORTE (prodotto hero), uno MEDIO (texture/colore secondario), uno LEGGERO (accessorio/sfondo). Se due elementi forti si scontrano, uno dei due va semplificato.

**Colore nel look:**
- Max 2 colori vividi per look (escludendo neutrali: bianco, nero, grigio, beige)
- Il colore dell'accent della collezione può apparire come un elemento del look, non dominare
- Per scatti Riviera: azzurri + beige/sabbia — no rossi, no viola
- Per scatti Flag: un colore forte + bianco/nero

**Proporzioni:**
- Top voluminoso → bottoms slim
- Bottom voluminoso → top slim o tucked
- Layer: visibile stratificazione (giacca aperta su tee) → lettura chiara del prodotto

---

## 6. Caption editoriali — formato BKS

Tre livelli di caption (scegliere in base al contesto):

**Tipo 1 — Manifesto (post principale campagna):**
```
[Frase di apertura potente — max 8 parole]
[Sviluppo — 1-2 righe]
[Chiamata all'azione discreta]
[Hashtag: #bakabo #bksstudio #collection:[nome]]
```

**Tipo 2 — Product drop (post prodotto specifico):**
```
[Nome prodotto in Bebas style: TUTTO MAIUSCOLO]
[Collezione: BKS [NOME] — [stagione]]
[1 frase sul mood/uso]
[Link: bakabo.club/products/[handle]]
```

**Tipo 3 — Story/Reel (breve):**
```
[Emozione in una parola]
[1 frase. Fine.]
```

---

## 7. Timing editoriale — calendario drop BKS

| Mese | Contenuto prioritario | Collezione in spotlight |
|---|---|---|
| Gen–Feb | AW campaign, lookbook BKS Hours + Glyph | Hours, Glyph |
| Mar–Apr | Transizione SS, Origin launch, Riviera preview | Origin, Riviera |
| Mag–Giu | SS editorial, Riviera peak, Flag drop | Riviera, Flag |
| Lug–Ago | Resort content, Token teaser | Token, Riviera |
| Set–Ott | AW preview, Marker + Pulse focus | Marker, Pulse |
| Nov–Dic | Drop finale anno, archive | Tutti |

---

## 8. Pre-publish gate editoriale

Prima di ogni post/campagna, verificare:
- [ ] Armocromia coerente con collezione (usa bakabo-armocromia)
- [ ] Typography e caption nel registro BKS (usa bakabo-editorial-typographer)
- [ ] Anatomia immagine AI verificata (usa feedback_image_anatomy_check)
- [ ] Prodotto riconoscibile nell'immagine (60% regola)
- [ ] Strategia commerciale allineata (usa bakabo-commercial-strategy)
- [ ] Hashtag e link corretti
