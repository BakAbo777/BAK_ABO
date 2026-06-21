"""Fetch footer.liquid from live theme and save locally."""
import os, requests, urllib3, sys
urllib3.disable_warnings()  # type: ignore
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
from pathlib import Path
for raw in Path("I:/BAK ABO/.env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ:
            os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

r = requests.get(
    f"{BASE}/themes/202392961362/assets.json?asset[key]=sections/footer.liquid",
    headers=HDR, verify=False, timeout=20)
val = r.json().get("asset", {}).get("value", "") or ""
out = Path("I:/BAK ABO/scripts/_footer_live.liquid")
out.write_text(val, encoding="utf-8")
print(f"Saved: {out} ({len(val)} chars)")

# Print the Support section area
lines = val.splitlines()
for i, line in enumerate(lines):
    if "COL 3" in line or "Support" in line or "linklists.support" in line:
        start = max(0, i-2)
        end   = min(len(lines), i+20)
        print(f"\n--- around L{i+1} ---")
        for j in range(start, end):
            print(f"  L{j+1:4}: {lines[j]}")
        break
