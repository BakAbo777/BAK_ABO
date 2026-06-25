"""Check Roberto's customer tags on Shopify."""
import os, requests, urllib3
from pathlib import Path
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
HDR    = {"X-Shopify-Access-Token": TOKEN}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"
CID    = "9137173365074"

r = requests.get(f"{BASE}/customers/{CID}.json?fields=id,first_name,email,tags,orders_count",
                 headers=HDR, verify=False, timeout=15)
c = r.json().get("customer", {})
print(f"Name:   {c.get('first_name')}")
print(f"Email:  {c.get('email')}")
print(f"Orders: {c.get('orders_count')}")
print(f"Tags:   [{c.get('tags')}]")
