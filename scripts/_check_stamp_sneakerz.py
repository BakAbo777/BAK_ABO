"""Check if Stamp Sneakerz still exists."""
import os, requests, urllib3, sys
urllib3.disable_warnings()  # type: ignore
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
from pathlib import Path
for raw in Path("I:/BAK ABO/.env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ:
            os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

r = requests.get(f"{BASE}/products.json?title=Stamp+Sneakerz&fields=id,title,status,handle",
                 headers=HDR, verify=False, timeout=20)
products = r.json().get("products", [])
if products:
    for p in products:
        print(f"[{p['id']}] '{p['title']}' status={p['status']} handle={p['handle']}")
else:
    print("NOT FOUND — Stamp Sneakerz non esiste più nel catalogo")
