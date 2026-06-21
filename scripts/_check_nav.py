"""Verifica menu di navigazione e link rotti su Shopify."""
import os, requests, urllib3, json
urllib3.disable_warnings()

for raw in open("I:/BAK ABO/.env", encoding="utf-8"):
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ:
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VER     = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
GRAPHQL = f"https://{DOMAIN}/admin/api/{VER}/graphql.json"

QUERY = """
{
  menu1: menu(handle: "main-menu-1") {
    title
    items { title url items { title url } }
  }
  menu2: menu(handle: "main-menu") {
    title
    items { title url items { title url } }
  }
}
"""

r = requests.post(GRAPHQL, json={"query": QUERY}, headers=HDR, verify=False, timeout=20)
data = r.json().get("data", {})

for key in ("menu1", "menu2"):
    menu = data.get(key)
    if not menu:
        print(f"--- {key}: not found")
        continue
    print(f"\n=== {menu['title']} ({key}) ===")
    for item in menu.get("items", []):
        print(f"  {item['title']}  ->  {item['url']}")
        for sub in item.get("items", []):
            print(f"      {sub['title']}  ->  {sub['url']}")

r2 = requests.get(
    f"https://{DOMAIN}/admin/api/{VER}/pages.json?handle=contact&limit=1",
    headers={"X-Shopify-Access-Token": TOKEN}, verify=False, timeout=10
)
pages_contact = r2.json().get("pages", [])
print(f"\n/pages/contact -> {'EXISTS' if pages_contact else 'MISSING'}")
