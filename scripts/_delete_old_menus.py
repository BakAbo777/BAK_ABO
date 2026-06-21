"""Delete obsolete Shopify navigation menus via GraphQL."""
import os, requests, urllib3, sys, json
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
URL    = f"https://{DOMAIN}/admin/api/2025-01/graphql.json"
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

TO_DELETE = ["main-menu-copy", "main-menu-1", "bks-base-menu", "bks-menu-base", "bks-main-menu-base"]

# 1. Fetch all menus
LIST_QUERY = """{ menus(first: 50) { nodes { id title handle } } }"""
r = requests.post(URL, headers=HDR, json={"query": LIST_QUERY}, verify=False, timeout=20)
menus = r.json().get("data", {}).get("menus", {}).get("nodes", [])
print(f"Found {len(menus)} menus total:")
for m in menus:
    marker = " ← DELETE" if m["handle"] in TO_DELETE else ""
    print(f"  [{m['handle']}] {m['title']}{marker}")

# 2. Delete matching menus
DELETE_MUTATION = """
mutation deleteMenu($id: ID!) {
  menuDelete(id: $id) {
    deletedMenuId
    userErrors { field message }
  }
}
"""
deleted, errors = 0, 0
for m in menus:
    if m["handle"] in TO_DELETE:
        r2 = requests.post(URL, headers=HDR,
                           json={"query": DELETE_MUTATION, "variables": {"id": m["id"]}},
                           verify=False, timeout=20)
        result = r2.json().get("data", {}).get("menuDelete", {})
        errs = result.get("userErrors", [])
        if errs:
            print(f"  ERR [{m['handle']}]: {errs}")
            errors += 1
        else:
            print(f"  DELETED [{m['handle']}] {m['title']}")
            deleted += 1

print(f"\nDeleted: {deleted} | Errors: {errors}")
