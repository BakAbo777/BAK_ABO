---
name: bakabo-navigation
description: Use this skill when modifying, extending or debugging the BKS Studio Streamlit navigation sidebar, progress indicators, or multi-page app structure. Covers the bks_nav.py module, sidebar layout, collection health dots, catalog progress bar, and rules for adding new pages.
---

# BKS Studio — Navigation Skill
## v1 — 19 Giugno 2026

---

## 1. ARCHITETTURA MULTI-PAGE

BKS Studio è un'app Streamlit multi-page. File chiave:

| File | Ruolo |
|---|---|
| `streamlit_master.py` | Home page (root entry point) |
| `pages/00_BKS_Algorithm.py` | Scoring catalogo, priority queue, gate |
| `pages/01_Agente_Progressione.py` | Agente AI, routine, Q&A |
| `pages/02_Gestione.py` | Servizi, asset attivi |
| `pages/03_Social.py` | Social Hub, post queue, Amazon Merch |
| `pages/04_Project_Manager.py` | Project phases, milestone tracking |
| `pages/05_Tema_BKS.py` | Deploy tema Shopify TM04 |
| `pages/06_Catalogo.py` | Catalog engine, SEO, export |
| `pages/07_Image_Factory.py` | Image Factory launcher |
| `pages/08_Camerino.py` | Virtual Try-On, member area |
| `pages/08_Google_Merchant.py` | Google Merchant Center monitor |
| `pages/09_Marketing.py` | Offerte, coupon, UTM builder |
| `pages/10_Analytics.py` | Shopify analytics, revenue, ordini |
| `bks_nav.py` | **Modulo condiviso sidebar + progress** |

---

## 2. MODULO bks_nav.py

Modulo Python nella root del progetto. Importato da ogni page con:

```python
import bks_nav
# dopo set_page_config():
bks_nav.render("page_key")
```

### Cosa renderizza nella sidebar

1. **Wordmark** — "BKS STUDIO / bakabo.club" in oro `#b8a165`
2. **Catalog progress bar** — `ready / total` prodotti P3 ready
3. **Score medio** — colorato: verde ≥80, ambra ≥60, rosso <60
4. **Alert P0 critical** — se esistono prodotti con score critico
5. **Collection health dots** — 8 dot colorati con tooltip (hover = handle + score)
6. **Separatore** — linea oro 33% opacity

### Dati — fonte

`bks_nav._load_data()` chiama `BKSAlgorithm` con `@st.cache_data(ttl=90)`.
Se BKSAlgorithm non è disponibile (es. Streamlit Cloud senza CSV), fallback silenzioso — sidebar mostra solo il wordmark.

### Colori status collection

| Status | Icona | Colore |
|---|---|---|
| ok | ● | `#2f9e44` verde |
| warn | ◐ | `#e67700` ambra |
| critical | ! | `#c92a2a` rosso |
| empty | ○ | `#bbb` grigio |

---

## 3. REGOLE PER AGGIUNGERE UNA NUOVA PAGE

1. Crea `pages/NN_Nome_Page.py` con numerazione progressiva
2. Aggiungi `sys.path.insert(0, str(BASE_DIR))` PRIMA di `import bks_nav`
3. Chiama `bks_nav.render("key")` SUBITO DOPO `st.set_page_config()`
4. Usa sempre `initial_sidebar_state="expanded"` (mai `"collapsed"`)
5. Aggiorna la lista `_PAGES` in `bks_nav.py` con la nuova voce

---

## 4. THEME SIDEBAR

Il tema Streamlit (`config.toml`) usa `base = "light"` con:
- `secondaryBackgroundColor = "#ede8dc"` — sfondo sidebar
- `primaryColor = "#b8a165"` — accento gold

Il CSS del sidebar NON viene sovrascritto dalle pagine che usano `background: #0A0A0A` (che targettano solo `stAppViewContainer`, non `stSidebar`).

---

## 5. PROGRESS INDICATORS — LOGICA

```
ready_pct = P3_count / total_products        # barra progresso 0.0–1.0
score_color:
  ≥ 80 → #2f9e44 (verde)
  ≥ 60 → #e67700 (ambra)
  < 60 → #c92a2a (rosso)

collection dots: 8 dots in 2 righe da 4
  formato: "● HRS" "● GLY" "● MRK" "● RIV"
           "● PUL" "● TOK" "● FLG" "● ORI"
  hover title: "{handle} — {avg_score} · {n} prod"
```

---

## 6. MANUTENZIONE

Per forzare refresh dati sidebar (TTL 90s di default):
```python
st.cache_data.clear()
```

Per aggiornare l'accent color di una collezione:
```python
# In bks_nav.py — dizionario _COLL_ACCENTS
_COLL_ACCENTS = {
    "bks-hours":   "#c8c4be",
    "bks-glyph":   "#9b7cba",
    ...
}
```

---

## 7. DEPLOY

`bks_nav.py` è nella root del progetto e viene pushato con tutto il resto su `github.com/BakAbo777/BAK_ABO`. Nessun deploy separato necessario — fa parte del bundle Streamlit Cloud.
