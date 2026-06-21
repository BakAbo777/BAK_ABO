"""Set inventory qty=9999 for BKS Lounge Pants — Origin 03 (id=10841342443858)."""
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
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

# Get first active location
r = requests.get(f"{BASE}/locations.json?fields=id,name,active", headers=HDR, verify=False, timeout=20)
locs = r.json().get("locations", [])
print("Locations:", [(l["id"], l["name"], l.get("active")) for l in locs])
loc_id = next((l["id"] for l in locs if l.get("active")), locs[0]["id"] if locs else None)
print(f"Using location: {loc_id}\n")

VARIANT_IDS = [53656838799698, 53656838832466, 53656838865234, 53656838898002]
ok = err = 0

for vid in VARIANT_IDS:
    # Get inventory_item_id
    r_var = requests.get(f"{BASE}/variants/{vid}.json?fields=id,title,inventory_item_id",
                         headers=HDR, verify=False, timeout=20)
    v = r_var.json().get("variant", {})
    inv_item_id = v.get("inventory_item_id")
    title = v.get("title", "?")

    # Set inventory level
    r3 = requests.post(
        f"{BASE}/inventory_levels/set.json",
        headers=HDR,
        json={"location_id": loc_id, "inventory_item_id": inv_item_id, "available": 9999},
        verify=False, timeout=20
    )
    if r3.ok:
        lvl = r3.json().get("inventory_level", {})
        ok += 1
        print(f"  OK  [{vid}] {title:20} inv_item={inv_item_id} -> qty={lvl.get('available')}")
    else:
        err += 1
        print(f"  ERR [{vid}] {title}: {r3.status_code} {r3.text[:100]}")

print(f"\nDone: {ok}/{len(VARIANT_IDS)} OK, {err} errors")
