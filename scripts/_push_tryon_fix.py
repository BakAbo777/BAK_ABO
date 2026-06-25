"""Push bks-tryon.js (iOS download fix) to Shopify live theme."""
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
THEME  = "202392961362"
BASE   = f"https://{DOMAIN}/admin/api/2025-01"
HDR    = {"X-Shopify-Access-Token": TOKEN}

key  = "assets/bks-tryon.js"
body = (ROOT / "04_TEMA_SHOPIFY" / key).read_text(encoding="utf-8")
r = requests.put(f"{BASE}/themes/{THEME}/assets.json",
    json={"asset": {"key": key, "value": body}},
    headers=HDR, timeout=30, verify=False)
print(f"{r.status_code}  {key}")
if r.status_code not in (200, 201):
    print(r.text[:200])
