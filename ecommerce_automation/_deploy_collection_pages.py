"""Create page templates + update page template_suffix for all 8 BKS collection guide pages."""
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

COLLECTIONS = {
    "hours":    {"accent": "#c8c4be", "bg": "#1a1a18", "lead": "Time made textile. Monochrome rhythm across every hour and every layer.", "meta1": "Monochrome", "meta2": "Urban Neutral"},
    "glyph":    {"accent": "#d4a030", "bg": "#0f0e08", "lead": "Abstract glyphs decoded into wearable geometry. Gold ink on every surface.", "meta1": "Geometric", "meta2": "Gold Ink"},
    "marker":   {"accent": "#c04418", "bg": "#100800", "lead": "Raw mark-making and editorial heat translated into bold all-over prints.", "meta1": "Bold Print", "meta2": "Editorial Heat"},
    "riviera":  {"accent": "#0ca898", "bg": "#04100f", "lead": "Mediterranean light and water patterns as a wearable surface system.", "meta1": "Mediterranean", "meta2": "Aquatic"},
    "pulse":    {"accent": "#8888cc", "bg": "#0A0A0A", "lead": "Optical movement and digital pressure translated into wearable surface.", "meta1": "Technical Layer", "meta2": "Optical"},
    "token":    {"accent": "#9828d8", "bg": "#0a0010", "lead": "Cryptographic symbols and blockchain-era aesthetics rendered as fashion.", "meta1": "Crypto Art", "meta2": "Digital"},
    "flag":     {"accent": "#c82020", "bg": "#100000", "lead": "Signal codes and identity flags as all-over wearable art pieces.", "meta1": "Signal", "meta2": "Identity"},
    "origin":   {"accent": "#489808", "bg": "#040e00", "lead": "Botanical origins and organic DNA translated into earth-tone fashion.", "meta1": "Botanical", "meta2": "Organic"},
}

PRODUCTS_BY_COLL = {
    "hours":   [("Tee", "tee"), ("Puffer", "puffer"), ("Lounge Pants", "lounge_pants"), ("Windbreaker", "windbreaker"), ("Travel Bag", "travel_bag")],
    "glyph":   [("Tee", "tee"), ("Puffer", "puffer"), ("Backpack", "backpack"), ("Sneakers", "sneakers"), ("Travel Bag", "travel_bag")],
    "marker":  [("Tee", "tee"), ("Hoodie", "hoodie"), ("Windbreaker", "windbreaker"), ("Backpack", "backpack"), ("Shorts", "shorts")],
    "riviera": [("Tee", "tee"), ("Swim Trunks", "swim_trunks"), ("Beach Towel", "beach_towel"), ("Flip Flops", "flip_flops"), ("Hawaiian", "hawaiian")],
    "pulse":   [("Tee", "tee"), ("Hoodie", "hoodie"), ("Windbreaker", "windbreaker"), ("Sneakers", "sneakers"), ("Backpack", "backpack")],
    "token":   [("Tee", "tee"), ("Backpack", "backpack"), ("Sneakers", "sneakers"), ("Windbreaker", "windbreaker"), ("Travel Bag", "travel_bag")],
    "flag":    [("Tee", "tee"), ("Hoodie", "hoodie"), ("Beach Towel", "beach_towel"), ("Shorts", "shorts"), ("Windbreaker", "windbreaker")],
    "origin":  [("Tee", "tee"), ("Lounge Pants", "lounge_pants"), ("Beach Towel", "beach_towel"), ("Windbreaker", "windbreaker"), ("Travel Bag", "travel_bag")],
}

def shopify_put(path, body):
    r = requests.put(
        f"https://{SHOP}/admin/api/{API}/{path}",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"},
        json=body, verify=False, timeout=30,
    )
    return r.json()

def shopify_get(path):
    r = requests.get(
        f"https://{SHOP}/admin/api/{API}/{path}",
        headers={"X-Shopify-Access-Token": TOKEN},
        verify=False, timeout=30,
    )
    return r.json()

def make_template(coll, cfg):
    products = PRODUCTS_BY_COLL[coll]
    blocks = {}
    block_order = []
    for label, ptype in products:
        bid = f"link_{ptype}"
        blocks[bid] = {
            "type": "quick_link",
            "settings": {
                "label": label,
                "link": f"/collections/bks-{coll}/{ptype.replace('_', '-')}",
            }
        }
        block_order.append(bid)

    return {
        "sections": {
            "page_hero": {
                "type": "bks-page-hero",
                "settings": {
                    "kicker": f"BKS Studio — {coll.title()}",
                    "title": coll.upper(),
                    "lead": cfg["lead"],
                    "meta_1": cfg["meta1"],
                    "meta_2": cfg["meta2"],
                    "meta_3": "Made to Order",
                    "primary_label": f"Shop {coll.title()}",
                    "primary_link": f"/collections/bks-{coll}",
                    "secondary_label": "All Collections",
                    "secondary_link": "/collections/all",
                    "background_color": cfg["bg"],
                    "text_color": "#FAFAF7",
                    "accent_color": cfg["accent"],
                },
                "blocks": blocks,
                "block_order": block_order,
            },
            "main": {"type": "main-page", "settings": {}},
        },
        "order": ["page_hero", "main"],
    }

# 1. Create and deploy all templates
for coll, cfg in COLLECTIONS.items():
    tmpl = make_template(coll, cfg)
    key = f"templates/page.bks-{coll}.json"
    local = THEME_DIR / f"templates/page.bks-{coll}.json"
    local.write_text(json.dumps(tmpl, indent=2), encoding="utf-8")
    result = shopify_put(f"themes/{THEME}/assets.json", {"asset": {"key": key, "value": json.dumps(tmpl, indent=2)}})
    ok = "key" in result.get("asset", {})
    print(f"{'OK' if ok else 'ERR'} template: {key}")
    time.sleep(0.3)

# 2. Find each page and update template_suffix
for coll in COLLECTIONS:
    handle = f"bks-{coll}"
    pages = shopify_get(f"pages.json?handle={handle}&fields=id,handle,template_suffix").get("pages", [])
    if not pages:
        print(f"  NOT FOUND: page handle={handle}")
        continue
    page = pages[0]
    if page.get("template_suffix") == f"bks-{coll}":
        print(f"  SKIP (already set): {handle}")
        continue
    resp = shopify_put(f"pages/{page['id']}.json", {"page": {"id": page["id"], "template_suffix": f"bks-{coll}"}})
    ok = resp.get("page", {}).get("template_suffix") == f"bks-{coll}"
    print(f"  {'OK' if ok else 'ERR'} page: {handle} → template_suffix=bks-{coll}")
    time.sleep(0.3)

print("\nDone.")
