# BakAbo / BKS — Programma Operativo

Cartella progetto: `I:\BAK ABO`

Documenti procedurali:

- `00_PROCEDURA/README.md`
- `00_PROCEDURA/01_ORDINE_ESECUZIONE.md`
- `00_PROCEDURA/02_STATO_ATTUALE.md`

## Avvio Sistema

Launcher principale:

```bat
00_START_BKS_MASTER.bat
```

Menu interattivo ANSI v4.0: avvia, monitora e gestisce tutti i servizi.
Opzioni: `[1]` Studio · `[2]` Try-On · `[3]` Master Panel · `[A]` tutto
Auto-kill porte conflittuali incluso.

Launcher tecnici (richiamabili anche dal master):

- `01_START_CATALOG_ENGINE.bat` — Streamlit Studio su porta 8501
- `05_START_TRYON_ENGINE.bat` — Try-On AI Engine su porta 8010

## Porte Attive

| Porta | Servizio | URL |
| ----- | -------- | --- |
| 8501 | BKS Studio (Streamlit) | <http://localhost:8501> |
| 8010 | Try-On AI Engine | <http://127.0.0.1:8010> |
| 8600 | Master Panel | <http://127.0.0.1:8600> |

## Stato Sistema (20 Giugno 2026)

- Tema live: `BKS TM04 20_06_2026 V.22` — id `202392961362`
- Backup tema: id `202600382802`
- Homepage: Video Hero → Weekly Editorial → Piano Hero → Magazine → Reviews → Trust
- Catalogo: 202 prodotti, 8 collezioni, 674 pezzi
- Members: Metal Tier (Lead / Iron / Brass / Silver / Gold)
- Try-On: attivo tier Brass+ (3+ ordini)
- AI Worker: `bks-agent.bakabo.workers.dev` (Cloudflare, v20/06/2026)

## File Attivi Principali

- CSV catalogo: `collezioni_csv/collezione 12_06_2026_SHOPIFY_IMPORT_READY_SEO_TAGS_READY.csv`
- DB SQLite: `collezioni_csv/bks_catalog.db`
- Deploy tema: `scripts/deploy_theme_section.py`
- Deploy Worker CF: `scripts/_deploy_worker.py`
- Sorgente tema: `04_TEMA_SHOPIFY/`

## Regole Operative

- MAI modificare `.env` direttamente
- Printify Shop ID: `12030061` — NON cambiare
- Google Merchant ID: `5295165689` — NON cambiare
- PRE-PUBLISH GATE: armocromia + tipografo + copy + photo studio + commercial strategy
- Immagini cliente: NON nel repository git

Operatore: Roberto Picchioni — BKS Studio / bakabo.club
