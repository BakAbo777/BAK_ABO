"""Test rembg pipeline su 3 prodotti campione prima del batch completo."""
from __future__ import annotations
import os, time, base64, requests, urllib3
from io import BytesIO
from pathlib import Path
from PIL import Image
import rembg

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

COLLECTION_COLORS: dict[str, tuple[int, int, int]] = {
    "bks-hours":   (200, 196, 190),
    "bks-glyph":   (212, 160,  48),
    "bks-marker":  (192,  68,  24),
    "bks-riviera": ( 12, 168, 152),
    "bks-pulse":   (136, 136, 204),
    "bks-token":   (152,  40, 216),
    "bks-flag":    (200,  32,  32),
    "bks-origin":  ( 72, 152,   8),
}
CANVAS  = 1200
PAD_PCT = 0.12
OUT_DIR = ROOT / "output" / "catalog_images" / "bks_bg_test"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Prendo 3 prodotti da 3 collezioni diverse
r = requests.get(f"{BASE}/products.json", headers=HDR,
    params={"status": "active", "limit": 50, "fields": "id,handle,images,tags"},
    verify=False)
prods = r.json().get("products", [])

samples = []
seen_cols: set[str] = set()
for p in prods:
    tags = [t.strip().lower() for t in p.get("tags", "").split(",")]
    col  = next((t for t in tags if t in COLLECTION_COLORS), None)
    if col and col not in seen_cols and p.get("images"):
        seen_cols.add(col)
        samples.append({"handle": p["handle"], "collection": col,
                        "img_url": p["images"][0]["src"].split("?")[0]})
    if len(samples) == 3:
        break

print(f"Campione: {len(samples)} prodotti\n")

for prod in samples:
    handle = prod["handle"]
    col    = prod["collection"]
    bg     = COLLECTION_COLORS[col]
    url    = prod["img_url"]

    print(f"  {handle} [{col}]")
    t0 = time.time()

    img_bytes = requests.get(url, timeout=20, verify=False).content
    fg = Image.open(BytesIO(rembg.remove(img_bytes))).convert("RGBA")

    pad    = int(CANVAS * PAD_PCT)
    max_d  = CANVAS - 2 * pad
    fg.thumbnail((max_d, max_d), Image.LANCZOS)
    canvas = Image.new("RGBA", (CANVAS, CANVAS), bg + (255,))
    x = (CANVAS - fg.width)  // 2
    y = (CANVAS - fg.height) // 2
    canvas.paste(fg, (x, y), mask=fg)
    result = canvas.convert("RGB")

    out = OUT_DIR / f"{handle}_bks_bg.png"
    result.save(out, "PNG", optimize=True)
    elapsed = time.time() - t0
    print(f"  -> {out.name}  {out.stat().st_size // 1024} KB  ({elapsed:.1f}s)")

print(f"\nFile salvati in: {OUT_DIR}")
print("Apri e verifica la qualita' prima di lanciare il batch completo.")
