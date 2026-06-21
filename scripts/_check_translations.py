"""
Check Shopify Translations API for Italian product title translations.
Shopify REST: GET /admin/api/2025-01/translations.json (per resource)
GraphQL: translations(resourceId, locale) query
"""
import os, requests, urllib3, json
urllib3.disable_warnings()  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN","")
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

# Check Italian translations for a known legacy product
# Try fetching translations for the "support" menu to confirm API access
r = requests.post(
    f"https://{DOMAIN}/admin/api/2025-01/graphql.json",
    headers=HDR,
    json={"query": """
    {
      translatableResources(resourceType: MENU, first: 5) {
        nodes {
          resourceId
          translatableContent {
            key
            value
            digest
          }
          translations(locale: "it") {
            key
            value
            outdated
          }
        }
      }
    }
    """},
    verify=False, timeout=20
)
data = r.json()
if "errors" in data:
    print(f"GraphQL errors: {data['errors']}")
else:
    print("=== MENU TRANSLATIONS (it) ===")
    for node in data.get("data", {}).get("translatableResources", {}).get("nodes", []):
        rid = node["resourceId"]
        content = {c["key"]: c["value"] for c in node["translatableContent"]}
        translations = node["translations"]
        if translations:
            print(f"\n{rid}")
            for t in translations:
                orig = content.get(t["key"], "?")
                print(f"  [{t['key']}] {orig!r:40} -> IT: {t['value']!r}")

# Also check a product
print("\n\n=== PRODUCT TITLE TRANSLATIONS (it) sample ===")
r2 = requests.post(
    f"https://{DOMAIN}/admin/api/2025-01/graphql.json",
    headers=HDR,
    json={"query": """
    {
      translatableResources(resourceType: PRODUCT, first: 10) {
        nodes {
          resourceId
          translatableContent { key value digest }
          translations(locale: "it") { key value outdated }
        }
      }
    }
    """},
    verify=False, timeout=20
)
data2 = r2.json()
if "errors" in data2:
    print(f"GraphQL errors: {data2['errors']}")
else:
    count = 0
    for node in data2.get("data", {}).get("translatableResources", {}).get("nodes", []):
        translations = [t for t in node["translations"] if t["key"] == "title"]
        if translations:
            content = {c["key"]: c["value"] for c in node["translatableContent"]}
            eng = content.get("title", "?")
            it = translations[0]["value"]
            outdated = translations[0].get("outdated", False)
            print(f"  EN: {eng[:50]:50} IT: {it[:50]} outdated={outdated}")
            count += 1
    if not count:
        print("  (No Italian title translations found in first 10)")
