"""Test hero pipeline: ghost front + rimozione sfondo bianco + BKS color. 6 campioni."""
from __future__ import annotations
import os, requests, urllib3
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

TOKEN   = os.environ["PRINTIFY_API_TOKEN"]
SHOP_ID = os.environ.get("PRINTIFY_SHOP_ID", "12030061")
SH_DOM  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
SH_TOK  = os.environ["SHOPIFY_ADMIN_TOKEN"]
PY_HDR  = {"Authorization": f"Bearer {TOKEN}"}
SH_HDR  = {"X-Shopify-Access-Token": SH_TOK}

COLLECTION_COLORS = {
    "bks-hours":   (200, 196, 190), "bks-glyph":   (212, 160,  48),
    "bks-marker":  (192,  68,  24), "bks-riviera": ( 12, 168, 152),
    "bks-pulse":   (136, 136, 204), "bks-token":   (152,  40, 216),
    "bks-flag":    (200,  32,  32), "bks-origin":  ( 72, 152,   8),
}
PAPER = (250, 250, 247)
PRODUCT_TYPE_BLEND = {
    "All Over Prints": 0.35, "Windbreaker Jacket": 0.28, "Pullover Hoodie": 0.38,
    "Lounge Pants": 0.45, "Dress": 0.48, "T-Shirt": 0.52,
    "Athletics Shorts": 0.52, "Swim Trunks": 0.58, "Swimwear": 0.58,
    "Shoes": 0.62, "Sneakers": 0.62, "Bags": 0.40, "Travel Bag": 0.40,
}

def tinted(col, ptype):
    base  = COLLECTION_COLORS[col]
    blend = PRODUCT_TYPE_BLEND.get(ptype, 0.45)
    return tuple(int(base[i] + (PAPER[i] - base[i]) * blend) for i in range(3))

OUT = ROOT / "output" / "catalog_images" / "bks_hero_test"
OUT.mkdir(parents=True, exist_ok=True)

def remove_white_bg(img: Image.Image, thresh: int = 240) -> Image.Image:
    """
    Edge-connected flood fill: rimuove solo il bianco connesso ai bordi.
    NON tocca le zone bianche interne al prodotto (stampe, pattern chiari).
    """
    from collections import deque
    rgba = img.convert("RGBA")
    arr  = np.array(rgba, dtype=np.uint8)
    h, w = arr.shape[:2]

    r = arr[:,:,0].astype(np.float32)
    g = arr[:,:,1].astype(np.float32)
    b = arr[:,:,2].astype(np.float32)
    lum = 0.299*r + 0.587*g + 0.114*b
    is_bg = lum >= thresh  # True = pixel "abbastanza bianco"

    # BFS dai 4 bordi: marca solo il bianco connesso all'esterno
    visited = np.zeros((h, w), dtype=bool)
    queue   = deque()

    for x in range(w):
        for y_edge in (0, h - 1):
            if is_bg[y_edge, x] and not visited[y_edge, x]:
                visited[y_edge, x] = True
                queue.append((y_edge, x))
    for y in range(h):
        for x_edge in (0, w - 1):
            if is_bg[y, x_edge] and not visited[y, x_edge]:
                visited[y, x_edge] = True
                queue.append((y, x_edge))

    while queue:
        cy, cx = queue.popleft()
        for dy, dx in ((-1,0),(1,0),(0,-1),(0,1)):
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx] and is_bg[ny, nx]:
                visited[ny, nx] = True
                queue.append((ny, nx))

    # Soft feather al confine: 1 pixel di fade sui vicini del bg
    fade_mask = visited.copy()
    arr[visited, 3] = 0
    arr[visited, :3] = 0

    # Dissolvi leggermente i pixel al bordo del prodotto (anti-aliasing)
    boundary_alpha = np.full((h, w), 255, dtype=np.uint8)
    boundary_alpha[visited] = 0
    # Un pixel adiacente al background prende alpha 180 (leggero feather)
    for dy, dx in ((-1,0),(1,0),(0,-1),(0,1)):
        shifted = np.roll(visited, (dy, dx), axis=(0, 1))
        border  = shifted & ~visited
        boundary_alpha[border] = np.minimum(boundary_alpha[border], 180)
    arr[:,:,3] = boundary_alpha

    return Image.fromarray(arr, "RGBA")

def make_gradient_bg(size: int, top_rgb: tuple, bot_rgb: tuple) -> Image.Image:
    """Gradiente verticale lineare da top_rgb a bot_rgb."""
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    for y in range(size):
        t = y / (size - 1)
        arr[y, :, 0] = int(top_rgb[0] + (bot_rgb[0] - top_rgb[0]) * t)
        arr[y, :, 1] = int(top_rgb[1] + (bot_rgb[1] - top_rgb[1]) * t)
        arr[y, :, 2] = int(top_rgb[2] + (bot_rgb[2] - top_rgb[2]) * t)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def add_drop_shadow(fg: Image.Image, offset_y: int = 18, blur_r: int = 22,
                    opacity: int = 60) -> Image.Image:
    """Aggiunge ombra morbida sotto il prodotto (layer separato)."""
    from PIL import ImageFilter
    shadow_layer = Image.new("RGBA", fg.size, (0, 0, 0, 0))
    # Usa il canale alpha del fg come forma dell'ombra
    alpha = fg.split()[3]
    shadow_alpha = alpha.filter(ImageFilter.GaussianBlur(radius=blur_r))
    shadow_alpha = shadow_alpha.point(lambda p: min(opacity, int(p * 0.7)))
    shadow_color = Image.new("RGBA", fg.size, (20, 20, 20, 0))
    shadow_color.putalpha(shadow_alpha)
    # Sposta ombra verso il basso
    result = Image.new("RGBA", fg.size, (0, 0, 0, 0))
    result.paste(shadow_color, (0, offset_y), mask=shadow_alpha)
    return result


def compose(fg: Image.Image, bg_rgb: tuple, rotation_deg: float = 0.0) -> Image.Image:
    CANVAS, PAD = 1200, 108

    # Ruota il fg prima del resize
    if rotation_deg != 0.0:
        fg = fg.rotate(rotation_deg, resample=Image.BICUBIC, expand=True)

    fg.thumbnail((CANVAS - 2*PAD, CANVAS - 2*PAD), Image.LANCZOS)

    # Gradiente: top = accent schiarito 40%, bottom = accent tinted
    LIGHT = (250, 250, 247)
    top_c = tuple(int(bg_rgb[i] + (LIGHT[i] - bg_rgb[i]) * 0.45) for i in range(3))
    bot_c = tuple(int(bg_rgb[i] * 0.88) for i in range(3))  # leggermente scurito

    bg = make_gradient_bg(CANVAS, top_c, bot_c)

    # Drop shadow
    shadow = add_drop_shadow(fg)

    # Compositing: shadow prima, poi fg sopra
    x = (CANVAS - fg.width)  // 2
    y = (CANVAS - fg.height) // 2
    bg.paste(shadow, (x, y + 8), mask=shadow)  # shadow leggermente in basso
    bg.paste(fg, (x, y), mask=fg)

    return bg.convert("RGB")

def get_ghost_url(images: list) -> str | None:
    for label in ["front", "back", "closeup"]:
        for img in images:
            src = img.get("src", "")
            if f"camera_label={label}" in src and "on-person" not in src:
                return src
    for img in images:
        if "on-person" not in img.get("src", ""):
            return img.get("src")
    return None

# Carica tutti i prodotti Printify
print("Carico prodotti Printify...")
all_py = []
for page in range(1, 10):
    d = requests.get(f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json",
                     headers=PY_HDR, params={"page": page, "limit": 50}, verify=False).json()
    batch = d.get("data", [])
    if not batch: break
    all_py.extend(batch)
    if page >= int(d.get("last_page", page)): break

# Carica tags Shopify per trovare le collezioni
print("Carico tags Shopify...")
sh_map = {}
url = f"https://{SH_DOM}/admin/api/2025-01/products.json"
params = {"status": "active", "limit": 250, "fields": "id,handle,tags,product_type"}
while url:
    r = requests.get(url, headers=SH_HDR, params=params, verify=False)
    for p in r.json().get("products", []):
        sh_map[str(p["id"])] = p
    link = r.headers.get("Link", ""); url = None; params = {}
    if 'rel="next"' in link:
        for part in link.split(","):
            if 'rel="next"' in part:
                url = part.strip().split(";")[0].strip("<> ")

print(f"  Printify: {len(all_py)} | Shopify: {len(sh_map)}")

# Seleziona 6 campioni: 1 per collezione, tipi diversi
seen_cols: set[str] = set()
samples = []
for py_p in all_py:
    ext_id = str((py_p.get("external") or {}).get("id", ""))
    sh_p   = sh_map.get(ext_id)
    if not sh_p: continue
    tags = [t.strip().lower() for t in sh_p.get("tags", "").split(",")]
    col  = next((t for t in tags if t in COLLECTION_COLORS), None)
    if not col or col in seen_cols: continue
    ghost = get_ghost_url(py_p.get("images", []))
    if not ghost: continue
    seen_cols.add(col)
    samples.append({
        "handle": sh_p["handle"],
        "col":    col,
        "ptype":  sh_p.get("product_type", "").strip(),
        "ghost":  ghost,
    })
    if len(samples) == 8: break

print(f"\nCampione: {len(samples)} prodotti\n")

for s in samples:
    handle, col, ptype = s["handle"], s["col"], s["ptype"]
    bg = tinted(col, ptype)
    blend = PRODUCT_TYPE_BLEND.get(ptype, 0.45)
    print(f"  {col:12s} | {ptype:22s} | blend={blend:.0%} | RGB{bg}")
    print(f"  ghost: ...{s['ghost'][-60:]}")

    img_bytes = requests.get(s["ghost"], timeout=20, verify=False).content
    src_img   = Image.open(BytesIO(img_bytes)).convert("RGB")
    print(f"  src size: {src_img.size}")

    # Rotazione deterministica: ±3° basata su hash handle
    rot = (hash(handle) % 7) - 3  # -3 a +3 gradi
    print(f"  rotation: {rot:+d}deg")

    fg     = remove_white_bg(src_img)
    result = compose(fg, bg, rotation_deg=rot)

    out = OUT / f"{handle}_hero.png"
    result.save(out, "PNG", optimize=True)
    print(f"  -> {out.name}  {out.stat().st_size//1024} KB\n")

print(f"Output: {OUT}")
