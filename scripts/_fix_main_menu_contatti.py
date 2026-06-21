"""Fix 'Contatti' → 'Contact' in main-menu via menuUpdate."""
import os, requests, urllib3, json
urllib3.disable_warnings()  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

MENU_GID = "gid://shopify/Menu/231167721810"

# Fetch current items
r = requests.post(f"https://{DOMAIN}/admin/api/2025-01/graphql.json", headers=HDR,
    json={"query": f'{{ menu(id: "{MENU_GID}") {{ id handle title items {{ id title url type }} }} }}'},
    verify=False, timeout=20)
menu = r.json()["data"]["menu"]
print(f"Menu: {menu['handle']}")

# Build updated items list — change 'Contatti' to 'Contact'
updated_items = []
for item in menu["items"]:
    new_title = "Contact" if item["title"] == "Contatti" else item["title"]
    updated_items.append({
        "id": item["id"],
        "title": new_title,
        "url": item["url"],
        "type": item["type"],
    })
    print(f"  {item['title']!r:30} -> {new_title!r}")

mutation = """
mutation menuUpdate($id: ID!, $title: String!, $items: [MenuItemUpdateInput!]!) {
  menuUpdate(id: $id, title: $title, items: $items) {
    menu { id handle title items { id title url } }
    userErrors { field message }
  }
}
"""

r = requests.post(f"https://{DOMAIN}/admin/api/2025-01/graphql.json", headers=HDR,
    json={"query": mutation, "variables": {
        "id": MENU_GID,
        "title": menu["title"],
        "items": updated_items,
    }},
    verify=False, timeout=20)
result = r.json()
if "errors" in result:
    print(f"\nGraphQL errors: {result['errors']}")
else:
    data = result.get("data", {}).get("menuUpdate", {})
    errs = data.get("userErrors", [])
    if errs:
        print(f"\nUser errors: {errs}")
    else:
        print("\nOK — menu updated:")
        for item in data["menu"]["items"]:
            print(f"  {item['title']!r} -> {item['url']}")
