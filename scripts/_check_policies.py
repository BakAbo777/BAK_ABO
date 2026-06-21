"""Check Shopify store policy page titles (live)."""
import os, requests, urllib3
urllib3.disable_warnings()  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN}

r = requests.get(f"https://{DOMAIN}/admin/api/2025-01/policies.json",
                 headers=HDR, verify=False, timeout=20)
for p in r.json().get("policies", []):
    print(f"  [{p['handle']}] title={p['title']!r} url={p['url']}")
