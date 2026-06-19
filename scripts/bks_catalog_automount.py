"""
BKS Catalog Automount — v1
Composizione automatica spread editoriali + cover collection.

Input:  output/foto collezioni/00_originals_catalogued/{collection}/{type}/*.webp
Output:
  output/catalog_spreads/{collection}/cover_1200x1500.jpg       — cover collection (Shopify)
  output/catalog_spreads/{collection}/spread_1800x1200.jpg      — spread editoriale (2 pagine)
  output/catalog_spreads/{collection}/{type}_grid_1200x900.jpg  — grid per tipo prodotto

Regole BKS:
  - Paper: #fafaf7   Bone: #efeae0   Ink: #0a0a0a
  - Accent: per-collection (vedi ACCENTS dict)
  - Label style: [WINDBREAKERS.]  — bracket notation
  - Grid: 2×2 o 2×3 prodotti su bone background
  - Cover: immagine hero a piena pagina + overlay BKS
"""
from __future__ import annotations
import os, sys
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
PHOTO_BASE   = ROOT / "output" / "foto collezioni" / "00_originals_catalogued"
FACTORY_BASE = Path("E:/BAKSITO/BAKABO/BAK ABO/BAKABO_IMAGE_FACTORY_v1.1/output/source")
OUT_BASE     = ROOT / "output" / "catalog_spreads"

# Load published Shopify handles (active only)
def _load_published_handles() -> set[str]:
    import csv
    csv_path = ROOT / "output" / "live_shopify_products.csv"
    published: set[str] = set()
    if not csv_path.exists():
        return published
    with open(csv_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            h = (row.get("handle") or row.get("Handle") or "").strip().lower()
            s = (row.get("status") or row.get("Status") or "").strip().lower()
            if h and s == "active":
                published.add(h)
    return published

PUBLISHED = _load_published_handles()

def _factory_images_for_handle(handle: str) -> list[Path]:
    """Return Image Factory source images for a given product handle."""
    if not FACTORY_BASE.exists():
        return []
    d = FACTORY_BASE / handle
    if d.is_dir():
        imgs = sorted(d.glob("*.jpg")) + sorted(d.glob("*.png")) + sorted(d.glob("*.webp"))
        return imgs
    return []

def _extract_handle_from_img(img_path: Path) -> str:
    """Extract Shopify product handle from image filename."""
    name = img_path.stem
    parts = name.split("source-4x5-")
    if len(parts) == 2:
        return parts[1].rsplit("-gallery-", 1)[0]
    return ""

# ── BKS design tokens ──────────────────────────────────────────────────────────
PAPER   = (250, 250, 247)
BONE    = (239, 234, 224)
INK     = (10,  10,  10)
MUTED   = (130, 122, 110)

ACCENTS = {
    "hours":   (200, 196, 190),
    "origin":  ( 72, 152,   8),
    "glyph":   (212, 160,  48),
    "marker":  (192,  68,  24),
    "riviera": ( 12, 168, 152),
    "pulse":   (136, 136, 204),
    "token":   (152,  40, 216),
    "flag":    (200,  32,  32),
}

SERIES = {
    "hours":   "measured urban stillness",
    "origin":  "invented narrative marks",
    "glyph":   "constructed signs",
    "marker":  "gesture and motion",
    "riviera": "coastal geometry",
    "pulse":   "optical movement",
    "token":   "digital objects",
    "flag":    "graphic fields",
}

# Product type priority order for cover selection
COVER_PRIORITY = [
    "windbreaker", "puffer-jacket", "sneakers", "swimwear",
    "swim-trunks", "pullover-hoodie", "backpack", "travel-bag",
    "athletic-shorts", "lounge-pants", "flip-flops", "racerback-dress",
    "one-piece-swimsuit", "womens-tee", "duffle-bag", "beach-towel",
    "cozy-slipper", "hawaiian-shirt", "product",
]

def _resolve_key(coll_dir: Path) -> str:
    """Map folder name to BKS collection key."""
    name = coll_dir.name.lower().replace("bks-", "")
    for k in ACCENTS:
        if name.startswith(k) or k in name:
            return k
    return name

def _pick_images(type_dir: Path, n: int = 6, only_published: bool = True) -> list[Path]:
    """Pick n best images from a product type directory.
    Only uses images whose product handle is in the published set.
    Also checks Image Factory for higher-quality images first.
    """
    raw = sorted(type_dir.glob("*.webp")) + sorted(type_dir.glob("*.jpg")) + sorted(type_dir.glob("*.png"))
    results: list[Path] = []
    seen_handles: set[str] = set()

    for img in raw:
        handle = _extract_handle_from_img(img)
        if not handle:
            continue
        if only_published and handle not in PUBLISHED:
            continue
        if handle in seen_handles:
            continue
        seen_handles.add(handle)

        # Prefer Image Factory high-quality image
        factory_imgs = _factory_images_for_handle(handle)
        if factory_imgs:
            results.append(factory_imgs[0])
        else:
            results.append(img)

        if len(results) >= n:
            break

    # If still not enough, relax published filter
    if len(results) < 2:
        primary = [p for p in raw if "gallery-1" in p.name and "gallery-10" not in p.name]
        others  = [p for p in raw if p not in primary]
        return (primary + others)[:n]

    return results

def _load_and_crop(path: Path, w: int, h: int, position: str = "center") -> Image.Image:
    """Load image, resize to fill w×h, crop to exact size."""
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    new_w = round(iw * scale)
    new_h = round(ih * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - w) // 2
    top  = (new_h - h) // 2 if position == "center" else 0
    return img.crop((left, top, left + w, top + h))

def _draw_bracket_label(draw: ImageDraw.ImageDraw, text: str, x: int, y: int,
                         font_size: int = 18, color: tuple = INK) -> None:
    """Draw [TEXT.] bracket label."""
    label = f"[ {text.upper()} . ]"
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = None
    if font:
        draw.text((x, y), label, fill=color, font=font)
    else:
        draw.text((x, y), label, fill=color)

def _draw_text(draw: ImageDraw.ImageDraw, text: str, x: int, y: int,
               size: int = 16, color: tuple = INK, bold: bool = False) -> None:
    try:
        from PIL import ImageFont
        font_name = "arialbd.ttf" if bold else "arial.ttf"
        font = ImageFont.truetype(font_name, size)
    except Exception:
        font = None
    if font:
        draw.text((x, y), text, fill=color, font=font)
    else:
        draw.text((x, y), text, fill=color)

def _draw_accent_line(draw: ImageDraw.ImageDraw, x1: int, y: int, x2: int,
                       accent: tuple, thickness: int = 3) -> None:
    draw.rectangle([x1, y, x2, y + thickness - 1], fill=accent)

# ── COVER ─────────────────────────────────────────────────────────────────────
def build_cover(coll_dir: Path, out_dir: Path, key: str) -> Optional[Path]:
    """Full-bleed collection cover with BKS overlay. 1200×1500px."""
    accent = ACCENTS.get(key, MUTED)
    series = SERIES.get(key, "visual system")
    display_name = f"BKS {key.upper()}"

    # Find hero image
    hero_img = None
    for ptype in COVER_PRIORITY:
        type_dir = coll_dir / ptype
        if type_dir.exists():
            imgs = _pick_images(type_dir, 1)
            if imgs:
                hero_img = imgs[0]
                break

    if not hero_img:
        print(f"  [SKIP] {coll_dir.name} — no cover image found")
        return None

    W, H = 1200, 1500
    canvas = Image.new("RGB", (W, H), PAPER)

    # Hero image (full bleed)
    hero = _load_and_crop(hero_img, W, H, position="top")
    canvas.paste(hero, (0, 0))

    # Dark gradient overlay (bottom 45%)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    grad_start = int(H * 0.48)
    for i in range(H - grad_start):
        alpha = int(220 * (i / (H - grad_start)) ** 1.4)
        ov_draw.line([(0, grad_start + i), (W, grad_start + i)],
                     fill=(10, 10, 10, alpha))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(canvas)

    # Accent bar (bottom)
    _draw_accent_line(draw, 0, H - 4, W, accent, thickness=4)

    # Masthead top-left: BKS STUDIO
    _draw_text(draw, "BKS STUDIO", 32, 28, size=13, color=(250, 250, 247), bold=False)
    # Series top-right
    _draw_text(draw, series.upper(), W - 220, 28, size=11, color=(200, 196, 190))

    # Collection name (large, bottom)
    _draw_text(draw, display_name, 36, H - 200, size=72, color=(250, 250, 247), bold=True)

    # Rule line
    draw.line([(36, H - 118), (W - 36, H - 118)], fill=(250, 250, 247, 80), width=1)

    # Series label + pieces count
    _draw_text(draw, series, 36, H - 100, size=16, color=(200, 195, 188))
    _draw_text(draw, "Printed on demand · bakabo.club", 36, H - 72, size=12, color=(140, 132, 120))

    # Accent dot
    draw.ellipse([36, H - 48, 48, H - 36], fill=accent)

    out_path = out_dir / "cover_1200x1500.jpg"
    canvas.save(out_path, "JPEG", quality=90, optimize=True)
    print(f"  ✓ cover → {out_path.name}")
    return out_path

# ── PRODUCT TYPE GRID ─────────────────────────────────────────────────────────
def build_type_grid(type_dir: Path, out_dir: Path, key: str, type_name: str) -> Optional[Path]:
    """Product type catalog grid. 1200×900px — bone background, 2×3 or 2×2 product images."""
    imgs = _pick_images(type_dir, 6)
    if not imgs:
        return None

    accent = ACCENTS.get(key, MUTED)
    cols   = 3 if len(imgs) >= 3 else 2
    rows   = 2
    n      = min(cols * rows, len(imgs))
    imgs   = imgs[:n]

    W, H   = 1200, 900
    PAD    = 48           # outer padding
    HEADER = 72           # space for bracket label
    GAP    = 8

    cell_w = (W - 2 * PAD - GAP * (cols - 1)) // cols
    cell_h = (H - PAD - HEADER - GAP * (rows - 1) - PAD // 2) // rows

    canvas = Image.new("RGB", (W, H), BONE)
    draw   = ImageDraw.Draw(canvas)

    # Header accent bar
    _draw_accent_line(draw, PAD, PAD, PAD + 32, accent, thickness=2)

    # Bracket label
    _draw_bracket_label(draw, type_name, PAD + 44, PAD - 4, font_size=14, color=INK)

    # Bottom rule
    draw.line([(PAD, H - PAD // 2 + 4), (W - PAD, H - PAD // 2 + 4)],
              fill=tuple(c // 5 for c in MUTED), width=1)

    # Products
    for i, img_path in enumerate(imgs):
        col = i % cols
        row = i // cols
        x = PAD + col * (cell_w + GAP)
        y = PAD + HEADER + row * (cell_h + GAP)

        # White card background
        card_margin = 4
        canvas.paste(Image.new("RGB", (cell_w, cell_h), PAPER), (x, y))

        # Product image
        try:
            prod = _load_and_crop(img_path, cell_w - card_margin * 2,
                                   cell_h - card_margin * 2 - 38, "center")
            canvas.paste(prod, (x + card_margin, y + card_margin))
        except Exception as e:
            print(f"    [warn] {img_path.name}: {e}")

        # Product number
        num_txt = f"{i + 1:02d}"
        _draw_text(draw, num_txt, x + 8, y + 8, size=13,
                   color=accent if i == 0 else MUTED)

        # Product info bar at bottom of card
        info_y = y + cell_h - 36
        draw.rectangle([x, info_y, x + cell_w, y + cell_h], fill=PAPER)
        _draw_text(draw, f"BKS {key.upper()} · {type_name.upper()}", x + 8, info_y + 4,
                   size=8, color=MUTED)
        _draw_text(draw, "bakabo.club", x + cell_w - 72, info_y + 4,
                   size=8, color=MUTED)

    out_path = out_dir / f"{type_name}_grid_1200x900.jpg"
    canvas.save(out_path, "JPEG", quality=88, optimize=True)
    print(f"  ✓ grid  → {out_path.name}")
    return out_path

# ── EDITORIAL SPREAD ──────────────────────────────────────────────────────────
def build_spread(coll_dir: Path, out_dir: Path, key: str) -> Optional[Path]:
    """
    2-page editorial spread: left = hero photo, right = product catalog.
    1800×1200px total (900×1200 each page).
    Matches the open book reference: model/hero left + scontornati grid right.
    """
    accent = ACCENTS.get(key, MUTED)
    series = SERIES.get(key, "visual system")

    # Left: hero product (windbreaker or first available)
    hero_img = None
    hero_type = None
    for ptype in COVER_PRIORITY:
        td = coll_dir / ptype
        if td.exists():
            imgs = _pick_images(td, 1)
            if imgs:
                hero_img = imgs[0]
                hero_type = ptype
                break
    if not hero_img:
        return None

    # Right: grid products — pick from different types
    grid_imgs = []
    for ptype in COVER_PRIORITY:
        if ptype == hero_type:
            continue
        td = coll_dir / ptype
        if td.exists():
            imgs = _pick_images(td, 1)
            if imgs:
                grid_imgs.append((ptype, imgs[0]))
        if len(grid_imgs) >= 6:
            break

    W, H = 1800, 1200
    PAGE = W // 2      # 900
    canvas = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(canvas)

    # ── Left page: hero ────────────────────────────────────────────────────────
    hero = _load_and_crop(hero_img, PAGE, H, "top")
    canvas.paste(hero, (0, 0))

    # Bottom overlay on left page
    overlay_left = Image.new("RGBA", (PAGE, H), (0, 0, 0, 0))
    ol_draw = ImageDraw.Draw(overlay_left)
    for i in range(int(H * 0.36)):
        alpha = int(190 * (i / (H * 0.36)) ** 1.5)
        ol_draw.line([(0, H - 1 - i), (PAGE, H - 1 - i)], fill=(10, 10, 10, alpha))
    left_view = canvas.crop((0, 0, PAGE, H)).convert("RGBA")
    left_comp = Image.alpha_composite(left_view, overlay_left).convert("RGB")
    canvas.paste(left_comp, (0, 0))
    draw = ImageDraw.Draw(canvas)

    # Left text: collection name bottom-left
    _draw_text(draw, f"BKS {key.upper()}", 28, H - 120, size=52, color=PAPER, bold=True)
    _draw_text(draw, series, 28, H - 56, size=13, color=(180, 174, 165))
    _draw_accent_line(draw, 28, H - 68, 28 + 48, accent, thickness=2)

    # Center divider line
    draw.line([(PAGE, 24), (PAGE, H - 24)], fill=(220, 216, 210), width=1)

    # ── Right page: catalog ─────────────────────────────────────────────────────
    # Bone background
    right_bg = Image.new("RGB", (PAGE, H), BONE)
    canvas.paste(right_bg, (PAGE, 0))
    draw = ImageDraw.Draw(canvas)

    # Right header
    rx = PAGE + 32
    _draw_accent_line(draw, rx, 28, rx + 28, accent, thickness=2)
    _draw_bracket_label(draw, f"BKS {key} catalog", rx + 38, 22, font_size=13)
    draw.line([(rx, 64), (W - 32, 64)], fill=(180, 175, 166), width=1)

    # Product grid: 2 cols × 3 rows
    cols, rows = 2, 3
    grid_pad = 32
    gap = 8
    header_h = 80
    cell_w = (PAGE - 2 * grid_pad - gap) // cols
    cell_h = (H - header_h - 2 * grid_pad - gap * (rows - 1) - 24) // rows

    for i, (ptype, img_path) in enumerate(grid_imgs[:cols * rows]):
        col = i % cols
        row = i // cols
        cx = PAGE + grid_pad + col * (cell_w + gap)
        cy = header_h + grid_pad + row * (cell_h + gap)

        # White card
        card = Image.new("RGB", (cell_w, cell_h), PAPER)
        canvas.paste(card, (cx, cy))

        # Product image (keep proportions, center in upper 70%)
        img_area_h = int(cell_h * 0.68)
        try:
            prod = _load_and_crop(img_path, cell_w - 8, img_area_h - 4, "center")
            canvas.paste(prod, (cx + 4, cy + 4))
        except Exception:
            pass

        draw = ImageDraw.Draw(canvas)

        # Accent number
        _draw_text(draw, f"{i+1:02d}", cx + 6, cy + 6, size=11,
                   color=accent if i < 2 else MUTED)

        # Info bar
        info_y = cy + cell_h - 36
        draw.rectangle([cx, info_y, cx + cell_w, cy + cell_h], fill=PAPER)
        label = ptype.replace("-", " ").title()
        _draw_text(draw, label, cx + 6, info_y + 4, size=8, color=INK)
        _draw_text(draw, "MTO", cx + cell_w - 28, info_y + 4, size=8, color=MUTED)

    out_path = out_dir / "spread_1800x1200.jpg"
    canvas.save(out_path, "JPEG", quality=90, optimize=True)
    print(f"  ✓ spread → {out_path.name}")
    return out_path

# ── MAIN ──────────────────────────────────────────────────────────────────────
def run(collections: list[str] | None = None, skip_grid: bool = False) -> dict:
    """
    Run automount for all (or selected) collections.
    Returns summary dict.
    """
    OUT_BASE.mkdir(parents=True, exist_ok=True)
    summary = {}

    coll_dirs = sorted(PHOTO_BASE.iterdir()) if PHOTO_BASE.exists() else []

    for coll_dir in coll_dirs:
        if not coll_dir.is_dir() or coll_dir.name in ("uncategorized", "neo-classic"):
            continue
        key = _resolve_key(coll_dir)
        if collections and key not in collections:
            continue

        out_dir = OUT_BASE / coll_dir.name
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'─'*50}")
        print(f"  {coll_dir.name.upper()} (accent: {ACCENTS.get(key, MUTED)})")
        print(f"{'─'*50}")

        results = {}

        # Cover
        cover = build_cover(coll_dir, out_dir, key)
        results["cover"] = str(cover) if cover else None

        # Spread
        spread = build_spread(coll_dir, out_dir, key)
        results["spread"] = str(spread) if spread else None

        # Product type grids
        if not skip_grid:
            results["grids"] = {}
            for type_dir in sorted(coll_dir.iterdir()):
                if type_dir.is_dir() and type_dir.name not in ("product",):
                    grid = build_type_grid(type_dir, out_dir, key, type_dir.name)
                    if grid:
                        results["grids"][type_dir.name] = str(grid)

        summary[coll_dir.name] = results

    return summary

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="BKS Catalog Automount")
    parser.add_argument("--collections", nargs="*", default=None,
                        help="Collections to process (e.g. marker glyph). Default: all.")
    parser.add_argument("--no-grid", action="store_true",
                        help="Skip individual product type grids.")
    args = parser.parse_args()

    print("\n BKS Catalog Automount — v1")
    print(" Rules: paper #fafaf7 · bone #efeae0 · ink #0a0a0a · per-collection accent")
    print(" Output: output/catalog_spreads/\n")

    summary = run(
        collections=args.collections,
        skip_grid=args.no_grid,
    )

    total_covers  = sum(1 for v in summary.values() if v.get("cover"))
    total_spreads = sum(1 for v in summary.values() if v.get("spread"))
    total_grids   = sum(len(v.get("grids", {})) for v in summary.values())

    print(f"\n{'═'*50}")
    print(f"  Done: {len(summary)} collections")
    print(f"  {total_covers} covers · {total_spreads} spreads · {total_grids} grids")
    print(f"  Output: output/catalog_spreads/")
    print(f"{'═'*50}")
