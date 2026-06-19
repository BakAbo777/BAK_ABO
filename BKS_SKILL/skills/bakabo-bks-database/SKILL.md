---
name: BKS Database Maintenance
version: 2.0
status: active
trust_gate: trust_foundation
owner: Roberto Picchioni
last_updated: 2026-06-19
---

# BKS Database Maintenance Skill

## Two layers

| Layer | Module | What it holds |
|---|---|---|
| **SQLite operational DB** | `ecommerce_automation/bks_db.py` | 53 tables from all CSV/JSON — products, collections, payloads, connectors |
| **Asset Registry** | `ecommerce_automation/bks_asset_db.py` | All visual assets across all drives — photos, NFT, AI art, videos, portraits |

---

## Layer 1 — SQLite DB (`bks_db`)

**Location:** `output/bks_database.sqlite`

```python
from ecommerce_automation.bks_db import bks_db
bks_db.query("SELECT handle, title FROM bks_collection_plan_v20 LIMIT 5")
bks_db.get_table("live_shopify_products")
bks_db.list_tables()   # 53 tables
bks_db.rebuild()       # reimports all output/*.csv and key JSONs
```

**Key tables:**
- `bks_collection_plan_v20` — 25 rows: 8 collections + 17 product types
- `live_shopify_products` — 203 products (refreshed by `catalog_live_sync.py`)
- `live_printify_products` — 674 products in shop 12030061
- `agent_os_connector_registry` — 38 API connectors

**Rules:** rebuild after any batch CSV update. Never edit `.sqlite` directly. Archive zone: `output/99_ARCHIVIO/`.

---

## Layer 2 — Asset Registry (`bks_asset_db`)

```python
from ecommerce_automation.bks_asset_db import query, style_dna, summary

summary()                                              # all source paths + counts
query(asset_type="product_photo", collection="marker") # catalog photos by collection
query(asset_type="nft", series="2023 BAK ABO", ext=".png", limit=10)
query(asset_type="ai_art", series="UNDERGROUND 00 A")
style_dna(collection="Glyph")                         # Basquiat/TEXT affinity + notes
```

**Sources:**
| Source | Path | Count |
|---|---|---|
| Catalog photos | `I:\BAK ABO\output\foto collezioni\00_originals_catalogued` | 858 (686 published) |
| Image Factory | `E:\BAKSITO\...\BAKABO_IMAGE_FACTORY_v1.1\output\source` | 359 mockups / 46 products |
| AI artworks | `E:\IMMAGINI AI` | 2 362 imgs / 49 series |
| NFT artworks | `E:\NFT` | 12 711 imgs / 135 dirs |
| Social videos | `E:\NFT\VIDEO FACEBOOK` | 16 MP4 |
| AI videos | `E:\IMMAGINI AI\video` | 18 MP4 |
| Portraits | `E:\RITRATTI` | 11 imgs — **reserved, future collection** |

**BakAbo visual DNA:** urban graphic, pop art, art brut, neo-impressionism, surrealism.
References: Basquiat, Mirò, Escher, De Chirico. NFT archive = POD print/texture library.
Collection→art series affinity: `bks_asset_db.BAKABO_STYLE_DNA["collection_affinity"]`

---

## Archive
```
output/99_ARCHIVIO/
  logs/              — process logs
  stale_reports/     — superseded audits
  run_batches/       — archived foto-collezioni runs
  collection_plan_v19/ — superseded by v20
```
