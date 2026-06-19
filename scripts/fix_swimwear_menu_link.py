"""Fix one wrong menu item: 'BKS Swimwear' in main-menu-1 points to /pages/bks-sneakers
(copy-paste bug) instead of /pages/bks-swimwear (which exists live). Scoped single-item
fix via menuUpdate, preserving every other item exactly as-is.
"""
import os, requests, urllib3, json, sys
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
GQL = f"https://{DOMAIN}/admin/api/{VERSION}/graphql.json"
HDR = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
STORE = f"https://{os.environ.get('SHOPIFY_STORE', 'bakabo.club')}"


def gql(query, variables=None):
    r = requests.post(GQL, json={"query": query, "variables": variables or {}}, headers=HDR, timeout=30, verify=False)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        print("GraphQL errors:", data["errors"])
    return data


Q = """
{
  menus(first: 20) {
    edges {
      node {
        id title handle
        items { id title url type resourceId
          items { id title url type resourceId }
        }
      }
    }
  }
}
"""

data = gql(Q)
menus = data["data"]["menus"]["edges"]
menu_node = next(e["node"] for e in menus if e["node"]["handle"] == "main-menu-1")
menu_id = menu_node["id"]


def to_update_input(item):
    node = {"id": item["id"], "title": item["title"], "type": item["type"]}
    if item.get("resourceId"):
        node["resourceId"] = item["resourceId"]
    else:
        node["url"] = item["url"]
    if item.get("items"):
        node["items"] = [to_update_input(sub) for sub in item["items"]]
    return node


items_input = []
changed = False
for item in menu_node["items"]:
    built = to_update_input(item)
    if item.get("items"):
        for i, sub in enumerate(item["items"]):
            if sub["title"] == "BKS Swimwear":
                print(f"Found 'BKS Swimwear' raw item: {json.dumps(sub)}")
                built["items"][i].pop("resourceId", None)
                built["items"][i]["url"] = "/pages/bks-swimwear"
                built["items"][i]["type"] = "HTTP"
                changed = True
    items_input.append(built)

if not changed:
    print("Nessuna voce 'BKS Swimwear' trovata da correggere.")
else:
    MUT = """
    mutation menuUpdate($id: ID!, $title: String!, $items: [MenuItemUpdateInput!]!) {
      menuUpdate(id: $id, title: $title, items: $items) {
        menu { id handle }
        userErrors { field message }
      }
    }
    """
    result = gql(MUT, {"id": menu_id, "title": menu_node["title"], "items": items_input})
    print(json.dumps(result, indent=2))
