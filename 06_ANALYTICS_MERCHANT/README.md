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

Nota crawl: se `tools/audit_live_site.py` restituisce `429 Verifying your connection`, il sito sta proteggendo il traffico automatico. Attendere e rilanciare con calma, oppure verificare manualmente da browser le pagine critiche.
