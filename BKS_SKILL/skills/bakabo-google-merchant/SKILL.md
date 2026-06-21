---
name: bakabo-google-merchant
description: >
  Google Merchant Center + Google & YouTube channel management for BakAbo/BKS Studio.
  Use this skill for: feed quality issues, product approval status, missing attributes,
  identifier_exists, age_group, gender, condition metafields, local inventory settings,
  GTIN/MPN flags, Korea/India market issues, feed refresh triggers, Not Approved analysis.
  Works with: bakabo-commercial-strategy, bakabo-photo-studio.
metadata:
  type: skill
  version: "1.2"
  created: "2026-06-18"
  updated: "2026-06-20"
---

# BakAbo — Google Merchant Center Skill

## 1. Store Identity

| Field | Value |
|---|---|
| GMC Account | `5295165689` (bakabo.club) |
| Shopify Google channel | `admin.shopify.com/store/bakabo/apps/google/overview` |
| Google Ads | Active |
| Feed source | Shopify → Google & YouTube channel (auto-sync) |

---

## 2. Feed Attribute Metafields (namespace `mm-google-shopping`)

All set via `scripts/fix_google_merchant_attributes.py`:

| Key | Value | Scope | Status |
|---|---|---|---|
| `age_group` | `adult` | All 203 products | ✅ 18/06/2026 |
| `gender` | `male`/`female`/`unisex` | Per product type | ✅ 18/06/2026 |
| `condition` | `new` | All 203 products | ✅ 18/06/2026 |
| `identifier_exists` | `no` | All 203 products (POD, no GTIN) | ✅ 18/06/2026 |

### Gender logic (auto-detected by `fix_google_merchant_attributes.py`):
- `female`: handles/types matching `racerback-dress`, `one-piece`, `womens-tee`, `women`, `bikini`, `swimsuit`, `dress`
- `male`: handles/types matching `swim-trunk`, `mens-tee`
- `unisex`: all others (puffers, windbreakers, hoodies, sneakers, bags, etc.)

### Distribution (203 products):
- male: 34 | female: 43 | unisex: 126

---

## 3. Critical Issues & Fixes

### P0: identifier_exists = no (POD products — no GTIN)
BKS products are Print-on-Demand via Printify. They have no barcode/GTIN.
Without `identifier_exists = no`, Google rejects ~63% of listings as "Not Approved".
**Fix**: `python scripts/fix_google_merchant_attributes.py` (sets all 4 attributes).

### P1: Local Inventory Mancante (76% of listings)
**Cause**: NOT Shopify (local inventory sync is already OFF, 0 of 1 locations active).
Root cause: Google Business Profile has a physical location "Sede — Via Monte Vettore 1" registered.
Google sees this GBP location and expects local inventory data for it.
**Fix (manual — Google Business Profile)**:
> `business.google.com` → Sede → Impostazioni → Cambia tipo → **"Area di servizio"** (Service area business)
> This tells Google there is no physical retail point of sale → eliminates the local inventory requirement.
> DO NOT use Shopify → Google & YouTube settings (already correctly set to OFF).

### P2: Pagina prodotto non disponibile (27.4%)
**Cause**: Google has cached old variant URLs (pre-rename: "Suola nera" → "Onyx Sole").
**Fix**: Wait 24-48h for Google re-crawl after feed bump. No action needed.
Active products: 201/203. 2 draft products contribute minimally.

### P3: Korea business registration
**Cause**: South Korea market active in GMC without Korean registration number.
**Fix (manual — UI)**:
> GMC → Settings → Shipping & Returns → Remove South Korea
> OR Shopify → Google & YouTube → Markets → Remove Corea del Sud

### P4: GTINs (medium-term)
Google suggests adding GTINs for better ranking. For POD: `identifier_exists=no` is correct.
If BKS creates its own product line with physical barcodes, add GTINs then.

---

## 4. Feed Stats

### 20/06/2026 — Current state

| Metric | Value |
|---|---|
| Total products | 35.1K ("Numero limitato" — visible but quality-limited) |
| Approvato | 0 |
| Numero limitato | 35.1K |
| GMC Account status | Active (no misrepresentation suspension) |
| Google Ads | Active |

**Active alerts (Merchant Center → Avvisi → Problemi):**

| Problema | Quantità | Causa | Fix |
|---|---|---|---|
| Taglia mancante | 10.2K | Variant option non mappata al feed | Verificare nomi opzioni varianti (Italian?) |
| Colore mancante | 8.72K | Variant option non mappata al feed | Verificare nomi opzioni varianti |
| Età mancante | 8.85K | age_group metafield mancante | Script `_fix_google_feed_attributes.py` (20/06) |
| Genere mancante | 8.1K | gender metafield mancante | Script `_fix_google_feed_attributes.py` (20/06) |

### 18/06/2026 — After first metafield fix

| Metric | Value |
|---|---|
| Total listings | 152,887 (products × variants × markets) |
| Approved | 56,369 (36.9%) |
| Not Approved | 96,441 (63.1%) |
| Namespace used | `mm-google-shopping` |

### Metafield namespace issue
Two scripts exist with different namespaces:
- `scripts/fix_google_merchant_attributes.py` → namespace `mm-google-shopping` (Shopify Google & YouTube app)
- `scripts/_fix_google_feed_attributes.py` → namespace `google` (run 20/06/2026)

**Active feed source**: Possibly **Wixpa Google Shopping** app (installed in Shopify) rather than native Google & YouTube channel. Wixpa may have its own attribute mapping. Check Wixpa app settings if metafield fixes don't resolve alerts after 48h.

### 20/06/2026 — Second fix run (namespace `google`)
- `age_group = adult` added to 125/202 products
- `gender = unisex` added to 72/202 products
- 207 errors — `google` namespace may be reserved by Shopify for some products; old mm-google-shopping values already present
- **Variant options confirmed**: all products use `size` and `color` as option names (English) — GMC should map these from variants automatically

### Next action (24-48h):
Check Merchant Center again. If Taglia/Colore still missing → open **Wixpa Google Shopping** in Shopify Apps → check attribute mapping for Size and Color variant options → verify they are enabled in the feed.

---

## 5. Scripts

| Script | Action |
|---|---|
| `scripts/fix_google_merchant_attributes.py` | Sets age_group, gender, condition, identifier_exists for all products |
| `scripts/full_channel_sync.py` | Full sync: Shopify + Printify + GMC spot-check + feed bump |
| `scripts/migrate_series_tags.py` | (done) Migrated series:* → archive:* |

**Run full attribute fix**:
```bash
python scripts/fix_google_merchant_attributes.py
```

**Run channel sync** (reports diff, bumps feed):
```bash
python scripts/full_channel_sync.py
```

---

## 6. Automation — Master Agent Integration

The `ecommerce_automation/google_merchant_monitor.py` module exposes `payload()` which returns the known GMC issues.

In `master_agent.py`, the agent can respond to queries about:
- "GMC status", "merchant center", "google shopping", "prodotti non approvati"
- "feed quality", "identifier_exists", "age group", "gender"

**Scheduled refresh**: Run `full_channel_sync.py` daily after the 12:00 CET agent refresh cron.

---

## 7. Local Inventory — How to Disable (Manual Steps)

The "Local inventory: 1" tab in Shopify Google & YouTube is causing 76% of listings to show
"Dati di inventario locale mancanti". To remove:

1. Go to `admin.shopify.com/store/bakabo/apps/google/overview`
2. Click on **Local inventory** tab
3. Click the existing entry → **Delete** or **Disable**
4. Save changes

This will immediately remove the "local inventory missing" warning from GMC diagnostics.

---

## 8. Feed Refresh Cadence

After any product data change, the GMC feed updates within:
- Shopify → Google channel sync: **15-60 minutes**
- GMC crawl + approval update: **24-72 hours**
- Use `full_channel_sync.py` step 5 (feed bump via updated_at touch) to accelerate.
