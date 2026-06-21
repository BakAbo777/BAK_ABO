"""Read collections and pages from Shopify store."""
import os, requests, urllib3, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
urllib3.disable_warnings()  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
VER    = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE   = f"https://{DOMAIN}/admin/api/{VER}"
HDR    = {"X-Shopify-Access-Token": TOKEN}

# Collections
r1 = requests.get(f"{BASE}/custom_collections.json?limit=250", headers=HDR, verify=False)
r2 = requests.get(f"{BASE}/smart_collections.json?limit=250", headers=HDR, verify=False)
all_colls = r1.json().get("custom_collections", []) + r2.json().get("smart_collections", [])
print(f"=== COLLEZIONI ({len(all_colls)}) ===")
for c in sorted(all_colls, key=lambda x: x["handle"]):
    print(f"  {c['handle']:45}  \"{c['title']}\"")

print()

# Pages
r3 = requests.get(f"{BASE}/pages.json?limit=250", headers=HDR, verify=False)
pages = r3.json().get("pages", [])
print(f"=== PAGINE ({len(pages)}) ===")
for p in sorted(pages, key=lambda x: x["handle"]):
    print(f"  {p['handle']:45}  \"{p['title']}\"")
