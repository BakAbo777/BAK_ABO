"""Check alt texts for products in BKS Origin collection."""
import os, requests, urllib3, time
urllib3.disable_warnings()  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

# Find BKS Origin collection by handle
r = requests.get(f"{BASE}/custom_collections.json?handle=bks-origin&fields=id,title,handle",
                 headers=HDR, verify=False, timeout=20)
colls = r.json().get("custom_collections", [])
if not colls:
    r2 = requests.get(f"{BASE}/smart_collections.json?handle=bks-origin&fields=id,title,handle",
                      headers=HDR, verify=False, timeout=20)
    colls = r2.json().get("smart_collections", [])
if not colls:
    print("BKS Origin collection not found")
    exit(1)

coll = colls[0]
print(f"Collection: {coll['title']} (id={coll['id']})\n")

# Get first 5 products in collection
r = requests.get(f"{BASE}/collections/{coll['id']}/products.json?fields=id,title&limit=5",
                 headers=HDR, verify=False, timeout=20)
products = r.json().get("products", [])
print(f"Sampling {len(products)} products:")
empty_alt = folk_alt = ok_alt = 0
for p in products:
    r2 = requests.get(f"{BASE}/products/{p['id']}/images.json?fields=id,alt,position",
                      headers=HDR, verify=False, timeout=20)
    images = r2.json().get("images", [])
    print(f"\n  {p['title']}")
    for img in images[:3]:
        alt = img.get("alt") or "(empty)"
        print(f"    img#{img['position']}: {alt!r}")
        if not img.get("alt"): empty_alt += 1
        elif "folklore" in alt.lower(): folk_alt += 1
        else: ok_alt += 1
    time.sleep(0.1)

print(f"\nSummary: empty={empty_alt}, folklore={folk_alt}, ok={ok_alt}")
