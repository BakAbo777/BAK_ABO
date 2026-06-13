# BakAbo / BKS Programma Operativo

Cartella riorganizzata per procedura. Parti da:

- `00_PROCEDURA/README.md`
- `00_PROCEDURA/01_ORDINE_ESECUZIONE.md`
- `00_PROCEDURA/02_STATO_ATTUALE.md`

Launcher principale:

1. `Start_Master.bat`

Nuovo control plane ECAMP / BKS Master:

1. `Start_Master.bat`
2. Oppure: `.venv_dashboard\Scripts\python.exe -m streamlit run streamlit_master.py --server.port 8600`
3. Apri `http://127.0.0.1:8600`
4. Specifica tecnica: `docs/ECAMP_CONTROL_PLANE.md`

Launcher tecnici richiamabili anche dal master:

1. `01_START_CATALOG_ENGINE.bat`
2. `02_START_COLLECTIONS_DASHBOARD.bat`
3. `03_START_METAFIELDS_RUNNER.bat`

Il master apre `http://127.0.0.1:8600` con Streamlit multipagina: Overview,
Agente/Progressione, Gestione, Social, Project Manager e Tema BKS. La vecchia
dashboard Flask resta disponibile con `python -m ecommerce_automation.app` per
endpoint/API e fallback tecnico.

## BKS Master Agent

La dashboard Flask e' il control plane unico del progetto. L'agente e'
conversazionale: legge i dati locali, mostra la progressione in real time,
propone una sola prossima azione e registra l'esito nella Knowledge DB.

Moduli principali:

- Real-Time Control: progressione visibile con grafici leggeri.
- Catalog Sync Shopify / Printify: scarica prodotti via API, genera CSV live,
  aggiorna `external_references` e segnala differenze di mapping/stato.
- Network Trust Monitor: DNS, MX, SPF, DKIM, DMARC, DSN/bounce, endpoint HTTPS
  e suffissi dati.
- Google Merchant & Trust Contract: recupero sospensione e prove di fiducia.
- Growth CRM & Member Area: segmenti clienti, PDP clarity, welcome flow,
  recensioni e member area senza over-engineering.
- Photo Studio: workflow immagini prodotto fedele ai mockup reali.
- Agent Routine & Cost Guard: usa prima dati locali, poi API leggere, poi
  chiede approvazione per azioni pubbliche, pagamenti, DNS, email e Ads.

Endpoint utili:

- `GET /api/realtime-control`
- `GET /api/catalog-live-sync`
- `POST /api/catalog-live-sync/run`
- `GET /api/network-monitor?live=1`
- `POST /api/agent/chat`

Collegamento Desktop creato:

- `C:\Users\Utente\Desktop\BakAbo BKS Master Monitor.lnk`

File attivi principali:

- Catalogo corrente: `collezioni_csv/collezione 12_06_2026_SHOPIFY_IMPORT_READY.csv`
- Tema pronto: `04_TEMA_SHOPIFY/BKS_TM03_clean_12JUN2026_SEO_READY.zip`
- Selezione asset: `output/bks_active_assets.json`
- Testi/policy: `output/site_texts_v1/`
- Audit live/link/SEO: `output/live_site_audit/` quando generato
- Prompt OpenAI: `output/openai_image_prompts/`
- Immagini OpenAI: `output/openai_images/`
- Avatar Production: `output/avatar_production/`
- Archivio storico: `99_ARCHIVIO/`
