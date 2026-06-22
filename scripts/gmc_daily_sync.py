"""GMC Daily Sync — verifica feed Google Merchant e segnala anomalie prezzi.

Eseguire ogni mattina (schedulato o manuale):
  python scripts/gmc_daily_sync.py

Output:
  - Stampa report sintetico
  - Scrive output/gmc_sync_report.json
  - Alert su prodotti con prezzo fuori dal price ladder approvato
"""
from __future__ import annotations
import os, json, requests, urllib3
from pathlib import Path
from datetime import datetime

urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]:
        os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
HDR    = {"X-Shopify-Access-Token": TOKEN}
API    = f"https://{DOMAIN}/admin/api/2025-01"

# Approved price ladder (EUR, rounded)
PRICE_LADDER = {35,39,45,49,55,59,65,69,75,79,85,89,95,99,105,109,115,119,125,129,135,139}

# Min/max per product type
PRICE_RANGES = {
    "Sneakers":              (75, 105),
    "Backpack":              (75,  95),
    "Swim Trunks":           (45,  65),
    "Puffer":                (109, 139),
    "Windbreaker":           (95,  125),
    "Travel Bag":            (85,  115),
    "Swimwear":              (55,  75),
    "Racerback Dress":       (55,  75),
    "Athletic Shorts":       (45,  65),
    "Lounge Pants":          (55,  75),
    "Pullover Hoodie":       (65,  85),
    "Hawaiian Shirt":        (65,  85),
    "Slipper":               (35,  55),
    "Cut & Sew Tee":         (45,  65),
    "Flip Flops":            (35,  55),
    "Beach Towel":           (39,  55),
    "All Over Prints":       (45, 139),  # catch-all for puffer/hawaiian/one-piece
}

def fetch_all_products():
    products = []
    url = f"{API}/products.json"
    params = {"limit": 250, "status": "active", "fields": "id,title,product_type,variants"}
    while url:
        r = requests.get(url, headers=HDR, params=params, verify=False)
        data = r.json()
        products.extend(data.get("products", []))
        link = r.headers.get("Link", "")
        url = None
        if 'rel="next"' in link:
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.split(";")[0].strip().strip("<>")
                    params = {}
                    break
    return products

def check_price(price_str: str, product_type: str) -> tuple[bool, str]:
    try:
        price = round(float(price_str))
    except (ValueError, TypeError):
        return False, "price parse error"

    # Check if on ladder
    nearest = min(PRICE_LADDER, key=lambda x: abs(x - price))
    if abs(nearest - price) > 2:
        return False, f"${price} not on approved ladder (nearest: ${nearest})"

    # Check range for product type
    for pt_key, (min_p, max_p) in PRICE_RANGES.items():
        if pt_key.lower() in product_type.lower() or product_type.lower() in pt_key.lower():
            if price < min_p:
                return False, f"${price} below minimum ${min_p} for {pt_key}"
            if price > max_p:
                return False, f"${price} above maximum ${max_p} for {pt_key}"
            break

    return True, "ok"

print(f"GMC Daily Sync — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("Fetching active Shopify products...")

products = fetch_all_products()
print(f"Products fetched: {len(products)}")

alerts = []
ok_count = 0
skipped = 0

for p in products:
    ptype = p.get("product_type", "")
    variants = p.get("variants", [])
    if not variants:
        skipped += 1
        continue

    # Check first variant price (all variants of same product should have same base price or similar)
    price_str = variants[0].get("price", "0")
    ok, reason = check_price(price_str, ptype)

    if not ok:
        alerts.append({
            "id": p["id"],
            "title": p["title"],
            "product_type": ptype,
            "price": price_str,
            "issue": reason,
        })
    else:
        ok_count += 1

print(f"\nRESULT:")
print(f"  OK:      {ok_count}")
print(f"  ALERTS:  {len(alerts)}")
print(f"  Skipped: {skipped} (no variants)")

if alerts:
    print(f"\nPRICE ALERTS ({len(alerts)}):")
    for a in alerts:
        print(f"  [{a['product_type']}] {a['title'][:45]} — ${a['price']} — {a['issue']}")
else:
    print("\nAll prices within approved ladder. No alerts.")

# Write report
report = {
    "timestamp": datetime.now().isoformat(),
    "total_active": len(products),
    "ok": ok_count,
    "alerts": len(alerts),
    "skipped": skipped,
    "price_alerts": alerts,
}
out = ROOT / "output" / "gmc_sync_report.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nReport saved: {out}")
