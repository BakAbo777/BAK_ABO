# Comandi Rapidi — BKS Studio

Aggiornato 17 Giugno 2026. Venv attivo: `.venv_catalog`

## Avvio sistema

```bat
00_START_BKS_MASTER.bat
```

App Streamlit unificata su `http://localhost:8501`

## Test sintassi Python

```bat
python -m py_compile streamlit_master.py bks_assets.py bks_collection_specs.py catalog_engine.py tools\create_collections.py tools\export_collection_plan.py tools\export_site_texts.py tools\audit_legal_references.py tools\audit_live_site.py tools\generate_openai_image.py tools\enrich_shopify_catalog.py
```

## Catalogo

```bat
python tools\enrich_shopify_catalog.py
```

Arricchisce il CSV attivo e aggiorna il DB SQLite in `collezioni_csv/bks_catalog.db`.

## Collection Shopify

```bat
python tools\create_collections.py --dry-run
python tools\create_collections.py
python tools\create_collections.py --upsert
python tools\export_collection_plan.py
```

## Deploy tema (singola sezione o lista)

```bat
python scripts\deploy_theme_section.py
```

Per file specifici dalla cartella `_merged_tm04/` usare uno snippet Python inline — vedi sessione 17/06.

## Navigazione menu

```bat
python scripts\setup_navigation.py
python scripts\fix_main_menu.py
python scripts\rebuild_main_menu.py
```

## Prezzi e prodotti

```bat
python scripts\fix_critical_prices.py
python tools\bks_price_audit.py
python scripts\archive_products_no_image.py --dry-run
python scripts\archive_products_no_image.py --execute
```

## Testi e policy

```bat
python tools\export_site_texts.py
python scripts\publish_policies.py
```

## Audit

```bat
python tools\audit_legal_references.py
python tools\audit_live_site.py
python scripts\check_live_titles.py
python scripts\check_market_prices.py
```

## Generazione immagine OpenAI

```bat
python tools\generate_openai_image.py --prompt-file output\openai_image_prompts\bks-hours.txt --name bks-hours-hero --size 1024x1536 --quality medium
```

Con SSL disabilitato (se certificato rifiutato in locale):

```bat
python tools\generate_openai_image.py --prompt-file output\openai_image_prompts\bks-hours.txt --name bks-hours-hero --size 1024x1536 --quality medium --no-verify-ssl
```

## Cloudflare Workers

```bat
cd cloudflare && wrangler deploy
cd webhook && wrangler deploy
```

## Tier e member

```bat
python scripts\assign_tiers.py
python scripts\register_tier_webhook.py
python scripts\list_customers.py
```
