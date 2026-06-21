"""Get full bks-policy.liquid and save to local file."""
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
Path("I:/BAK ABO/scripts/_bks_policy_live.liquid").write_text(val, encoding="utf-8")
print(f"Saved {len(val)} chars")
# Print sections with Italian text
import re
lines = val.splitlines()
for i, line in enumerate(lines, 1):
    if any(x in line for x in ["Normativa", "normativa", "Informativa", "informativa", "rimborsi", "privacy", "rimbors", "spediz", "BAKABO", "bakabo", "shop.policies"]):
        print(f"L{i:4}: {line[:120]}")
