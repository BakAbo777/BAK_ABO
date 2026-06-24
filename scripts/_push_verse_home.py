"""Push BKS Verse home section + updated dashboard to tema live."""
import os, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]:
        os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
LIVE_ID = "202392961362"
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

FILES = [
    "sections/bks-verse-intro.liquid",
    "sections/bks-member-dashboard.liquid",
    "templates/index.json",
]

ok = 0
for rel in FILES:
    src = ROOT / "04_TEMA_SHOPIFY" / rel
    body = src.read_text(encoding="utf-8")
    r = requests.put(
        f"{BASE}/themes/{LIVE_ID}/assets.json",
        headers=HDR,
        json={"asset": {"key": rel, "value": body}},
        timeout=30, verify=False,
    )
    if r.status_code in (200, 201):
        print(f"[OK]  {rel}")
        ok += 1
    else:
        print(f"[ERR] {rel} — {r.status_code}: {r.text[:120]}")

print(f"\n{ok}/{len(FILES)} file pushati al tema live {LIVE_ID}")
