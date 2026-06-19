"""Rebuild BKS main menu on Shopify — delete existing + recreate con struttura completa."""
from __future__ import annotations
import os, json, time, requests
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
BASE    = "https://bakabo.club"


def gql(query: str, variables: dict | None = None) -> dict:
    r = requests.post(GQL, json={"query": query, "variables": variables or {}}, headers=HDR, timeout=30, verify=False)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(json.dumps(data["errors"], indent=2))
    return data


def u(path: str) -> str:
    return f"{BASE}{path}"


def it(title: str, path: str, children: list | None = None) -> dict:
    obj: dict = {"title": title, "type": "HTTP", "url": u(path)}
    if children:
        obj["items"] = children
    return obj


# ── Menu completo ─────────────────────────────────────────────────────────────
ITEMS = [
    it("Home", "/"),
    it("Shop", "/collections/all", [
        it("New Arrivals",  "/collections/new-arrivals"),
        it("All Products",  "/collections/all"),
    ]),
    it("Man", "/pages/man-collection", [
        it("BKS Sneakers",          "/collections/sneakers"),
        it("BKS Graphic Sneakers",  "/collections/bks-graphic-sneakers"),
        it("BKS Swim Trunks",       "/collections/swim-trunks"),
        it("BKS Hawaiian Shirts",   "/collections/hawaiian-shirts"),
        it("BKS Pullover Hoodies",  "/collections/pullover-hoodies"),
        it("BKS Athletic Shorts",   "/collections/athletic-shorts"),
        it("BKS Puffer Jackets",    "/collections/puffer-jacket"),
        it("BKS Windbreakers",      "/collections/windbreaker-jackets"),
        it("BKS Graphic Tees",      "/collections/t-shirts"),
    ]),
    it("Woman", "/pages/woman-collection", [
        it("BKS Sneakers",           "/collections/sneakers"),
        it("BKS One-Piece Swimsuits","/collections/one-piece-swimsuits"),
        it("BKS Swimwear",           "/collections/swimwear"),
        it("BKS Racerback Dresses",  "/collections/racerback-dresses"),
        it("BKS Pajama Pants",       "/collections/pajama-pants"),
        it("BKS Pullover Hoodies",   "/collections/pullover-hoodies"),
        it("BKS Puffer Jackets",     "/collections/puffer-jacket"),
        it("BKS Windbreakers",       "/collections/windbreaker-jackets"),
        it("BKS Graphic Tees",       "/collections/t-shirts"),
        it("BKS Flip Flops",         "/collections/flip-flops"),
    ]),
    it("Accessories", "/collections/accessories", [
        it("BKS Backpacks",    "/collections/backpacks"),
        it("BKS Travel Bags",  "/collections/travel-bags"),
        it("BKS Duffel Bags",  "/collections/duffel-bags"),
        it("BKS Beach Towels", "/collections/beach-towels"),
        it("BKS Flip Flops",   "/collections/flip-flops"),
        it("BKS Slippers",     "/collections/slippers"),
        it("BKS Travel Gear",  "/collections/travel-gear"),
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
    it("Drops", "/collections", [
        it("Mondello",       "/collections/mondello"),
        it("Island",         "/collections/island"),
        it("Japan",          "/collections/japan"),
        it("Arcade",         "/collections/arcade"),
        it("Fish Citizens",  "/collections/fish-citizens"),
    ]),
    it("BKS Members", "/pages/bks-members", [
        it("Dashboard",       "/pages/bks-members"),
        it("Wishlist",        "/pages/bks-members#wishlist"),
        it("Camerino",        "/pages/bks-members#camerino"),
        it("Orders",          "/account"),
        it("Studio Requests", "/pages/bks-members#studio-requests"),
    ]),
    it("AI Studio", "/pages/ai-studio"),
    it("About",     "/pages/about-bakabo"),
    it("Contact",   "/pages/contact"),
    it("Support", "/policies/contact-information", [
        it("Contact Information", "/policies/contact-information"),
        it("Legal Notice",        "/policies/legal-notice"),
        it("Privacy Policy",      "/policies/privacy-policy"),
        it("Refund Policy",       "/policies/refund-policy"),
        it("Shipping Policy",     "/policies/shipping-policy"),
        it("Terms of Service",    "/policies/terms-of-service"),
    ]),
]


# ── Step 1: trova menu corrente (non il default) ─────────────────────────────
print("=== BKS Main Menu Rebuild ===\n")
print("Step 1 — Ricerca menu esistenti…")

menus_q = """
query { menus(first: 20) { edges { node { id handle title } } } }
"""
data     = gql(menus_q)
all_menus = [e["node"] for e in data["data"]["menus"]["edges"]]
print(f"  Trovati: {[m['handle'] for m in all_menus]}")

# Cerca esattamente main-menu-1
target = next(
    (m for m in all_menus if m["handle"] == "main-menu-1"),
    None,
)
if not target:
    # Nessun menu custom trovato — creeremo da zero
    print("  Nessun menu custom trovato — creazione diretta.")
    existing_id = None
    new_handle  = "main-menu-1"
else:
    existing_id = target["id"]
    new_handle  = target["handle"]
    print(f"  Target: {target['handle']} ({target['id']})")


# ── Step 2: elimina menu esistente ───────────────────────────────────────────
if existing_id:
    print(f"\nStep 2 — Elimino {new_handle}…")
    del_q = """
    mutation menuDelete($id: ID!) {
      menuDelete(id: $id) {
        deletedMenuId
        userErrors { field message }
      }
    }
    """
    res = gql(del_q, {"id": existing_id})
    errs = res["data"]["menuDelete"]["userErrors"]
    if errs:
        print(f"  ATTENZIONE delete: {errs}")
    else:
        print(f"  Eliminato: {existing_id}")
    time.sleep(2)
else:
    print("\nStep 2 — Skip (nessun menu da eliminare).")


# ── Step 3: crea nuovo menu ───────────────────────────────────────────────────
print(f"\nStep 3 — Creo '{new_handle}' con {len(ITEMS)} voci di primo livello…")

create_q = """
mutation menuCreate($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) {
  menuCreate(title: $title, handle: $handle, items: $items) {
    menu {
      id
      handle
      title
      items {
        id title url
        items { id title url }
      }
    }
    userErrors { field message }
  }
}
"""
res  = gql(create_q, {"title": "Main menu", "handle": new_handle, "items": ITEMS})
errs = res["data"]["menuCreate"]["userErrors"]
if errs:
    print(f"\n  ERRORI: {json.dumps(errs, indent=2)}")
else:
    menu = res["data"]["menuCreate"]["menu"]
    actual_handle = menu["handle"]
    print(f"\n  Creato: {menu['id']}")
    print(f"  Handle: {actual_handle}  (usa questo nel tema se diverso da '{new_handle}')")
    print(f"\n  Voci:")
    for top in menu["items"]:
        print(f"    [{top['title']}] → {top['url']}")
        for sub in top.get("items", []):
            print(f"      └─ [{sub['title']}] → {sub['url']}")

    if actual_handle != new_handle:
        print(f"\n  ⚠ Handle cambiato da '{new_handle}' a '{actual_handle}'")
        print("    Aggiorna bakabo-header.liquid con il nuovo handle!")

print("\n=== Fine ===")
