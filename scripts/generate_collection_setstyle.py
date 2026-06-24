"""Genera BKS Collection Setstyle heroes.

Per ogni collezione:
  1. Prende 3 prodotti rappresentativi da output/catalog_images/bks_hero/
  2. Rimuove lo sfondo colorato con flood-fill dai bordi (no rembg)
  3. Compone i prodotti su canvas cream #fafaf7 in layout editoriale flat-lay
  4. Salva in output/catalog_images/setstyle/bks-[handle]-hero.jpg

Output: 8 immagini 1920x1080 JPEG, pronte per upload Shopify.
"""
from __future__ import annotations
import os, sys
from pathlib import Path
from collections import deque
import struct

try:
    from PIL import Image, ImageFilter, ImageDraw
except ImportError:
    print("pip install Pillow")
    sys.exit(1)

ROOT       = Path(__file__).resolve().parent.parent
BKSHERO    = ROOT / "output" / "catalog_images" / "bks_hero"
OUT_DIR    = ROOT / "output" / "catalog_images" / "setstyle"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Canvas settings
CANVAS_W, CANVAS_H = 1920, 1080
BG_COLOR = (250, 250, 247)       # #fafaf7

# Product selection per collection: (folder, filename)
COLLECTIONS: dict[str, list[tuple[str, str]]] = {
    "bks-hours": [
        ("bks-hours-walker-swim-trunks",   "bks-hours-walker-swim-trunks_hero.png"),
        ("bks-hours-pane™-lounge-pants",   "bks-hours-pane™-lounge-pants_hero.png"),
    ],
    "bks-glyph": [
        ("bks-glyph-cross-puffer",         "bks-glyph-cross-puffer_hero.png"),
        ("bks-glyph-lattice-sneakers",     "bks-glyph-lattice-sneakers_hero.png"),
        ("bks-glyph-script-swim-trunks",   "bks-glyph-script-swim-trunks_hero.png"),
    ],
    "bks-marker": [
        ("bks-marker-hybrid-sneakers",     "bks-marker-hybrid-sneakers_hero.png"),
        ("bks-marker-flux-swim-trunks",    "bks-marker-flux-swim-trunks_hero.png"),
        ("bks-marker-tag-swim-trunks",     "bks-marker-tag-swim-trunks_hero.png"),
    ],
    "bks-riviera": [
        ("bks-riviera-argyle-sneakers",    "bks-riviera-argyle-sneakers_hero.png"),
        ("bks-riviera-tile-swim-trunks",   "bks-riviera-tile-swim-trunks_hero.png"),
        ("bks-riviera-blocks™-athletic-long-shorts", "bks-riviera-blocks™-athletic-long-shorts_hero.png"),
    ],
    "bks-pulse": [
        ("bks-pulse-wave-sneakers",        "bks-pulse-wave-sneakers_hero.png"),
        ("bks-pulse-chord-swim-trunks",    "bks-pulse-chord-swim-trunks_hero.png"),
        ("bks-pulse-block-hawaiian",       "bks-pulse-block-hawaiian_hero.png"),
    ],
    "bks-token": [
        ("bks-token-vault-windbreaker",    "bks-token-vault-windbreaker_hero.png"),
        ("bks-token-score-sneakers",       "bks-token-score-sneakers_hero.png"),
    ],
    "bks-flag": [
        ("bks-flag-arc-sneakers",          "bks-flag-arc-sneakers_hero.png"),
        ("bks-flag-bloc-swim-trunks",      "bks-flag-bloc-swim-trunks_hero.png"),
        ("bks-flag-column-sneakers",       "bks-flag-column-sneakers_hero.png"),
    ],
    "bks-origin": [
        ("folklore-field-windbreaker",     "folklore-field-windbreaker_hero.png"),
        ("folklore-arabesque-puffer",      "folklore-arabesque-puffer_hero.png"),
        ("folklore-bloom-sneakers",        "folklore-bloom-sneakers_hero.png"),
    ],
}


def remove_bg_floodfill(img: Image.Image, tolerance: int = 45) -> Image.Image:
    """Remove solid-color background using border flood-fill. Returns RGBA."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    w, h = img.size
    pixels = img.load()

    # Sample background color from many border pixels (handles gradient backgrounds)
    border_pixels: list[tuple] = []
    step = max(1, min(w, h) // 20)
    for x in range(0, w, step):
        border_pixels.append(pixels[x, 0][:3])
        border_pixels.append(pixels[x, h - 1][:3])
    for y in range(0, h, step):
        border_pixels.append(pixels[0, y][:3])
        border_pixels.append(pixels[w - 1, y][:3])

    # Use median channel values as background reference (robust to outliers)
    border_pixels.sort(key=lambda p: p[0] + p[1] + p[2])
    mid = len(border_pixels) // 2
    bg_color = border_pixels[mid]

    def is_bg(px: tuple) -> bool:
        return (abs(int(px[0]) - bg_color[0]) + abs(int(px[1]) - bg_color[1]) + abs(int(px[2]) - bg_color[2])) < tolerance * 3

    # BFS flood fill from all border pixels
    visited = bytearray(w * h)  # faster than 2D list
    queue: deque = deque()

    def enqueue(x: int, y: int) -> None:
        idx = x * h + y
        if not visited[idx] and is_bg(pixels[x, y][:3]):
            visited[idx] = 1
            queue.append((x, y))

    for x in range(w):
        enqueue(x, 0)
        enqueue(x, h - 1)
    for y in range(h):
        enqueue(0, y)
        enqueue(w - 1, y)

    while queue:
        cx, cy = queue.popleft()
        for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
            if 0 <= nx < w and 0 <= ny < h:
                idx = nx * h + ny
                if not visited[idx] and is_bg(pixels[nx, ny][:3]):
                    visited[idx] = 1
                    queue.append((nx, ny))

    # Apply transparency + feather
    result = img.copy()
    rp = result.load()
    for x in range(w):
        for y in range(h):
            idx = x * h + y
            if visited[idx]:
                rp[x, y] = (rp[x, y][0], rp[x, y][1], rp[x, y][2], 0)
            else:
                px = rp[x, y]
                adjacent_bg = any(
                    0 <= x + dx < w and 0 <= y + dy < h and visited[(x + dx) * h + (y + dy)]
                    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
                )
                if adjacent_bg:
                    rp[x, y] = (px[0], px[1], px[2], 180)
    return result


def load_product(folder_name: str, filename: str) -> Image.Image | None:
    path = BKSHERO / folder_name / filename
    if not path.exists():
        print(f"    NOT FOUND: {path}")
        return None
    try:
        img = Image.open(path)
        return remove_bg_floodfill(img)
    except Exception as e:
        print(f"    ERROR loading {filename}: {e}")
        return None


def compose_setstyle(products: list[Image.Image], collection_handle: str) -> Image.Image:
    """Arrange up to 3 products on 1920x1080 cream canvas."""
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), BG_COLOR + (255,))

    n = min(len(products), 3)
    if n == 0:
        return canvas.convert("RGB")

    # Layout: products centered with generous margins
    # For 1 product: centered large
    # For 2 products: left-center + right-center, equal spacing
    # For 3 products: main (large, center) + two secondaries (smaller, sides)

    margin_x = 120
    gap = 80
    avail_w = CANVAS_W - 2 * margin_x
    avail_h = CANVAS_H - 160  # top/bottom margin 80px each

    if n == 1:
        layouts = [(CANVAS_W // 2, CANVAS_H // 2, 0.78)]
    elif n == 2:
        cx1 = margin_x + avail_w // 4
        cx2 = margin_x + 3 * avail_w // 4
        cy = CANVAS_H // 2
        layouts = [(cx1, cy, 0.68), (cx2, cy, 0.62)]
    else:
        # 3 products: main center (large) + two sides (smaller)
        cx_main = CANVAS_W // 2
        cx_left = margin_x + avail_w // 5
        cx_right = CANVAS_W - margin_x - avail_w // 5
        cy = CANVAS_H // 2
        cy_sides = int(CANVAS_H * 0.52)
        layouts = [(cx_main, cy, 0.74), (cx_left, cy_sides, 0.52), (cx_right, cy_sides, 0.52)]

    for i, (prod_img, (cx, cy, scale)) in enumerate(zip(products[:n], layouts)):
        # Compute target size
        max_dim = int(min(avail_w, avail_h) * scale)
        orig_w, orig_h = prod_img.size
        ratio = min(max_dim / orig_w, max_dim / orig_h)
        new_w = int(orig_w * ratio)
        new_h = int(orig_h * ratio)

        resized = prod_img.resize((new_w, new_h), Image.LANCZOS)

        # Add subtle shadow by pasting a blurred dark ellipse under the product
        shadow_layer = Image.new("RGBA", (new_w, new_h + 20), (0, 0, 0, 0))
        draw = ImageDraw.Draw(shadow_layer)
        sw = int(new_w * 0.7)
        sh = 18
        sx = (new_w - sw) // 2
        sy = new_h
        draw.ellipse([sx, sy, sx + sw, sy + sh], fill=(10, 10, 10, 45))
        shadow_blurred = shadow_layer.filter(ImageFilter.GaussianBlur(radius=8))

        paste_x = cx - new_w // 2
        paste_y = cy - new_h // 2

        # Paste shadow first
        canvas.paste(shadow_blurred, (paste_x, paste_y), shadow_blurred)
        # Paste product
        canvas.paste(resized, (paste_x, paste_y), resized)

    return canvas.convert("RGB")


# ─────────────────────────────────────────────────────────────────────────────
print("=" * 62)
print("BKS Collection Setstyle — Generation Pipeline")
print("=" * 62)

generated: list[str] = []
skipped: list[str] = []

for handle, product_list in COLLECTIONS.items():
    print(f"\n[{handle}]")
    out_path = OUT_DIR / f"{handle}-hero.jpg"

    products: list[Image.Image] = []
    for folder, fname in product_list:
        print(f"  Loading: {fname[:50]}...", end=" ", flush=True)
        img = load_product(folder, fname)
        if img:
            products.append(img)
            print("OK")
        else:
            print("SKIP")

    if not products:
        print(f"  SKIP {handle} — no products loaded")
        skipped.append(handle)
        continue

    print(f"  Composing {len(products)} products on 1920x1080...", end=" ", flush=True)
    composed = compose_setstyle(products, handle)
    composed.save(str(out_path), "JPEG", quality=93, optimize=True)
    print(f"OK -> {out_path.name} ({out_path.stat().st_size // 1024}KB)")
    generated.append(handle)

print(f"\n{'=' * 62}")
print(f"Generated: {len(generated)} | Skipped: {len(skipped)}")
print(f"Output: {OUT_DIR}")
if generated:
    print("\nNext step:")
    print("  python scripts/upload_setstyle_heroes.py")
    print("  (uploads to Shopify Files + updates collection templates)")
