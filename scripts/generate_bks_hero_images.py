"""
BKS Hero Images — Pipeline v2
Usa ghost mannequin (camera_label=front) da Printify.
Sfondo bianco studio = rimozione banale con soglia HSV.
Zero rembg, zero artefatti ombre/fumo.
Risultato: prodotto pulito su sfondo BKS collection color sfumato verso carta.
"""
from __future__ import annotations
import os, time, base64, sqlite3, json, requests, urllib3
from io import BytesIO
from pathlib import Path
import numpy as np
from PIL import Image

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

SHOPIFY_DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
SHOPIFY_TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
PRINTIFY_TOKEN  = os.environ["PRINTIFY_API_TOKEN"]
SHOP_ID         = os.environ.get("PRINTIFY_SHOP_ID", "12030061")
SH_VERSION      = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
SH_BASE         = f"https://{SHOPIFY_DOMAIN}/admin/api/{SH_VERSION}"
SH_HDR_GET      = {"X-Shopify-Access-Token": SHOPIFY_TOKEN}
SH_HDR_POST     = {"X-Shopify-Access-Token": SHOPIFY_TOKEN, "Content-Type": "application/json"}
PY_HDR          = {"Authorization": f"Bearer {PRINTIFY_TOKEN}", "Content-Type": "application/json;charset=utf-8"}
PY_BASE         = "https://api.printify.com/v1"

# ── BKS color system ──────────────────────────────────────────────────────────
COLLECTION_COLORS: dict[str, tuple[int,int,int]] = {
    "bks-hours":   (200, 196, 190),
    "bks-glyph":   (212, 160,  48),
    "bks-marker":  (192,  68,  24),
    "bks-riviera": ( 12, 168, 152),
    "bks-pulse":   (136, 136, 204),
    "bks-token":   (152,  40, 216),
    "bks-flag":    (200,  32,  32),
    "bks-origin":  ( 72, 152,   8),
}

# Normalizza i tag Shopify → chiave collezione BKS
# Supporta entrambi i formati: "bks-glyph" e "collection:glyph"
_SHORT_TO_BKS = {k.replace("bks-", ""): k for k in COLLECTION_COLORS}

def resolve_collection(tags: list[str]) -> str | None:
    for t in tags:
        if t in COLLECTION_COLORS:
            return t
        if t.startswith("collection:"):
            short = t[len("collection:"):]
            if short in _SHORT_TO_BKS:
                return _SHORT_TO_BKS[short]
    return None
PAPER = (250, 250, 247)

PRODUCT_TYPE_BLEND: dict[str, float] = {
    "All Over Prints":    0.35,
    "Windbreaker Jacket": 0.28,
    "Pullover Hoodie":    0.38,
    "Lounge Pants":       0.45,
    "Dress":              0.48,
    "T-Shirt":            0.52,
    "Athletics Shorts":   0.52,
    "Swim Trunks":        0.58,
    "Swimwear":           0.58,
    "Shoes":              0.62,
    "Sneakers":           0.62,
    "Flip Flop":          0.70,
    "Bags":               0.40,
    "Travel Bag":         0.40,
}
DEFAULT_BLEND = 0.45

def tinted_bg(collection: str, product_type: str) -> tuple[int,int,int]:
    base  = COLLECTION_COLORS.get(collection, (200, 200, 195))
    blend = PRODUCT_TYPE_BLEND.get(product_type, DEFAULT_BLEND)
    return (
        int(base[0] + (PAPER[0] - base[0]) * blend),
        int(base[1] + (PAPER[1] - base[1]) * blend),
        int(base[2] + (PAPER[2] - base[2]) * blend),
    )

# ── Canvas params ─────────────────────────────────────────────────────────────
CANVAS  = 1200
PAD_PCT = 0.10   # 10% padding — prodotto occupa 80% del canvas

OUT_DIR = ROOT / "output" / "catalog_images" / "bks_hero"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── DB ────────────────────────────────────────────────────────────────────────
asset_meta  = json.loads((ROOT / "output" / "bks_active_assets.json").read_text())
db_path     = asset_meta.get("catalog_db", "")
conn        = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

def already_done(handle: str) -> bool:
    return conn.execute(
        "SELECT id FROM assets WHERE product_handle=? AND asset_type='bks_hero' LIMIT 1",
        (handle,)
    ).fetchone() is not None

def register_asset(handle: str, collection: str, product_type: str, local: str, url: str) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO assets "
        "(product_handle, asset_type, collection, file_path, url, meta_json) "
        "VALUES (?, 'bks_hero', ?, ?, ?, ?)",
        (handle, collection, local, url, json.dumps({"product_type": product_type, "source": "ghost_front"}))
    )
    conn.commit()

# ── Printify — recupera immagini ghost mannequin ──────────────────────────────
def py_get(path: str, **params) -> dict:
    r = requests.get(f"{PY_BASE}{path}", headers=PY_HDR, params=params, timeout=30, verify=False)
    r.raise_for_status()
    return r.json()

def get_ghost_front_url(printify_product: dict) -> str | None:
    """
    Seleziona immagine ghost mannequin (camera_label=front senza 'on-person').
    Ordine preferenza: front > back > closeup > qualsiasi altra.
    """
    images = printify_product.get("images", [])
    preferred_labels = ["front", "back", "closeup"]
    for label in preferred_labels:
        for img in images:
            src = img.get("src", "")
            qs  = src.lower()
            if f"camera_label={label}" in qs and "on-person" not in qs:
                return src
    # Fallback: prima immagine senza on-person
    for img in images:
        src = img.get("src", "")
        if "on-person" not in src.lower():
            return src
    # Ultimo fallback: default image
    for img in images:
        if img.get("is_default"):
            return img.get("src")
    return images[0]["src"] if images else None

# ── Image processing ──────────────────────────────────────────────────────────
def remove_white_bg(img: Image.Image, thresh: int = 240) -> Image.Image:
    """
    Edge-connected flood fill: rimuove solo il bianco connesso ai bordi.
    REGOLA FISSA: non usare soglia luminanza pura — taglia il prodotto.
    Zone bianche interne al print non vengono mai toccate.

    3 passaggi (pipeline v3):
      1.   Edge flood fill (lum>=240) — sfondo principale
      1.5  Near-neutral expansion da visited (top 20% + bottom 35%):
           ombra pavimento studio + interstizi zip/manico bag (lum>=170, chroma<12)
      2.   Zone chiuse interne (anello backpack, foro manico) — near-neutral, lum>=242
    """
    from collections import deque
    rgba = img.convert("RGBA")
    arr  = np.array(rgba, dtype=np.uint8)
    h, w = arr.shape[:2]

    lum   = (0.299 * arr[:,:,0].astype(np.float32)
           + 0.587 * arr[:,:,1].astype(np.float32)
           + 0.114 * arr[:,:,2].astype(np.float32))
    # chroma = max-min canali: 0 per grigio puro, alto per colori saturi
    r_ch = arr[:,:,0].astype(np.float32)
    g_ch = arr[:,:,1].astype(np.float32)
    b_ch = arr[:,:,2].astype(np.float32)
    chroma = (np.maximum(np.maximum(r_ch, g_ch), b_ch)
            - np.minimum(np.minimum(r_ch, g_ch), b_ch))

    is_bg = lum >= thresh

    # ── Pass 1: edge flood fill standard ──────────────────────────────────────
    visited = np.zeros((h, w), dtype=bool)
    queue   = deque()
    for x in range(w):
        for yr in (0, h - 1):
            if is_bg[yr, x] and not visited[yr, x]:
                visited[yr, x] = True; queue.append((yr, x))
    for y in range(h):
        for xr in (0, w - 1):
            if is_bg[y, xr] and not visited[y, xr]:
                visited[y, xr] = True; queue.append((y, xr))
    while queue:
        cy, cx = queue.popleft()
        for dy, dx in ((-1,0),(1,0),(0,-1),(0,1)):
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx] and is_bg[ny, nx]:
                visited[ny, nx] = True; queue.append((ny, nx))

    # ── Pass 1.5: near-neutral bg expansion da visited (top+bottom zone) ─────
    # Cattura: ombra pavimento studio (bottom 35%), interstizi manico/zip (top 20%).
    # Condizione: lum>=170, chroma(max-min)<12 = vero grigio studio, non tessuto.
    # Seed SOLO da pixel adiacenti a background gia' rimosso da pass 1:
    # cosi' non si mangiano tessuti chiari ai bordi.
    top_zone_end    = int(h * 0.20)   # righe 0..top_zone_end-1
    shadow_row_start = int(h * 0.65)  # righe shadow_row_start..h-1
    shadow_cand = (lum >= 170) & (chroma < 12) & ~visited

    def _expand_near_neutral(row_min: int, row_max: int) -> None:
        """BFS su shadow_cand nella zona [row_min, row_max), seed da visited."""
        sh_q: deque = deque()
        for y in range(row_min, row_max):
            for x in range(w):
                if shadow_cand[y, x]:
                    for dy2, dx2 in ((-1,0),(1,0),(0,-1),(0,1)):
                        ny2, nx2 = y + dy2, x + dx2
                        if 0 <= ny2 < h and 0 <= nx2 < w and visited[ny2, nx2]:
                            visited[y, x] = True; sh_q.append((y, x)); break
        while sh_q:
            cy, cx = sh_q.popleft()
            for dy, dx in ((-1,0),(1,0),(0,-1),(0,1)):
                ny, nx = cy + dy, cx + dx
                if (row_min <= ny < row_max and 0 <= nx < w
                        and not visited[ny, nx] and shadow_cand[ny, nx]):
                    visited[ny, nx] = True; sh_q.append((ny, nx))

    _expand_near_neutral(0, top_zone_end)        # zip/manico in alto
    _expand_near_neutral(shadow_row_start, h)    # pavimento studio in basso

    alpha = np.full((h, w), 255, dtype=np.uint8)
    alpha[visited] = 0
    for dy, dx in ((-1,0),(1,0),(0,-1),(0,1)):
        border = np.roll(visited, (dy, dx), axis=(0, 1)) & ~visited
        alpha[border] = np.minimum(alpha[border], 64)

    # ── Pass 2: zone chiuse interne (anello backpack, foro manico borsa) ──────
    # near-neutral (chroma<20) e lum>=242: vero studio white non raggiunto dal bordo
    inner_thresh = 242
    inner_bg     = (lum >= inner_thresh) & (chroma < 20) & ~visited
    if inner_bg.any():
        from collections import deque as _deque
        labeled  = np.zeros((h, w), dtype=np.int32)
        label_id = 0
        for sy in range(h):
            for sx in range(w):
                if inner_bg[sy, sx] and labeled[sy, sx] == 0:
                    label_id += 1
                    q2 = _deque([(sy, sx)])
                    labeled[sy, sx] = label_id
                    while q2:
                        cy2, cx2 = q2.popleft()
                        for dy2, dx2 in ((-1,0),(1,0),(0,-1),(0,1)):
                            ny2, nx2 = cy2+dy2, cx2+dx2
                            if 0<=ny2<h and 0<=nx2<w and inner_bg[ny2,nx2] and labeled[ny2,nx2]==0:
                                labeled[ny2,nx2] = label_id
                                q2.append((ny2,nx2))
        inner_mask = labeled > 0
        alpha[inner_mask] = 0
        visited = visited | inner_mask

    arr[:,:,3] = alpha
    arr[visited, :3] = 0
    return Image.fromarray(arr, "RGBA")


def make_gradient_bg(size: int, top_rgb: tuple, bot_rgb: tuple) -> Image.Image:
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    for y in range(size):
        t = y / (size - 1)
        for c in range(3):
            arr[y, :, c] = int(top_rgb[c] + (bot_rgb[c] - top_rgb[c]) * t)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def add_drop_shadow(fg: Image.Image, offset_y: int = 18, blur_r: int = 22,
                    opacity: int = 60) -> Image.Image:
    from PIL import ImageFilter
    alpha        = fg.split()[3]
    shadow_alpha = alpha.filter(ImageFilter.GaussianBlur(radius=blur_r))
    shadow_alpha = shadow_alpha.point(lambda p: min(opacity, int(p * 0.7)))
    shadow_layer = Image.new("RGBA", fg.size, (20, 20, 20, 0))
    shadow_layer.putalpha(shadow_alpha)
    result = Image.new("RGBA", fg.size, (0, 0, 0, 0))
    result.paste(shadow_layer, (0, offset_y), mask=shadow_alpha)
    return result


def compose(fg: Image.Image, bg_rgb: tuple[int,int,int],
            rotation_deg: float = 0.0) -> Image.Image:
    LIGHT = (250, 250, 247)
    top_c = tuple(int(bg_rgb[i] + (LIGHT[i] - bg_rgb[i]) * 0.45) for i in range(3))
    bot_c = tuple(int(bg_rgb[i] * 0.88) for i in range(3))

    if rotation_deg != 0.0:
        fg = fg.rotate(rotation_deg, resample=Image.BICUBIC, expand=True)

    pad = int(CANVAS * PAD_PCT)
    fg.thumbnail((CANVAS - 2 * pad, CANVAS - 2 * pad), Image.LANCZOS)

    bg     = make_gradient_bg(CANVAS, top_c, bot_c)
    shadow = add_drop_shadow(fg)
    x = (CANVAS - fg.width)  // 2
    y = (CANVAS - fg.height) // 2
    bg.paste(shadow, (x, y + 8), mask=shadow)
    bg.paste(fg, (x, y), mask=fg)
    return bg.convert("RGB")

# ── Shopify — carica prodotti con tags collection ─────────────────────────────
def get_all_shopify_products() -> list[dict]:
    products: list[dict] = []
    url    = f"{SH_BASE}/products.json"
    params: dict = {"status": "active", "limit": 250,
                    "fields": "id,handle,title,images,tags,product_type"}
    while url:
        r      = requests.get(url, headers=SH_HDR_GET, params=params, verify=False, timeout=20)
        batch  = r.json().get("products", [])
        products.extend(batch)
        link   = r.headers.get("Link", "")
        url    = None; params = {}
        if 'rel="next"' in link:
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.strip().split(";")[0].strip("<> ")
                    break
        time.sleep(0.3)
    return products

def get_all_printify_products() -> list[dict]:
    products: list[dict] = []
    for page in range(1, 20):
        d = py_get(f"/shops/{SHOP_ID}/products.json", page=page, limit=50)
        batch = d.get("data", [])
        if not batch:
            break
        products.extend(batch)
        if page >= int(d.get("last_page", page)):
            break
        time.sleep(0.3)
    return products

def upload_shopify_img(product_id: int, img_path: Path, position: int = 2) -> str | None:
    img_b64 = base64.b64encode(img_path.read_bytes()).decode()
    r = requests.post(
        f"{SH_BASE}/products/{product_id}/images.json",
        headers=SH_HDR_POST,
        json={"image": {"attachment": img_b64, "filename": img_path.name, "position": position}},
        timeout=40, verify=False,
    )
    if r.status_code in (200, 201):
        return r.json().get("image", {}).get("src", "")
    print(f"         upload FAIL {r.status_code}: {r.text[:100]}")
    return None

# ── Main ─────────────────────────────────────────────────────────────────────
print("Carico prodotti Shopify...")
sh_products = get_all_shopify_products()
print(f"  Shopify attivi: {len(sh_products)}")

print("Carico prodotti Printify...")
py_products = get_all_printify_products()
print(f"  Printify totale: {len(py_products)}")

# Mappa handle Shopify -> ID Shopify
sh_map: dict[str, dict] = {p["handle"]: p for p in sh_products}

# Mappa external_id Printify -> prodotto Printify (external.id = Shopify product id)
py_map: dict[str, dict] = {}
for p in py_products:
    ext_id = str((p.get("external") or {}).get("id", ""))
    if ext_id:
        py_map[ext_id] = p

print(f"  Match Printify<->Shopify: {sum(1 for p in sh_products if str(p['id']) in py_map)}")
print()

# Costruisci lista eligible
eligible: list[dict] = []
for sh in sh_products:
    tags = [t.strip().lower() for t in sh.get("tags", "").split(",")]
    col  = resolve_collection(tags)
    if not col:
        continue
    py_prod = py_map.get(str(sh["id"]))
    if not py_prod:
        continue
    ghost_url = get_ghost_front_url(py_prod)
    if not ghost_url:
        continue
    eligible.append({
        "shopify_id":   sh["id"],
        "handle":       sh["handle"],
        "collection":   col,
        "product_type": sh.get("product_type", "").strip(),
        "ghost_url":    ghost_url,
    })

already = sum(1 for e in eligible if already_done(e["handle"]))
to_do   = [e for e in eligible if not already_done(e["handle"])]

print(f"Eligibili : {len(eligible)}")
print(f"Gia' fatti: {already}  (skip)")
print(f"Da fare   : {len(to_do)}")
if to_do:
    est = len(to_do) * 2.5
    print(f"Stima     : ~{est/60:.0f} min\n")

ok_gen = ok_up = errors = 0

for i, prod in enumerate(to_do, 1):
    handle = prod["handle"]
    col    = prod["collection"]
    ptype  = prod["product_type"]
    bg     = tinted_bg(col, ptype)
    blend  = PRODUCT_TYPE_BLEND.get(ptype, DEFAULT_BLEND)

    print(f"[{i:3d}/{len(to_do)}] {handle[:52]}")
    print(f"         [{col}]  type={ptype or '?'}  blend={blend:.0%}  bg=RGB{bg}")

    try:
        r = requests.get(prod["ghost_url"], timeout=20, verify=False)
        if r.status_code != 200:
            print(f"         SKIP download {r.status_code}")
            errors += 1
            continue

        src_img = Image.open(BytesIO(r.content)).convert("RGB")
        rot     = (hash(handle) % 7) - 3
        fg      = remove_white_bg(src_img)
        result  = compose(fg, bg, rotation_deg=rot)

        prod_dir = OUT_DIR / handle
        prod_dir.mkdir(exist_ok=True)
        out_path = prod_dir / f"{handle}_hero.png"
        result.save(out_path, "PNG", optimize=True)
        ok_gen += 1
        print(f"         gen OK  {out_path.stat().st_size // 1024} KB")

        time.sleep(0.3)
        cdn = upload_shopify_img(prod["shopify_id"], out_path, position=2)
        if cdn:
            ok_up += 1
            print(f"         upload OK")

        register_asset(handle, col, ptype, str(out_path), cdn or "")

    except Exception as ex:
        import traceback
        print(f"         ERROR: {ex}")
        traceback.print_exc()
        errors += 1

    if i % 50 == 0:
        print("\n--- pausa 3s ---\n")
        time.sleep(3)

conn.close()
print(f"\n{'='*60}")
print(f"Generati : {ok_gen}/{len(to_do)}")
print(f"Shopify  : {ok_up}/{ok_gen}")
print(f"Errori   : {errors}")
print(f"Output   : {OUT_DIR}")
