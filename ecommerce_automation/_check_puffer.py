"""Find puffer jacket products and their product types."""
import requests
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

r = requests.get(
    f"https://{env['SHOPIFY_MYSHOPIFY_DOMAIN']}/admin/api/2025-01/products.json",
    params={"fields": "id,title,product_type,tags", "limit": 250},
    headers={"X-Shopify-Access-Token": env["SHOPIFY_ADMIN_TOKEN"]},
    verify=False, timeout=30,
)
products = r.json().get("products", [])
puffers = [p for p in products if "puffer" in p["title"].lower() or "puffer" in p.get("tags","").lower()]
print(f"Found {len(puffers)} puffer products:")
for p in puffers[:10]:
    print(f"  type={repr(p['product_type']):25s}  title={p['title'][:60]}")

print("\n--- All types with count ---")
from collections import Counter
counts = Counter(p["product_type"] for p in products)
for t, n in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {n:3d}  {repr(t)}")
