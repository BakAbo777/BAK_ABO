"""
Trova immagini person-front per il prodotto puffer jacket signature di ogni collezione.
Match per prefisso handle (non tag, che non coprono tutti i prodotti).
"""
from __future__ import annotations
import os, requests, urllib3
from io import BytesIO
from pathlib import Path
from PIL import Image

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

# Prefissi handle Shopify → collezione BKS
# bks-origin usa anche "folklore", "origin" come prefisso
COL_PREFIXES = {
    "bks-hours":   ["hours"],
    "bks-glyph":   ["glyph"],
    "bks-marker":  ["marker"],
    "bks-riviera": ["riviera", "bks-riviera"],
    "bks-pulse":   ["pulse"],
    "bks-token":   ["token"],
    "bks-flag":    ["flag"],
    "bks-origin":  ["folklore", "origin", "folk"],
}

# Priorità per tipo prodotto (dal product_type Shopify)
TYPE_PRIORITY = [
    "Puffer Jacket", "Windbreaker Jacket", "Pullover Hoodie",
    "Hoodie", "Racerback Dress", "Dress", "Swimwear", "Swim Trunks",
    "Travel Bag", "Backpack", "Shoes", "Athletics Shorts", "Lounge Pants",
]

def col_for_handle(handle: str) -> str | None:
    h = handle.lower()
    for col, prefixes in COL_PREFIXES.items():
        for pfx in prefixes:
            if h.startswith(pfx + "-") or h.startswith(pfx + "_"):
                return col
    return None

# ── Carica prodotti Shopify (cursor pagination)
print("Carico Shopify...")
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
print(f"  {len(sh_prods)} prodotti")

# ── Carica prodotti Printify
print("Carico Printify...")
all_py = []
for pg in range(1, 30):
    d = requests.get(f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json",
                     headers=PY_HDR, params={"page":pg,"limit":50}, verify=False).json()
    batch = d.get("data", [])
    if not batch: break
    all_py.extend(batch)
    if pg >= int(d.get("last_page", pg)): break
py_map = {str((p.get("external") or {}).get("id","")): p for p in all_py}
print(f"  {len(all_py)} prodotti Printify")

# ── Scansione per collezione
OUT = ROOT / "output" / "catalog_images" / "hero_candidates"
OUT.mkdir(parents=True, exist_ok=True)

print("\n=== HERO CANDIDATES (person-front) ===\n")
results: dict[str, dict] = {}

for col, prefixes in COL_PREFIXES.items():
    # Trova prodotti Shopify con handle nel prefisso giusto
    col_prods = []
    for sh in sh_prods:
        col_match = col_for_handle(sh.get("handle",""))
        if col_match != col: continue
        ptype = sh.get("product_type","?").strip()
        rank = TYPE_PRIORITY.index(ptype) if ptype in TYPE_PRIORITY else 99
        col_prods.append({**sh, "_rank": rank})
    col_prods.sort(key=lambda x: x["_rank"])

    # Cerca first person-front
    best = None
    for sh in col_prods:
        py_p = py_map.get(str(sh["id"]))
        if not py_p: continue
        for img in py_p.get("images", []):
            src = img.get("src","")
            # camera_label=person-front (confirmed from probe)
            if "camera_label=person-front" in src:
                best = {"handle": sh["handle"], "ptype": sh["product_type"], "url": src}
                break
        if best: break

    print(f"{col.upper()}")
    if not best:
        # Fallback: mostra product_types e labels disponibili
        types_avail = list({p["product_type"] for p in col_prods})
        print(f"  NESSUNA person-front | disponibili: {types_avail[:5]}")
        # Prova person-back o front come fallback
        for sh in col_prods[:5]:
            py_p = py_map.get(str(sh["id"]))
            if not py_p: continue
            labels = set()
            for img in py_p.get("images",[]):
                src = img.get("src","")
                if "camera_label=" in src:
                    lbl = src.split("camera_label=")[1].split("&")[0]
                    labels.add(lbl)
            if labels:
                print(f"  Labels in {sh['handle']}: {sorted(labels)}")
                break
    else:
        print(f"  -> {best['handle']} ({best['ptype']})")
        try:
            img_bytes = requests.get(best["url"], timeout=20, verify=False).content
            img = Image.open(BytesIO(img_bytes))
            img.thumbnail((600, 600))
            fname = f"{col}_best_{best['ptype'].lower().replace(' ','-')}.jpg"
            img.save(OUT / fname, "JPEG", quality=88)
            print(f"  -> SALVATO: {fname} ({img.width}x{img.height}px orig)")
            results[col] = {**best, "file": fname}
        except Exception as e:
            print(f"  -> ERRORE download: {e}")
    print()

print(f"Output: {OUT}")
print(f"\nRisultati trovati: {len(results)}/8")
for col, r in results.items():
    print(f"  {col}: {r['handle']} ({r['ptype']})")
