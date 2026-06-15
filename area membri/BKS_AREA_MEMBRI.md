# BKS Studio — Area membri
*Struttura confermata — giugno 2026*

---

## Tier system (tag Shopify)

| Tier | Tag | Soglia |
|---|---|---|
| BKS Subscriber | `bks-subscriber` | Account + iscritto newsletter |
| BKS Drop | `bks-drop` | 1 ordine |
| BKS Archive | `bks-archive` | 2+ ordini |

Implementazione: Liquid condizionale su tag cliente. Nessuna app aggiuntiva richiesta.

---

## Contenuti esclusivi per tier

### BKS Subscriber (tutti i membri)
- Wishlist con condivisione link (uso gifting)
- Early access drops — teaser drop successivo: nome · visual · data
- Link referral personale (€10 credito per chi porta + €10 per chi arriva)

### BKS Drop (1 ordine)
- Tutto BKS Subscriber +
- Tracker timeline ordine MTO visivo (In produzione → Stampato → Spedito → Consegnato)
- CTA recensione 7 giorni post-consegna (via Judge.me)
- Cross-sell dalla stessa collection nell'email post-purchase

### BKS Archive (2+ ordini)
- Tutto BKS Drop +
- Early access +24h prima del lancio pubblico
- **BKS Studio Archivio** (`/pages/bks-studio`, accesso solo `bks-archive`):
  - Prompt library parziale — mostra il processo AI, non l'intera library
  - Pattern gallery scartati — "gli scarti che ci piacciono"
  - Process notes — 1 nota per ogni drop su come è stato costruito
  - Download wallpaper — pattern AI in alta risoluzione, uso personale

---

## Pagine member area

| Pagina | URL | Tier minimo |
|---|---|---|
| Dashboard account | `/account/` | tutti |
| I miei ordini + tracker MTO | `/account/orders` | tutti |
| Wishlist | `/account/wishlist` | bks-subscriber |
| Early access drops | `/pages/early-access` | bks-subscriber |
| Referral | `/pages/referral` | bks-subscriber |
| BKS Studio Archivio | `/pages/bks-studio` | bks-archive |
| Profilo + GDPR | `/account/` | tutti |

---

## Referral — meccanica

- Link personale generato per ogni bks-subscriber
- €10 credito per chi porta un nuovo cliente
- €10 credito per chi arriva al primo ordine
- Crediti non scadono entro 12 mesi
- Gestione manuale via metafield cliente Shopify fino a 50 acquirenti
- Scalare a LoyaltyLion o Smile.io oltre i 50 acquirenti

---

## Loyalty — punti

- 1€ speso = 1 punto
- 100 punti = €5 credito
- Bonus: recensione con foto +5 punti · primo acquisto +20 punti · referral convertito +50 punti
- Gestione manuale via metafield fino a 50 acquirenti

---

## Note implementazione

- Liquid condizionale: `{% if customer.tags contains 'bks-archive' %}`
- Nessun portale separato — layer di contenuto sul tema Dawn esistente
- Free shipping permanente: attivo a livello account per bks-archive
- Email VIP per nuovo bks-archive: manuale dal fondatore, non automatizzata
