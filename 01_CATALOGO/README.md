# Fase 01 — Catalogo

Obiettivo: preparare il CSV prodotto, immagini prodotto e SEO prima del sync Shopify.

Launcher:

```bat
01_START_CATALOG_ENGINE.bat
```

Input attivo:

- `collezioni_csv/collezione 12_06_2026_SHOPIFY_IMPORT_READY.csv`
- Selezione dinamica da `output/bks_active_assets.json`

Output principali:

- `output/products_export_updated.csv`
- `output/seo_report.csv`
- `output/bakabo_export_package.zip`
- `output/images/`

Comando rapido per completare SEO/tag/metafield sul CSV attivo:

```bat
python tools\enrich_shopify_catalog.py --set-active
```

Regola visiva: immagini prodotto con sfondo trasparente o neutralizzato, leggibili su collection, banner e card prodotto.
