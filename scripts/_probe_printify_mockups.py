"""
Probe Printify products — analizza struttura images per trovare
mockup flat lay / product-only / ghost mannequin disponibili.
"""
from __future__ import annotations
import os, json, requests, urllib3
from pathlib import Path
from collections import defaultdict

urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]:
        os.environ[k] = v

TOKEN   = os.environ["PRINTIFY_API_TOKEN"]
SHOP_ID = os.environ.get("PRINTIFY_SHOP_ID", "12030061")
BASE    = "https://api.printify.com/v1"
HDR     = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json;charset=utf-8"}

def get(path, **params):
    r = requests.get(f"{BASE}{path}", headers=HDR, params=params, timeout=30, verify=False)
    r.raise_for_status()
    return r.json()

# Prendo prima pagina prodotti (50)
data = get(f"/shops/{SHOP_ID}/products.json", page=1, limit=20)
products = data.get("data", [])
print(f"Campione: {len(products)} prodotti\n")

# Analisi per ogni prodotto
type_sample = {}  # product_type → primo prodotto campione

for p in products:
    ptype = p.get("product_type") or p.get("tags", ["?"])[0] if p.get("tags") else "?"
    # Cerca product_type dal titolo o tags
    # In Printify, product type viene da blueprint
    if ptype not in type_sample:
        type_sample[ptype] = p

print("=" * 70)
print("STRUTTURA IMMAGINI PER PRODOTTO (campione)")
print("=" * 70)

for ptype, p in list(type_sample.items())[:8]:
    print(f"\n[{p.get('title', '')[:50]}]")
    print(f"  blueprint_id : {p.get('blueprint_id')}")
    print(f"  print_provider: {p.get('print_provider_id')}")
    images = p.get("images", [])
    print(f"  images count : {len(images)}")
    for i, img in enumerate(images[:6]):
        src = img.get("src", "")
        pos = img.get("position", "?")
        is_def = img.get("is_default", False)
        variant_ids = img.get("variant_ids", [])
        # Analizza URL per capire tipo mockup
        url_hint = ""
        for kw in ["flat", "ghost", "mannequin", "folded", "front", "back", "side", "lifestyle", "detail"]:
            if kw in src.lower():
                url_hint = kw
                break
        print(f"  img[{i}] pos={pos:8s} default={is_def} variants={len(variant_ids):3d} url_hint={url_hint or '?'}")
        print(f"         {src[-80:]}")

# Raggruppa per blueprint_id per capire quali blueprint hanno più mockup
print("\n\n" + "=" * 70)
print("BLUEPRINT → N. IMMAGINI (tutti i prodotti)")
print("=" * 70)

all_prods = []
for page in range(1, 6):
    d = get(f"/shops/{SHOP_ID}/products.json", page=page, limit=50)
    batch = d.get("data", [])
    if not batch:
        break
    all_prods.extend(batch)

bp_imgs = defaultdict(list)
for p in all_prods:
    bid = p.get("blueprint_id", 0)
    title = p.get("title", "?")[:40]
    n_imgs = len(p.get("images", []))
    bp_imgs[bid].append((title, n_imgs))

for bid, items in sorted(bp_imgs.items()):
    avg = sum(n for _, n in items) / len(items)
    print(f"  blueprint {bid:5d}  avg_imgs={avg:.1f}  ({len(items)} prodotti)  ex: {items[0][0]}")

# Cerca prodotti con più di 2 immagini (potrebbero avere flat lay)
print("\n\n" + "=" * 70)
print("PRODOTTI CON 3+ IMMAGINI (candidati flat lay / varianti)")
print("=" * 70)

for p in all_prods:
    imgs = p.get("images", [])
    if len(imgs) >= 3:
        print(f"\n  {p.get('title','?')[:50]} (blueprint {p.get('blueprint_id')})")
        for img in imgs:
            src = img.get("src", "")
            pos = img.get("position","?")
            print(f"    pos={pos:10s}  ...{src[-70:]}")
        if len([p for p in all_prods if len(p.get('images',[])) >= 3]) > 10:
            break  # evita output eccessivo
