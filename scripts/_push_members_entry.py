"""Push bks-members-entry.liquid e lista template account/customer live."""
import os, sys, requests, urllib3, time
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
MERGED = ROOT / "04_TEMA_SHOPIFY" / "_merged_tm04"

# Push bks-members-entry
path = MERGED / "sections" / "bks-members-entry.liquid"
r = requests.put(f"{BASE}/themes/{THEME}/assets.json",
    json={"asset": {"key": "sections/bks-members-entry.liquid", "value": path.read_text(encoding="utf-8")}},
    headers=HDR, timeout=30, verify=False)
print(f"bks-members-entry.liquid  ->  HTTP {r.status_code}")
if r.status_code not in (200, 201):
    print(f"  ERR: {r.text[:200]}")
time.sleep(0.5)

# Lista template customer/account nel tema live
print("\nTemplate account/customer nel tema live:")
r2 = requests.get(f"{BASE}/themes/{THEME}/assets.json", headers=HDR, timeout=20, verify=False)
assets = r2.json().get("assets", [])
found = [a["key"] for a in assets if "customer" in a["key"].lower() or "account" in a["key"].lower()]
for k in sorted(found):
    print(f"  {k}")
