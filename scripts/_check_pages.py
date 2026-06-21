"""Check which BKS custom pages exist in Shopify."""
import os, requests, urllib3
urllib3.disable_warnings()  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

HANDLES = [
    "bks-hours", "bks-glyph", "bks-marker", "bks-riviera",
    "bks-pulse", "bks-token", "bks-flag", "bks-origin",
    "bks-sneakers", "bks-puffer-jackets", "bks-windbreakers",
    "bks-pullover-hoodie", "bks-swim-trunks", "bks-swimwear",
    "bks-flip-flop", "bks-athletic-shorts", "bks-lounge-pants",
    "bks-hawaiian-shirt", "bks-one-piece-swimsuits", "bks-racerback-dresses",
    "bks-backpack", "bks-travel-bag", "bks-duffel-bag", "bks-beach-towel",
]

pages = {}
page_info = None
while True:
    params = "limit=250&fields=id,title,handle,template_suffix"
    if page_info:
        params += f"&page_info={page_info}"
    r = requests.get(f"https://{DOMAIN}/admin/api/2025-01/pages.json?{params}",
                     headers=HDR, verify=False, timeout=20)
    for p in r.json().get("pages", []):
        pages[p["handle"]] = (p["id"], p["title"], p.get("template_suffix",""))
    link = r.headers.get("Link", "")
    if 'rel="next"' not in link:
        break
    import re
    m = re.search(r'page_info=([^&>]+)[^>]*>;\s*rel="next"', link)
    page_info = m.group(1) if m else None

missing = []
for handle in HANDLES:
    if handle in pages:
        pid, title, tmpl = pages[handle]
        print(f"  OK  [{pid}] /pages/{handle}  title={title!r}  template={tmpl or '(default)'}")
    else:
        missing.append(handle)
        print(f"  MISS /pages/{handle}")

if missing:
    print(f"\nMISSING ({len(missing)}): {', '.join(missing)}")
