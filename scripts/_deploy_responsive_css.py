"""Deploy bks-responsive.css to live Shopify theme (id=202392961362)."""
import os, requests, urllib3, base64
urllib3.disable_warnings()  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

css_path = Path("I:/BAK ABO/04_TEMA_SHOPIFY/assets/bks-responsive.css")
css = css_path.read_text(encoding="utf-8")
print(f"CSS: {len(css)} chars from {css_path.name}")

r = requests.put(
    f"https://{DOMAIN}/admin/api/2025-01/themes/202392961362/assets.json",
    headers=HDR,
    json={"asset": {"key": "assets/bks-responsive.css", "value": css}},
    verify=False, timeout=30
)
if r.ok:
    asset = r.json().get("asset", {})
    print(f"OK — deployed {asset.get('key')} updated_at={asset.get('updated_at')}")
else:
    print(f"ERR {r.status_code}: {r.text[:300]}")
