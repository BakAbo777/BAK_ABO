"""Check bks-shopping-guide collection."""
import os, requests, urllib3
urllib3.disable_warnings()  # type: ignore
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
KW      = {"headers": HDR, "timeout": 20, "verify": False}

# cerca per handle
r = requests.get(f"{BASE}/custom_collections.json?handle=bks-shopping-guide", **KW)
cols = r.json().get("custom_collections", [])
if cols:
    c = cols[0]
    print(f"CUSTOM COLLECTION: id={c['id']} handle={c['handle']} title={c['title']}")
    # conta prodotti
    r2 = requests.get(f"{BASE}/custom_collections/{c['id']}/products/count.json", **KW)
    print(f"  Products count: {r2.json().get('count', '?')}")
else:
    print("bks-shopping-guide not found as custom collection")
    # prova smart collection
    r2 = requests.get(f"{BASE}/smart_collections.json?handle=bks-shopping-guide", **KW)
    smart = r2.json().get("smart_collections", [])
    if smart:
        c = smart[0]
        print(f"SMART COLLECTION: id={c['id']} handle={c['handle']} title={c['title']}")
        r3 = requests.get(f"{BASE}/smart_collections/{c['id']}/products/count.json", **KW)
        print(f"  Products count: {r3.json().get('count', '?')}")
    else:
        print("  Not found as smart collection either")
