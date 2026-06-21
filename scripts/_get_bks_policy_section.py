"""Dump bks-policy.liquid from live theme."""
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

r = requests.get(
    f"https://{DOMAIN}/admin/api/2025-01/themes/202392961362/assets.json?asset[key]=sections/bks-policy.liquid",
    headers=HDR, verify=False, timeout=20)
val = r.json().get("asset", {}).get("value", "")
if val:
    print(val[:3000])
else:
    print(f"Not found. Response: {r.json()}")
    # List all sections
    r2 = requests.get(f"https://{DOMAIN}/admin/api/2025-01/themes/202392961362/assets.json",
                      headers=HDR, verify=False, timeout=20)
    assets = r2.json().get("assets", [])
    policy_assets = [a["key"] for a in assets if "policy" in a["key"].lower() or "bks-" in a["key"].lower()]
    print("BKS/policy assets:", policy_assets[:20])
