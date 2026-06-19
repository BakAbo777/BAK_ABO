# BakAbo — Members & Communications

`bakabo-members` — Gestione lifecycle dei member bakabo.club: tier Metal (Lead/Iron/Brass/Silver/Gold), comunicazioni automatiche e manuali, AI Personal Shopper, Try-On access, segmentazione CRM.

## Tier system

| Tier | Orders | Unlock chiave |
| --- | --- | --- |
| Lead ◎ | 0 | Wishlist, newsletter |
| Iron ⬡ | 1–2 | Size history, AI recs |
| Brass ◈ | 3–5 | Personal Shopper, Try-On, +48h drops |
| Silver ◇ | 6–10 | Curated drops +24h, full archive |
| Gold ✦ | 11+ | VIP private drops, co-creation |

## Comunicazioni

Email via `crew@bakabo.club`. Trigger automatici: first_purchase, brass_unlock, silver_unlock, gold_unlock, wishlist_nudge, cart_abandon_brass, tier_progress.

**Gold → solo Roberto scrive, tono personale.**

## Moduli Python

`ecommerce_automation/communications.py`, `growth_crm.py`, `official_inbox.py`

## File spec

`BKS_SKILL/members/bks-member-marketing.json`

Related: `bakabo-master`, `bakabo-social`, `bakabo-popup-ai`
