# ECAMP - Ecommerce Automation Control Plane

Nuova interfaccia unica per coordinare BakAbo/BKS sopra gli strumenti gia'
presenti: catalog engine, collection dashboard, metafields runner, image
factory, Shopify, Printify, Make, social, Avatar Production e futuri
marketplace.

## Avvio locale

```bat
python -m ecommerce_automation.app
```

Dashboard:

```text
http://127.0.0.1:8600
```

Il launcher principale `Start_Master.bat` ora punta a questa interfaccia.
I cruscotti Streamlit legacy restano disponibili dai rispettivi file finche
non vengono spostati in `old`.

## Variabili ambiente principali

Il pannello legge il file `.env` nella root del progetto.

```text
SHOPIFY_MYSHOPIFY_DOMAIN=11628e-2.myshopify.com
SHOPIFY_ADMIN_TOKEN=<shopify-admin-token>
SHOPIFY_API_VERSION=2025-01
PRINTIFY_API_TOKEN=<printify-token>
PRINTIFY_SHOP_ID=<printify-shop-id>
PRINTIFY_SHOP_TITLE=bakabo.club
MAKE_WEBHOOK_URL=<make-webhook-url>
MAKE_WEBHOOK_SECRET=<make-webhook-secret>
OPENAI_API_KEY=<openai-api-key>
```

## Cosa contiene

- `core/state_manager.py`: stato persistente delle 9 fasi.
- `core/run_ledger.py`: registro run con idempotency key.
- `core/orchestrator.py`: esecuzione controllata delle fasi.
- `core/http_client.py`: sessione HTTP con retry/backoff per API esterne.
- `services/printify_client.py`: shops, products, publish, orders.
- `services/make_webhook_handler.py`: webhook outbound/inbound Make.
- `services/shopify_client.py`: health Admin API Shopify.
- `phases/`: moduli fase con agganci ai servizi reali.
- `avatar_production.py`: standard operativo bakabo-avatar-production per
  script, immagini 9:16, HeyGen export e delivery metadata.
- `skill_registry.py`: indice automatico delle skill `docs/*_SKILL.md`, con
  CSV e markdown di controllo per project management.

## Fasi operative

1. Config & Make setup
2. Import & Printify sync
3. Images base
4. AI content & video
5. Shopify & Printify publish
6. Google validation
7. Social & marketplaces
8. Amazon configuration
9. Avatar production
10. Project skill registry

Questo strato convive con i launcher esistenti. La migrazione consigliata e'
progressiva: prima stato e health, poi Printify/Make, poi publish retry-safe.

## Nota importante

ECAMP non sostituisce subito Streamlit, Flask o gli script esistenti. Li
coordina. La riscrittura completa del backend ha senso solo dopo avere
stabilizzato idempotenza, log eventi e API contracts.
