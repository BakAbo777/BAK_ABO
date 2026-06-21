"""Remove all published Shopify languages except English and Italian."""
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
URL    = f"https://{DOMAIN}/admin/api/2025-01/graphql.json"
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

KEEP = {"en", "it"}

# 1. List all shop locales
LIST = """{ shopLocales { locale name primary published } }"""
r = requests.post(URL, headers=HDR, json={"query": LIST}, verify=False, timeout=20)
print(f"Response: {r.status_code} {r.text[:200]}")
locales = (r.json() or {}).get("data", {}).get("shopLocales", [])
print(f"Current locales ({len(locales)}):")
for l in locales:
    marker = "KEEP" if l["locale"] in KEEP else "REMOVE"
    print(f"  [{l['locale']}] {l['name']} published={l['published']} primary={l['primary']} → {marker}")

# 2. Remove unwanted locales
REMOVE_MUTATION = """
mutation removeLocale($locale: String!) {
  shopLocaleDisable(locale: $locale) {
    locale
    userErrors { field message }
  }
}
"""
removed, errors = 0, 0
for l in locales:
    if l["locale"] in KEEP or l["primary"]:
        continue
    r2 = requests.post(URL, headers=HDR,
                       json={"query": REMOVE_MUTATION, "variables": {"locale": l["locale"]}},
                       verify=False, timeout=20)
    result = r2.json().get("data", {}).get("shopLocaleDisable", {})
    errs = result.get("userErrors", [])
    if errs:
        print(f"  ERR [{l['locale']}]: {errs}")
        errors += 1
    else:
        print(f"  REMOVED [{l['locale']}] {l['name']}")
        removed += 1

print(f"\nRemoved: {removed} | Errors: {errors}")
print("Remaining: English (default) + Italian")
