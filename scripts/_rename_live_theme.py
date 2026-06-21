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

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
BASE    = f"https://{DOMAIN}/admin/api/2025-01"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
KW      = {"headers": HDR, "timeout": 20, "verify": False}

LIVE_ID  = 202392961362
NEW_NAME = "BKS TM04 20_06_2026 V.22"

r = requests.put(f"{BASE}/themes/{LIVE_ID}.json",
    json={"theme": {"id": LIVE_ID, "name": NEW_NAME}},
    **KW)
if r.status_code == 200:
    t = r.json().get("theme", {})
    print(f"OK: id={t['id']} name={t['name']!r} role={t['role']}")
else:
    print(f"ERROR {r.status_code}: {r.text[:300]}")
