"""
Fix BKS Glyph page: unescape HTML entities in body_html.
Also check all BKS collection/product pages for the same escaped-HTML issue.
"""
import os, requests, urllib3, sys, html
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
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

# Fetch all pages and find ones with escaped HTML
r = requests.get(f"{BASE}/pages.json?limit=250&fields=id,title,handle,body_html",
                 headers=HDR, verify=False, timeout=30)
pages = r.json().get("pages", [])

fixed = 0
for p in pages:
    body = p.get("body_html") or ""
    # Detect escaped HTML: body contains &lt; which is < in HTML source
    if "&lt;" in body and "&gt;" in body:
        clean = html.unescape(body)
        print(f"  ESCAPED [{p['id']}] '{p['title']}' handle={p['handle']}")
        print(f"    before: {body[:80]}")
        print(f"    after:  {clean[:80]}")
        r2 = requests.put(f"{BASE}/pages/{p['id']}.json", headers=HDR,
                          json={"page": {"id": p["id"], "body_html": clean}},
                          verify=False, timeout=20)
        if r2.ok:
            print(f"    -> FIXED")
            fixed += 1
        else:
            print(f"    -> ERR {r2.status_code}")

if fixed == 0:
    print("No escaped-HTML pages found (or all already clean).")
else:
    print(f"\nFixed {fixed} pages with escaped HTML.")
