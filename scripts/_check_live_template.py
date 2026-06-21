"""Legge il template collection.bks-origin.json live su Shopify."""
import os, requests, urllib3, json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
urllib3.disable_warnings()  # type: ignore
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
VER    = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
THEME  = "202392961362"
BASE   = f"https://{DOMAIN}/admin/api/{VER}"
HDR    = {"X-Shopify-Access-Token": TOKEN}

r = requests.get(f"{BASE}/themes/{THEME}/assets.json?asset[key]=templates/collection.bks-origin.json",
                 headers=HDR, verify=False)
asset = r.json().get("asset", {})
raw   = asset.get("value", "")
if raw:
    tmpl = json.loads(raw)
    print(json.dumps(tmpl, indent=2, ensure_ascii=False))
else:
    print("Vuoto o non trovato")
