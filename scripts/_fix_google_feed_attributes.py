"""
Add missing Google Shopping metafields to all active Shopify products.
Sets: age_group=adult, gender=unisex (default for BKS apparel).
Also checks variant options for size/color mapping.
"""
import os, requests, urllib3, sys, time
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
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

def get_all_products():
    products, url = [], f"{BASE}/products.json?limit=250&status=active&fields=id,title,options"
    while url:
        r = requests.get(url, headers=HDR, verify=False, timeout=30)
        data = r.json()
        products.extend(data.get("products", []))
        link = r.headers.get("Link", "")
        url = None
        if 'rel="next"' in link:
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.split(";")[0].strip().strip("<>")
    return products

def get_product_metafields(pid):
    r = requests.get(f"{BASE}/products/{pid}/metafields.json?namespace=google",
                     headers=HDR, verify=False, timeout=20)
    return {m["key"]: m["id"] for m in r.json().get("metafields", [])}

def set_metafield(pid, namespace, key, value, mf_id=None):
    payload = {"metafield": {"namespace": namespace, "key": key,
                              "value": value, "type": "single_line_text_field"}}
    if mf_id:
        r = requests.put(f"{BASE}/metafields/{mf_id}.json", headers=HDR,
                         json=payload, verify=False, timeout=20)
    else:
        r = requests.post(f"{BASE}/products/{pid}/metafields.json", headers=HDR,
                          json=payload, verify=False, timeout=20)
    return r.ok

# ── Main ────────────────────────────────────────────────────────────────────
print("Fetching all active products...")
products = get_all_products()
print(f"Found {len(products)} active products\n")

# Check variant options on first few products
option_names = {}
for p in products[:5]:
    for opt in p.get("options", []):
        name = opt["name"].lower()
        option_names[name] = option_names.get(name, 0) + 1

print(f"Variant option names (sample): {option_names}")
print()

added_age = 0
added_gender = 0
skipped = 0
errors = 0

for i, p in enumerate(products):
    pid = p["id"]
    existing = get_product_metafields(pid)

    changed = False
    if "age_group" not in existing:
        ok = set_metafield(pid, "google", "age_group", "adult")
        if ok: added_age += 1
        else: errors += 1
        changed = True

    if "gender" not in existing:
        ok = set_metafield(pid, "google", "gender", "unisex")
        if ok: added_gender += 1
        else: errors += 1
        changed = True

    if not changed:
        skipped += 1

    if (i + 1) % 20 == 0:
        print(f"  [{i+1}/{len(products)}] age={added_age} gender={added_gender} skip={skipped} err={errors}")
        time.sleep(0.5)

print(f"\nDone.")
print(f"  age_group added: {added_age}")
print(f"  gender added:    {added_gender}")
print(f"  already set:     {skipped}")
print(f"  errors:          {errors}")
