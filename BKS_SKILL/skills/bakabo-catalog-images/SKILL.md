# bakabo-catalog-images

Catalog image generation skill for BKS Studio / bakabo.club.
Uses Printify mockups as the authoritative product reference.
AI is free to create the scene — the product itself is immutable.

---

## Core rules

| What AI can do | What AI cannot do |
|----------------|-------------------|
| ✅ Change background, environment, scene | ❌ Change product type or garment category |
| ✅ Change lighting, atmosphere, shadows | ❌ Change the print/artwork/texture on the product |
| ✅ Change framing, composition, angle | ❌ Change product colors or material appearance |
| ✅ Change staging (flat lay, studio, location) | ❌ Add any text, labels, logos, or typography |
| ✅ Change mood and visual narrative | ❌ Substitute a different garment/object |

---

## HARD RULES — Never override

1. **No text on images** — zero typography, labels, logos, overlays, watermarks anywhere.
2. **Product type preserved** — if the mockup shows a hoodie, the output must show a hoodie.
3. **Texture/print preserved** — every detail of the artwork applied to the product must remain identical.
4. **Source integrity** — always start from the Printify mockup; never generate a product from scratch.
5. **Patches cataloged** — every artwork/print used in a collection product must be recorded in `printify_uploads` with its `used_in_collections` field populated.

---

## Pipeline

```
Printify API
  └─ /uploads.json          → artwork patches (designs applied to products)
  └─ /catalog/{id}.json     → blueprint (product model: brand, model, dimensions)
  └─ /shops/{id}/products   → shop products with mockup images + print_areas (patch refs)

sync_printify_library.py
  ├─ Downloads textures/patches  → output/printify_library/textures/{id}_{filename}
  ├─ Downloads mockups           → output/printify_library/mockups/{collection}/{handle}/
  ├─ Catalogs in DB              → printify_uploads, printify_blueprints, printify_products
  └─ Cross-references patches    → printify_uploads.used_in_collections updated per collection

generate_catalog_images.py
  ├─ Reads products + blueprints from DB
  ├─ Uses Printify mockup as reference (product type + texture preserved)
  ├─ AI free to create: background, lighting, framing, environment
  ├─ Model: gpt-image-1 images.edit
  └─ Records output as asset_type='catalog_ai' in DB

prepare_catalog_images.py  (fallback — no AI)
  └─ Copies Printify mockups AS-IS, resizes to 2000px for catalog use
```

---

## DB tables

| Table | Content |
|-------|---------|
| `printify_uploads` | Artwork patches: `printify_id`, `filename`, `url`, `local_path`, `used_in_collections` (JSON array) |
| `printify_blueprints` | Product models: `blueprint_id`, `brand`, `model`, dimensions |
| `printify_products` | Shop products: `blueprint_id`, `upload_ids_json` (patches used), `mockup_urls_json`, `local_mockup_paths_json`, `collection` |
| `assets` | Generated outputs registered as `catalog_ai` or `catalog_mockup` |

### Patch → collection query
```sql
-- Which patches are used in bks-hours?
SELECT pu.printify_id, pu.filename, pu.local_path
FROM printify_uploads pu
WHERE json_extract(pu.used_in_collections, '$') LIKE '%bks-hours%';

-- All patches per collection
SELECT collection, upload_ids_json
FROM printify_products
WHERE collection = 'bks-hours';
```

---

## Collection environments (AI prompt data)

| Collection | Background | Lighting | Mood |
|------------|-----------|---------|------|
| Hours | Dark raw concrete | Hard lateral single source | Urban, contemplative |
| Glyph | Matte black plane | Flat studio ring light | Graphic, coded |
| Marker | Rough paper / iron | Hard lateral, sharp shadow | Gestural, raw |
| Riviera | Travertine / linen | Golden hour from right | Resort, mediterranean |
| Pulse | Dark tiles / geometric | Front ring light | Optical, kinetic |
| Token | Reflective plexiglass | Low-key neon accent | Arcade, digital |
| Flag | White studio | Flat uniform | Pop, graphic |
| Origin | Light stone / linen | Soft overcast | Narrative, artisanal |

---

## Shot variants (2 default per product)

| Variant | Framing |
|---------|---------|
| `front_editorial` | Centered front view, full product, editorial proportions |
| `three_quarter` | Three-quarter angle, front+side, dynamic composition |
| `detail_texture` | Extreme close-up of print and fabric texture |
| `flat_lay` | Overhead composition, product laid flat |

---

## Commands

```bash
# 1. Sync Printify library (patches + mockups + blueprints → DB + disk)
python scripts/sync_printify_library.py

# 2. Generate AI catalog shots (free scene, preserved product+texture)
python scripts/generate_catalog_images.py
python scripts/generate_catalog_images.py --collection bks-hours --shots 2
python scripts/generate_catalog_images.py --dry-run

# 3. Check which patches are cataloged per collection
python -c "
from bks_assets import active_catalog_db
from ecommerce_automation import catalog_db
db = active_catalog_db()
print(catalog_db.printify_library_summary(db))
"

# Fallback (no AI, use mockups directly)
python scripts/prepare_catalog_images.py
```

---

## Pre-publish gate

Before any AI-generated catalog image goes live:
1. `product_type_preserved: true` in asset meta_json
2. `texture_preserved: true` in asset meta_json
3. `no_text: true` in asset meta_json
4. Anatomy check if a model is shown (no extra limbs)
5. Not in `rejected_assets` table
6. Source mockup exists in `printify_products.local_mockup_paths_json`
