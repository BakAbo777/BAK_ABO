"""
Audit completo: per ogni collezione, tutti i product_type con person-front disponibili.
Poi mostra le thumbnail migliori per tipo.
"""
from __future__ import annotations
import os, requests, urllib3
from collections import defaultdict
from pathlib import Path
urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, _, v = line.partition("=")
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v
SH_DOM  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
SH_TOK  = os.environ["SHOPIFY_ADMIN_TOKEN"]
PY_TOK  = os.environ["PRINTIFY_API_TOKEN"]
SHOP_ID = os.environ.get("PRINTIFY_SHOP_ID", "12030061")
SH_HDR  = {"X-Shopify-Access-Token": SH_TOK}
PY_HDR  = {"Authorization": f"Bearer {PY_TOK}"}

COL_PREFIXES = {
    "bks-hours":   ["hours"],
    "bks-glyph":   ["glyph"],
    "bks-marker":  ["marker"],
    "bks-riviera": ["riviera","bks-riviera"],
    "bks-pulse":   ["pulse"],
    "bks-token":   ["token"],
    "bks-flag":    ["flag"],
    "bks-origin":  ["folklore","origin"],
}

def col_for_handle(h: str) -> str | None:
    h = h.lower()
    for col, pfxs in COL_PREFIXES.items():
        for pfx in pfxs:
            if h.startswith(pfx + "-") or h.startswith(pfx + "_"):
                return col
    return None

# Shopify cursor pagination
sh_prods = []
url = f"https://{SH_DOM}/admin/api/2025-01/products.json"
params = {"status":"active","limit":250,"fields":"id,handle,tags,product_type"}
while url:
    r = requests.get(url, headers=SH_HDR, params=params, verify=False)
    params = None
    sh_prods.extend(r.json().get("products", []))
    link = r.headers.get("Link","")
    url = None
    for part in link.split(","):
        if 'rel="next"' in part:
            url = part.strip().split(";")[0].strip("<>")
sh_map = {str(p["id"]): p for p in sh_prods}

# Printify
all_py = []
for pg in range(1, 30):
    d = requests.get(f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json",
                     headers=PY_HDR, params={"page":pg,"limit":50}, verify=False).json()
    batch = d.get("data", [])
    if not batch: break
    all_py.extend(batch)
    if pg >= int(d.get("last_page", pg)): break
print(f"Shopify: {len(sh_prods)} | Printify: {len(all_py)}\n")

# Per ogni prodotto Printify, resolve collezione via Shopify product_type
# Usa external ID → Shopify product_type (più affidabile)
col_types: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))

for py_p in all_py:
    ext_id = str((py_p.get("external") or {}).get("id",""))
    sh_p = sh_map.get(ext_id)
    if not sh_p: continue
    ptype = sh_p.get("product_type","?").strip()
    handle = sh_p.get("handle","")
    col = col_for_handle(handle)
    if not col: continue

    person_front_url = None
    for img in py_p.get("images",[]):
        src = img.get("src","")
        if "camera_label=person-front" in src:
            person_front_url = src; break

    if person_front_url:
        col_types[col][ptype].append({"handle": handle, "url": person_front_url})

# Report
print("=== PRODUCT TYPES CON person-front PER COLLEZIONE ===\n")
for col in COL_PREFIXES:
    types = col_types.get(col, {})
    if not types:
        print(f"{col.upper()}: NESSUNO")
    else:
        print(f"{col.upper()}:")
        for ptype, items in sorted(types.items()):
            print(f"  {ptype:35} ({len(items)}) -> {items[0]['handle']}")
    print()
