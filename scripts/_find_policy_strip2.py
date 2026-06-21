"""Find the NORMATIVA E ASSISTENZA section in live theme."""
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

r = requests.get(f"https://{DOMAIN}/admin/api/2025-01/themes/202392961362/assets.json",
                 headers=HDR, verify=False, timeout=20)
assets = r.json().get("assets", [])
sections = [a["key"] for a in assets if a["key"].startswith("sections/") and a["key"].endswith(".liquid")]

SEARCH_TERMS = ["shop.policies", "normativa", "assistenza bakabo", "policy_strip", "bks-pl__"]
found = []
for key in sections:
    r2 = requests.get(
        f"https://{DOMAIN}/admin/api/2025-01/themes/202392961362/assets.json?asset[key]={key}",
        headers=HDR, verify=False, timeout=20)
    val = r2.json().get("asset", {}).get("value", "") or ""
    val_lower = val.lower()
    hits = [t for t in SEARCH_TERMS if t.lower() in val_lower]
    if hits:
        found.append((key, hits, val[:200]))
        print(f"\n[{key}] matches: {hits}")
        # Print matching lines (safe for unicode)
        for i, line in enumerate(val.splitlines(), 1):
            if any(t.lower() in line.lower() for t in SEARCH_TERMS):
                try:
                    print(f"  L{i:4}: {line[:100]}")
                except UnicodeEncodeError:
                    print(f"  L{i:4}: (unicode line)")

print(f"\n\nTotal sections with policy terms: {len(found)}")
