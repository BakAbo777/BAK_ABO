import os, requests, urllib3
urllib3.disable_warnings()
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
BASE   = f"https://{DOMAIN}/admin/api/2025-01"
HDR    = {"X-Shopify-Access-Token": TOKEN}
KW     = {"headers": HDR, "timeout": 20, "verify": False}

r = requests.get(f"{BASE}/products/count.json?collection_id=686367211858", **KW)
print("Products count:", r.json())
r2 = requests.get(f"{BASE}/custom_collections/686367211858.json", **KW)
c = r2.json().get("custom_collection", {})
print("title:", c.get("title"))
print("body:", c.get("body_html", "")[:80])
print("published_at:", c.get("published_at"))
