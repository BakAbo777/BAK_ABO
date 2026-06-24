"""Add bks-product-type-grid section to all product type page templates."""
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

# suffix → (section_title, accent, collection_1, collection_2, collection_3, collection_4)
GRID_CONFIG = {
    "bks-swim-trunks":      ("Swim Trunks", "#0ca898", "bks-riviera", "bks-flag",   "",          ""),
    "bks-puffer-jacket":    ("Puffer Jackets","#c8c4be","bks-hours",  "bks-glyph",  "bks-marker","bks-pulse"),
    "bks-windbreaker":      ("Windbreakers", "#c04418", "bks-marker", "bks-hours",  "bks-pulse", "bks-token"),
    "bks-backpack":         ("Backpacks",    "#d4a030", "bks-glyph",  "bks-marker", "bks-pulse", "bks-token"),
    "bks-sneakers":         ("Sneakers",     "#9828d8", "bks-glyph",  "bks-pulse",  "bks-token", ""),
    "bks-travel-bag":       ("Travel Bags",  "#C9B79C", "bks-hours",  "bks-riviera","bks-token", "bks-flag"),
    "bks-beach-towel":      ("Beach Towels", "#0ca898", "bks-riviera","bks-flag",   "bks-origin",""),
    "bks-pullover-hoodie":  ("Hoodies",      "#c82020", "bks-marker", "bks-pulse",  "bks-flag",  ""),
    "bks-athletic-shorts":  ("Shorts",       "#c82020", "bks-marker", "bks-flag",   "",          ""),
    "bks-lounge-pants":     ("Lounge Pants", "#c8c4be", "bks-hours",  "bks-origin", "",          ""),
    "bks-flip-flop":        ("Flip Flops",   "#0ca898", "bks-riviera","",           "",          ""),
    "bks-hawaiian-shirt":   ("Hawaiian",     "#0ca898", "bks-riviera","",           "",          ""),
    "bks-duffel-bag":       ("Duffel Bags",  "#C9B79C", "bks-hours",  "bks-marker", "",          ""),
    "bks-swimwear":         ("Swimwear",     "#0ca898", "bks-riviera","",           "",          ""),
    "bks-one-piece-swimsuit":("One Piece",   "#0ca898", "bks-riviera","",           "",          ""),
    "bks-racerback-dress":  ("Dresses",      "#8888cc", "bks-riviera","bks-pulse",  "",          ""),
    "bks-shoes":            ("Shoes",        "#9828d8", "bks-glyph",  "bks-pulse",  "bks-token", ""),
    "bks-men":              ("Men's Collection","#C9B79C","bks-hours", "bks-marker","bks-pulse", "bks-flag"),
    "bks-woman":            ("Women's Collection","#C9B79C","bks-riviera","bks-glyph","bks-pulse","bks-origin"),
}

def shopify_put_asset(key, value):
    r = requests.put(
        f"https://{SHOP}/admin/api/{API}/themes/{THEME}/assets.json",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"},
        json={"asset": {"key": key, "value": value}},
        verify=False, timeout=30,
    )
    return "key" in r.json().get("asset", {})

for suffix, (stitle, accent, c1, c2, c3, c4) in GRID_CONFIG.items():
    tmpl_path = THEME_DIR / f"templates/page.{suffix}.json"
    if not tmpl_path.exists():
        print(f"  SKIP (no file): {suffix}")
        continue

    tmpl = json.loads(tmpl_path.read_text(encoding="utf-8"))

    # Add grid section if not already present
    if "product_grid" not in tmpl["sections"]:
        grid_settings = {
            "section_title": stitle,
            "accent_color": accent,
            "bg_color": "#fafaf7",
            "collection_1": c1,
            "products_per_collection": 12,
        }
        if c2: grid_settings["collection_2"] = c2
        if c3: grid_settings["collection_3"] = c3
        if c4: grid_settings["collection_4"] = c4

        tmpl["sections"]["product_grid"] = {
            "type": "bks-product-type-grid",
            "settings": grid_settings,
        }
        # Insert before main section
        order = tmpl.get("order", [])
        if "main" in order:
            idx = order.index("main")
            order.insert(idx, "product_grid")
        else:
            order.append("product_grid")
        tmpl["order"] = order

        tmpl_json = json.dumps(tmpl, indent=2)
        tmpl_path.write_text(tmpl_json, encoding="utf-8")
        key = f"templates/page.{suffix}.json"
        ok = shopify_put_asset(key, tmpl_json)
        print(f"{'OK' if ok else 'ERR'}  {suffix}")
        time.sleep(0.3)
    else:
        print(f"  SKIP (grid exists): {suffix}")

print("\nDone.")
