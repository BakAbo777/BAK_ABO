import os, sys, requests, urllib3
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
urllib3.disable_warnings()
ROOT = Path("I:/BAK ABO")
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1); k=k.strip(); v=v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v
DOMAIN=os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN=os.environ["SHOPIFY_ADMIN_TOKEN"]
VER=os.environ.get("SHOPIFY_API_VERSION","2025-01")
THEME="202392961362"
BASE=f"https://{DOMAIN}/admin/api/{VER}"
HDR={"X-Shopify-Access-Token": TOKEN}
src = ROOT / "04_TEMA_SHOPIFY/assets/bks-tryon.css"
body = src.read_text(encoding="utf-8")
r = requests.put(f"{BASE}/themes/{THEME}/assets.json", json={"asset":{"key":"assets/bks-tryon.css","value":body}}, headers=HDR, timeout=30, verify=False)
ok = "OK" if r.status_code in (200,201) else "FAIL"
print(f"  {ok} HTTP {r.status_code}  assets/bks-tryon.css")
