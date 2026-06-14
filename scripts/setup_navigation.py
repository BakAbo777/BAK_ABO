"""Create/update Shopify navigation menus via GraphQL.

main-menu  → header desktop (6 items with dropdowns)
footer-info → footer policy links
"""
from __future__ import annotations
import os, requests, urllib3, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
GQL     = f"https://{DOMAIN}/admin/api/{VERSION}/graphql.json"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
urllib3.disable_warnings()

STORE = f"https://{os.environ.get('PRIMARY_DOMAIN', 'bakabo.club')}"


def gql(query: str, variables: dict = None) -> dict:
    for attempt in range(4):
        r = requests.post(GQL, json={"query": query, "variables": variables or {}},
                          headers=HDR, timeout=30, verify=False)
        if r.status_code == 429:
            time.sleep(2 ** attempt + 1)
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()


def find_menu(title: str) -> str | None:
    q = """{ menus(first:20) { edges { node { id title handle } } } }"""
    data = gql(q)
    menus = data.get("data", {}).get("menus", {}).get("edges", [])
    for edge in menus:
        n = edge["node"]
        if n["title"].lower() == title.lower() or n["handle"] == title.lower().replace(" ", "-"):
            return n["id"]
    return None


def build_items(items: list[dict]) -> list[dict]:
    out = []
    for item in items:
        node = {"title": item["title"], "url": item["url"], "type": "HTTP"}
        if item.get("items"):
            node["items"] = build_items(item["items"])
        out.append(node)
    return out


CREATE_MENU = """
mutation menuCreate($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) {
  menuCreate(title: $title, handle: $handle, items: $items) {
    menu { id title handle }
    userErrors { field message }
  }
}"""

UPDATE_MENU = """
mutation menuUpdate($id: ID!, $title: String!, $items: [MenuItemUpdateInput!]!) {
  menuUpdate(id: $id, title: $title, items: $items) {
    menu { id title handle }
    userErrors { field message }
  }
}"""

DELETE_MENU = """
mutation menuDelete($id: ID!) {
  menuDelete(id: $id) { deletedMenuId userErrors { field message } }
}"""


def upsert_menu(title: str, handle: str, items: list[dict]) -> None:
    built = build_items(items)
    existing_id = find_menu(handle)

    if existing_id:
        # Delete and recreate — menuUpdate has quirks with nested items
        gql(DELETE_MENU, {"id": existing_id})
        time.sleep(0.5)

    result = gql(CREATE_MENU, {"title": title, "handle": handle, "items": built})
    errs = result.get("data", {}).get("menuCreate", {}).get("userErrors", [])
    if errs:
        print(f"  ERROR: {errs}")
        return
    menu = result.get("data", {}).get("menuCreate", {}).get("menu", {})
    print(f"  OK  {menu.get('handle')}  id={menu.get('id')}")


MAIN_ITEMS = [
    {"title": "Shop", "url": f"{STORE}/collections/all", "items": [
        {"title": "New Arrivals",  "url": f"{STORE}/collections/new-arrivals"},
        {"title": "Sneakers",      "url": f"{STORE}/collections/sneakers"},
        {"title": "Puffer Jacket", "url": f"{STORE}/collections/puffer-jacket"},
        {"title": "Swimwear",      "url": f"{STORE}/collections/swimwear"},
        {"title": "Outerwear",     "url": f"{STORE}/collections/outerwear"},
        {"title": "Travel Bag",    "url": f"{STORE}/collections/travel-bag"},
        {"title": "Backpack",      "url": f"{STORE}/collections/backpack"},
        {"title": "All products",  "url": f"{STORE}/collections/all"},
    ]},
    {"title": "Collections", "url": f"{STORE}/collections", "items": [
        {"title": "Folklore",        "url": f"{STORE}/collections/bks-folklore"},
        {"title": "Glyph",           "url": f"{STORE}/collections/bks-glyph"},
        {"title": "Marker",          "url": f"{STORE}/collections/bks-marker"},
        {"title": "Riviera",         "url": f"{STORE}/collections/bks-riviera"},
        {"title": "Pulse",           "url": f"{STORE}/collections/bks-pulse"},
        {"title": "Token",           "url": f"{STORE}/collections/bks-token"},
        {"title": "Flag",            "url": f"{STORE}/collections/bks-flag"},
        {"title": "Hours",           "url": f"{STORE}/collections/bks-hours"},
        {"title": "All collections", "url": f"{STORE}/collections"},
    ]},
    {"title": "Man",   "url": f"{STORE}/collections/sneakers"},
    {"title": "Woman", "url": f"{STORE}/collections/one-piece-swimsuit"},
    {"title": "About", "url": f"{STORE}/pages/about-bakabo"},
]

# Footer: sovrascrive il menu "footer" esistente (handle=footer)
FOOTER_ITEMS = [
    {"title": "Shipping", "url": f"{STORE}/policies/shipping-policy"},
    {"title": "Returns",  "url": f"{STORE}/policies/refund-policy"},
    {"title": "Privacy",  "url": f"{STORE}/policies/privacy-policy"},
    {"title": "Terms",    "url": f"{STORE}/policies/terms-of-service"},
    {"title": "Contact",  "url": f"{STORE}/pages/contact"},
    {"title": "Track Order", "url": f"{STORE}/apps/parcelpanel"},
]


def main() -> None:
    print("=== BKS Navigation setup ===\n")
    # main-menu-1 e' il menu attivo nel tema (header-group.json)
    print("Main menu (main-menu-1):")
    upsert_menu("main-menu", "main-menu-1", MAIN_ITEMS)
    time.sleep(0.6)
    print("Footer:")
    upsert_menu("Footer menu", "footer", FOOTER_ITEMS)
    print("\nDone.")


if __name__ == "__main__":
    main()
