# BKS Piano Hero — Guida installazione
## Shopify · Dawn / OS 2.0 · Giugno 2026

---

## File da caricare

| File | Dove | Note |
|---|---|---|
| `sections/bks-piano-hero.liquid` | Theme → Sections | Copia-incolla nel theme editor |
| `assets/bks-piano-hero.css` | Theme → Assets | Upload diretto |
| `assets/bks-piano-hero.js` | Theme → Assets | Upload diretto |
| `BKS-Concept-Ambient-001.mp3` … `008.mp3` | Theme → Assets | Dopo generazione Suno |

---

## Installazione

### 1. Caricare i file

**Via Shopify Admin → Online Store → Themes → Edit code:**

1. `sections/` → tasto "Add a new section" → nome `bks-piano-hero` → incolla il contenuto del file `.liquid`
2. `assets/` → tasto "Add a new asset" → upload `bks-piano-hero.css`
3. `assets/` → tasto "Add a new asset" → upload `bks-piano-hero.js`

### 2. Aggiungere alla homepage

**Via Shopify Admin → Online Store → Themes → Customize:**

1. Homepage → "Add section" → cerca "BKS Piano Hero"
2. Trascinare nella posizione desiderata (consigliato: seconda sezione dopo l'hero principale)
3. Ogni collezione appare come un **block** → aggiungere 8 block tipo "Collezione"

### 3. Configurare ogni block

Per ogni collezione (in ordine: Hours, Glyph, Marker, Riviera, Pulse, Token, Flag, Folklore):

| Campo | Valore |
|---|---|
| Nome collezione | Es: `Hours` |
| Nota musicale | Es: `Do` |
| Frequenza (Hz) | Es: `261` |
| Tasto bianco | ✅ per bianco, ☐ per nero |
| Colore collezione | Hex dalla palette BKS |
| URL collezione | `/collections/bks-hours` |
| Citazione editoriale | Dal file prompts Suno |
| Prodotti | `Sneakers, Backpack, Duffle` |
| Stagione armocromica | `Stagione Inverno` |
| File audio | `BKS-Concept-Ambient-001.mp3` |

### 4. Audio — due opzioni

**Opzione A — File in assets (consigliata per file < 10MB)**
- Caricare i file MP3 Suno in Theme → Assets
- Nel block, campo "File audio": inserire il nome del file (es. `BKS-Concept-Ambient-001.mp3`)

**Opzione B — URL esterno (CDN, per file più grandi)**
- Caricare i file su Cloudflare R2, AWS S3, o Google Cloud Storage
- Nel block, campo "URL audio esterno": incollare l'URL diretto HTTPS al file MP3

**Fallback Web Audio:**
- Se nessun file audio è configurato, il sistema genera note sintetizzate automaticamente
- Attivare/disattivare in Settings → "Usa Web Audio se nessun file audio"

---

## Configurazione tasti bianchi/neri

Ordine corretto per la tastiera musicale:

| # | Collezione | Tasto | Nota | Freq Hz |
|---|---|---|---|---|
| 1 | Hours    | Bianco | Do   | 261 |
| 2 | Glyph    | Nero   | Re♭  | 277 |
| 3 | Marker   | Bianco | Re   | 293 |
| 4 | Riviera  | Nero   | Mi♭  | 311 |
| 5 | Pulse    | Bianco | Mi   | 329 |
| 6 | Token    | Bianco | Fa   | 349 |
| 7 | Flag     | Nero   | Sol♭ | 369 |
| 8 | Folklore | Bianco | Sol  | 392 |

---

## Checklist pre-pubblicazione

- [ ] 8 block collezione configurati
- [ ] Tutti gli URL collezione impostati e funzionanti
- [ ] File audio caricati o URL esterni configurati
- [ ] Test click su ogni tasto (desktop e mobile)
- [ ] Test audio (richiede interazione utente per policy browser)
- [ ] Test "Torna al piano"
- [ ] Verifica responsive mobile (< 640px)
- [ ] File audio rights: piano Suno Pro/Premier verificato → `Rights OK = OK Commercial`

---

## Note tecniche

**Performance:**
- Il canvas usa `requestAnimationFrame` — impatto CPU minimo a schermo statico
- I file audio hanno `preload="none"` — non caricano finché non vengono attivati
- Il JS è vanilla, zero dipendenze esterne

**Browser support:**
- Canvas 2D: tutti i browser moderni
- Web Audio API: Chrome, Firefox, Safari, Edge (richiede interazione utente per avvio)
- HTML5 Audio: tutti i browser moderni

**Accessibilità:**
- Canvas ha `aria-label` descrittivo
- Il pannello collezione ha `aria-live="polite"`
- Navigazione keyboard: ← → per cambiare tasto, Enter/Spazio per aprire, Esc per tornare
- Back button ha `aria-label`
