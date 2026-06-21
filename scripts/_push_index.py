"""Push templates/index.json al tema Shopify live."""
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
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
LIVE_ID = "202392961362"
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

src  = ROOT / "04_TEMA_SHOPIFY" / "templates" / "index.json"
body = src.read_text(encoding="utf-8")
key  = "templates/index.json"

print(f"Pushing {key} ({len(body)} chars) to theme {LIVE_ID}...")
r = requests.put(
    f"{BASE}/themes/{LIVE_ID}/assets.json",
    headers=HDR,
    json={"asset": {"key": key, "value": body}},
    timeout=30,
    verify=False,
)

print(f"Status: {r.status_code}")
if r.status_code in (200, 201):
    asset = r.json().get("asset", {})
    print(f"OK — key={asset.get('key')} updated_at={asset.get('updated_at')}")
else:
    print(r.text[:800])
