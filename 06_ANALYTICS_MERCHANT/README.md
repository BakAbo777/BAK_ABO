# Fase 06 — Analytics, Merchant Center e Link

Aggiornato 17 Giugno 2026.

Obiettivo: GA4, GTM, Merchant Center e audit link coerenti con il tema live.

## IDs

| Elemento | Valore |
| --- | --- |
| GA4 Property | `bakabo-9a8c5` — ID `483501489` |
| GTM Container | `GTM-PF5Z85KS` — live nel tema TM04 |
| Merchant Center | `5295165689` — account `bakabo.club` |

## Audit live

```bat
python tools\audit_live_site.py
python scripts\check_live_titles.py
python scripts\check_market_prices.py
```

## Azioni Merchant Center in sospeso

1. **Inventario locale mancante**: BKS non ha stock fisico — disattivare local inventory ads/free local listings in Merchant Center.
2. **Pagine prodotto non disponibili**: prodotti eliminati non ancora reindicizzati. Dopo deploy pulito: risincronizzare feed Shopify → richiedere nuovo controllo sito.
3. **Attributi apparel**: completare `size`, `color`, `gender`, `age_group` nel feed. Gestiti da metafield CSV.
4. **Mercati**: attivi solo EU + US. India/Corea in pausa fino a shipping e checkout configurati.

## Nota crawl

Se `audit_live_site.py` restituisce `429 Verifying your connection`, il sito sta filtrando traffico automatico. Verificare manualmente da browser le pagine critiche, poi riprovare.

## Setup Google Merchant (task pendente)

Vedi `memory/project_bks_pending.md` per i passi di configurazione Google Merchant Center non ancora completati.
