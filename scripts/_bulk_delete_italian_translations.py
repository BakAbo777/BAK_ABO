









"""
Bulk delete Italian product title translations.
Requires: read_translations + write_translations scopes on the API token.

When Italian locale is active, Shopify shows TRANSLATED titles stored in
the translation layer — these are the old Printify Italian names.
This script deletes all Italian 'title' translations for products so that
the English master titles show in all locales.

Run AFTER adding the two scopes to the Shopify custom app.
"""
import io, os, requests, urllib3, sys, time
urllib3.disable_warnings()  # type: ignore
if isinstance(sys.stdout, io.TextIOWrapper):
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
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
GRAPHQL = f"https://{DOMAIN}/admin/api/2025-01/graphql.json"

LOCALE = "it"

# ── Step 1: Fetch all product GIDs ────────────────────────────────────────
PRODUCTS_QUERY = """
query getProducts($cursor: String) {
  products(first: 250, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    edges {
      node { id title }
    }
  }
}
"""

product_gids = []
cursor = None
while True:
    r = requests.post(GRAPHQL, headers=HDR,
        json={"query": PRODUCTS_QUERY, "variables": {"cursor": cursor}},
        verify=False, timeout=30)
    data = r.json()
    edges = data.get("data", {}).get("products", {}).get("edges", [])
    for e in edges:
        product_gids.append(e["node"]["id"])
    pi = data.get("data", {}).get("products", {}).get("pageInfo", {})
    if not pi.get("hasNextPage"):
        break
    cursor = pi["endCursor"]
    time.sleep(0.3)

print(f"Total products: {len(product_gids)}")

# ── Step 2: For each product, fetch Italian translations ──────────────────
TRANSLATIONS_QUERY = """
query getTranslations($id: ID!, $locale: String!) {
  translatableResource(resourceId: $id) {
    resourceId
    translations(locale: $locale) {
      key
      value
      locale
    }
  }
}
"""

REMOVE_MUTATION = """
mutation removeTranslations($resourceId: ID!, $translationKeys: [String!]!, $locales: [String!]!) {
  translationsRemove(
    resourceId: $resourceId
    translationKeys: $translationKeys
    locales: $locales
  ) {
    removedTranslations { locale key }
    userErrors { field message }
  }
}
"""

removed = 0
skipped = 0
errors  = 0

for gid in product_gids:
    # Fetch translations
    r = requests.post(GRAPHQL, headers=HDR,
        json={"query": TRANSLATIONS_QUERY, "variables": {"id": gid, "locale": LOCALE}},
        verify=False, timeout=20)
    resource = r.json().get("data", {}).get("translatableResource", {})
    translations = resource.get("translations", [])

    title_trans = [t for t in translations if t["key"] == "title"]
    if not title_trans:
        skipped += 1
        continue

    # Remove the title translation
    r2 = requests.post(GRAPHQL, headers=HDR,
        json={"query": REMOVE_MUTATION, "variables": {
            "resourceId": gid,
            "translationKeys": ["title"],
            "locales": [LOCALE],
        }},
        verify=False, timeout=20)
    result = r2.json()
    errs = result.get("data", {}).get("translationsRemove", {}).get("userErrors", [])
    if errs:
        print(f"  ERR {gid}: {errs}")
        errors += 1
    else:
        removed_list = result.get("data", {}).get("translationsRemove", {}).get("removedTranslations", [])
        val_preview = title_trans[0]["value"][:60]
        print(f"  DEL [{gid[-8:]}] Italian title: '{val_preview}'")
        removed += 1

    time.sleep(0.15)  # rate limit

print(f"\nDone: {removed} Italian title translations deleted, {skipped} had none, {errors} errors")
print("\nNote: Products will now show English master titles in ALL locales.")
print("Italian visitors will see the same English titles as English visitors.")
