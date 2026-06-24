"""Probe Shopify active products — count, image structure, collection tags."""
import os, requests, urllib3, json
from pathlib import Path

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
BASE   = f"https://{DOMAIN}/admin/api/2025-01"
HDR    = {"X-Shopify-Access-Token": TOKEN}

r = requests.get(f"{BASE}/products/count.json", headers=HDR, params={"status": "active"}, verify=False)
total = r.json().get("count", 0)
print(f"Prodotti attivi: {total}\n")

r2 = requests.get(f"{BASE}/products.json", headers=HDR,
    params={"status": "active", "limit": 8, "fields": "id,handle,title,images,tags"},
    verify=False)
prods = r2.json().get("products", [])
print("Campione (8 prodotti):")
for p in prods:
    imgs = p.get("images", [])
    img_url = imgs[0]["src"] if imgs else "NO_IMAGE"
    tags = [t.strip() for t in p.get("tags", "").split(",") if "bks-" in t.strip().lower()]
    print(f"  handle: {p['handle'][:50]}")
    print(f"  tags:   {tags}")
    print(f"  image:  ...{img_url[-50:]}")
    print()
