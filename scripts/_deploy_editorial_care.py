"""Deploy bks-product-editorial-care.liquid to live theme."""
import os, requests, urllib3
from pathlib import Path
urllib3.disable_warnings()  # type: ignore
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1); k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
VER    = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
r = requests.get(f"https://{DOMAIN}/admin/api/{VER}/themes.json", headers=HDR, verify=False)
tid = next(t["id"] for t in r.json()["themes"] if t.get("role") == "main")
print(f"Theme id={tid}")
src = ROOT / "04_TEMA_SHOPIFY/sections/bks-product-editorial-care.liquid"
content = src.read_text(encoding="utf-8")
r2 = requests.put(f"https://{DOMAIN}/admin/api/{VER}/themes/{tid}/assets.json",
    headers=HDR, json={"asset": {"key": "sections/bks-product-editorial-care.liquid", "value": content}},
    verify=False, timeout=60)
print(f"Deploy: {'OK' if r2.ok else f'ERR {r2.status_code} {r2.text[:100]}'} ({len(content):,} chars)")
