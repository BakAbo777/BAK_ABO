"""Check tema vecchio e pagine duplicate prima di eventuale cleanup."""
import os, requests, urllib3, json
urllib3.disable_warnings()  # type: ignore
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
KW      = {"headers": HDR, "timeout": 20, "verify": False}

# 1) TEMI
print("=== TEMI SHOPIFY ===")
r = requests.get(f"{BASE}/themes.json", **KW)
themes = r.json().get("themes", [])
for t in themes:
    marker = " <-- LIVE" if t["role"] == "main" else ""
    marker += " <-- BACKUP 20/06" if t["id"] == 202600382802 else ""
    marker += " <-- VECCHIO?" if t["id"] == 202388308306 else ""
    print(f"  id={t['id']} name={t['name']!r:40} role={t['role']}{marker}")

# 2) PAGINE DUPLICATE
print("\n=== PAGINE DA VERIFICARE ===")
PAGE_IDS = [171938808146, 173590118738]
for pid in PAGE_IDS:
    r = requests.get(f"{BASE}/pages/{pid}.json", **KW)
    if r.status_code == 200:
        p = r.json().get("page", {})
        print(f"  id={p['id']} handle={p['handle']!r:30} title={p['title']!r} published={p.get('published_at') is not None}")
    else:
        print(f"  id={pid} → {r.status_code} (non trovata o eliminata)")

# 3) MENU PRINCIPALE — verifica se referenziano le pagine
print("\n=== NAVIGAZIONE MAIN MENU ===")
r = requests.get(f"{BASE}/blogs.json", **KW)  # verifica connessione
r2 = requests.get(f"{BASE}/custom_collections.json?limit=5", **KW)

# Shopify non ha API diretta per menu linklist via REST — usiamo GraphQL
GRAPHQL_URL = f"https://{DOMAIN}/admin/api/{VERSION}/graphql.json"
query = """
{
  menu(handle: "main-menu") {
    items {
      title
      url
    }
  }
}
"""
rg = requests.post(GRAPHQL_URL, headers={**HDR, "Content-Type": "application/json"},
                   json={"query": query}, timeout=20, verify=False)
if rg.status_code == 200:
    data = rg.json()
    items = data.get("data", {}).get("menu", {})
    if items:
        print(f"  Main menu items:")
        for item in items.get("items", []):
            print(f"    {item['title']:30} → {item['url']}")
    else:
        print(f"  {data}")
else:
    print(f"  GraphQL error {rg.status_code}")
