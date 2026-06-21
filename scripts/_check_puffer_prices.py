"""Check puffer jacket prices and identify blanket/slipper products needing action."""
import os, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()  # type: ignore
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, _, v = line.partition("="); k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
BASE   = f"https://{DOMAIN}/admin/api/2025-01"
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

KEYWORDS = {
    "puffer":   {"tag": "puffer", "target": 129},
    "blanket":  {"tag": "blanket", "target": None},  # check status
    "slipper":  {"tag": "slipper", "target": 55},
}

products = []
page_info = None
while True:
    params = "limit=250&fields=id,title,status,product_type,variants"
    if page_info:
        params += f"&page_info={page_info}"
    r = requests.get(f"{BASE}/products.json?{params}", headers=HDR, verify=False, timeout=30)
    data = r.json().get("products", [])
    products.extend(data)
    link = r.headers.get("Link", "")
    if 'rel="next"' not in link:
        break
    import re
    m = re.search(r'page_info=([^&>]+)[^>]*>;\s*rel="next"', link)
    page_info = m.group(1) if m else None

print(f"Total products: {len(products)}\n")

for kw, cfg in KEYWORDS.items():
    matches = [p for p in products if kw in p["title"].lower() or kw in p["product_type"].lower()]
    if not matches:
        print(f"[{kw.upper()}] No products found")
        continue
    print(f"[{kw.upper()}] {len(matches)} products:")
    for p in matches:
        prices = [float(v["price"]) for v in p.get("variants", []) if v.get("price")]
        avg = sum(prices) / len(prices) if prices else 0
        target = cfg["target"]
        flag = ""
        if target and avg < target:
            flag = f" ← NEEDS REPRICE to ${target}"
        if kw == "blanket" and p["status"] != "draft":
            flag = " ← CRITICAL: should be DRAFT (EU margin negative)"
        print(f"  [{p['status'].upper()}] {p['title'][:50]} | avg ${avg:.2f}{flag}")
    print()
