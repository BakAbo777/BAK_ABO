"""List all distinct product types from Shopify catalog."""
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
    params={"fields": "product_type", "limit": 250},
    headers={"X-Shopify-Access-Token": env["SHOPIFY_ADMIN_TOKEN"]},
    verify=False, timeout=30,
)
types = sorted(set(p["product_type"] for p in r.json().get("products", []) if p.get("product_type")))
for t in types:
    print(repr(t))
