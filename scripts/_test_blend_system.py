"""Test del sistema blend elegante — 3 tipi diversi dalla stessa collezione BKS Flag."""
from __future__ import annotations
import os, requests, urllib3
from io import BytesIO
from pathlib import Path
import numpy as np
from PIL import Image
import rembg
from rembg import new_session
_SESSION = new_session("u2net_human_seg")

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

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
BASE   = f"https://{DOMAIN}/admin/api/2025-01"
HDR    = {"X-Shopify-Access-Token": TOKEN}

COLLECTION_COLORS = {
    "bks-hours":   (200, 196, 190),
    "bks-glyph":   (212, 160,  48),
    "bks-marker":  (192,  68,  24),
    "bks-riviera": ( 12, 168, 152),
    "bks-pulse":   (136, 136, 204),
    "bks-token":   (152,  40, 216),
    "bks-flag":    (200,  32,  32),
    "bks-origin":  ( 72, 152,   8),
}
PAPER = (250, 250, 247)
PRODUCT_TYPE_BLEND = {
    "All Over Prints": 0.35,
    "Windbreaker Jacket": 0.28,
    "Pullover Hoodie": 0.38,
    "Lounge Pants": 0.45,
    "Dress": 0.48,
    "T-Shirt": 0.52,
    "Athletics Shorts": 0.52,
    "Swim Trunks": 0.60,
    "Swimwear": 0.60,
    "Shoes": 0.65,
    "Sneakers": 0.65,
    "Flip Flop": 0.72,
    "Bags": 0.42,
    "Travel Bag": 0.42,
}

def tinted(collection, product_type):
    base  = COLLECTION_COLORS[collection]
    blend = PRODUCT_TYPE_BLEND.get(product_type, 0.50)
    return (
        int(base[0] + (PAPER[0] - base[0]) * blend),
        int(base[1] + (PAPER[1] - base[1]) * blend),
        int(base[2] + (PAPER[2] - base[2]) * blend),
    )

OUT_DIR = ROOT / "output" / "catalog_images" / "bks_bg_test2"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Prendo prodotti di TIPI diversi da BKS Token per vedere la gradazione
r = requests.get(f"{BASE}/products.json", headers=HDR,
    params={"status": "active", "limit": 250,
            "fields": "id,handle,images,tags,product_type"}, verify=False)
prods = r.json().get("products", [])

# Seleziona: 1 puffer, 1 sneakers, 1 accessory — da collection diverse per mostrare il range
targets = [
    ("bks-token",   "All Over Prints"),
    ("bks-token",   "Shoes"),
    ("bks-glyph",   "All Over Prints"),
    ("bks-glyph",   "Swim Trunks"),
    ("bks-riviera", "Swimwear"),
    ("bks-flag",    "All Over Prints"),
]

selected = []
for col_want, type_want in targets:
    for p in prods:
        tags  = [t.strip().lower() for t in p.get("tags", "").split(",")]
        col   = next((t for t in tags if t in COLLECTION_COLORS), None)
        ptype = p.get("product_type", "").strip()
        imgs  = p.get("images", [])
        if col == col_want and ptype == type_want and imgs:
            selected.append({"handle": p["handle"], "collection": col,
                             "product_type": ptype, "img_url": imgs[0]["src"].split("?")[0]})
            break

print(f"Campione: {len(selected)} prodotti\n")
CANVAS = 1200
PAD    = int(CANVAS * 0.11)

PRODUCT_ONLY_TYPES = {"Shoes", "Sneakers", "Flip Flop", "Bags", "Travel Bag"}

def clean_alpha_halo(arr, hard_cut=15, fade_top=60):
    a = arr[:, :, 3].astype(np.float32)
    arr[a < hard_cut, 3] = 0
    mask = (a >= hard_cut) & (a < fade_top)
    arr[mask, 3] = ((a[mask] - hard_cut) / (fade_top - hard_cut) * fade_top).astype(np.uint8)
    arr[arr[:, :, 3] == 0, :3] = 0
    return arr

def cut_floor_shadow(arr, product_type="", fade_px=6):
    alpha = arr[:, :, 3]
    h, w = alpha.shape
    has_content = np.any(alpha > 30, axis=1)
    if not np.any(has_content):
        return arr
    idxs = np.where(has_content)[0]
    top_y = int(idxs.min())
    bot_y = int(idxs.max())
    content_h = bot_y - top_y

    if product_type in PRODUCT_ONLY_TYPES:
        # product-only mockup: smoke/glass is large — scan top-down for where
        # product density drops (transition to smoke/reflection zone)
        dense_th = max(1, int(w * 0.15))  # 15% of width = real product row
        last_dense = top_y + content_h // 3  # fallback
        consec_sparse = 0
        for y in range(top_y, bot_y + 1):
            if int(np.sum(alpha[y] > 180)) >= dense_th:
                last_dense = y
                consec_sparse = 0
            else:
                consec_sparse += 1
                if consec_sparse >= 8:  # 8 sparse rows in a row → entered smoke
                    break
        cut_y = last_dense + 4
    else:
        # human model: floor reflection is thin, just bottom 7% of content
        cut_y = bot_y - int(content_h * 0.07)

    cut_y = min(cut_y, bot_y)
    arr[cut_y:, :, 3] = 0
    arr[cut_y:, :3]   = 0
    for dy in range(1, fade_px + 1):
        y = cut_y - dy
        if y < 0: continue
        ratio = dy / fade_px
        arr[y, :, 3] = (arr[y, :, 3].astype(np.float32) * ratio).astype(np.uint8)
    return arr

for prod in selected:
    handle = prod["handle"]
    col    = prod["collection"]
    ptype  = prod["product_type"]
    bg     = tinted(col, ptype)
    blend  = PRODUCT_TYPE_BLEND.get(ptype, 0.50)
    print(f"  {col:12s} | {ptype:22s} | blend={blend:.0%} | RGB{bg}")

    r2 = requests.get(prod["img_url"], timeout=20, verify=False)
    fg  = Image.open(BytesIO(rembg.remove(r2.content, session=_SESSION))).convert("RGBA")
    arr = np.array(fg, dtype=np.uint8)
    arr = clean_alpha_halo(arr)
    arr = cut_floor_shadow(arr, product_type=ptype)
    fg  = Image.fromarray(arr, "RGBA")
    fg.thumbnail((CANVAS - 2*PAD, CANVAS - 2*PAD), Image.LANCZOS)
    canvas = Image.new("RGBA", (CANVAS, CANVAS), bg + (255,))
    x = (CANVAS - fg.width)  // 2
    y = (CANVAS - fg.height) // 2
    canvas.paste(fg, (x, y), mask=fg)
    out = OUT_DIR / f"{handle}_{ptype.replace(' ','_')}_bks_bg.png"
    canvas.convert("RGB").save(out, "PNG", optimize=True)
    print(f"  -> {out.name}  {out.stat().st_size//1024} KB")

print(f"\nOutput: {OUT_DIR}")
