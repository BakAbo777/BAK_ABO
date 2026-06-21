"""Check image alt texts for BKS Origin products."""
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

# Get first 5 origin products
r = requests.get(f"{BASE}/products.json?title=BKS Origin&fields=id,title&limit=5",
                 headers=HDR, verify=False, timeout=20)
products = r.json().get("products", [])
for p in products[:5]:
    r2 = requests.get(f"{BASE}/products/{p['id']}/images.json?fields=id,alt,position&limit=3",
                      headers=HDR, verify=False, timeout=20)
    images = r2.json().get("images", [])
    print(f"\n{p['title']}")
    for img in images:
        alt = img.get("alt") or "(empty)"
        print(f"  img#{img['position']}: {alt!r}")
    time.sleep(0.1)
