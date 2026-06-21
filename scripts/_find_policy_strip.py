"""Find the policy strip section (NORMATIVA E ASSISTENZA BAKABO) in live theme."""
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

# Get list of all theme assets
r = requests.get(f"https://{DOMAIN}/admin/api/2025-01/themes/202392961362/assets.json",
                 headers=HDR, verify=False, timeout=20)
assets = r.json().get("assets", [])
sections = [a["key"] for a in assets if a["key"].startswith("sections/") and a["key"].endswith(".liquid")]
print(f"Found {len(sections)} section files\n")

# Search each section for the policy strip text
KEYWORDS = ["normativa", "assistenza bakabo", "shop.policies", "policy_list", "bks-trust"]
for key in sections:
    r2 = requests.get(
        f"https://{DOMAIN}/admin/api/2025-01/themes/202392961362/assets.json?asset[key]={key}",
        headers=HDR, verify=False, timeout=20)
    val = r2.json().get("asset", {}).get("value", "").lower()
    for kw in KEYWORDS:
        if kw in val:
            print(f"FOUND [{kw}] in {key}")
            # Print matching lines
            for i, line in enumerate(val.splitlines(), 1):
                if kw in line:
                    print(f"  L{i}: {line[:100]}")
            break
