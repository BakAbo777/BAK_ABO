# Pulizia Cartella — BKS Studio

Aggiornato 17 Giugno 2026.

## Regola

Materiale non più attivo → `i:\BKS database\BAK_ABO_ARCHIVIO\`
Non si cancella nulla senza verifica. Non si spostano file referenziati da codice Python attivo.

## File attivi in root

```text
streamlit_master.py          app Streamlit unificata (porta 8501)
catalog_engine.py            motore catalogo
bks_assets.py                path resolution, asset discovery
bks_collection_specs.py      specifiche 8 collezioni + 18 product type
_init_catalog.py             init DB catalogo
requirements.txt
requirements-optional.txt
.env                         MAI toccare, MAI committare
README.md
skills-lock.json             Claude Code skills — non spostare
```

## Launcher attivi in root

```text
00_START_BKS_MASTER.bat      master menu ANSI (entry point unico)
01_START_CATALOG_ENGINE.bat  avvia Streamlit 8501
05_START_TRYON_ENGINE.bat    avvia Try-On engine
```

## Cartelle attive — non spostare

```text
ecommerce_automation/        agent AI, sync, marketing, API
pages/                       pagine Streamlit (01–07)
scripts/                     deploy Shopify, fix, push
tools/                       tool ausiliari
04_TEMA_SHOPIFY/             tema locale + _merged_tm04/ (sorgente deploy)
BKS_SKILL/                   skill AI, dati strutturati, size guide
docs/                        documenti referenziati dall'agente Python
cloudflare/                  Cloudflare Workers
webhook/                     agent refresh Worker, tier upgrade Worker
collezioni_csv/              CSV + DB SQLite catalogo attivo
output/                      output generati dai tool
input/                       input immagini/modelli
static/                      asset UI
templates/                   template HTML
members_tryon/               Try-On member module
tryon_engine/                Try-On engine
```

## Cartelle con path hardcoded — non spostare senza aggiornare il codice

```text
00_PROCEDURA/                google_merchant_monitor.py → 00_PROCEDURA/02_STATO_ATTUALE.md
02_COLLEZIONI/               avatar_production.py
05_TESTI_POLICY/             legal_guardrails.py
Video_Avatar/                avatar_production.py (output video)
BAKABO_IMAGE_FACTORY_v1.1/   pages/07_Image_Factory.py + bks_assets.py
01_CATALOGO/ 03_META/        streamlit_master.py (display README path)
06_ANALYTICS/ 07_DEPLOY/     streamlit_master.py (display README path)
```

## Cartelle sistema — non toccare mai

```text
.git/  .venv_catalog/  .venv_dashboard/  .venv_metafields/
.wrangler/  .agents/  .claude/  .codex_work/
```

## Già archiviato in i:\BKS database\BAK_ABO_ARCHIVIO\

```text
AGGIORNAMENTI DA FARE/       note TODO
BACKUP_ZIP/                  backup ZIP tema
LOGHI/                       loghi PNG/ICO
99_ARCHIVIO/                 archivio storico
archivio/                    archivio legacy
old/                         file vecchi
temp/                        file temporanei
logs/                        log di avvio
ecamp_master/                app legacy
videos/                      video asset
area membri/                 doc legacy
Start_Master.bat             launcher legacy
02_START_COLLECTIONS_DASHBOARD.bat
03_START_METAFIELDS_RUNNER.bat
04_START_IMAGE_FACTORY.bat
ELIMINA_VECCHIA_DIRECTORY.bat
streamlit_collections.py
streamlit_metafields_runner.py
```
