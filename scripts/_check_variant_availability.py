"""Check variant details for sold-out Athletic Shorts product."""
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
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

# Search by handle from the audit URL
handle = "flag-drop-athletic-long-shorts"
r = requests.get(
    f"https://{DOMAIN}/admin/api/2025-01/products.json?handle={handle}"
    "&fields=id,title,status,variants,published_at",
    headers=HDR, verify=False, timeout=20
)
products = r.json().get("products", [])
if not products:
    # Try title search
    r2 = requests.get(
        f"https://{DOMAIN}/admin/api/2025-01/products.json"
        f"&fields=id,title,handle,status,variants,published_at&limit=250",
        headers=HDR, verify=False, timeout=30
    )
    products = [p for p in r2.json().get("products",[])
                if "athletic" in p["title"].lower() and "flag" in p["title"].lower()]

print(f"Found {len(products)} matching products\n")
for p in products:
    print(f"PRODUCT: {p['title']} (id={p['id']}) handle={p.get('handle')} status={p['status']}")
    print(f"  published_at: {p.get('published_at','N/A')}")
    for v in p.get("variants", []):
        qty = v.get('inventory_quantity','?')
        mgmt = v.get('inventory_management','none')
        policy = v['inventory_policy']
        avail = "YES" if (mgmt != "shopify" or policy == "continue" or qty > 0) else "NO"
        print(f"  [{v['id']}] {v['title']:20} policy={policy:8} qty={qty:4} mgmt={mgmt} -> available={avail}")
