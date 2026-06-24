"""Rimuove tutte le immagini AI hero shots dai prodotti Shopify.
Legge hero_generation_log.json → per ogni shopify_image_id trova il product_id → DELETE."""
import os, sys, json, time, requests, urllib3
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
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
VER    = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
GQL    = f"https://{DOMAIN}/admin/api/{VER}/graphql.json"
REST   = f"https://{DOMAIN}/admin/api/{VER}"
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

LOG_PATH = ROOT / "output" / "hero_generation_log.json"
log = json.loads(LOG_PATH.read_text(encoding="utf-8"))

# Collect all image IDs to remove (only status=ok entries)
hero_image_ids = set()
for pid, entry in log.items():
    if entry.get("status") == "ok" and entry.get("shopify_image_id"):
        hero_image_ids.add(int(entry["shopify_image_id"]))

print(f"Hero images to remove: {len(hero_image_ids)}")

# Build image_id → product_id map by fetching all products+images via GraphQL
print("\nFetching all products and their images from Shopify...")
Q = """query($cursor:String) {
  products(first:50, after:$cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      id
      images(first:10) {
        nodes { id }
      }
    }
  }
}"""

image_to_product = {}  # numeric image id → numeric product id
cursor = None
page = 0
while True:
    page += 1
    resp = requests.post(GQL, headers=HDR, json={"query": Q, "variables": {"cursor": cursor}}, timeout=30, verify=False)
    data = resp.json()["data"]["products"]
    for prod in data["nodes"]:
        prod_num = int(prod["id"].split("/")[-1])
        for img in prod["images"]["nodes"]:
            img_num = int(img["id"].split("/")[-1])
            image_to_product[img_num] = prod_num
    print(f"  Page {page}: {len(data['nodes'])} products fetched")
    if not data["pageInfo"]["hasNextPage"]:
        break
    cursor = data["pageInfo"]["endCursor"]
    time.sleep(0.5)

print(f"\nTotal images mapped: {len(image_to_product)}")

# Delete hero images
deleted = 0
not_found = 0
errors = 0

for img_id in sorted(hero_image_ids):
    prod_id = image_to_product.get(img_id)
    if not prod_id:
        print(f"  NOT FOUND: image {img_id}")
        not_found += 1
        continue
    url = f"{REST}/products/{prod_id}/images/{img_id}.json"
    r = requests.delete(url, headers=HDR, timeout=15, verify=False)
    if r.status_code == 200:
        deleted += 1
        print(f"  DELETED: product {prod_id} image {img_id}")
    elif r.status_code == 404:
        not_found += 1
        print(f"  404 (already gone): product {prod_id} image {img_id}")
    else:
        errors += 1
        print(f"  ERR {r.status_code}: product {prod_id} image {img_id} → {r.text[:100]}")
    time.sleep(0.3)  # rate limit

print(f"\n=== DONE ===")
print(f"Deleted:   {deleted}")
print(f"Not found: {not_found}")
print(f"Errors:    {errors}")
