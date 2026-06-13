import argparse
import csv
import io
import math
import re
from pathlib import Path
from urllib.parse import urlparse

import requests
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

try:
    from rembg import remove as rembg_remove
except Exception:
    rembg_remove = None


BKS_BACKGROUNDS = {
    "bone": "#EFEAE0",
    "salt": "#FAFAF7",
    "shadow": "#242833",
    "onyx": "#0A0A0A",
}

BKS_RATIOS = {
    "product": (4, 5, 2000, 2500),
    "mockup": (4, 5, 2000, 2500),
    "editorial": (16, 9, 3840, 2160),
    "hero": (16, 9, 3840, 2160),
    "compact": (1, 1, 1080, 1080),
    "ugc": (1, 1, 1080, 1080),
    "lookbook": (3, 4, 1800, 2400),
}


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value or "").strip("-").lower()
    return value or "bks-image"


def hex_to_rgb(value: str):
    value = value.strip().lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def load_image(src: str, timeout=30) -> Image.Image:
    parsed = urlparse(src)
    if parsed.scheme in {"http", "https"}:
        resp = requests.get(src, timeout=timeout, headers={"User-Agent": "BKSStudioImageProcessor/1.0"})
        resp.raise_for_status()
        return Image.open(io.BytesIO(resp.content)).convert("RGBA")
    return Image.open(src).convert("RGBA")


def fallback_remove_background(img: Image.Image, tolerance=42) -> Image.Image:
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    samples = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1)]
    avg = [0, 0, 0]
    for x, y in samples:
        r, g, b, _ = px[x, y]
        avg[0] += r
        avg[1] += g
        avg[2] += b
    bg = tuple(v // len(samples) for v in avg)
    out = img.copy()
    opx = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = opx[x, y]
            dist = math.sqrt((r - bg[0]) ** 2 + (g - bg[1]) ** 2 + (b - bg[2]) ** 2)
            if dist < tolerance:
                opx[x, y] = (r, g, b, 0)
    return out


def remove_background(img: Image.Image) -> Image.Image:
    if rembg_remove:
        return rembg_remove(img)
    return fallback_remove_background(img)


def fit_canvas(img: Image.Image, width: int, height: int, bg: str, remove_bg=True) -> Image.Image:
    work = remove_background(img) if remove_bg else img.convert("RGBA")
    bbox = work.getbbox()
    if bbox:
        work = work.crop(bbox)

    canvas = Image.new("RGBA", (width, height), hex_to_rgb(bg) + (255,))
    max_w = int(width * 0.84)
    max_h = int(height * 0.84)
    work.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

    if remove_bg:
        alpha = work.getchannel("A").filter(ImageFilter.GaussianBlur(10))
        shadow = Image.new("RGBA", work.size, (0, 0, 0, 58))
        shadow.putalpha(alpha)
        sx = (width - work.width) // 2
        sy = (height - work.height) // 2 + int(height * 0.025)
        canvas.alpha_composite(shadow, (sx + 12, sy + 18))

    x = (width - work.width) // 2
    y = (height - work.height) // 2
    canvas.alpha_composite(work, (x, y))
    return canvas.convert("RGB")


def neutral_color_correction(img: Image.Image) -> Image.Image:
    # Fixed BKS correction: neutral daylight, no Instagram-style cold cast, no oversaturation.
    img = ImageOps.autocontrast(img, cutoff=0.4)
    img = ImageEnhance.Color(img).enhance(0.96)
    img = ImageEnhance.Contrast(img).enhance(1.03)
    img = ImageEnhance.Sharpness(img).enhance(1.04)
    return img


def process_one(src: str, out_dir: Path, handle: str, mode: str, bg_key: str, index: int, fmt: str):
    ratio = BKS_RATIOS[mode]
    bg = BKS_BACKGROUNDS[bg_key]
    img = load_image(src)
    final = fit_canvas(img, ratio[2], ratio[3], bg, remove_bg=mode in {"product", "mockup", "compact", "ugc"})
    final = neutral_color_correction(final)
    suffix = "webp" if fmt == "webp" else "jpg"
    out = out_dir / f"{slugify(handle)}-{mode}-{index}.{suffix}"
    out.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "webp":
        final.save(out, "WEBP", quality=90, method=6)
    else:
        final.save(out, "JPEG", quality=90, optimize=True)
    return out


def process_csv(csv_path: Path, out_dir: Path, mode: str, bg_key: str, fmt: str, limit: int = 0):
    written = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            src = (row.get("Image Src") or "").strip()
            if not src:
                continue
            if limit and len(written) >= limit:
                break
            handle = row.get("Handle") or row.get("Title") or csv_path.stem
            try:
                written.append(process_one(src, out_dir, handle, mode, bg_key, len(written) + 1, fmt))
            except Exception as exc:
                print(f"ERROR {handle}: {exc}")
    return written


def main():
    parser = argparse.ArgumentParser(description="BKS Studio visual-standard image processor")
    parser.add_argument("--csv", type=Path, help="Shopify CSV with Image Src")
    parser.add_argument("--image", help="Single local image or URL")
    parser.add_argument("--handle", default="bks-image")
    parser.add_argument("--out", type=Path, default=Path("output/bks_images"))
    parser.add_argument("--mode", choices=sorted(BKS_RATIOS), default="product")
    parser.add_argument("--background", choices=sorted(BKS_BACKGROUNDS), default="bone")
    parser.add_argument("--format", choices=["webp", "jpg"], default="webp")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    if args.csv:
        written = process_csv(args.csv, args.out, args.mode, args.background, args.format, args.limit)
    elif args.image:
        written = [process_one(args.image, args.out, args.handle, args.mode, args.background, 1, args.format)]
    else:
        raise SystemExit("Provide --csv or --image")

    print(f"Processed {len(written)} images")
    for path in written[:20]:
        print(path)


if __name__ == "__main__":
    main()
