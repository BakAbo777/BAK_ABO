"""Check BKS Lounge Pants — Origin 03 sold-out status."""
import os, requests, urllib3, re
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

# Fetch all lounge pants from origin collection
r = requests.get(f"{BASE}/collections/685331054930/products.json?fields=id,title,status,variants&limit=250",
                 headers=HDR, verify=False, timeout=30)
products = r.json().get("products", [])

# Find lounge pants
lounge = [p for p in products if "lounge" in p["title"].lower() or "pants" in p["title"].lower()]
print(f"Lounge Pants in Origin: {len(lounge)}")

for p in lounge:
    print(f"\n[{p['id']}] {p['title']} status={p['status']}")
    for v in p.get("variants", []):
        qty = v.get("inventory_quantity", 0)
        policy = v.get("inventory_policy", "?")
        mgmt = v.get("inventory_management", "?")
        avail = "AVAIL" if (mgmt != "shopify" or policy == "continue" or qty > 0) else "SOLD OUT"
        print(f"  [{v['id']}] {v['title']:20} qty={qty:4} policy={policy:8} mgmt={mgmt} -> {avail}")

# Also check ALL origin products for SOLD OUT risk
print("\n\n=== SOLD OUT RISK CHECK (Origin products) ===")
sold_out_risk = []
for p in products:
    for v in p.get("variants", []):
        if v.get("inventory_management") == "shopify" and v.get("inventory_policy") == "deny" and v.get("inventory_quantity", 0) <= 0:
            sold_out_risk.append((p["title"], v["title"], v["id"]))

if sold_out_risk:
    print(f"VARIANTS AT RISK (policy=deny, qty<=0): {len(sold_out_risk)}")
    for title, vtitle, vid in sold_out_risk[:10]:
        print(f"  [{vid}] {title[:40]} | {vtitle}")
else:
    print("No sold-out risk variants found (all have policy=continue or qty>0)")
