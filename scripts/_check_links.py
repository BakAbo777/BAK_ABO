"""Verifica collections e pages attive su Shopify."""
import os, requests, urllib3
urllib3.disable_warnings()

for raw in open("I:/BAK ABO/.env", encoding="utf-8"):
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ:
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
VER    = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE   = f"https://{DOMAIN}/admin/api/{VER}"
HDR    = {"X-Shopify-Access-Token": TOKEN}

# Collections
r1 = requests.get(f"{BASE}/custom_collections.json?limit=250", headers=HDR, verify=False)
r2 = requests.get(f"{BASE}/smart_collections.json?limit=250", headers=HDR, verify=False)
colls = r1.json().get("custom_collections", []) + r2.json().get("smart_collections", [])
print(f"=== COLLECTIONS ({len(colls)}) ===")
for c in sorted(colls, key=lambda x: x["handle"]):
    print(f"  /collections/{c['handle']}  [{c['title']}]")

# Pages
r3 = requests.get(f"{BASE}/pages.json?limit=250", headers=HDR, verify=False)
pages = r3.json().get("pages", [])
print(f"\n=== PAGES ({len(pages)}) ===")
for p in sorted(pages, key=lambda x: x["handle"]):
    pub = "PUB" if p.get("published_at") else "---"
    print(f"  {pub}  /pages/{p['handle']}  [{p['title']}]")

# Products (count only)
r4 = requests.get(f"{BASE}/products/count.json", headers=HDR, verify=False)
print(f"\n=== PRODUCTS: {r4.json().get('count',0)} ===")
