"""Update the original 'footer' menu with BKS items and delete footer-1 duplicate."""
import os, requests, urllib3, time
from pathlib import Path

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
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
GQL     = f"https://{DOMAIN}/admin/api/{VERSION}/graphql.json"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
STORE   = f"https://{os.environ.get('PRIMARY_DOMAIN', 'bakabo.club')}"

FOOTER_ITEMS = [
    {"title": "Shipping",    "url": f"{STORE}/policies/shipping-policy",  "type": "HTTP"},
    {"title": "Returns",     "url": f"{STORE}/policies/refund-policy",    "type": "HTTP"},
    {"title": "Privacy",     "url": f"{STORE}/policies/privacy-policy",   "type": "HTTP"},
    {"title": "Terms",       "url": f"{STORE}/policies/terms-of-service", "type": "HTTP"},
    {"title": "Contact",     "url": f"{STORE}/pages/contact",             "type": "HTTP"},
    {"title": "Track Order", "url": f"{STORE}/apps/parcelpanel",          "type": "HTTP"},
]

FOOTER_ID    = "gid://shopify/Menu/231167754578"   # original 'footer'
FOOTER_1_ID  = "gid://shopify/Menu/330398957906"   # duplicate 'footer-1'

UPDATE = """
mutation menuUpdate($id: ID!, $title: String!, $items: [MenuItemUpdateInput!]!) {
  menuUpdate(id: $id, title: $title, items: $items) {
    menu { id handle title }
    userErrors { field message }
  }
}"""

DELETE = """
mutation menuDelete($id: ID!) {
  menuDelete(id: $id) { deletedMenuId userErrors { field message } }
}"""


def gql(query, variables=None):
    r = requests.post(GQL, json={"query": query, "variables": variables or {}},
                      headers=HDR, timeout=20, verify=False)
    r.raise_for_status()
    return r.json()


def main():
    print("1. Aggiorno menu 'footer' originale...")
    res = gql(UPDATE, {"id": FOOTER_ID, "title": "Footer menu", "items": FOOTER_ITEMS})
    errs = res.get("data", {}).get("menuUpdate", {}).get("userErrors", [])
    if errs:
        print(f"   ERRORE: {errs}")
    else:
        m = res["data"]["menuUpdate"]["menu"]
        print(f"   OK  handle={m['handle']}  id={m['id']}")

    time.sleep(0.5)

    print("2. Elimino duplicato 'footer-1'...")
    res2 = gql(DELETE, {"id": FOOTER_1_ID})
    errs2 = res2.get("data", {}).get("menuDelete", {}).get("userErrors", [])
    if errs2:
        print(f"   ERRORE: {errs2}")
    else:
        print(f"   OK  eliminato {FOOTER_1_ID}")

    print("\nDone.")


if __name__ == "__main__":
    main()
