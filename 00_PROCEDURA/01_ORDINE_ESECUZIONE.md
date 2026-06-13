# Ordine Esecuzione

## Control Plane — ECAMP

Launcher:

```bat
python -m ecommerce_automation.app
```

Dashboard:

```text
http://127.0.0.1:8600
```

Uso:

- controllare health Make, Printify, Shopify, OpenAI e Amazon;
- avviare fasi operative con run ledger;
- leggere eventi e ultimi run;
- coordinare i launcher esistenti senza riscriverli subito.

## Fase 01 — Catalogo

Launcher:

```bat
01_START_CATALOG_ENGINE.bat
```

Uso:

- correggere CSV prodotto;
- generare export prodotto;
- verificare SEO prodotto;
- preparare immagini/prodotti.

Output attivi:

- `BKS_COLLEZIONE_26_v6.csv`
- `output/products_export_updated.csv`
- `output/seo_report.csv`
- `output/bakabo_export_package.zip`

## Fase 02 — Collezioni

Launcher:

```bat
02_START_COLLECTIONS_DASHBOARD.bat
```

Uso:

- verificare collection live Shopify;
- creare o aggiornare le 16 collection mancanti;
- controllare template assignment;
- controllare audit metafield legacy collection;
- generare prompt immagini collection;
- aprire monitoraggio Analytics/Merchant Center dopo il deploy.

Output attivi:

- `output/bks_collection_plan_v20.csv`
- `output/bks_collection_template_assignment_v20.csv`
- `output/bks_collection_template_exclusions_v20.csv`
- `output/bks_collection_payloads_v20.json`
- `output/bks_collection_image_prompts_v20.md`

## Fase 03 — Metafields e Metaobjects

Launcher:

```bat
03_START_METAFIELDS_RUNNER.bat
```

Ordine script:

```bat
python tools\create_metafields.py
python tools\create_metaobjects.py
python tools\populate_metafields.py --resume
```

Output:

- `output/metafield_definitions_log.csv`
- `output/metaobjects_log.csv`
- `output/populate_metafields_log.csv`

## Fase 04 — Tema Shopify

Tema attivo:

```text
output/BKS_V20_TEXTS_COLOR_READY.zip
```

Controlli:

- template editoriali BKS presenti;
- template prodotto `product.bks-men` e `product.bks-woman` allineati;
- pagine `page.about`, `page.help-faq`, `page.policy`;
- footer con EU Representative;
- GTM unico;
- contrasto testi leggibile;
- media prodotto trasparent-friendly.

## Fase 05 — Testi e Policy

Cartella:

```text
output/site_texts_v1/
```

Usa preferibilmente i file `_reviewed.html`.

## Fase 06 — Domini, Analytics e Link

Controlli:

- dominio primario e alias collegati;
- customer account domain collegato;
- GTM installato nel tema;
- GA4 attivo;
- Merchant Center senza residui critici dopo reindicizzazione;
- pagine policy/FAQ/About/Contact raggiungibili;
- collection e product link principali senza 404.

Nel cruscotto:

```bat
02_START_COLLECTIONS_DASHBOARD.bat
```

Aprire il tab `06 Analytics`.

Nota Merchant Center: se Google segnala pagine prodotto non disponibili per prodotti eliminati, trattare il dato come residuo di indicizzazione/feed. Prima pulire feed/sitemap, poi richiedere nuovo controllo a Google.

## Fase 07 — Deploy

Prima del publish:

1. Caricare tema zip.
2. Controllare Theme Editor.
3. Assegnare template collection/prodotto.
4. Inserire policy in Shopify Settings -> Policies.
5. Lanciare audit link live.
6. Controllare tab `06 Analytics`.
7. Richiedere ricontrollo Merchant Center se necessario.
8. Fare ordine test.
