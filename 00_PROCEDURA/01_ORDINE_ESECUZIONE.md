# Ordine Esecuzione — BKS Studio

Aggiornato 17 Giugno 2026. Architettura: Streamlit unificato (porta 8501) + ecommerce_automation agent (porta 8600).

---

## Entry point unico

```bat
00_START_BKS_MASTER.bat
```

Menu interattivo ANSI: avvia, monitora e killa tutti i servizi.

---

## Control Plane — Ecommerce Agent

```bat
python -m ecommerce_automation.app
```

Dashboard: `http://127.0.0.1:8600`

Uso:

- health check Make, Printify, Shopify, OpenAI, Amazon, Telegram;
- agente AI BKS con snapshot completo (catalog, sales_channels, marketing);
- run ledger e log eventi;
- social hub e AI assistant API (`/api/theme-ai-assistant`).

---

## Fase 01 — Catalogo

```bat
01_START_CATALOG_ENGINE.bat
```

App Streamlit: `http://localhost:8501` → pagina `06_Catalogo`

Operazioni chiave:

```bat
python tools\enrich_shopify_catalog.py
```

Output attivi:

- `collezioni_csv/bks_catalog.db` — DB SQLite (fonte di verità)
- `collezioni_csv/collezione 12_06_2026_SHOPIFY_IMPORT_READY_SEO_TAGS_READY.csv` — export Shopify
- `output/bks_ai_index.json` — indice prodotti per AI

---

## Fase 02 — Collezioni

Script diretti (launcher legacy rimosso):

```bat
python tools\create_collections.py --dry-run
python tools\create_collections.py --upsert
python tools\export_collection_plan.py
```

Output:

- `output/bks_collection_payloads_v20.json`
- `output/bks_collection_plan_v20.csv`

Stato: 8 collezioni editorial + 18 product type — tutte live e raggiungibili `200`.

---

## Fase 03 — Metafields e Metaobjects

Script diretti (launcher legacy rimosso):

```bat
python tools\create_metafields.py
python tools\create_metaobjects.py
python tools\populate_metafields.py --resume
```

Output:

- `output/metafield_definitions_log.csv`
- `output/metaobjects_log.csv`
- `output/populate_metafields_log.csv`

---

## Fase 04 — Tema Shopify

Tema live: `202392961362` — "BKS TM04 MEMBER TIER + SHOPPER 17JUN2026"
Sorgente locale: `04_TEMA_SHOPIFY/_merged_tm04/`

Deploy file singolo o lista:

```bat
python scripts\deploy_theme_section.py
```

Deploy push tema completo (nuovo tema draft):

```bat
python scripts\push_draft_theme.py
python scripts\retry_draft_theme.py
```

Checklist tema:

- 8 collezioni editorial con accent color CSS per collezione
- Tutti i template `page.bks-*`, `collection.bks-*`, `product.*` allineati
- Metal tier member area live (`bks-member-dashboard.liquid`)
- Smart account dropdown con tier dot (`bakabo-header.liquid`)
- AI assistant top-right con member context injection
- BKS Shopping Guide live (`page.bks-shopping-guide`)
- Help FAQ in inglese (`page.help-faq`)
- Lingua inglese unica (`locales/it.json` sovrascritto)
- Locale selector rimosso (MutationObserver in header)
- GTM `GTM-PF5Z85KS` attivo
- Footer dark `#0A0A0A` (color_scheme: accent-1)

---

## Fase 05 — Testi e Policy

Cartella: `05_TESTI_POLICY/`

```bat
python scripts\publish_policies.py
```

Referenced da `ecommerce_automation/legal_guardrails.py`.

---

## Fase 06 — Domini, Analytics e Link

Controlli:

- domini `bakabo.club`, `www.bakabo.club`, `account.bakabo.club` — tutti Connected
- GTM `GTM-PF5Z85KS` attivo nel tema live
- GA4 property `483501489` attiva
- Google Merchant Center: richiedere ricontrollo feed/sitemap dopo deploy
- Tutte le pagine policy/FAQ/About/Contact raggiungibili `200`
- Collection e product link senza `404`

Audit:

```bat
python tools\audit_live_site.py
python scripts\check_live_titles.py
python scripts\check_market_prices.py
```

---

## Fase 07 — Deploy e post-publish

1. Pushare sezioni aggiornate: `python scripts\deploy_theme_section.py`
2. Verificare nel Theme Editor (`/admin/themes/202392961362/editor`)
3. Controllare template assignment pagine da Shopify Admin → Pages
4. Lanciare audit link live: `python tools\audit_live_site.py`
5. Richiedere ricontrollo Merchant Center se necessario
6. Fare ordine test end-to-end
7. Aggiornare `00_PROCEDURA/02_STATO_ATTUALE.md`
