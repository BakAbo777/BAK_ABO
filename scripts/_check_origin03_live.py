"""Check current live status of BKS Lounge Pants — Origin 03."""
import os, requests, urllib3
urllib3.disable_warnings()  # type: ignore
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

r = requests.get(
    f"{BASE}/products/10841342443858.json?fields=id,title,status,published_at,variants",
    headers=HDR, verify=False, timeout=20
)
p = r.json().get("product", {})
print(f"[{p['id']}] {p['title']}")
print(f"status={p['status']}  pub={str(p.get('published_at', ''))[:10]}")
for v in p.get("variants", []):
    print(f"  {v['title']:4}  qty={v['inventory_quantity']:5}  policy={v['inventory_policy']:8}  mgmt={v['inventory_management']}")

all_vars = p.get("variants", [])
prod_available = any(
    v["inventory_policy"] == "continue" or v["inventory_quantity"] > 0
    for v in all_vars
)
print(f"\nproduct.available (Liquid equivalent) = {prod_available}")
print("=> SOLD OUT badge will show" if not prod_available else "=> SOLD OUT badge will NOT show")
