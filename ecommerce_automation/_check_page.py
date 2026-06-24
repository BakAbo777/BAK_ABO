"""Check page template_suffix. Usage: python _check_page.py <handle>"""
import sys, json, requests
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

handle = sys.argv[1] if len(sys.argv) > 1 else "bks-swim-trunks"
r = requests.get(
    f"https://{env['SHOPIFY_MYSHOPIFY_DOMAIN']}/admin/api/2025-01/pages.json",
    params={"handle": handle, "fields": "id,handle,title,template_suffix"},
    headers={"X-Shopify-Access-Token": env["SHOPIFY_ADMIN_TOKEN"]},
    verify=False, timeout=15,
)
pages = r.json().get("pages", [])
if pages:
    print(json.dumps(pages[0], indent=2))
else:
    print(f"NOT FOUND: {handle}")
