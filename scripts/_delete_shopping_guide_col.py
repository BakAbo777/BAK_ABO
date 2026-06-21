import os, requests, urllib3
urllib3.disable_warnings()  # type: ignore
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

COL_ID = 686367211858
r = requests.delete(f"{BASE}/custom_collections/{COL_ID}.json", **KW)
print(f"DELETE /custom_collections/{COL_ID} status={r.status_code}")
if r.status_code == 200:
    print("OK — bks-shopping-guide collection eliminata")
else:
    print(r.text[:300])
