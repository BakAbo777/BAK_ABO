"""Download bks-trust-strip.liquid and bks-trust-reviews.liquid from live theme."""
import os, requests, urllib3
urllib3.disable_warnings()  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN","")
HDR    = {"X-Shopify-Access-Token": TOKEN}

for key in ["sections/bks-trust-strip.liquid", "sections/bks-trust-reviews.liquid"]:
    r = requests.get(
        f"https://{DOMAIN}/admin/api/2025-01/themes/202392961362/assets.json?asset[key]={key}",
        headers=HDR, verify=False, timeout=20)
    val = r.json().get("asset", {}).get("value", "")
    fname = key.replace("sections/", "").replace(".liquid", "_live.liquid")
    Path(f"I:/BAK ABO/scripts/_{fname}").write_text(val, encoding="utf-8")
    print(f"{key}: {len(val)} chars -> scripts/_{fname}")
