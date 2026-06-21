"""Check all contact-related pages."""
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

r = requests.get(f"{BASE}/pages.json?fields=id,title,handle,published_at,body_html&limit=250",
                 headers=HDR, verify=False, timeout=20)
pages = r.json().get("pages", [])
contact_pages = [p for p in pages if any(x in p["handle"].lower() for x in ["contact", "contatt"])]
print(f"Contact-related pages ({len(contact_pages)}):")
for p in contact_pages:
    body_preview = (p.get("body_html") or "")[:80].replace("\n", " ")
    print(f"  [{p['id']}] handle='{p['handle']}'  title='{p['title']}'")
    print(f"    pub={str(p.get('published_at',''))[:10]}  body_preview: {body_preview}")
