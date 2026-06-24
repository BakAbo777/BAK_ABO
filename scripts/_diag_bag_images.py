"""Diagnostica immagini bag/backpack: scarica ghost front e mostra stats."""
import os, requests, urllib3
from io import BytesIO
from pathlib import Path
import numpy as np
from PIL import Image

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

SHORT_TO_BKS = {k.replace("bks-", ""): k for k in COLS}

def resolve_col(tags):
    for t in tags:
        if t in COLS: return t
        if t.startswith("collection:"):
            s = t[len("collection:"):]
            if s in SHORT_TO_BKS: return SHORT_TO_BKS[s]
    return None

# Shopify bag products
r = requests.get(f"https://{SH_DOM}/admin/api/2025-01/products.json", headers=SH_HDR,
    params={"status":"active","limit":250,"fields":"id,handle,tags,product_type"}, verify=False)
sh_prods = r.json().get("products", [])

bag_types = {"Bags", "Travel Bag"}
bags = [p for p in sh_prods
        if p.get("product_type","").strip() in bag_types
        and resolve_col([t.strip().lower() for t in p.get("tags","").split(",")])]
print(f"Bag/Travel Bag con collection tag: {len(bags)}")

# Printify map
all_py = []
for page in range(1, 20):
    d = requests.get(f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json",
                     headers=PY_HDR, params={"page":page,"limit":50}, verify=False).json()
    batch = d.get("data", [])
    if not batch: break
    all_py.extend(batch)
    if page >= int(d.get("last_page", page)): break

py_map = {str((p.get("external") or {}).get("id","")): p for p in all_py}

OUT = ROOT / "output" / "catalog_images" / "bag_diag"
OUT.mkdir(parents=True, exist_ok=True)

# Analizza 4 bag
sample = bags[:4]
for sh in sample:
    handle = sh["handle"]
    py_p   = py_map.get(str(sh["id"]))
    if not py_p:
        print(f"  {handle}: NO PRINTIFY MATCH"); continue

    imgs = py_p.get("images", [])
    print(f"\n[{handle}] blueprint={py_p.get('blueprint_id')}  imgs={len(imgs)}")
    for img in imgs[:6]:
        src = img.get("src","")
        qs  = "?" + src.split("?")[1] if "?" in src else ""
        print(f"  {qs}")

    # Seleziona ghost
    ghost = None
    for label in ["front","back","closeup"]:
        for img in imgs:
            src = img.get("src","")
            if f"camera_label={label}" in src and "on-person" not in src:
                ghost = src; break
        if ghost: break
    if not ghost:
        for img in imgs:
            if "on-person" not in img.get("src",""):
                ghost = img.get("src"); break
    if not ghost and imgs:
        ghost = imgs[0].get("src")

    if not ghost:
        print("  NO GHOST URL"); continue

    print(f"  -> ghost: ...{ghost[-60:]}")
    img_bytes = requests.get(ghost, timeout=20, verify=False).content
    src_img   = Image.open(BytesIO(img_bytes)).convert("RGB")
    arr       = np.array(src_img)

    # Analisi sfondo: angoli top-left 20x20
    corners = [
        arr[:20, :20],    # top-left
        arr[:20, -20:],   # top-right
        arr[-20:, :20],   # bottom-left
        arr[-20:, -20:],  # bottom-right
    ]
    for name, c in zip(["TL","TR","BL","BR"], corners):
        lum = 0.299*c[:,:,0] + 0.587*c[:,:,1] + 0.114*c[:,:,2]
        print(f"  corner {name}: mean_lum={lum.mean():.1f}  min={lum.min():.0f}  max={lum.max():.0f}")

    # Salva immagine grezza per ispezione
    src_img.save(OUT / f"{handle}_raw.jpg")
    print(f"  raw saved")
