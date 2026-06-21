"""Dump full collection.bks-origin.json and check ALL section settings."""
import os, requests, urllib3, json, sys
urllib3.disable_warnings()  # type: ignore
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN","")
HDR    = {"X-Shopify-Access-Token": TOKEN}

r = requests.get(
    f"https://{DOMAIN}/admin/api/2025-01/themes/202392961362/assets.json?asset[key]=templates/collection.bks-origin.json",
    headers=HDR, verify=False, timeout=20)
val = r.json().get("asset", {}).get("value", "")
print(json.dumps(json.loads(val), indent=2, ensure_ascii=False))
