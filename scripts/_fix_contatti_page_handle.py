"""
Rename page handle contatti -> contact and update main menu URL.
Steps:
  1. Find page with handle 'contatti'
  2. Update page handle to 'contact'
  3. Fetch main menu, replace /pages/contatti -> /pages/contact, push menuUpdate
"""
import os, requests, json, urllib3, sys
urllib3.disable_warnings()  # type: ignore
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
from pathlib import Path

for raw in Path("I:/BAK ABO/.env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ:
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR_JSON = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
HDR_GQL  = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
BASE    = f"https://{DOMAIN}/admin/api/2025-01"
GRAPHQL = f"https://{DOMAIN}/admin/api/2025-01/graphql.json"
MENU_GID = "gid://shopify/Menu/231167721810"

# ── Step 1: Find the page ──────────────────────────────────────────────────
r = requests.get(f"{BASE}/pages.json?handle=contatti&fields=id,title,handle",
                 headers=HDR_JSON, verify=False, timeout=20)
pages = r.json().get("pages", [])
if not pages:
    print("No page found with handle 'contatti' — maybe already renamed?")
    # Still proceed to fix menu URL just in case
    page_id = None
else:
    page = pages[0]
    page_id = page["id"]
    print(f"Found: [{page_id}] '{page['title']}' handle='{page['handle']}'")

# ── Step 2: Rename page handle ─────────────────────────────────────────────
if page_id:
    r2 = requests.put(
        f"{BASE}/pages/{page_id}.json",
        headers=HDR_JSON,
        json={"page": {"id": page_id, "handle": "contact"}},
        verify=False, timeout=20
    )
    if r2.ok:
        updated = r2.json().get("page", {})
        print(f"Page handle updated: '{updated.get('handle')}' (id={updated.get('id')})")
    else:
        print(f"ERR updating page: {r2.status_code} {r2.text[:200]}")

# ── Step 3: Fetch current main menu ───────────────────────────────────────
QUERY_MENU = """
query getMenu($id: ID!) {
  menu(id: $id) {
    id
    title
    items {
      id
      title
      url
      type
      items {
        id
        title
        url
        type
      }
    }
  }
}
"""
r3 = requests.post(GRAPHQL,
    headers=HDR_GQL,
    json={"query": QUERY_MENU, "variables": {"id": MENU_GID}},
    verify=False, timeout=20)
data = r3.json()
menu = data.get("data", {}).get("menu", {})
print(f"\nCurrent menu '{menu.get('title')}' — {len(menu.get('items',[]))} items")

# ── Step 4: Build updated items list replacing /pages/contatti ─────────────
def fix_url(url):
    if url and "/pages/contatti" in url:
        return url.replace("/pages/contatti", "/pages/contact")
    return url

def item_to_input(item):
    inp = {
        "id":    item["id"],
        "title": item["title"],
        "url":   fix_url(item.get("url") or ""),
        "type":  item["type"],
    }
    if item.get("items"):
        inp["items"] = [item_to_input(sub) for sub in item["items"]]
    return inp

new_items = [item_to_input(i) for i in menu.get("items", [])]

# Show diff
for i in new_items:
    orig_url = next((x.get("url") for x in menu["items"] if x["id"] == i["id"]), "")
    if orig_url != i["url"]:
        print(f"  URL change: '{orig_url}' -> '{i['url']}'")

# ── Step 5: Push menuUpdate ────────────────────────────────────────────────
MUTATION = """
mutation menuUpdate($id: ID!, $title: String!, $items: [MenuItemUpdateInput!]!) {
  menuUpdate(id: $id, title: $title, items: $items) {
    menu { id title items { id title url } }
    userErrors { field message }
  }
}
"""
r4 = requests.post(GRAPHQL,
    headers=HDR_GQL,
    json={"query": MUTATION, "variables": {
        "id":    MENU_GID,
        "title": menu["title"],
        "items": new_items,
    }},
    verify=False, timeout=20)
result = r4.json()
errors = result.get("data", {}).get("menuUpdate", {}).get("userErrors", [])
if errors:
    print(f"menuUpdate errors: {errors}")
else:
    updated_menu = result.get("data", {}).get("menuUpdate", {}).get("menu", {})
    print(f"\nmenuUpdate OK — '{updated_menu.get('title')}' {len(updated_menu.get('items',[]))} items")
    for item in updated_menu.get("items", []):
        print(f"  {item['title']:30} {item.get('url','')}")
