"""Test if read_translations scope is now available."""
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
DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
GRAPHQL = f"https://{DOMAIN}/admin/api/2025-01/graphql.json"

# Fetch first product GID
r0 = requests.post(GRAPHQL, headers=HDR,
    json={"query": "{ products(first:1){ edges{ node{ id title } } } }"},
    verify=False, timeout=20)
gid = r0.json()["data"]["products"]["edges"][0]["node"]["id"]
title = r0.json()["data"]["products"]["edges"][0]["node"]["title"]
print(f"Test product: {title} ({gid})")

# Try reading Italian translations
QUERY = """
query($id: ID!, $locale: String!) {
  translatableResource(resourceId: $id) {
    resourceId
    translations(locale: $locale) { key value locale }
  }
}
"""
r = requests.post(GRAPHQL, headers=HDR,
    json={"query": QUERY, "variables": {"id": gid, "locale": "it"}},
    verify=False, timeout=20)
data = r.json()

if "errors" in data:
    errs = data["errors"]
    for e in errs:
        msg = e.get("message","")
        if "access" in msg.lower() or "scope" in msg.lower() or "unauthorized" in msg.lower():
            print(f"\nSCOPE MISSING: {msg}")
            print("=> Add read_translations + write_translations to API token, then re-run the bulk delete script.")
        else:
            print(f"\nERR: {msg}")
else:
    translations = data.get("data",{}).get("translatableResource",{}).get("translations",[])
    print(f"\nread_translations: OK — found {len(translations)} Italian translation(s)")
    for t in translations:
        print(f"  key={t['key']}  value='{t['value'][:60]}'")
    if not translations:
        print("  (no Italian translations for this product)")
    print("\n=> Scope is available. Safe to run _bulk_delete_italian_translations.py")
