"""Show all distinct product types currently in Shopify."""
import requests
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

SHOP  = env["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN = env["SHOPIFY_ADMIN_TOKEN"]

# Fetch all products (paginate)
products = []
url = f"https://{SHOP}/admin/api/2025-01/products.json"
params = {"limit": 250, "fields": "id,title,product_type"}
while url:
    r = requests.get(url, params=params, headers={"X-Shopify-Access-Token": TOKEN}, verify=False, timeout=30)
    batch = r.json().get("products", [])
    products.extend(batch)
    link = r.headers.get("Link", "")
    url = None
    params = {}
    if 'rel="next"' in link:
        for part in link.split(","):
            if 'rel="next"' in part:
                url = part.split(";")[0].strip().strip("<>")
                break

counts = Counter(p["product_type"] for p in products)
print(f"Total products: {len(products)}")
print(f"\nProduct types ({len(counts)} distinct):")
for ptype, cnt in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {cnt:4d}  '{ptype}'")
