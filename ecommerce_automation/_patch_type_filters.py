"""Update product_type_filter in all bks-product-type-grid template sections."""
import json, time
from pathlib import Path
import requests

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

# suffix → exact Shopify product_type string
TYPE_FILTERS = {
    "bks-swim-trunks":       "Swim Trunks",
    "bks-puffer-jacket":     "Puffer Jacket",
    "bks-windbreaker":       "Windbreaker Jacket",
    "bks-backpack":          "Backpack",
    "bks-sneakers":          "Sneakers",
    "bks-travel-bag":        "Travel Bag",
    "bks-beach-towel":       "Beach Towel",
    "bks-pullover-hoodie":   "Pullover Hoodie",
    "bks-athletic-shorts":   "Athletics Shorts",
    "bks-lounge-pants":      "Lounge Pants",
    "bks-flip-flop":         "Flip Flop",
    "bks-hawaiian-shirt":    "Hawaiian Shirt",
    "bks-duffel-bag":        "Duffel Bag",
    "bks-swimwear":          "Swimwear",
    "bks-one-piece-swimsuit":"One-Piece Swimsuit",
    "bks-racerback-dress":   "Dress",
    "bks-shoes":             "Shoes",
}

def shopify_put_asset(key, value):
    r = requests.put(
        f"https://{SHOP}/admin/api/{API}/themes/{THEME}/assets.json",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"},
        json={"asset": {"key": key, "value": value}},
        verify=False, timeout=30,
    )
    return "key" in r.json().get("asset", {})

for suffix, ptype in TYPE_FILTERS.items():
    tmpl_path = THEME_DIR / f"templates/page.{suffix}.json"
    if not tmpl_path.exists():
        print(f"  SKIP (no file): {suffix}")
        continue
    tmpl = json.loads(tmpl_path.read_text(encoding="utf-8"))
    grid = tmpl.get("sections", {}).get("product_grid")
    if not grid:
        print(f"  SKIP (no grid): {suffix}")
        continue
    grid["settings"]["product_type_filter"] = ptype
    # Also expand to all collections (not limit per collection, show more)
    grid["settings"]["products_per_collection"] = 24
    tmpl_json = json.dumps(tmpl, indent=2)
    tmpl_path.write_text(tmpl_json, encoding="utf-8")
    ok = shopify_put_asset(f"templates/page.{suffix}.json", tmpl_json)
    print(f"{'OK' if ok else 'ERR'}  {suffix:35s}  filter={ptype}")
    time.sleep(0.3)

print("\nDone.")
