"""Download verse templates from live theme to local."""
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
THEME  = "202392961362"
SRC    = ROOT / "04_TEMA_SHOPIFY"

keys = [
    "templates/page.bks-verse.json",
    "templates/page.bks-verse-hall.json",
    "sections/bks-verse-intro.liquid",
    "sections/bks-verse-leaderboard.liquid",
]

for key in keys:
    r = requests.get(f"{BASE}/themes/{THEME}/assets.json?asset[key]={key}",
                     headers=HDR, verify=False, timeout=15)
    if r.status_code == 200:
        content = r.json().get("asset", {}).get("value", "")
        dest = SRC / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        print(f"  OK  {key} ({len(content)} chars)")
    else:
        print(f"  ERR {r.status_code}  {key}")
