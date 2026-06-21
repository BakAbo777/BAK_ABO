"""Check if ghost product type pages still exist in Shopify."""
import os, requests, urllib3
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

GHOST_HANDLES = [
    "bks-hawaiian-shirt",
    "bks-duffel-bag",
    "bks-beach-towel",
]

for handle in GHOST_HANDLES:
    r = requests.get(f"{BASE}/pages.json?handle={handle}&fields=id,title,handle",
                     headers=HDR, verify=False, timeout=20)
    pages = r.json().get("pages", [])
    if pages:
        p = pages[0]
        print(f"EXISTS: [{p['id']}] /pages/{p['handle']} title={p['title']!r}")
    else:
        print(f"GONE:   /pages/{handle} (not found)")

# Also check for legacy description patterns in sneakers
import re
r2 = requests.get(f"{BASE}/products.json?product_type=Shoes&fields=id,title,body_html&limit=5",
                  headers=HDR, verify=False, timeout=20)
for p in r2.json().get("products", []):
    if "casey" in (p.get("body_html") or "").lower() or "artist 2000" in (p.get("body_html") or "").lower():
        print(f"\nLEGACY DESC: [{p['id']}] {p['title'][:50]}")
        print(f"  body snippet: {p['body_html'][:100]}")
