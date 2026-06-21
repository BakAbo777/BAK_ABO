# 00 PROCEDURA — BKS Studio / bakabo.club

Indice operativo aggiornato al 20 Giugno 2026. Architettura: Streamlit unificato + Try-On Engine + Master Panel.

## Launcher attivi

| Launcher | Funzione | Porta |
| --- | --- | --- |
| `00_START_BKS_MASTER.bat` | Menu interattivo — avvia/monitora tutti i servizi (v4.0, auto-kill porte) | — |
| `01_START_CATALOG_ENGINE.bat` | BKS Studio — Streamlit master app (tutte le pagine) | 8501 |
| `05_START_TRYON_ENGINE.bat` | Try-On AI Engine — camerino virtuale Brass+ | 8010 |

Entry point unico: **`00_START_BKS_MASTER.bat`**

## Fasi operative

| Fase | Cartella | Funzione |
| --- | --- | --- |
| 01 | `01_CATALOGO/` | Pulizia CSV, SEO prodotto, immagini |
| 02 | `02_COLLEZIONI/` | Sync collection, template assignment |
| 03 | `03_METAFIELDS_METAOBJECTS/` | Metafield, metaobject BKS |
| 04 | `04_TEMA_SHOPIFY/` | Tema TM04, sezioni, deploy |
| 05 | `05_TESTI_POLICY/` | About, FAQ, shipping, returns, policy |
| 06 | `06_ANALYTICS_MERCHANT/` | GA4/GTM, Google Merchant Center |
| 07 | `07_DEPLOY_CHECK/` | Checklist pre-publish |

## Pagine Streamlit (porta 8501)

| Pagina | File | Funzione |
| --- | --- | --- |
| Home | `streamlit_master.py` | Overview sistema, metriche live |
| Agente | `pages/01_Agente_Progressione.py` | AI agent BKS |
| Gestione | `pages/02_Gestione.py` | Store management |
| Social | `pages/03_Social.py` | Social media |
| Project | `pages/04_Project_Manager.py` | Project manager |
| Tema | `pages/05_Tema_BKS.py` | Deploy tema Shopify |
| Catalogo | `pages/06_Catalogo.py` | Catalog engine (ex Flask 5000) |
| Image Factory | `pages/07_Image_Factory.py` | Launcher Image Factory |

## File critici — non spostare

```text
.env                       credenziali API
bks_assets.py              path resolution, asset discovery
bks_collection_specs.py    specifiche collezioni
catalog_engine.py          motore catalogo (legacy + attivo)
ecommerce_automation/      agent, sync, AI, marketing
pages/                     pagine Streamlit
scripts/                   deploy scripts Shopify
tools/                     tool ausiliari
output/                    output attivi
collezioni_csv/            CSV + DB catalogo attivo
input/                     input immagini/modelli
04_TEMA_SHOPIFY/           tema locale + merged TM04
BKS_SKILL/                 skill AI e dati strutturati
docs/                      documenti referenziati dall'agente
webhook/                   Cloudflare Workers (agent refresh, tier upgrade)
```

## Catalogo attivo

```text
collezioni_csv/collezione 12_06_2026_SHOPIFY_IMPORT_READY_SEO_TAGS_READY.csv
```

DB SQLite: `collezioni_csv/bks_catalog.db` — fonte di verità primaria. CSV è export derivato.

## Tema Shopify attivo

- **ID:** `202392961362` — "BKS TM04 20_06_2026 V.22"
- **Sorgente locale:** `04_TEMA_SHOPIFY/_merged_tm04/`
- **Script deploy:** `scripts/deploy_theme_section.py`

## Archivio

Output storici, backup ZIP, script legacy → `i:\BKS database\BAK_ABO_ARCHIVIO\`
