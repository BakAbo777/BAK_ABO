# ECAMP Control Plane - BakAbo

## Decisione architetturale

La direzione migliore per BakAbo non e' un semplice starter kit Flask, ne' una
riscrittura immediata di tutto il progetto. Il livello corretto e' un control
plane operativo sopra il sistema gia' funzionante.

ECAMP deve coordinare:

- Shopify come storefront e sistema commerciale principale.
- Printify come motore POD: draft, varianti, publish, fulfillment.
- Make come orchestratore esterno per automazioni social, alert e flussi no-code.
- OpenAI/Image Factory come generatore e QA immagini.
- Google/Merchant/Analytics come validazione post-deploy.
- Amazon e marketplace minori come estensioni, non come blocco iniziale.

## Principi

1. Non duplicare prodotti Printify: ogni run deve avere idempotency key e retry.
2. Non spostare subito gli script funzionanti: prima orchestration, poi migrazione.
3. Separare health check da azioni mutanti: leggere e pubblicare sono flussi diversi.
4. Make non sostituisce il pannello: riceve trigger e restituisce stati.
5. Printify e Shopify devono essere trattati come sorgenti operative reali, non come CSV passivi.

## Fasi ECAMP

1. Config & Make setup
2. Import & Printify sync
3. Images base
4. AI content & video
5. Shopify & Printify publish
6. Google validation
7. Social & marketplaces
8. Amazon configuration

## Strato tecnico attuale

Cartella:

```text
ecommerce_automation/
```

Componenti principali:

```text
core/state_manager.py
core/run_ledger.py
core/orchestrator.py
core/http_client.py
services/printify_client.py
services/make_webhook_handler.py
services/shopify_client.py
phases/
```

## Prossimo salto di qualita

1. Aggiungere tabella `external_references`:
   - local product handle
   - printify_product_id
   - shopify_product_id
   - last_publish_status
   - last_error

2. Implementare `phase_import` come riconciliazione:
   - legge catalogo attivo
   - cerca prodotto Printify esistente per handle/title/SKU
   - crea bozza solo se manca
   - salva `printify_product_id`

3. Implementare `phase_shopify` come publish retry-safe:
   - prende `printify_product_id`
   - chiama publish Printify
   - verifica prodotto Shopify
   - aggiorna stato senza duplicare

4. Implementare `phase_social`:
   - costruisce payload standard
   - invia a Make
   - riceve callback su `/api/make/inbound`

5. Rendere la dashboard un centro operativo:
   - service health live/manuale
   - run ledger
   - ultimi errori
   - retry per fase/prodotto
   - link ai launcher esistenti

