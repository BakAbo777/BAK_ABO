"""Lista tutti i product_type unici nello store Shopify."""
import os, requests, urllib3
from pathlib import Path
from collections import Counter

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

all_prods = []
url = f"{BASE}/products.json"
params = {"status": "active", "limit": 250, "fields": "handle,product_type,tags"}
while url:
    r = requests.get(url, headers=HDR, params=params, verify=False, timeout=20)
    batch = r.json().get("products", [])
    all_prods.extend(batch)
    link = r.headers.get("Link", "")
    url = None; params = {}
    if 'rel="next"' in link:
        for part in link.split(","):
            if 'rel="next"' in part:
                url = part.strip().split(";")[0].strip("<> ")
                break

types = Counter(p.get("product_type", "").strip() for p in all_prods)
print(f"Product types unici ({len(types)}):\n")
for t, n in sorted(types.items(), key=lambda x: -x[1]):
    print(f"  {n:4d}x  '{t}'")
