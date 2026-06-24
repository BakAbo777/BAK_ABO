"""Debug: mostra product_types disponibili per collezione e immagini Printify disponibili."""
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

COLS = ["bks-hours","bks-glyph","bks-marker","bks-riviera","bks-pulse","bks-token","bks-flag","bks-origin"]

# Shopify: cursor-based pagination
sh_prods = []
url = f"https://{SH_DOM}/admin/api/2025-01/products.json"
params = {"status":"active","limit":250,"fields":"id,handle,tags,product_type"}
while url:
    r = requests.get(url, headers=SH_HDR, params=params, verify=False)
    params = None
    data = r.json()
    sh_prods.extend(data.get("products", []))
    link = r.headers.get("Link","")
    url = None
    for part in link.split(","):
        if 'rel="next"' in part:
            url = part.strip().split(";")[0].strip("<>")

print(f"Totale prodotti Shopify: {len(sh_prods)}")

# Organizza per collezione
col_types = defaultdict(lambda: defaultdict(int))
col_prods = defaultdict(list)

for p in sh_prods:
    tags_raw = [t.strip().lower() for t in p.get("tags","").split(",")]
    col = None
    for t in tags_raw:
        if t in COLS: col = t; break
    if not col: continue
    ptype = p.get("product_type","?").strip()
    col_types[col][ptype] += 1
    col_prods[col].append(p)

print("\n-- PRODUCT TYPES PER COLLEZIONE:")
for col in COLS:
    types = col_types.get(col, {})
    print(f"  {col}: {dict(types)}")

# Carica Printify
print("\n\nCarico prodotti Printify...")
all_py = []
for pg in range(1, 20):
    d = requests.get(f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json",
                     headers=PY_HDR, params={"page":pg,"limit":50}, verify=False).json()
    batch = d.get("data", [])
    if not batch: break
    all_py.extend(batch)
    if pg >= int(d.get("last_page", pg)): break
py_map = {str((p.get("external") or {}).get("id","")): p for p in all_py}
print(f"Totale prodotti Printify: {len(all_py)}")

# Per ogni collezione, trova il primo prodotto con on-person-front
print("\n-- PRIMA IMMAGINE on-person-front PER COLLEZIONE:")
for col in COLS:
    found = False
    for sh in col_prods.get(col, []):
        py_p = py_map.get(str(sh["id"]))
        if not py_p: continue
        for img in py_p.get("images", []):
            src = img.get("src","")
            if "on-person-front" in src:
                print(f"  {col}: {sh['handle']} ({sh['product_type']}) -> {src[:80]}...")
                found = True; break
        if found: break
    if not found:
        # Show available camera_labels for first product
        for sh in col_prods.get(col, [])[:2]:
            py_p = py_map.get(str(sh["id"]))
            if py_p:
                labels = [img.get("src","").split("camera_label=")[-1].split("&")[0]
                          for img in py_p.get("images",[]) if "camera_label=" in img.get("src","")]
                print(f"  {col}: NESSUNA — {sh['handle']} labels={labels}")
                break
