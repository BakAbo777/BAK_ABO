"""BKS Studio — Image Generator v1.1
Fixes:
- Hero 16:7: generate at 1536x1024, then pad (not crop) to 2400x1050
- dry_run: creates labelled placeholder PNG with prompt text
"""
from __future__ import annotations
import base64
import logging
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

from config.settings import (
    OPENAI_API_KEY, OPENAI_IMAGE_MODEL, OPENAI_IMAGE_QUALITY, GENERATED_DIR
)

log = logging.getLogger("bif.image_generator")

# API generation sizes (what we request from OpenAI)
SLOT_API_SIZES = {
    "product_front":    "1024x1024",
    "product_back":     "1024x1024",
    "editorial_square": "1024x1024",
    "editorial_4x5":    "1024x1536",
    "hero_banner":      "1536x1024",  # closest available; will pad, not crop
    "texture_detail":   "1024x1024",
}

# Final Shopify output sizes
SLOT_FINAL_SIZES = {
    "product_front":    (2000, 2000),
    "product_back":     (2000, 2000),
    "editorial_square": (2000, 2000),
    "editorial_4x5":    (1600, 2000),
    "hero_banner":      (2400, 1050),
    "texture_detail":   (1500, 1500),
}

# For hero: use pad (letterbox) not crop to preserve full image
SLOT_USE_PAD = {"hero_banner"}

# Placeholder background colors per slot
_SLOT_COLORS = {
    "product_front":    (250, 250, 247),
    "product_back":     (240, 240, 237),
    "editorial_square": (30,  30,  30),
    "editorial_4x5":    (20,  20,  20),
    "hero_banner":      (10,  10,  10),
    "texture_detail":   (60,  50,  40),
}


def generate(
    reference_path: Path,
    prompt: str,
    slug: str,
    collection: str,
    slot: str,
    variant: int = 1,
    output_dir: Path | None = None,
    dry_run: bool = False,
) -> dict:
    """Generate one editorial image or a dry-run placeholder."""
    out_dir = output_dir or (GENERATED_DIR / collection / slug)
    out_dir.mkdir(parents=True, exist_ok=True)

    base      = f"bks-{collection}-{slug}-{slot}-{variant:02d}"
    raw_png   = out_dir / f"{base}_raw.png"
    final_png = out_dir / f"{base}.png"
    final_jpg = out_dir / f"{base}.jpg"
    prompt_f  = out_dir / f"{base}_prompt.txt"

    # Always save prompt
    prompt_f.write_text(prompt, encoding="utf-8")

    if dry_run:
        _make_placeholder(final_png, final_jpg, slot, prompt, collection, slug, variant)
        return {
            "success": True, "output_png": final_png, "output_jpg": final_jpg,
            "prompt": prompt, "status": "dry-run", "error": "",
        }

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        api_size = SLOT_API_SIZES.get(slot, "1024x1024")

        with open(reference_path, "rb") as ref:
            response = client.images.edit(
                model=OPENAI_IMAGE_MODEL,
                image=ref,
                prompt=prompt,
                n=1,
                size=api_size,
                quality=OPENAI_IMAGE_QUALITY,
            )

        img_b64 = response.data[0].b64_json
        raw_png.write_bytes(base64.b64decode(img_b64))

        final_size = SLOT_FINAL_SIZES.get(slot, (2000, 2000))
        if slot in SLOT_USE_PAD:
            _resize_pad(raw_png, final_png, final_size, "PNG")
            _resize_pad(raw_png, final_jpg, final_size, "JPEG")
        else:
            _resize_cover(raw_png, final_png, final_size, "PNG")
            _resize_cover(raw_png, final_jpg, final_size, "JPEG")

        log.info("Generated %s", final_jpg)
        time.sleep(0.5)
        return {
            "success": True, "output_png": final_png, "output_jpg": final_jpg,
            "prompt": prompt, "status": "generated", "error": "",
        }

    except Exception as exc:
        log.error("Generation failed for %s: %s", base, exc)
        return {
            "success": False, "output_png": None, "output_jpg": None,
            "prompt": prompt, "status": "failed", "error": str(exc),
        }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _resize_cover(src: Path, dst: Path, size: tuple[int, int], fmt: str) -> None:
    """Fill frame exactly — may crop to preserve aspect ratio."""
    img = Image.open(src).convert("RGB")
    img = ImageOps.fit(img, size, Image.LANCZOS)
    _save(img, dst, fmt)


def _resize_pad(src: Path, dst: Path, size: tuple[int, int], fmt: str) -> None:
    """Fit entire image with letterbox padding — NO cropping.
    Used for hero_banner to preserve full composition.
    """
    img = Image.open(src).convert("RGB")
    img.thumbnail(size, Image.LANCZOS)          # shrink to fit within size

    # Determine background color from edges (dominant edge color ≈ bg)
    edge_px = list(img.getdata())[:img.width]
    avg_r = sum(p[0] for p in edge_px) // len(edge_px)
    avg_g = sum(p[1] for p in edge_px) // len(edge_px)
    avg_b = sum(p[2] for p in edge_px) // len(edge_px)
    bg_color = (avg_r, avg_g, avg_b)

    canvas = Image.new("RGB", size, bg_color)
    x = (size[0] - img.width)  // 2
    y = (size[1] - img.height) // 2
    canvas.paste(img, (x, y))
    _save(canvas, dst, fmt)


def _save(img: Image.Image, dst: Path, fmt: str) -> None:
    if fmt == "JPEG":
        img.save(dst, "JPEG", quality=92, optimize=True)
    else:
        img.save(dst, "PNG", optimize=True)


def _make_placeholder(
    png_out: Path, jpg_out: Path,
    slot: str, prompt: str,
    collection: str, slug: str, variant: int,
) -> None:
    """Create a labelled placeholder image for dry-run preview."""
    final_size = SLOT_FINAL_SIZES.get(slot, (1024, 1024))
    # Work at 512 max for speed, then resize
    work_w = min(512, final_size[0])
    work_h = int(work_w * final_size[1] / final_size[0])
    work_size = (work_w, work_h)

    bg_color = _SLOT_COLORS.get(slot, (30, 30, 30))
    img  = Image.new("RGB", work_size, bg_color)
    draw = ImageDraw.Draw(img)

    # Determine text color
    brightness = sum(bg_color) / 3
    tc = (250, 250, 247) if brightness < 128 else (10, 10, 10)
    ac = (201, 183, 156)  # --bks-dune

    # Border
    draw.rectangle([2, 2, work_w - 3, work_h - 3], outline=ac, width=1)

    # Slot label
    draw.text((12, 12), f"DRY-RUN", fill=ac)
    draw.text((12, 28), slot.replace("_", " ").upper(), fill=tc)
    draw.text((12, 44), f"{collection.upper()} · {slug[:30]}", fill=tc)
    draw.text((12, 60), f"Variant {variant:02d}", fill=tc)

    # Prompt preview (wrap at ~50 chars)
    lines = _wrap(prompt[:400], 50)
    y_pos = 88
    for line in lines[:8]:
        if y_pos + 14 > work_h - 16:
            break
        draw.text((12, y_pos), line, fill=(180, 170, 160))
        y_pos += 14

    # Scale up to final size
    img = img.resize(final_size, Image.NEAREST)
    _save(img, png_out, "PNG")
    _save(img.convert("RGB"), jpg_out, "JPEG")
    log.debug("Placeholder created: %s", jpg_out.name)


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur += (" " if cur else "") + w
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines
