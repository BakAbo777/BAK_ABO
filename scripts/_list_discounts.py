import os, requests, urllib3
from pathlib import Path
urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1); k=k.strip(); v=v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
HDR = {"X-Shopify-Access-Token": TOKEN}
BASE = f"https://{DOMAIN}/admin/api/2025-01"
r = requests.get(f"{BASE}/price_rules.json?limit=50", headers=HDR, verify=False, timeout=15)
rules = r.json().get("price_rules", [])
print(f"Total: {len(rules)}")
for x in rules:
    print(f"  {x['id']}: '{x['title']}' | value={x['value']}")
