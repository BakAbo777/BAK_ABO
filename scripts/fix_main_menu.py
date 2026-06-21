"""Ricostruisce main-menu-1 con handle reali verificati dallo store."""
import os, json, time, requests, urllib3, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
urllib3.disable_warnings()  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VER     = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
GQL     = f"https://{DOMAIN}/admin/api/{VER}/graphql.json"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
BASE    = "https://bakabo.club"


def gql(query, variables=None):
    r = requests.post(GQL, json={"query": query, "variables": variables or {}},
                      headers=HDR, timeout=30, verify=False)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(json.dumps(data["errors"], indent=2))
    return data


def u(path):
    return f"{BASE}{path}"


def it(title, path, children=None):
    obj = {"title": title, "type": "HTTP", "url": u(path)}
    if children:
        obj["items"] = children
    return obj


# ── Menu corretto — handle verificati dal vivo ────────────────────────────────
ITEMS = [
    it("Home", "/"),
    it("Shop", "/collections/all", [
        it("New Arrivals",  "/collections/new-arrivals"),
        it("All Products",  "/collections/all"),
    ]),
    it("Man", "/pages/bks-men", [
        it("Sneakers",         "/pages/bks-sneakers"),
        it("Swim Trunks",      "/pages/bks-swim-trunks"),
        it("Hawaiian Shirts",  "/pages/bks-hawaiian-shirt"),
        it("Pullover Hoodies", "/pages/bks-pullover-hoodie"),
        it("Athletic Shorts",  "/pages/bks-athletic-shorts"),
        it("Puffer Jackets",   "/pages/bks-puffer-jackets"),
        it("Windbreakers",     "/pages/bks-windbreakers"),
    ]),
    it("Woman", "/pages/bks-woman", [
        it("Sneakers",            "/pages/bks-sneakers"),
        it("One-Piece Swimsuits", "/pages/bks-one-piece-swimsuits"),
        it("Swimwear",            "/pages/bks-swimwear"),
        it("Racerback Dresses",   "/pages/bks-racerback-dresses"),
        it("Lounge Pants",        "/pages/bks-lounge-pants"),
        it("Pullover Hoodies",    "/pages/bks-pullover-hoodie"),
        it("Puffer Jackets",      "/pages/bks-puffer-jackets"),
        it("Windbreakers",        "/pages/bks-windbreakers"),
        it("Flip Flops",          "/pages/bks-flip-flop"),
    ]),
    it("Accessories", "/collections/bks-accessories", [
        it("Backpacks",     "/pages/bks-backpack"),
        it("Travel Bags",   "/pages/bks-travel-bag"),
        it("Duffel Bags",   "/pages/bks-duffel-bag"),
        it("Beach Towels",  "/pages/bks-beach-towel"),
        it("Flip Flops",    "/pages/bks-flip-flop"),
        it("Shoes",         "/pages/bks-shoes"),
    ]),
    it("Collections", "/collections", [
        it("BKS Hours",   "/collections/bks-hours"),
        it("BKS Origin",  "/collections/bks-origin"),
        it("BKS Glyph",   "/collections/bks-glyph"),
        it("BKS Marker",  "/collections/bks-marker"),
        it("BKS Riviera", "/collections/bks-riviera"),
        it("BKS Pulse",   "/collections/bks-pulse"),
        it("BKS Token",   "/collections/bks-token"),
        it("BKS Flag",    "/collections/bks-flag"),
    ]),
    it("BKS Members", "/pages/bks-members", [
        it("Dashboard",       "/pages/bks-members"),
        it("Wishlist",        "/pages/bks-members#wishlist"),
        it("Camerino",        "/pages/bks-members#camerino"),
        it("Orders",          "/account"),
        it("Studio Requests", "/pages/bks-members#studio-requests"),
    ]),
    it("About",   "/pages/about-bakabo"),
    it("Contact", "/pages/contact"),
    it("Support", "/policies/contact-information", [
        it("Legal Notice",   "/policies/legal-notice"),
        it("Privacy Policy", "/policies/privacy-policy"),
        it("Refund Policy",  "/policies/refund-policy"),
        it("Shipping",       "/policies/shipping-policy"),
        it("Terms",          "/policies/terms-of-service"),
        it("Help & FAQ",     "/pages/help-faq"),
    ]),
]

FIND_Q = "query { menus(first:20) { edges { node { id handle } } } }"
DELETE_Q = "mutation menuDelete($id: ID!) { menuDelete(id: $id) { deletedMenuId userErrors { field message } } }"
CREATE_Q = """
mutation menuCreate($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) {
  menuCreate(title: $title, handle: $handle, items: $items) {
    menu { id handle title items { id title url items { id title url } } }
    userErrors { field message }
  }
}"""

print("=== Fix main-menu-1 ===\n")

# Step 1: trova ed elimina main-menu-1 esistente
menus = [e["node"] for e in gql(FIND_Q)["data"]["menus"]["edges"]]
target = next((m for m in menus if m["handle"] == "main-menu-1"), None)
if target:
    print(f"Elimino menu esistente: {target['id']}")
    res = gql(DELETE_Q, {"id": target["id"]})
    errs = res["data"]["menuDelete"]["userErrors"]
    if errs:
        print(f"  ERRORE delete: {errs}")
        raise SystemExit(1)
    print("  Eliminato.")
    time.sleep(1)
else:
    print("Nessun main-menu-1 esistente.")

# Step 2: crea nuovo menu
print(f"\nCreo main-menu-1 con {len(ITEMS)} voci di primo livello...")
res = gql(CREATE_Q, {"title": "Main menu", "handle": "main-menu-1", "items": ITEMS})
errs = res["data"]["menuCreate"]["userErrors"]
if errs:
    print(f"\nERRORI: {json.dumps(errs, indent=2)}")
    raise SystemExit(1)

menu = res["data"]["menuCreate"]["menu"]
print(f"\nCreato: {menu['id']}  handle={menu['handle']}\n")
for top in menu["items"]:
    print(f"  [{top['title']}] → {top['url']}")
    for sub in top.get("items", []):
        print(f"      └─ {sub['title']} → {sub['url']}")

print("\n=== Fine ===")
