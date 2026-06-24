"""Debug smart collection: verify rule and products via API."""
import requests, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

SHOP  = env["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN = env["SHOPIFY_ADMIN_TOKEN"]
HDR   = {"X-Shopify-Access-Token": TOKEN}

# Get puffer jacket smart collection details
r = requests.get(f"https://{SHOP}/admin/api/2025-01/smart_collections.json",
    params={"handle": "bks-type-puffer-jacket"},
    headers=HDR, verify=False, timeout=30)
cols = r.json().get("smart_collections", [])
if cols:
    c = cols[0]
    print(f"ID:             {c['id']}")
    print(f"Handle:         {c['handle']}")
    print(f"Title:          {c['title']}")
    print(f"products_count: {c.get('products_count')}")
    print(f"Rules:          {json.dumps(c.get('rules'), indent=2)}")
    print(f"Published:      {c.get('published_at')}")

# Try fetching products directly from the smart collection
cid = cols[0]["id"] if cols else None
if cid:
    r2 = requests.get(f"https://{SHOP}/admin/api/2025-01/collections/{cid}/products.json",
        params={"limit": 5, "fields": "id,title,product_type"},
        headers=HDR, verify=False, timeout=30)
    prods = r2.json().get("products", [])
    print(f"\nProducts via collection API ({len(prods)} returned):")
    for p in prods:
        print(f"  {p['id']}  {p['product_type']:20s}  {p['title'][:50]}")
    if not prods:
        print("  (empty — Shopify still indexing or rule mismatch)")
