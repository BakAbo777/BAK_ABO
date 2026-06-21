"""
Fix 1: Ricostruisce main-menu-1 con struttura esatta da Roberto.
Fix 2: Imposta bks_use_context_color=false in tutti i template collection su Shopify live.
"""
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
REST    = f"https://{DOMAIN}/admin/api/{VER}"
THEME   = os.environ.get("SHOPIFY_THEME_ID", "202392961362")
HDR_GQL = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
HDR_REST= {"X-Shopify-Access-Token": TOKEN}
BASE    = "https://bakabo.club"


def gql(query, variables=None):
    r = requests.post(GQL, json={"query": query, "variables": variables or {}},
                      headers=HDR_GQL, timeout=30, verify=False)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(json.dumps(data["errors"], indent=2))
    return data


def rest_get(path):
    r = requests.get(f"{REST}{path}", headers=HDR_REST, timeout=20, verify=False)
    r.raise_for_status()
    return r.json()


def rest_put(path, payload):
    r = requests.put(f"{REST}{path}", json=payload, headers=HDR_REST, timeout=20, verify=False)
    r.raise_for_status()
    return r.json()


def u(path):
    return f"{BASE}{path}"


def it(title, path, children=None):
    obj = {"title": title, "type": "HTTP", "url": u(path)}
    if children:
        obj["items"] = children
    return obj


# ═══════════════════════════════════════════════════════════════════
# FIX 1 — Menu struttura esatta
# ═══════════════════════════════════════════════════════════════════
ITEMS = [
    it("Home", "/"),
    it("BKS Man", "/pages/bks-men"),
    it("BKS Woman", "/pages/bks-woman"),
    it("Collections", "/collections", [
        it("BKS Hours",       "/collections/bks-hours"),
        it("BKS Origin",      "/collections/bks-origin"),
        it("BKS Glyph",       "/collections/bks-glyph"),
        it("BKS Marker",      "/collections/bks-marker"),
        it("BKS Riviera",     "/collections/bks-riviera"),
        it("BKS Pulse",       "/collections/bks-pulse"),
        it("BKS Token",       "/collections/bks-token"),
        it("BKS Flag",        "/collections/bks-flag"),
        it("All collections", "/collections"),
    ]),
    it("Product Types", "/collections/all", [
        it("BKS Puffer Jackets",      "/pages/bks-puffer-jackets"),
        it("BKS Windbreakers",        "/pages/bks-windbreakers"),
        it("BKS Pullover Hoodies",    "/pages/bks-pullover-hoodie"),
        it("BKS Lounge Pants",        "/pages/bks-lounge-pants"),
        it("BKS Sneakers",            "/pages/bks-sneakers"),
        it("BKS Backpacks",           "/pages/bks-backpack"),
        it("BKS Travel Bags",         "/pages/bks-travel-bag"),
        it("BKS Swimwear",            "/pages/bks-swimwear"),
        it("BKS Flip Flops",          "/pages/bks-flip-flop"),
        it("BKS Athletic Shorts",     "/pages/bks-athletic-shorts"),
        it("BKS One-Piece Swimsuits", "/pages/bks-one-piece-swimsuits"),
        it("BKS Racerback Dresses",   "/pages/bks-racerback-dresses"),
        it("BKS Swim Trunks",         "/pages/bks-swim-trunks"),
        it("BKS Hawaiian Shirts",     "/pages/bks-hawaiian-shirt"),
        it("BKS Beach Towels",        "/pages/bks-beach-towel"),
        it("BKS Duffel Bags",         "/pages/bks-duffel-bag"),
        it("All products",            "/collections/all"),
    ]),
    it("BKS Members", "/pages/bks-members", [
        it("Wishlist",       "/pages/bks-members#wishlist"),
        it("Mobile Try-On",  "/pages/bks-members#camerino"),
        it("Account",        "/account"),
        it("Cart",           "/cart"),
    ]),
    it("About", "/pages/about-bakabo"),
]

FIND_Q   = "query { menus(first:20) { edges { node { id handle } } } }"
DELETE_Q = "mutation menuDelete($id: ID!) { menuDelete(id: $id) { deletedMenuId userErrors { field message } } }"
CREATE_Q = """
mutation menuCreate($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) {
  menuCreate(title: $title, handle: $handle, items: $items) {
    menu { id handle title items { id title url items { id title url } } }
    userErrors { field message }
  }
}"""

print("=== FIX 1 — main-menu-1 ===\n")
menus = [e["node"] for e in gql(FIND_Q)["data"]["menus"]["edges"]]
target = next((m for m in menus if m["handle"] == "main-menu-1"), None)
if target:
    print(f"Elimino menu esistente: {target['id']}")
    res = gql(DELETE_Q, {"id": target["id"]})
    errs = res["data"]["menuDelete"]["userErrors"]
    if errs:
        print(f"  ERRORE delete: {errs}"); raise SystemExit(1)
    print("  Eliminato.")
    time.sleep(1)

res  = gql(CREATE_Q, {"title": "Main menu", "handle": "main-menu-1", "items": ITEMS})
errs = res["data"]["menuCreate"]["userErrors"]
if errs:
    print(f"ERRORI: {json.dumps(errs, indent=2)}"); raise SystemExit(1)

menu = res["data"]["menuCreate"]["menu"]
print(f"Creato: {menu['id']}  handle={menu['handle']}")
for top in menu["items"]:
    print(f"  [{top['title']}]")
    for sub in top.get("items", []):
        print(f"      └─ {sub['title']}")
print()


# ═══════════════════════════════════════════════════════════════════
# FIX 2 — bks_use_context_color = false in tutti i template live
# ═══════════════════════════════════════════════════════════════════
print("=== FIX 2 — uniforma colori collection templates ===\n")

# Legge la lista asset del tema
assets_data = rest_get(f"/themes/{THEME}/assets.json")
assets = assets_data.get("assets", [])

collection_templates = [
    a["key"] for a in assets
    if a["key"].startswith("templates/collection") and a["key"].endswith(".json")
]
print(f"Template collection trovati: {len(collection_templates)}")

ok_count = 0
skip_count = 0
err_count = 0

for key in sorted(collection_templates):
    # Scarica il template
    asset_data = rest_get(f"/themes/{THEME}/assets.json?asset[key]={key}")
    asset = asset_data.get("asset", {})
    raw = asset.get("value", "")
    if not raw:
        print(f"  SKIP {key} (vuoto)")
        skip_count += 1
        continue

    try:
        tmpl = json.loads(raw)
    except json.JSONDecodeError:
        print(f"  ERR  {key} (json invalido)")
        err_count += 1
        continue

    changed = False
    for sec_id, sec in tmpl.get("sections", {}).items():
        settings = sec.get("settings", {})
        # Rimuovi context color per avere sfondo neutro uniforme
        if settings.get("bks_use_context_color") is True:
            settings["bks_use_context_color"] = False
            changed = True
        # Assicura color_scheme neutro (background-1 = bianco/crema del tema)
        if "color_scheme" in settings and settings["color_scheme"] not in ("background-1", "background-2"):
            settings["color_scheme"] = "background-1"
            changed = True

    if not changed:
        print(f"  OK   {key} (nessuna modifica necessaria)")
        skip_count += 1
        continue

    # Carica il template aggiornato
    updated_raw = json.dumps(tmpl, ensure_ascii=False, indent=2)
    put_data = rest_put(f"/themes/{THEME}/assets.json", {
        "asset": {"key": key, "value": updated_raw}
    })
    if "asset" in put_data:
        print(f"  PUSH {key}")
        ok_count += 1
    else:
        print(f"  ERR  {key}: {put_data}")
        err_count += 1

    time.sleep(0.4)

print(f"\nFix 2 completato: {ok_count} aggiornati, {skip_count} invariati, {err_count} errori")
print("\n=== Fine ===")
