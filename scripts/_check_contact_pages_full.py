"""Show full body of both contact pages."""
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
HDR    = {"X-Shopify-Access-Token": TOKEN}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

for pid in [120387338578, 173871792466]:
    r = requests.get(f"{BASE}/pages/{pid}.json", headers=HDR, verify=False, timeout=20)
    p = r.json().get("page", {})
    print(f"\n{'='*60}")
    print(f"[{p['id']}] handle='{p['handle']}'  title='{p['title']}'  pub={str(p.get('published_at',''))[:10]}")
    print(f"BODY:\n{p.get('body_html','')}")
