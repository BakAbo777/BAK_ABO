"""Check collection card and card-product snippet for sold-out logic."""
import os, requests, urllib3, sys
urllib3.disable_warnings()  # type: ignore
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN","")
HDR    = {"X-Shopify-Access-Token": TOKEN}

for key in ["snippets/card-product.liquid", "sections/main-collection-product-grid-bks.liquid"]:
    r = requests.get(
        f"https://{DOMAIN}/admin/api/2025-01/themes/202392961362/assets.json?asset[key]={key}",
        headers=HDR, verify=False, timeout=20)
    val = r.json().get("asset", {}).get("value", "") or ""
    print(f"\n=== {key} ({len(val)} chars) ===")
    for i, line in enumerate(val.splitlines(), 1):
        if any(x in line.lower() for x in ["sold_out", "sold-out", "available", "inventory_quantity", "badge"]):
            print(f"  L{i:4}: {line[:120]}")
