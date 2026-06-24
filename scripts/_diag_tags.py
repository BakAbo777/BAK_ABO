"""Analisi tag reali sui prodotti Shopify senza tag bks-collection."""
import os, requests, urllib3
from pathlib import Path
from collections import Counter
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

SH_DOM = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
SH_TOK = os.environ["SHOPIFY_ADMIN_TOKEN"]
SH_HDR = {"X-Shopify-Access-Token": SH_TOK}
COLS   = {"bks-hours","bks-glyph","bks-marker","bks-riviera",
          "bks-pulse","bks-token","bks-flag","bks-origin"}

r = requests.get(f"https://{SH_DOM}/admin/api/2025-01/products.json", headers=SH_HDR,
    params={"status":"active","limit":250,"fields":"id,handle,tags,product_type"}, verify=False)
sh_prods = r.json().get("products", [])

all_tags = Counter()
untagged = []
for p in sh_prods:
    tags = [t.strip().lower() for t in p.get("tags","").split(",") if t.strip()]
    col  = next((t for t in tags if t in COLS), None)
    if not col:
        untagged.append({"handle": p["handle"], "tags": tags, "type": p.get("product_type","")})
        all_tags.update(tags)

print(f"Prodotti senza tag BKS: {len(untagged)}\n")
print("Top 30 tag trovati su questi prodotti:")
for tag, n in all_tags.most_common(30):
    marker = " <-- COLLECTION?" if any(c in tag for c in ["hours","glyph","marker","riviera","pulse","token","flag","origin","folklore","bks"]) else ""
    print(f"  {n:4d}x  {tag}{marker}")

print("\nSample (10 prodotti):")
for p in untagged[:10]:
    print(f"  {p['handle'][:50]}")
    print(f"    type={p['type']}  tags={p['tags'][:8]}")
