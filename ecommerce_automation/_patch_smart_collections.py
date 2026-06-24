"""Patch product type page templates to use smart collection handles.

Replaces: collection_1/2/3/4 + product_type_filter
With:     collection_1 = smart collection handle (e.g. bks-type-puffer-jacket)
Also:     updates hero primary_link + view_all_url to smart collection URL
"""
import json, time, requests
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEME_DIR = ROOT / "04_TEMA_SHOPIFY"
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

SHOP  = env["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN = env["SHOPIFY_ADMIN_TOKEN"]
THEME = "202392961362"
API   = "2025-01"
HDRS  = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

def shopify_put(key, value):
    r = requests.put(
        f"https://{SHOP}/admin/api/{API}/themes/{THEME}/assets.json",
        headers=HDRS,
        json={"asset": {"key": key, "value": value}},
        verify=False, timeout=30,
    )
    return r.json().get("asset", {}).get("key") == key

# page template suffix → smart collection handle
MAPPING = {
    "bks-puffer-jacket":     "bks-type-puffer-jacket",
    "bks-swim-trunks":       "bks-type-swim-trunks",
    "bks-windbreaker":       "bks-type-windbreaker",
    "bks-backpack":          "bks-type-backpack",
    "bks-sneakers":          "bks-type-sneakers",
    "bks-travel-bag":        "bks-type-travel-bag",
    "bks-beach-towel":       "bks-type-beach-towel",
    "bks-pullover-hoodie":   "bks-type-hoodie",
    "bks-athletic-shorts":   "bks-type-athletic-shorts",
    "bks-lounge-pants":      "bks-type-lounge-pants",
    "bks-flip-flop":         "bks-type-flip-flop",
    "bks-hawaiian-shirt":    "bks-type-hawaiian",
    "bks-duffel-bag":        "bks-type-duffel-bag",
    "bks-swimwear":          "bks-type-swimwear",
    "bks-one-piece-swimsuit":"bks-type-one-piece",
    "bks-racerback-dress":   "bks-type-dress",
    "bks-shoes":             "bks-type-shoes",
    "bks-tee":               "bks-type-tee",
}

# Deploy updated section first
print("Deploying updated bks-product-type-grid.liquid...")
section_path = THEME_DIR / "sections/bks-product-type-grid.liquid"
section_ok = shopify_put("sections/bks-product-type-grid.liquid", section_path.read_text(encoding="utf-8"))
print(f"  Section: {'OK' if section_ok else 'ERROR'}")
time.sleep(0.5)

ok_count = 0
err_count = 0

for suffix, smart_handle in MAPPING.items():
    tmpl_path = THEME_DIR / f"templates/page.{suffix}.json"
    if not tmpl_path.exists():
        print(f"  SKIP (no file): page.{suffix}.json")
        continue

    tmpl = json.loads(tmpl_path.read_text(encoding="utf-8"))
    sections = tmpl.get("sections", {})

    # Update product_grid section
    grid = sections.get("product_grid")
    if grid and grid.get("type") == "bks-product-type-grid":
        s = grid.setdefault("settings", {})
        s["collection_1"] = smart_handle
        s["collection_2"] = ""
        s["collection_3"] = ""
        s["collection_4"] = ""
        s.pop("product_type_filter", None)
        s["view_all_url"] = f"/collections/{smart_handle}"
        s["products_per_collection"] = 24

    # Update hero primary_link to smart collection
    hero = sections.get("page_hero")
    if hero:
        hs = hero.setdefault("settings", {})
        hs["primary_link"] = f"/collections/{smart_handle}"

    tmpl_json = json.dumps(tmpl, indent=2)
    tmpl_path.write_text(tmpl_json, encoding="utf-8")

    key = f"templates/page.{suffix}.json"
    ok = shopify_put(key, tmpl_json)
    status = "OK " if ok else "ERR"
    if ok:
        ok_count += 1
    else:
        err_count += 1
    print(f"  {status}  {suffix:35s}  -> {smart_handle}")
    time.sleep(0.35)

print(f"\nDone: {ok_count} OK, {err_count} errors")
