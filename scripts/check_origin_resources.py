"""Read-only check: live Page/Collection resources for bks-origin / bks-folklore handles, and any products still tagged Folklore."""
import os, requests, urllib3, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]:
        os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}


def get(path, params=None):
    r = requests.get(f"{BASE}/{path}", headers=HDR, params=params, timeout=30, verify=False)
    r.raise_for_status()
    return r.json()


print("=== PAGES (handle bks-origin / bks-folklore) ===")
for handle in ("bks-origin", "bks-folklore"):
    data = get("pages.json", {"handle": handle})
    pages = data.get("pages", [])
    if not pages:
        print(f"  {handle}: NESSUNA pagina trovata")
    for p in pages:
        print(f"  {handle}: id={p['id']} title=\"{p['title']}\" template_suffix={p.get('template_suffix')!r} published={bool(p.get('published_at'))}")

print("\n=== CUSTOM COLLECTIONS (handle bks-origin / bks-folklore) ===")
for handle in ("bks-origin", "bks-folklore"):
    data = get("custom_collections.json", {"handle": handle})
    cols = data.get("custom_collections", [])
    if not cols:
        print(f"  {handle}: NESSUNA custom collection trovata")
    for c in cols:
        print(f"  {handle}: id={c['id']} title=\"{c['title']}\" template_suffix={c.get('template_suffix')!r} published={bool(c.get('published_at'))}")

print("\n=== SMART COLLECTIONS (handle bks-origin / bks-folklore) ===")
for handle in ("bks-origin", "bks-folklore"):
    data = get("smart_collections.json", {"handle": handle})
    cols = data.get("smart_collections", [])
    if not cols:
        print(f"  {handle}: NESSUNA smart collection trovata")
    for c in cols:
        print(f"  {handle}: id={c['id']} title=\"{c['title']}\" template_suffix={c.get('template_suffix')!r} published={bool(c.get('published_at'))}")

print("\n=== PRODOTTI TAGGATI Folklore (via GraphQL search) ===")
GQL = f"{BASE}/graphql.json"
Q = """
{
  products(first: 20, query: "tag:Folklore OR tag:folklore OR tag:bks-folklore") {
    edges { node { id title handle tags } }
  }
}
"""
r = requests.post(GQL, json={"query": Q}, headers=HDR, timeout=30, verify=False)
edges = r.json().get("data", {}).get("products", {}).get("edges", [])
if not edges:
    print("  Nessun prodotto trovato con tag Folklore.")
for e in edges:
    n = e["node"]
    print(f"  {n['handle']}: \"{n['title']}\" tags={n['tags']}")
