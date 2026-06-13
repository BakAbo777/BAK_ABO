# Comandi Rapidi

## Avvio master

```bat
Start_Master.bat
```

## Test locale Python

```bat
python -m py_compile streamlit_master.py bks_collection_specs.py streamlit_collections.py tools\create_collections.py tools\export_collection_plan.py tools\export_site_texts.py tools\audit_legal_references.py tools\audit_live_site.py tools\generate_openai_image.py
```

## Rigenera piano collection

```bat
python tools\export_collection_plan.py
```

## Dry-run collection Shopify

```bat
python tools\create_collections.py --dry-run
```

## Crea collection mancanti

```bat
python tools\create_collections.py
```

## Aggiorna collection esistenti

```bat
python tools\create_collections.py --upsert
```

## Testi sito

```bat
python tools\export_site_texts.py
```

## Audit riferimenti legali

```bat
python tools\audit_legal_references.py
```

## Audit live link/GTM

```bat
python tools\audit_live_site.py
```

## Generazione immagine OpenAI da prompt salvato

```bat
python tools\generate_openai_image.py --prompt-file output\openai_image_prompts\bks-hours.txt --name bks-hours-hero --size 1024x1536 --quality medium
```

Se Python locale rifiuta il certificato OpenAI:

```bat
python tools\generate_openai_image.py --prompt-file output\openai_image_prompts\bks-hours.txt --name bks-hours-hero --size 1024x1536 --quality medium --no-verify-ssl
```
