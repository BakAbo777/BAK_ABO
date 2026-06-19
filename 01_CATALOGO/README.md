# Fase 01 — Catalogo

Aggiornato 17 Giugno 2026.

Obiettivo: mantenere il catalogo prodotti allineato tra DB locale, CSV Shopify e store live.

## Launcher

```bat
01_START_CATALOG_ENGINE.bat
```

App Streamlit: `http://localhost:8501` → pagina `06_Catalogo`

## Fonte di verità

```text
collezioni_csv/bks_catalog.db
```

Il DB SQLite è la fonte primaria. Il CSV è un export derivato — non modificare il CSV direttamente.

## CSV attivo (export dal DB)

```text
collezioni_csv/collezione 12_06_2026_SHOPIFY_IMPORT_READY_SEO_TAGS_READY.csv
```

1471 righe prodotto, 188 handle, ~1.2 MB. Pronto per import Shopify.

## Arricchimento catalogo

```bat
python tools\enrich_shopify_catalog.py
```

Scrive nel DB (`migrate_rows`) e rigenera il CSV Shopify-importabile (`export_csv_for_shopify`).
Filtra automaticamente righe-fantasma (handle contenente `<`).

## Selezione asset attivi

```text
output/bks_active_assets.json
```

Contiene i path risolti: `catalog_csv`, `catalog_db`, `image_factory_dir`, `theme_zip`.
Aggiornato da `bks_assets.py → save_active_assets()`.

## Output principali

```text
output/bks_ai_index.json          indice prodotti per AI interna
output/bks_shipping_sync.json     report spedizioni Printify (refresh 24h)
output/openai_image_prompts/      prompt immagini per ogni collezione
output/openai_images/             immagini generate da OpenAI
output/images/                    immagini prodotto scaricate
```

## Generazione immagini AI

```bat
python tools\generate_openai_image.py --prompt-file output\openai_image_prompts\bks-hours.txt --name bks-hours-hero --size 1024x1536 --quality medium
```

## Regola visiva

Immagini prodotto con sfondo trasparente o neutralizzato — leggibili su collection card, banner e product grid del tema TM04 (sfondo `#FAFAF7`).
