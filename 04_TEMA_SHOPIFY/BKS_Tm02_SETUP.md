# BKS_Tm02 — Setup post-import

Base: BKS_V21 (Dawn 15.4.1). Fusione V21 + BKS_Tm01.

## Fix e modifiche

| Cosa | Dettaglio |
|---|---|
| `sections/footer-group.json` | **FIX BLOCCANTE** — rimosso commento `/* */` che invalidava il JSON (l'import sarebbe fallito) |
| `sections/header-group.json` | Ricostruito: announcement bar (3 messaggi made-to-order) + app block Parcel Panel e Google recuperati dall'export precedente. Il widget Judge.me che viveva nell'header Dawn non è stato recuperato: le recensioni stanno in `bks-trust-reviews` |
| `layout/theme.liquid` | header-group ora renderizzato SOPRA l'header custom (announcement in cima) |
| `snippets/bakabo-header.liquid` | Nav desktop: dropdown COLLECTIONS con le 8 collezioni + tagline, hover/focus accessibile. Catalog → `/collections/all` |
| `sections/bks-collection-signal.liquid` | Aggiunta subnav a blocchi (Apparel / Swim / Accessories / Editorial), link vuoto = collezione stessa |
| 8 × `collection.bks-*.json` | Subnav (4 blocchi) inserita in ogni template |
| `sections/bks-collections-index.liquid` | Portata da Tm01 — indice tipografico numerato |
| `templates/list-collections.json` | Riscritto: solo gli 8 mondi con tagline |
| `templates/index.json` | `bks-planet-orbit` rimosso dalla home; la nuova scheda editoriale usa `page.bks-planet-collections-orbit` e va linkata da EDITORIAL. Apre `bks-impact-home`, `bks-collections-index` al posto del vecchio collection-list-v2 |
| `sections/bks-impact-home.liquid` | Corretto nome schema (era "BKS editorial matrix" per copia-incolla) |

## Il problema "tutto su default" — mappa assegnazioni

Il problema nasce quando più collezioni/pagine condividono lo stesso template: modificarne una le modifica tutte. La soluzione è già nel tema — ogni entità va agganciata al SUO template in admin (pannello a destra → Theme template):

**Collezioni hub (8):**
`bks-hours → bks-hours` · `bks-folklore → bks-folklore` · `bks-glyph → bks-glyph` · `bks-marker → bks-marker` · `bks-riviera → bks-riviera` · `bks-pulse → bks-pulse` · `bks-token → bks-token` · `bks-flag → bks-flag`

**Collezioni categoria** → template omonimo già presente: `sneakers`, `swimwear`, `outerwear`, `backpack`, `travel-bag`, `lounge-pants`, `pullover-hoodie`, `windbreaker`, `puffer-jacket`, `athletic-shorts`, `one-piece-swimsuit`, `swim-trunks`, `flip-flop`, `cozy-slipper`, `racerback-dress`, `womens-tee`

**Pagine:** `about → about` · `help/FAQ → help-faq` · `policy → policy` · `planet orbit → bks-planet-collections-orbit`

**Restano su Default (intenzionale):** "New Arrivals", "AVADA - Best Sellers", "Digital Goods VAT Tax".

Nota: il carattere per-collezione del signal arriva dal metaobject `bks_collection` (campi `name`, `tagline`, `color_hex`) con fallback su titolo/descrizione collezione. Compila i metaobject per le 8 collezioni e ogni hub avrà nome, tagline e colore accent propri senza toccare il codice.

## Subnav delle 8 collezioni
I 4 link sono nel theme editor di ogni template. Link vuoto = punta alla collezione. Imposta:
- Tag URL (`/collections/bks-hours/type-swimwear`, richiede tag sui prodotti), oppure
- Sotto-collezioni (`/collections/bks-hours-swim`)
- Editorial → pagina campagna della collezione
