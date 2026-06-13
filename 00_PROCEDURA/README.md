# 00 PROCEDURA — BakAbo / BKS

Questa cartella è l'indice operativo del programma. I sorgenti restano in root e in `tools/` per non rompere launcher, import Python e cruscotti.

## Ordine ufficiale

1. `01_CATALOGO` — pulizia catalogo, CSV, immagini prodotto, SEO prodotto.
2. `02_COLLEZIONI` — creazione/sync collection, template assignment, prompt immagini.
3. `03_METAFIELDS_METAOBJECTS` — definizioni metafield, metaobject BKS, popolamento prodotti.
4. `04_TEMA_SHOPIFY` — tema Dawn/BKS, template, policy access, contrasto, recensioni.
5. `05_TESTI_POLICY` — About, FAQ, shipping, returns, privacy, terms, contact.
6. `06_ANALYTICS_MERCHANT` — domini, GA/GTM, Merchant Center, crawl link, pagine pubbliche.
7. `07_DEPLOY_CHECK` — pacchetto finale e checklist prima del publish.

## Launcher

| Fase | Launcher | URL |
|---|---|---|
| Master | `Start_Master.bat` | `http://localhost:8500` |
| 01 | `01_START_CATALOG_ENGINE.bat` | `http://localhost:5000` |
| 02 | `02_START_COLLECTIONS_DASHBOARD.bat` | `http://localhost:8501` |
| 03 | `03_START_METAFIELDS_RUNNER.bat` | `http://localhost:8502` |

`Start_Master.bat` è il punto unico di ingresso. Dal master si monitorano e si aprono i tre servizi tecnici, più audit live, file critici e configurazione.

Shortcut Desktop:

```text
C:\Users\Utente\Desktop\BakAbo BKS Master Monitor.lnk
```

## Regola di pulizia

- Non cancellare output storici: spostarli in `99_ARCHIVIO/`.
- Non spostare `app.py`, `streamlit_*.py`, `tools/`, `.env`, `input/`, `output/`, `templates/`, `static/`: sono percorsi usati dal programma.
- Il file operativo corrente del catalogo è `BKS_COLLEZIONE_26_v6.csv`.
