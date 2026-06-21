"""Get layout/theme.liquid and check for policy/section inclusions."""
import os, requests, urllib3, sys
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
    f"https://{DOMAIN}/admin/api/2025-01/themes/202392961362/assets.json?asset[key]=layout/theme.liquid",
    headers=HDR, verify=False, timeout=20)
val = r.json().get("asset", {}).get("value", "")
Path("I:/BAK ABO/scripts/_theme_layout_live.liquid").write_text(val, encoding="utf-8")
print(f"Saved {len(val)} chars\n")

# Find section/policy inclusions
for i, line in enumerate(val.splitlines(), 1):
    if any(x in line.lower() for x in ["normativa", "policy", "section", "render", "include", "content_for_layout"]):
        print(f"L{i:4}: {line[:120]}")
