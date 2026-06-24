"""
Ripristina i dropdown nel menu main-menu di Shopify.
- Collections: 8 subitems → /pages/bks-*
- Product Types: 16 subitems → /pages/bks-*
- Home / BKS Members / About BakAbo / Contact: invariati
"""
import requests, urllib3, json
from pathlib import Path

urllib3.disable_warnings()

env = {}
for line in Path("I:/BAK ABO/.env").read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

TOKEN = env.get("SHOPIFY_ADMIN_TOKEN", env.get("SHOPIFY_ADMIN_API_KEY", ""))
STORE = env.get("SHOPIFY_MYSHOPIFY_DOMAIN", "11628e-2.myshopify.com")
HDR   = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
GQL   = f"https://{STORE}/admin/api/2025-01/graphql.json"

MENU_GID = "gid://shopify/Menu/231167721810"
DOMAIN   = "https://bakabo.club"

# Current top-level item IDs (from API query)
ITEM_HOME       = "gid://shopify/MenuItem/809904865618"
ITEM_COLLECTIONS = "gid://shopify/MenuItem/809904898386"
ITEM_PRODTYPES  = "gid://shopify/MenuItem/809905193298"
ITEM_MEMBERS    = "gid://shopify/MenuItem/809905750354"
ITEM_ABOUT      = "gid://shopify/MenuItem/809905783122"
ITEM_CONTACT    = "gid://shopify/MenuItem/810260529490"

# Collections dropdown — canonical order, → editorial pages
COLLECTION_SUBS = [
    ("BKS Hours",    "/pages/bks-hours"),
    ("BKS Origin",   "/pages/bks-origin"),
    ("BKS Glyph",    "/pages/bks-glyph"),
    ("BKS Marker",   "/pages/bks-marker"),
    ("BKS Riviera",  "/pages/bks-riviera"),
    ("BKS Pulse",    "/pages/bks-pulse"),
    ("BKS Token",    "/pages/bks-token"),
    ("BKS Flag",     "/pages/bks-flag"),
]

# Product Types dropdown
PRODTYPE_SUBS = [
    ("BKS Sneakers",             "/pages/bks-sneakers"),
    ("BKS Puffer Jackets",       "/pages/bks-puffer-jackets"),
    ("BKS Windbreakers",         "/pages/bks-windbreakers"),
    ("BKS Pullover Hoodies",     "/pages/bks-pullover-hoodie"),
    ("BKS Swim Trunks",          "/pages/bks-swim-trunks"),
    ("BKS Swimwear",             "/pages/bks-swimwear"),
    ("BKS Flip Flops",           "/pages/bks-flip-flop"),
    ("BKS Athletic Shorts",      "/pages/bks-athletic-shorts"),
    ("BKS Lounge Pants",         "/pages/bks-lounge-pants"),
    ("BKS Hawaiian Shirts",      "/pages/bks-hawaiian-shirt"),
    ("BKS One-Piece Swimsuits",  "/pages/bks-one-piece-swimsuits"),
    ("BKS Racerback Dresses",    "/pages/bks-racerback-dresses"),
    ("BKS Backpacks",            "/pages/bks-backpack"),
    ("BKS Travel Bags",          "/pages/bks-travel-bag"),
    ("BKS Duffel Bags",          "/pages/bks-duffel-bag"),
    ("BKS Beach Towels",         "/pages/bks-beach-towel"),
]


def build_sub_input(subs):
    return [{"title": t, "url": DOMAIN + u, "type": "HTTP"} for t, u in subs]


def run_update():
    items = [
        {
            "id": ITEM_HOME,
            "title": "Home",
            "url": DOMAIN + "/",
            "type": "HTTP"
        },
        {
            "id": ITEM_COLLECTIONS,
            "title": "Collections",
            "url": DOMAIN + "/collections",
            "type": "HTTP",
            "items": build_sub_input(COLLECTION_SUBS)
        },
        {
            "id": ITEM_PRODTYPES,
            "title": "Product Types",
            "url": DOMAIN + "/collections/all",
            "type": "HTTP",
            "items": build_sub_input(PRODTYPE_SUBS)
        },
        {
            "id": ITEM_MEMBERS,
            "title": "BKS Members",
            "url": DOMAIN + "/pages/bks-members",
            "type": "HTTP"
        },
        {
            "id": ITEM_ABOUT,
            "title": "About BakAbo",
            "url": DOMAIN + "/pages/about-bakabo-1",
            "type": "HTTP"
        },
        {
            "id": ITEM_CONTACT,
            "title": "Contact",
            "url": DOMAIN + "/pages/contact",
            "type": "HTTP"
        },
    ]

    mutation = """
mutation menuUpdate($id: ID!, $title: String!, $items: [MenuItemUpdateInput!]!) {
  menuUpdate(id: $id, title: $title, items: $items) {
    menu {
      handle
      items {
        id title url
        items { id title url }
      }
    }
    userErrors { field message }
  }
}
"""
    variables = {"id": MENU_GID, "title": "Main Menu", "items": items}

    r = requests.post(GQL, json={"query": mutation, "variables": variables},
                      headers=HDR, timeout=20, verify=False)

    if not r.ok:
        print(f"HTTP ERR {r.status_code}: {r.text[:300]}")
        return False

    d = r.json()
    if "errors" in d:
        print("GQL ERR:", json.dumps(d["errors"])[:400])
        return False

    result = d.get("data", {}).get("menuUpdate", {})
    errors = result.get("userErrors", [])
    if errors:
        print("USER ERR:", json.dumps(errors))
        return False

    menu = result.get("menu", {})
    items_out = menu.get("items", [])
    print(f"\nMenu '{menu.get('handle')}' aggiornato — {len(items_out)} top-level items:")
    for it in items_out:
        subs = it.get("items", [])
        sub_str = " (%d sub)" % len(subs) if subs else ""
        print("  %-40s -> %s%s" % (it["title"], it.get("url", ""), sub_str))
    return True


if __name__ == "__main__":
    print("Ripristino dropdown main-menu Shopify...")
    ok = run_update()
    print("\nDone." if ok else "\nFallito.")
