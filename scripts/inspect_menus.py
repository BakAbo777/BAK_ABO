"""List all existing Shopify menus with their items."""
import os, requests, urllib3, json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

urllib3.disable_warnings()
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

Q = """
{
  menus(first: 20) {
    edges {
      node {
        id
        title
        handle
        items {
          id
          title
          url
          type
          items {
            id
            title
            url
          }
        }
      }
    }
  }
}
"""

r = requests.post(GQL, json={"query": Q}, headers=HDR, timeout=20, verify=False)
menus = r.json().get("data", {}).get("menus", {}).get("edges", [])

print(f"Menu esistenti: {len(menus)}\n")
for edge in menus:
    m = edge["node"]
    print(f"  [{m['handle']}]  \"{m['title']}\"  id={m['id']}")
    for item in m.get("items", []):
        print(f"    - {item['title']}  ({item['url']})")
        for sub in item.get("items", []):
            print(f"        - {sub['title']}  ({sub['url']})")
    print()
