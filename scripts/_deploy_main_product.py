"""One-shot: deploy _merged_tm04/sections/main-product.liquid to live Shopify theme."""
import os, base64, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()  # type: ignore
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ.get("SHOPIFY_ADMIN_TOKEN", "") or os.environ.get("SHOPIFY_API_TOKEN", "")
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

# Get active theme ID
r = requests.get(f"https://{DOMAIN}/admin/api/{VERSION}/themes.json", headers=HDR, verify=False)
themes = r.json().get("themes", [])
theme = next((t for t in themes if t.get("role") == "main"), None)
if not theme:
    print("ERROR: no main theme found"); exit(1)
theme_id = theme["id"]
print(f"Theme: {theme['name']} (id={theme_id})")

src = ROOT / "04_TEMA_SHOPIFY/_merged_tm04/sections/main-product.liquid"
content = src.read_text(encoding="utf-8")
payload = {"asset": {"key": "sections/main-product.liquid", "value": content}}
r2 = requests.put(
    f"https://{DOMAIN}/admin/api/{VERSION}/themes/{theme_id}/assets.json",
    headers=HDR, json=payload, verify=False, timeout=60
)
if r2.ok:
    print(f"OK — main-product.liquid deployed ({len(content):,} chars)")
else:
    print(f"ERROR {r2.status_code}: {r2.text[:200]}")
