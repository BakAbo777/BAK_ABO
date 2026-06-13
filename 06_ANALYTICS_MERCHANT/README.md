# Fase 06 — Analytics, Merchant Center e Link

Obiettivo: verificare che il sito pubblicato, GA4/GTM e Merchant Center siano coerenti dopo il deploy.

Nel cruscotto:

```bat
02_START_COLLECTIONS_DASHBOARD.bat
```

Aprire tab:

- `06 Analytics`

Stato registrato:

- GA4 property `bakabo-9a8c5`
- Property ID `483501489`
- GTM `GTM-PF5Z85KS`
- Merchant Center account `5295165689`

Nota Merchant Center: molte pagine prodotto non disponibili sono tracce di prodotti eliminati dalla collezione ma non ancora reindicizzati da Google. Dopo pulizia feed/sitemap, richiedere il nuovo controllo del sito.

Aggiornamento 13/06/2026:

- Prima azione: correggere "Dati di inventario locale mancanti". Se BakAbo/BKS non ha stock fisico in negozio, disattivare local inventory ads/free local listings in Merchant Center. In alternativa caricare un feed inventario locale completo con `id`, `store_code`, `availability` e `quantity`.
- Seconda azione: correggere "Pagina del prodotto non disponibile" rimuovendo prodotti vecchi dal feed, risincronizzando Shopify e verificando URL desktop/mobile.
- Terza azione: completare attributi apparel per Merchant: size, color, gender, age_group. Nel tema e stato aggiunto `bks-product-editorial-care.liquid` per rendere size guide, curation, spedizioni e resi visibili su ogni PDP.
- Quarta azione: tenere attivi solo i paesi con Shopify shipping, Merchant destination, checkout, resi e lingua coerenti. India/Corea vanno tenute in pausa se non completamente configurate.

Nota crawl: se `tools/audit_live_site.py` restituisce `429 Verifying your connection`, il sito sta proteggendo il traffico automatico. Attendere e rilanciare con calma, oppure verificare manualmente da browser le pagine critiche.
