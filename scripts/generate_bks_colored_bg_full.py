"""
BKS Colored Background — Pipeline elegante
Sfondo = colore accent collezione sfumato verso carta BKS (#fafaf7)
Il blend ratio dipende dalla categoria del prodotto:
  outerwear → colore pieno · footwear/accessori → tenue/carta
Risultato editoriale, coerente con il DNA del brand.
"""
from __future__ import annotations
import os, time, base64, sqlite3, json, requests, urllib3
from io import BytesIO
from pathlib import Path
import numpy as np
from PIL import Image
import rembg
from rembg import new_session

urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent

# ── Env ──────────────────────────────────────────────────────────────────────
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]:
        os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR_SH  = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
HDR_GET = {"X-Shopify-Access-Token": TOKEN}

# ── Colori accent BKS (colore pieno) ─────────────────────────────────────────
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

# ── Blend verso carta BKS (#fafaf7) per tipo prodotto ────────────────────────
# 0.0 = colore accent puro · 1.0 = carta pura
# Outerwear: colore ricco · Footwear/swim: tenue · Accessori: neutro caldo
PAPER = (250, 250, 247)

PRODUCT_TYPE_BLEND: dict[str, float] = {
    # valori reali da Shopify store (product_type field)
    "All Over Prints":         0.35,   # puffer / hoodie / capo principale
    "Windbreaker Jacket":      0.28,
    "Pullover Hoodie":         0.38,
    "Lounge Pants":            0.45,
    "Dress":                   0.48,
    "T-Shirt":                 0.52,
    "Athletics Shorts":        0.52,
    "Swim Trunks":             0.60,
    "Swimwear":                0.60,
    "Shoes":                   0.65,
    "Sneakers":                0.65,
    "Flip Flop":               0.72,
    "Bags":                    0.42,
    "Travel Bag":              0.42,
}
DEFAULT_BLEND = 0.45  # fallback per tipi non mappati

def tinted_bg(collection: str, product_type: str) -> tuple[int, int, int]:
    base  = COLLECTION_COLORS[collection]
    blend = PRODUCT_TYPE_BLEND.get(product_type, DEFAULT_BLEND)
    r = int(base[0] + (PAPER[0] - base[0]) * blend)
    g = int(base[1] + (PAPER[1] - base[1]) * blend)
    b = int(base[2] + (PAPER[2] - base[2]) * blend)
    return (r, g, b)

# ── Parametri canvas ──────────────────────────────────────────────────────────
CANVAS  = 1200
PAD_PCT = 0.11   # 11% padding — prodotto occupa 78% del canvas

OUT_DIR  = ROOT / "output" / "catalog_images" / "bks_bg"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Modello rembg specifico per silhouette umane (ignora ombre a terra)
print("Carico modello rembg u2net_human_seg...")
REMBG_SESSION = new_session("u2net_human_seg")

# ── DB ────────────────────────────────────────────────────────────────────────
data    = json.loads((ROOT / "output" / "bks_active_assets.json").read_text())
db_path = data.get("catalog_db", "")
conn    = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

def already_done(handle: str) -> bool:
    return conn.execute(
        "SELECT id FROM assets WHERE product_handle=? AND asset_type='bks_bg' LIMIT 1",
        (handle,)
    ).fetchone() is not None

def register_asset(handle: str, collection: str, product_type: str, local: str, url: str) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO assets "
        "(product_handle, asset_type, collection, file_path, url, meta_json) "
        "VALUES (?, 'bks_bg', ?, ?, ?, ?)",
        (handle, collection, local, url, json.dumps({"product_type": product_type}))
    )
    conn.commit()

# ── Shopify ───────────────────────────────────────────────────────────────────
def get_all_products() -> list[dict]:
    products: list[dict] = []
    url    = f"{BASE}/products.json"
    params: dict = {
        "status": "active", "limit": 250,
        "fields": "id,handle,title,images,tags,product_type",
    }
    while url:
        r = requests.get(url, headers=HDR_GET, params=params, verify=False, timeout=20)
        batch = r.json().get("products", [])
        products.extend(batch)
        link   = r.headers.get("Link", "")
        url    = None
        params = {}
        if 'rel="next"' in link:
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.strip().split(";")[0].strip("<> ")
                    break
        time.sleep(0.4)
    return products

def upload_as_img2(product_id: int, img_path: Path) -> str | None:
    img_b64 = base64.b64encode(img_path.read_bytes()).decode()
    r = requests.post(
        f"{BASE}/products/{product_id}/images.json",
        headers=HDR_SH,
        json={"image": {"attachment": img_b64, "filename": img_path.name, "position": 2}},
        timeout=40, verify=False,
    )
    if r.status_code in (200, 201):
        return r.json().get("image", {}).get("src", "")
    return None

# ── Image processing ──────────────────────────────────────────────────────────
def clean_alpha_halo(arr: np.ndarray, hard_cut: int = 15, fade_top: int = 60) -> np.ndarray:
    """Rimuove fringe semi-trasparenti ai bordi (halo rembg)."""
    a = arr[:, :, 3].astype(np.float32)
    arr[a < hard_cut, 3] = 0
    mask = (a >= hard_cut) & (a < fade_top)
    arr[mask, 3] = ((a[mask] - hard_cut) / (fade_top - hard_cut) * fade_top).astype(np.uint8)
    arr[arr[:, :, 3] == 0, :3] = 0
    return arr


def cut_floor_shadow(arr: np.ndarray, fade_px: int = 18) -> np.ndarray:
    """
    Rileva il piano (shadow zone sotto i piedi) e lo elimina.
    Strategia: scansione bottom-up per trovare l'ultima riga
    con densità di pixel SOLIDI (alpha > 200) >= 6% della larghezza.
    Sotto quella riga: fade su fade_px poi zero.
    """
    alpha = arr[:, :, 3]
    h, w  = alpha.shape
    solid_threshold = max(1, int(w * 0.06))

    feet_y = h - 1
    for y in range(h - 1, h // 3, -1):
        if np.sum(alpha[y] > 200) >= solid_threshold:
            feet_y = y
            break

    # Fade morbida dal piede verso il basso
    for dy in range(1, fade_px + 1):
        y = feet_y + dy
        if y >= h:
            break
        ratio = max(0.0, 1.0 - dy / fade_px)
        arr[y, :, 3] = (arr[y, :, 3].astype(np.float32) * ratio).astype(np.uint8)

    # Hard zero sotto la zona fade
    if feet_y + fade_px + 1 < h:
        arr[feet_y + fade_px + 1:, :, 3] = 0
        arr[feet_y + fade_px + 1:, :3]   = 0

    return arr


def process(img_bytes: bytes, bg_rgb: tuple) -> Image.Image:
    fg  = Image.open(BytesIO(rembg.remove(img_bytes, session=REMBG_SESSION))).convert("RGBA")
    arr = np.array(fg, dtype=np.uint8)
    arr = clean_alpha_halo(arr)
    arr = cut_floor_shadow(arr)
    fg  = Image.fromarray(arr, "RGBA")
    pad = int(CANVAS * PAD_PCT)
    fg.thumbnail((CANVAS - 2 * pad, CANVAS - 2 * pad), Image.LANCZOS)
    bg  = Image.new("RGBA", (CANVAS, CANVAS), bg_rgb + (255,))
    x   = (CANVAS - fg.width)  // 2
    y   = (CANVAS - fg.height) // 2
    bg.paste(fg, (x, y), mask=fg)
    return bg.convert("RGB")

# ── Main ─────────────────────────────────────────────────────────────────────
print("Carico prodotti da Shopify...")
products = get_all_products()
print(f"Prodotti attivi: {len(products)}\n")

eligible = []
for p in products:
    tags = [t.strip().lower() for t in p.get("tags", "").split(",")]
    col  = next((t for t in tags if t in COLLECTION_COLORS), None)
    imgs = p.get("images", [])
    if col and imgs:
        eligible.append({
            "id":           p["id"],
            "handle":       p["handle"],
            "collection":   col,
            "product_type": p.get("product_type", "").strip(),
            "img_url":      imgs[0]["src"].split("?")[0],
        })

already = sum(1 for e in eligible if already_done(e["handle"]))
to_do   = [e for e in eligible if not already_done(e["handle"])]

print(f"Eligibili : {len(eligible)}")
print(f"Gia' fatti: {already}  (skip)")
print(f"Da fare   : {len(to_do)}")
if to_do:
    est = len(to_do) * 3.5
    print(f"Stima tempo: ~{est/60:.0f} min ({est:.0f}s)\n")

ok_gen = ok_up = errors = 0

for i, prod in enumerate(to_do, 1):
    handle   = prod["handle"]
    col      = prod["collection"]
    ptype    = prod["product_type"]
    bg       = tinted_bg(col, ptype)
    blend_v  = PRODUCT_TYPE_BLEND.get(ptype, DEFAULT_BLEND)

    print(f"[{i:3d}/{len(to_do)}] {handle[:50]}")
    print(f"         [{col}]  type={ptype or '?'}  blend={blend_v:.0%}")

    try:
        r = requests.get(prod["img_url"], timeout=20, verify=False)
        if r.status_code != 200:
            print(f"         SKIP download {r.status_code}")
            errors += 1
            continue

        result = process(r.content, bg)

        prod_dir = OUT_DIR / handle
        prod_dir.mkdir(exist_ok=True)
        out_path = prod_dir / f"{handle}_bks_bg.png"
        result.save(out_path, "PNG", optimize=True)
        ok_gen += 1
        print(f"         gen OK  {out_path.stat().st_size // 1024} KB")

        time.sleep(0.4)
        cdn = upload_as_img2(prod["id"], out_path)
        if cdn:
            ok_up += 1
            print(f"         upload OK")
        else:
            print(f"         upload FAIL")

        register_asset(handle, col, ptype, str(out_path), cdn or "")

    except Exception as ex:
        print(f"         ERROR — {ex}")
        errors += 1

    if i % 40 == 0:
        print(f"\n--- pausa 3s ---\n")
        time.sleep(3)

conn.close()

print(f"\n{'='*60}")
print(f"Generati : {ok_gen}/{len(to_do)}")
print(f"Shopify  : {ok_up}/{ok_gen}")
print(f"Errori   : {errors}")
print(f"Output   : {OUT_DIR}")
