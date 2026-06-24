"""
Push AI SEO assets to Shopify TM04 theme:
  - templates/robots.txt.liquid  (AI crawler rules)
  - snippets/bks-json-ld.liquid  (MerchantReturnPolicy + shippingDetails)
  - layout/theme.liquid          (Organization description)

Uso:
    python scripts/_push_ai_seo.py
"""
import sys, requests, urllib3
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
urllib3.disable_warnings()

ROOT   = Path(__file__).resolve().parent.parent
env    = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

DOMAIN  = env["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = env["SHOPIFY_ADMIN_TOKEN"]
VERSION = env.get("SHOPIFY_API_VERSION", "2025-01")
THEME   = "202392961362"
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN}

THEME_DIR = ROOT / "04_TEMA_SHOPIFY"

FILES = [
    ("templates/robots.txt.liquid",  THEME_DIR / "templates" / "robots.txt.liquid"),
    ("snippets/bks-json-ld.liquid",  THEME_DIR / "snippets"  / "bks-json-ld.liquid"),
    ("layout/theme.liquid",          THEME_DIR / "layout"     / "theme.liquid"),
]

print("=== BKS AI SEO Push ===\n")
ok_count = 0
for key, path in FILES:
    if not path.exists():
        print(f"  SKIP (not found): {key}")
        continue
    body = path.read_text(encoding="utf-8")
    r = requests.put(
        f"{BASE}/themes/{THEME}/assets.json",
        json={"asset": {"key": key, "value": body}},
        headers=HDR, timeout=30, verify=False,
    )
    status = "OK" if r.status_code in (200, 201) else f"ERR {r.status_code}"
    print(f"  {status}  {key}")
    if r.status_code not in (200, 201):
        print(f"       {r.text[:200]}")
    else:
        ok_count += 1

print(f"\n{ok_count}/{len(FILES)} file pushati.")
if ok_count == len(FILES):
    print("SEO AI assets live su TM04.")
