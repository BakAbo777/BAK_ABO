"""
Rebuild canonico di tutti e 8 i template di collezione BKS.
- taglines canonici da bks-collection-signal.liquid
- subnav links allineati ai fallback_typologies del signal
- cindex order: Hours → Origin → Glyph → Marker → Riviera → Pulse → Token → Flag
- Deploy a Shopify TM04 202392961362
"""
import json, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()

# ── Shopify credentials ────────────────────────────────────────────────────
env = {}
for line in Path("I:/BAK ABO/.env").read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

TOKEN  = env.get("SHOPIFY_ADMIN_TOKEN", env.get("SHOPIFY_ADMIN_API_KEY", ""))
STORE  = env.get("SHOPIFY_MYSHOPIFY_DOMAIN", "11628e-2.myshopify.com")
THEME  = "202392961362"
BASE   = f"https://{STORE}/admin/api/2025-01/themes/{THEME}/assets.json"
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
OUTDIR = Path("I:/BAK ABO/04_TEMA_SHOPIFY/_merged_tm04/templates")

# ── Canonical data ─────────────────────────────────────────────────────────
# Order: canonical display order
COLLECTIONS = [
    {
        "handle":  "bks-hours",
        "name":    "BKS Hours",
        "tagline": "Measured urban stillness",
        "subnav": [
            ("Puffer Jackets",    "/collections/puffer-jacket"),
            ("Windbreakers",      "/collections/windbreaker"),
            ("Pullover Hoodies",  "/collections/pullover-hoodie"),
            ("Lounge Pants",      "/collections/lounge-pants"),
            ("Sneakers",          "/collections/sneakers"),
            ("Backpacks",         "/collections/backpack"),
            ("Travel Bags",       "/collections/travel-bag"),
        ],
    },
    {
        "handle":  "bks-origin",
        "name":    "BKS Origin",
        "tagline": "Invented narrative marks",
        "subnav": [
            ("Pullover Hoodies",    "/collections/pullover-hoodie"),
            ("Womens Tees",         "/collections/womens-tee"),
            ("Swim Trunks",         "/collections/swim-trunks"),
            ("One-Piece Swimsuits", "/collections/one-piece-swimsuit"),
            ("Racerback Dresses",   "/collections/racerback-dress"),
            ("Flip Flops",          "/collections/flip-flop"),
            ("Backpacks",           "/collections/backpack"),
        ],
    },
    {
        "handle":  "bks-glyph",
        "name":    "BKS Glyph",
        "tagline": "Constructed signs",
        "subnav": [
            ("Puffer Jackets",    "/collections/puffer-jacket"),
            ("Windbreakers",      "/collections/windbreaker"),
            ("Womens Tees",       "/collections/womens-tee"),
            ("Athletic Shorts",   "/collections/athletic-shorts"),
            ("Sneakers",          "/collections/sneakers"),
            ("Backpacks",         "/collections/backpack"),
            ("Travel Bags",       "/collections/travel-bag"),
        ],
    },
    {
        "handle":  "bks-marker",
        "name":    "BKS Marker",
        "tagline": "Gesture and motion",
        "subnav": [
            ("Windbreakers",     "/collections/windbreaker"),
            ("Pullover Hoodies", "/collections/pullover-hoodie"),
            ("Athletic Shorts",  "/collections/athletic-shorts"),
            ("Sneakers",         "/collections/sneakers"),
            ("Flip Flops",       "/collections/flip-flop"),
            ("Backpacks",        "/collections/backpack"),
        ],
    },
    {
        "handle":  "bks-riviera",
        "name":    "BKS Riviera",
        "tagline": "Coastal geometry",
        "subnav": [
            ("Swimwear",              "/collections/swimwear"),
            ("Swim Trunks",           "/collections/swim-trunks"),
            ("One-Piece Swimsuits",   "/collections/one-piece-swimsuit"),
            ("Racerback Dresses",     "/collections/racerback-dress"),
            ("Lounge Pants",          "/collections/lounge-pants"),
            ("Flip Flops",            "/collections/flip-flop"),
            ("Travel Bags",           "/collections/travel-bag"),
            ("Backpacks",             "/collections/backpack"),
        ],
    },
    {
        "handle":  "bks-pulse",
        "name":    "BKS Pulse",
        "tagline": "Optical movement",
        "subnav": [
            ("Puffer Jackets",    "/collections/puffer-jacket"),
            ("Windbreakers",      "/collections/windbreaker"),
            ("Pullover Hoodies",  "/collections/pullover-hoodie"),
            ("Athletic Shorts",   "/collections/athletic-shorts"),
            ("Sneakers",          "/collections/sneakers"),
            ("Womens Tees",       "/collections/womens-tee"),
            ("Backpacks",         "/collections/backpack"),
        ],
    },
    {
        "handle":  "bks-token",
        "name":    "BKS Token",
        "tagline": "Digital objects",
        "subnav": [
            ("Sneakers",         "/collections/sneakers"),
            ("Pullover Hoodies", "/collections/pullover-hoodie"),
            ("Womens Tees",      "/collections/womens-tee"),
            ("Lounge Pants",     "/collections/lounge-pants"),
            ("Cozy Slippers",    "/collections/cozy-slipper"),
            ("Backpacks",        "/collections/backpack"),
            ("Travel Bags",      "/collections/travel-bag"),
        ],
    },
    {
        "handle":  "bks-flag",
        "name":    "BKS Flag",
        "tagline": "Graphic fields",
        "subnav": [
            ("Puffer Jackets",  "/collections/puffer-jacket"),
            ("Windbreakers",    "/collections/windbreaker"),
            ("Athletic Shorts", "/collections/athletic-shorts"),
            ("Swim Trunks",     "/collections/swim-trunks"),
            ("Sneakers",        "/collections/sneakers"),
            ("Flip Flops",      "/collections/flip-flop"),
            ("Backpacks",       "/collections/backpack"),
        ],
    },
]

# ── Build canonical cindex blocks (shared across all templates) ────────────
def build_cindex():
    blocks = {}
    order  = []
    for i, col in enumerate(COLLECTIONS):
        key = f"c{i+1}"
        blocks[key] = {
            "type": "collection_row",
            "settings": {
                "name":               col["name"],
                "tagline":            col["tagline"],
                "collection_handle":  col["handle"],
                "link":               f"/collections/{col['handle']}",
            },
        }
        order.append(key)
    return {
        "type": "bks-collections-index",
        "blocks": blocks,
        "block_order": order,
        "settings": {
            "heading":    "Collections",
            "subheading": "Eight permanent visual worlds. Apparel, swim and accessories share the same graphic language inside each one.",
            "scheme":     "light",
        },
    }

CINDEX = build_cindex()

# ── Build template for a single collection ─────────────────────────────────
def build_template(col):
    subnav_blocks = {}
    subnav_order  = []
    for i, (label, link) in enumerate(col["subnav"]):
        key = f"p{i+1}"
        subnav_blocks[key] = {
            "type": "subnav_link",
            "settings": {"label": label, "link": link},
        }
        subnav_order.append(key)

    return {
        "sections": {
            "bks_signal": {
                "type":         "bks-collection-signal",
                "blocks":       subnav_blocks,
                "block_order":  subnav_order,
                "settings":     {},
            },
            "product-grid": {
                "type": "main-collection-product-grid",
                "settings": {
                    "products_per_page":          36,
                    "columns_desktop":            4,
                    "columns_mobile":             "2",
                    "color_scheme":               "background-1",
                    "image_ratio":                "portrait",
                    "image_shape":                "default",
                    "show_secondary_image":       True,
                    "show_vendor":                False,
                    "show_rating":                False,
                    "quick_add":                  "none",
                    "enable_filtering":           True,
                    "filter_type":                "drawer",
                    "enable_sorting":             True,
                    "padding_top":                36,
                    "padding_bottom":             36,
                    "bks_editorial_product_view": True,
                    "bks_grid_layout":            "scene-grid",
                    "bks_use_context_color":      True,
                    "bks_show_made_to_order":     True,
                    "bks_show_collection_badge":  True,
                },
            },
            "bks_cindex": CINDEX,
        },
        "order": ["bks_signal", "product-grid", "bks_cindex"],
    }


# ── Write + deploy ─────────────────────────────────────────────────────────
def deploy(shopify_key, content_str):
    r = requests.put(
        BASE,
        json={"asset": {"key": shopify_key, "value": content_str}},
        headers=HDR, timeout=20, verify=False,
    )
    ok = r.status_code in (200, 201)
    status = "OK" if ok else f"ERR {r.status_code}"
    print(f"  [{status}] {shopify_key}")
    if not ok:
        print(f"         {r.text[:160]}")
    return ok


def main():
    ok_count = 0
    total    = len(COLLECTIONS) + 1  # +1 for list-collections

    print(f"\nRebuild + deploy {len(COLLECTIONS)} collection templates -> Shopify {THEME}\n")

    for col in COLLECTIONS:
        tmpl      = build_template(col)
        content   = json.dumps(tmpl, indent=2, ensure_ascii=False)
        filename  = f"collection.{col['handle']}.json"
        filepath  = OUTDIR / filename
        filepath.write_text(content, encoding="utf-8")
        shopify_key = f"templates/{filename}"
        if deploy(shopify_key, content):
            ok_count += 1

    # also deploy updated list-collections.json
    lc_path = OUTDIR / "list-collections.json"
    lc_data = json.loads(lc_path.read_text(encoding="utf-8"))
    # fix BKS Origin tagline in list-collections too (block c2 currently has correct tagline)
    for block_key, block in lc_data["sections"]["index"]["blocks"].items():
        if block["settings"].get("collection_handle") == "bks-origin":
            block["settings"]["tagline"] = "Invented narrative marks"
    lc_content = json.dumps(lc_data, indent=2, ensure_ascii=False)
    lc_path.write_text(lc_content, encoding="utf-8")
    if deploy("templates/list-collections.json", lc_content):
        ok_count += 1

    print(f"\n{'='*52}")
    print(f"Deployed: {ok_count}/{total}")
    print(f"{'='*52}\n")


if __name__ == "__main__":
    main()
