"""
Set excluded_destination=free_local_listings,local_inventory_ads on all active products.
This tells GMC to never expect local inventory data for BKS (online-only / POD store).
"""
import os, time, requests, urllib3
from pathlib import Path
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
BASE   = f"https://{DOMAIN}/admin/api/2025-01"
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

EXCLUDED_VALUE = "free_local_listings,local_inventory_ads"

# Fetch all active products
products = []
url = f"{BASE}/products.json?status=active&limit=250&fields=id,title,status"
while url:
    r = requests.get(url, headers=HDR, verify=False, timeout=30)
    data = r.json()
    products.extend(data.get("products", []))
    link = r.headers.get("Link", "")
    url = None
    for part in link.split(","):
        if 'rel="next"' in part:
            url = part.split("<")[1].split(">")[0]
            break

print(f"Active products: {len(products)}")

def shopify_get(url):
    for attempt in range(5):
        r = requests.get(url, headers=HDR, verify=False, timeout=15)
        if r.status_code == 429:
            time.sleep(2 ** attempt)
            continue
        return r
    return r

def shopify_post(url, payload, method="post"):
    for attempt in range(5):
        fn = requests.post if method == "post" else requests.put
        r = fn(url, json=payload, headers=HDR, verify=False, timeout=15)
        if r.status_code == 429:
            time.sleep(2 ** attempt)
            continue
        return r
    return r

ok = err = skip = 0
for p in products:
    pid = p["id"]
    rm = shopify_get(
        f"{BASE}/products/{pid}/metafields.json?namespace=google_shopping&key=excluded_destination"
    )
    existing = rm.json().get("metafields", [])
    if existing and existing[0].get("value") == EXCLUDED_VALUE:
        skip += 1
        time.sleep(0.5)
        continue

    if existing:
        mid = existing[0]["id"]
        r2 = shopify_post(
            f"{BASE}/products/{pid}/metafields/{mid}.json",
            {"metafield": {"id": mid, "value": EXCLUDED_VALUE, "type": "single_line_text_field"}},
            method="put"
        )
    else:
        r2 = shopify_post(
            f"{BASE}/products/{pid}/metafields.json",
            {"metafield": {
                "namespace": "google_shopping",
                "key": "excluded_destination",
                "value": EXCLUDED_VALUE,
                "type": "single_line_text_field"
            }}
        )

    if r2.status_code in (200, 201):
        ok += 1
    else:
        print(f"  ERR {pid}: {r2.status_code} {r2.text[:80]}")
        err += 1

    if (ok + err) % 10 == 0:
        print(f"  ... {ok} updated, {err} errors")
    time.sleep(1.0)

print(f"\nDone: {ok} updated, {skip} already set, {err} errors")
print("GMC will pick up excluded_destination on next feed refresh (up to 24h).")
