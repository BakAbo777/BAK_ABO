"""List ALL sections in live theme and search for shop.policies usage."""
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

# All section liquid files
sections = sorted([a["key"] for a in assets if a["key"].startswith("sections/")])
# All snippet files
snippets = sorted([a["key"] for a in assets if a["key"].startswith("snippets/")])
# All layout files
layouts  = sorted([a["key"] for a in assets if a["key"].startswith("layout/")])

print("=== SECTIONS ===")
for s in sections: print(f"  {s}")

print(f"\n=== SNIPPETS ===")
for s in snippets: print(f"  {s}")

print(f"\n=== LAYOUTS ===")
for l in layouts: print(f"  {l}")

# Check each for shop.policies
print("\n\n=== CHECKING shop.policies USAGE ===")
for key in sections + snippets + layouts:
    if not key.endswith(".liquid"): continue
    r2 = requests.get(
        f"https://{DOMAIN}/admin/api/2025-01/themes/202392961362/assets.json?asset[key]={key}",
        headers=HDR, verify=False, timeout=20)
    val = r2.json().get("asset", {}).get("value", "") or ""
    if "shop.policies" in val:
        print(f"\nFOUND shop.policies in: {key}")
        for i, line in enumerate(val.splitlines(), 1):
            if "shop.policies" in line:
                print(f"  L{i}: {line[:120]}")
