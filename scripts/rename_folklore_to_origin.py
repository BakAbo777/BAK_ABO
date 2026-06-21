"""Live rename: BKS Folklore -> BKS Origin (smart collection + product tags).
User-authorized one-off correction (see chat 2026-06-16). Not reusable infra.
"""
import os, requests, urllib3, json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore

urllib3.disable_warnings()  # type: ignore
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
TOKEN = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

COLLECTION_ID = 685331054930
PRODUCT_HANDLE = "folklore-bestiary-athletic-long-shorts"

print("=== 1. Rename smart collection ===")
payload = {
    "smart_collection": {
        "id": COLLECTION_ID,
        "handle": "bks-origin",
        "title": "BKS Origin",
        "template_suffix": "bks-origin",
    }
}
r = requests.put(f"{BASE}/smart_collections/{COLLECTION_ID}.json", json=payload, headers=HDR, timeout=30, verify=False)
print(r.status_code, json.dumps(r.json(), indent=2)[:600])

print("\n=== 2. Find product by handle ===")
r = requests.get(f"{BASE}/products.json", params={"handle": PRODUCT_HANDLE}, headers=HDR, timeout=30, verify=False)
products = r.json().get("products", [])
if not products:
    print("Prodotto non trovato con handle", PRODUCT_HANDLE)
else:
    product = products[0]
    pid = product["id"]
    old_tags = [t.strip() for t in product["tags"].split(",")]
    new_tags = []
    for t in old_tags:
        if t == "bks-folklore":
            new_tags.append("bks-origin")
        elif t == "collection:folklore":
            new_tags.append("collection:origin")
        elif t.lower() == "folklore":
            new_tags.append("Origin")
        else:
            new_tags.append(t)
    print("Product id:", pid)
    print("Old tags:", old_tags)
    print("New tags:", new_tags)
    # Scope: tags only (per user request). Title/handle untouched to avoid URL/SEO impact not explicitly authorized.
    upd = {
        "product": {
            "id": pid,
            "tags": ", ".join(new_tags),
        }
    }
    r2 = requests.put(f"{BASE}/products/{pid}.json", json=upd, headers=HDR, timeout=30, verify=False)
    print(r2.status_code, json.dumps(r2.json(), indent=2)[:600])
