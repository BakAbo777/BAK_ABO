"""List BKS pages and their template suffixes."""
import requests
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

SHOP  = env["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN = env["SHOPIFY_ADMIN_TOKEN"]

r = requests.get(
    f"https://{SHOP}/admin/api/2025-01/pages.json",
    params={"limit": 250, "fields": "id,handle,title,template_suffix"},
    headers={"X-Shopify-Access-Token": TOKEN},
    verify=False, timeout=30,
)
pages = r.json().get("pages", [])
bks = [p for p in pages if "bks-" in p.get("handle", "")]
for p in sorted(bks, key=lambda x: x["handle"]):
    print(f"{p['handle']:45s} template='{p.get('template_suffix') or '(default)'}' id={p['id']}")
print(f"\nTotal: {len(bks)} BKS pages")
