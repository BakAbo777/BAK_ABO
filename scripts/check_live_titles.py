import os, requests, urllib3, time
from pathlib import Path

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
HDR    = {"X-Shopify-Access-Token": TOKEN}
urllib3.disable_warnings()

# Check a sample of handles that had ™ in CSV
handles = [
    "bks-hours-pane-lounge-pants",
    "marker-city-athletic-long-shorts",
    "glyph-gold-travel-bag",
    "folklore-panel-lounge-pants",
    "flag-drop-athletic-long-shorts",
]
print("=== Live Shopify titles ===")
for h in handles:
    r = requests.get(
        f"https://{DOMAIN}/admin/api/{VER}/products.json",
        headers=HDR, params={"handle": h, "fields": "handle,title"},
        timeout=15, verify=False
    )
    p = r.json().get("products", [])
    if p:
        title = p[0]["title"]
        tm = "™" in title
        print(f"  {'[TM]' if tm else '[OK]'} {h}: {title}")
    else:
        print(f"  [MISS] {h}")
    time.sleep(0.4)
