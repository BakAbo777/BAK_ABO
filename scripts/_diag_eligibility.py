"""Diagnostica: perche' solo 20/202 prodotti sono eligibili."""
import os, requests, urllib3
from pathlib import Path
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

SH_DOM  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
SH_TOK  = os.environ["SHOPIFY_ADMIN_TOKEN"]
PY_TOK  = os.environ["PRINTIFY_API_TOKEN"]
SHOP_ID = os.environ.get("PRINTIFY_SHOP_ID", "12030061")
SH_HDR  = {"X-Shopify-Access-Token": SH_TOK}
PY_HDR  = {"Authorization": f"Bearer {PY_TOK}"}
COLS    = {"bks-hours","bks-glyph","bks-marker","bks-riviera",
           "bks-pulse","bks-token","bks-flag","bks-origin"}

# Shopify
r = requests.get(f"https://{SH_DOM}/admin/api/2025-01/products.json", headers=SH_HDR,
    params={"status":"active","limit":250,"fields":"id,handle,tags,product_type"}, verify=False)
sh_prods = r.json().get("products", [])

no_tag = sum(1 for p in sh_prods
             if not next((t.strip().lower() for t in p.get("tags","").split(",")
                          if t.strip().lower() in COLS), None))
print(f"Shopify: {len(sh_prods)} | con tag BKS: {len(sh_prods)-no_tag} | senza tag: {no_tag}")

# Printify
all_py = []
for page in range(1, 20):
    d = requests.get(f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json",
                     headers=PY_HDR, params={"page":page,"limit":50}, verify=False).json()
    batch = d.get("data", [])
    if not batch: break
    all_py.extend(batch)
    if page >= int(d.get("last_page", page)): break

# Mappa per external.id (Shopify product ID)
py_by_ext  = {}
for p in all_py:
    ext = str((p.get("external") or {}).get("id", ""))
    if ext: py_by_ext[ext] = p

# Mappa per titolo come fallback
py_by_title = {p.get("title","").strip().lower(): p for p in all_py}

print(f"Printify: {len(all_py)} | con external.id: {len(py_by_ext)}")

# Analisi dettagliata
no_col = no_py_ext = no_py_title = no_img = ok = 0
missing_ext_sample = []

for sh in sh_prods:
    tags  = [t.strip().lower() for t in sh.get("tags","").split(",")]
    col   = next((t for t in tags if t in COLS), None)
    if not col:
        no_col += 1
        continue

    py_p = py_by_ext.get(str(sh["id"]))
    if not py_p:
        # Prova match per titolo
        sh_title = sh.get("title","").strip().lower()
        py_p = py_by_title.get(sh_title)
        if not py_p:
            no_py_ext += 1
            if len(missing_ext_sample) < 5:
                missing_ext_sample.append(sh["handle"])
            continue
        else:
            no_py_title += 1  # ha trovato per titolo

    imgs = py_p.get("images", [])
    if not imgs:
        no_img += 1
        continue
    ok += 1

print(f"\nEsclusi per:")
print(f"  no collection tag   : {no_col}")
print(f"  no Printify match   : {no_py_ext}")
print(f"    (found by title)  : {no_py_title}")
print(f"  no images           : {no_img}")
print(f"Eligibili             : {ok}")
if missing_ext_sample:
    print(f"\nSample senza match Printify:")
    for h in missing_ext_sample:
        print(f"  {h}")
