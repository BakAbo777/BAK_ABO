"""Push Camerino v3 assets to live Shopify theme."""
import os, requests, urllib3
urllib3.disable_warnings()
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

FILES = [
    ("04_TEMA_SHOPIFY/assets/bks-tryon.css",                "assets/bks-tryon.css"),
    ("04_TEMA_SHOPIFY/sections/bks-member-dashboard.liquid", "sections/bks-member-dashboard.liquid"),
]

for src_rel, key in FILES:
    src = ROOT / src_rel
    body = src.read_text(encoding="utf-8")
    print(f"Pushing {key} ({len(body)} chars)...")
    r = requests.put(
        f"{BASE}/themes/{LIVE_ID}/assets.json",
        headers=HDR,
        json={"asset": {"key": key, "value": body}},
        verify=False, timeout=30,
    )
    print(f"  {'OK' if r.ok else 'ERROR ' + str(r.status_code)}  {'' if r.ok else r.text[:120]}")

print("Done.")
