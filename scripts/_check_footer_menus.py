"""Check all navigation menus for Italian labels."""
import os, requests, urllib3, sys
urllib3.disable_warnings()  # type: ignore
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
from pathlib import Path
for raw in Path("I:/BAK ABO/.env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ:
            os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
GRAPHQL = f"https://{DOMAIN}/admin/api/2025-01/graphql.json"

QUERY = """
{
  menus(first: 20) {
    edges {
      node {
        id
        handle
        title
        items {
          id
          title
          url
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

r = requests.post(GRAPHQL, headers=HDR, json={"query": QUERY}, verify=False, timeout=20)
menus = r.json().get("data", {}).get("menus", {}).get("edges", [])
print(f"Menus found: {len(menus)}\n")
for edge in menus:
    m = edge["node"]
    print(f"[{m['handle']}] '{m['title']}' — {m['id']}")
    for item in m.get("items", []):
        print(f"  • {item['title']:35} {item.get('url','')}")
        for sub in item.get("items", []):
            print(f"      - {sub['title']:31} {sub.get('url','')}")
    print()
