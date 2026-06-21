"""Check BKS Lounge Pants — Origin 03 variants directly."""
import os, requests, urllib3
urllib3.disable_warnings()  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN","")
HDR    = {"X-Shopify-Access-Token": TOKEN}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

for pid in [8801495843154, 8801597194578, 10841342443858]:
    r = requests.get(f"{BASE}/products/{pid}.json?fields=id,title,status,variants,published_at",
                     headers=HDR, verify=False, timeout=20)
    p = r.json().get("product", {})
    print(f"\n[{p.get('id')}] {p.get('title')} status={p.get('status')} pub={p.get('published_at','?')[:10]}")
    for v in p.get("variants", []):
        qty = v.get("inventory_quantity", 0)
        policy = v.get("inventory_policy", "?")
        mgmt = v.get("inventory_management", "?")
        avail = "AVAIL" if (mgmt != "shopify" or policy == "continue" or qty > 0) else "SOLD OUT"
        print(f"  [{v['id']}] {v.get('title',''):20} qty={qty:5} policy={policy:8} mgmt={mgmt} -> {avail}")
