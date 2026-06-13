"""BKS Studio — Background Removal v1.1
Safe pipeline: conservative mask → multi-output set → comparison.

Outputs per product:
  cutout_safe.png   — RGBA cutout with conservative mask (no eaten edges)
  white_bg.jpg      — product on white #FAFAF7
  transparent.png   — same as cutout_safe (alias for Shopify)
  shadow.jpg        — product on white with soft drop shadow
"""
from __future__ import annotations
import io
import logging
import re
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

log = logging.getLogger("bif.bg_remover")


# ── Public API ────────────────────────────────────────────────────────────────

def remove_background_safe(
    input_path: Path,
    output_dir: Path,
    product_slug: str = "product",
    preserve_edges: bool = True,
    fallback_original: bool = True,
    min_opaque_pct: float = 4.0,
    background_hex: str = "#FAFAF7",
    background_name: str = "salt",
) -> dict:
    """Conservative background removal.  Returns dict with all output paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    warnings: list[str] = []
    mode = "cutout"
    background_hex = _safe_hex(background_hex)
    background_slug = _safe_slug(background_name or background_hex)
    original_rgba = Image.open(input_path).convert("RGBA")

    # ── 1. Run rembg with CONSERVATIVE settings ────────────────────────────
    try:
        from rembg import remove, new_session
        session = new_session("u2net")
        raw = input_path.read_bytes()
        result_bytes = remove(
            raw,
            session=session,
            alpha_matting=True,
            # Conservative thresholds: keep more of the garment
            alpha_matting_foreground_threshold=250,  # very high → less FG erosion
            alpha_matting_background_threshold=5,    # very low  → less BG expansion
            alpha_matting_erode_size=3,              # small erode → preserve edges
        )
        rgba = Image.open(io.BytesIO(result_bytes)).convert("RGBA")
        log.info("rembg OK — conservative mode")
    except ImportError:
        # Fallback: remove.bg REST API
        rgba, api_warnings = _remove_bg_api(input_path)
        warnings.extend(api_warnings)
        if rgba is None:
            return {"success": False, "warnings": warnings,
                    "error": "rembg not installed and remove.bg API unavailable"}

    # ── 2. Validation ──────────────────────────────────────────────────────
    issues = _validate_cutout(rgba)
    warnings.extend(issues)

    # ── 3. Edge refinement — protect details before saving anything ────────
    rgba = _fill_interior_holes(rgba)
    if preserve_edges:
        rgba = _expand_alpha_from_original(original_rgba, rgba)
        warnings.append("Preserve-product mode: edges expanded slightly to avoid eaten details.")

    metrics = _alpha_metrics(rgba)
    if metrics["opaque_pct"] < min_opaque_pct:
        warnings.append(
            f"Cutout risk: only {metrics['opaque_pct']}% opaque area. "
            "Product may be damaged or too small in frame."
        )
        if fallback_original:
            rgba = _original_without_transparency(original_rgba)
            mode = "fallback_original"
            warnings.append(
                "Cutout blocked: saved original-based outputs instead of a damaged transparent asset."
            )

    # ── 4. Save all output variants ────────────────────────────────────────
    outputs: dict[str, Path] = {}

    # cutout_safe.png — conservative RGBA
    p = output_dir / f"{product_slug}_cutout_safe.png"
    rgba.save(p, "PNG")
    outputs["cutout_safe"] = p

    # transparent.png — alias
    p2 = output_dir / f"{product_slug}_transparent.png"
    rgba.save(p2, "PNG")
    outputs["transparent"] = p2

    # commercial_bg.jpg — selected BKS background profile
    p3 = output_dir / f"{product_slug}_{background_slug}_commercial_bg.jpg"
    _compose_on_bg(rgba, background_hex, (2000, 2000)).save(p3, "JPEG", quality=92)
    outputs["commercial_bg"] = p3
    outputs["white_bg"] = p3

    # shadow.jpg
    p4 = output_dir / f"{product_slug}_{background_slug}_shadow.jpg"
    _compose_with_shadow(rgba, background_hex, (2000, 2000)).save(p4, "JPEG", quality=92)
    outputs["shadow"] = p4

    # checkerboard_review.jpg
    p5 = output_dir / f"{product_slug}_checkerboard_review.jpg"
    _compose_on_checkerboard(rgba, (2000, 2000)).save(p5, "JPEG", quality=92)
    outputs["checkerboard"] = p5

    # edge_review.jpg — black/white split to reveal halos and missing edges
    p6 = output_dir / f"{product_slug}_edge_review.jpg"
    _compose_on_split_bg(rgba, (2000, 2000)).save(p6, "JPEG", quality=92)
    outputs["edge_review"] = p6

    # alpha_mask_review.png — raw alpha channel for QA
    p7 = output_dir / f"{product_slug}_alpha_mask_review.png"
    rgba.split()[3].save(p7, "PNG")
    outputs["alpha_mask"] = p7

    log.info("Background removal complete: %s", list(outputs.keys()))
    return {
        "success":  True,
        "outputs":  outputs,
        "warnings": warnings,
        "mode": mode,
        "background": {
            "name": background_slug,
            "hex": background_hex,
        },
    }


def compare_original_cutout(original: Path, cutout: Path) -> dict:
    """Side-by-side comparison metrics: pixel retention, edge quality."""
    orig = Image.open(original).convert("RGBA").resize((512, 512), Image.LANCZOS)
    cut  = Image.open(cutout).convert("RGBA").resize((512, 512), Image.LANCZOS)

    orig_arr = np.array(orig)
    cut_arr  = np.array(cut)

    alpha_cut    = cut_arr[:, :, 3]
    total        = alpha_cut.size
    opaque_px    = (alpha_cut > 128).sum()
    transparent_px = (alpha_cut < 10).sum()
    retention    = round(opaque_px / total * 100, 1)

    # Edge sharpness: std of alpha gradient
    from PIL.ImageFilter import FIND_EDGES
    edge_img = cut.split()[3].filter(FIND_EDGES)
    edge_arr = np.array(edge_img)
    edge_sharpness = round(float(edge_arr.std()), 1)

    return {
        "retention_pct":   retention,
        "transparent_pct": round(transparent_px / total * 100, 1),
        "edge_sharpness":  edge_sharpness,
        "grade": (
            "✅ Excellent" if retention > 35 and edge_sharpness > 15 else
            "⚠️  Review"   if retention > 20 else
            "❌ Poor"
        ),
    }


# ── Internals ─────────────────────────────────────────────────────────────────

def _safe_hex(value: str) -> str:
    value = (value or "").strip()
    if re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        return value.upper()
    return "#FAFAF7"


def _safe_slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value or "").strip("-").lower()
    return value[:40] or "background"

def _validate_cutout(img: Image.Image) -> list[str]:
    warnings = []
    arr   = np.array(img.convert("RGBA"))
    alpha = arr[:, :, 3]
    total = alpha.size
    transparent = (alpha == 0).sum()
    opaque      = (alpha > 200).sum()

    if transparent / total > 0.92:
        warnings.append("⚠️ Pixel loss >92% transparent — garment may be missing")
    if opaque / total < 0.04:
        warnings.append("⚠️ Very little opaque area — check product detection")

    # Border should be mostly transparent
    border = np.concatenate([
        alpha[0, :], alpha[-1, :], alpha[:, 0], alpha[:, -1]
    ])
    if border.mean() > 30:
        warnings.append("⚠️ Non-transparent border — BG may not be fully removed")

    return warnings


def _alpha_metrics(rgba: Image.Image) -> dict:
    arr = np.array(rgba.convert("RGBA"))
    alpha = arr[:, :, 3]
    total = alpha.size
    return {
        "opaque_pct": round(float((alpha > 128).sum()) / total * 100, 1),
        "transparent_pct": round(float((alpha < 10).sum()) / total * 100, 1),
    }


def _fill_interior_holes(rgba: Image.Image) -> Image.Image:
    """Fill small transparent holes inside the garment silhouette."""
    arr   = np.array(rgba.copy())
    alpha = arr[:, :, 3].copy()

    # Binary close operation to fill small interior holes
    from PIL.ImageFilter import MaxFilter
    alpha_img   = Image.fromarray(alpha)
    closed      = alpha_img.filter(MaxFilter(7))  # dilate
    closed_arr  = np.array(closed)
    # Only fill where original was semi-transparent (interior holes)
    mask        = (alpha < 50) & (closed_arr > 200)
    arr[mask, 3] = 200  # partially fill
    return Image.fromarray(arr, "RGBA")


def _expand_alpha_from_original(original_rgba: Image.Image, cutout_rgba: Image.Image) -> Image.Image:
    """Recover a thin rim from the original image so straps, seams, and laces survive."""
    cutout = cutout_rgba.convert("RGBA")
    original = original_rgba.convert("RGBA").resize(cutout.size, Image.LANCZOS)

    cut_arr = np.array(cutout)
    orig_arr = np.array(original)
    alpha = cut_arr[:, :, 3]

    expanded = Image.fromarray(alpha).filter(ImageFilter.MaxFilter(5))
    expanded_arr = np.array(expanded)
    recover = (expanded_arr > alpha) & (expanded_arr > 24)

    cut_arr[recover, :3] = orig_arr[recover, :3]
    cut_arr[:, :, 3] = np.maximum(alpha, np.minimum(expanded_arr, 255))
    return Image.fromarray(cut_arr, "RGBA")


def _original_without_transparency(original_rgba: Image.Image) -> Image.Image:
    original = original_rgba.convert("RGBA")
    arr = np.array(original)
    arr[:, :, 3] = 255
    return Image.fromarray(arr, "RGBA")


def _compose_on_bg(rgba: Image.Image, bg_hex: str,
                    size: tuple[int, int]) -> Image.Image:
    r, g, b = int(bg_hex[1:3], 16), int(bg_hex[3:5], 16), int(bg_hex[5:], 16)
    bg = Image.new("RGB", size, (r, g, b))
    product = rgba.copy()
    product.thumbnail((int(size[0] * 0.82), int(size[1] * 0.82)), Image.LANCZOS)
    x = (size[0] - product.width)  // 2
    y = (size[1] - product.height) // 2
    bg.paste(product, (x, y), product)
    return bg


def _compose_with_shadow(rgba: Image.Image, bg_hex: str,
                          size: tuple[int, int]) -> Image.Image:
    """Compose product with a soft Gaussian drop shadow."""
    r, g, b = int(bg_hex[1:3], 16), int(bg_hex[3:5], 16), int(bg_hex[5:], 16)
    bg = Image.new("RGB", size, (r, g, b))

    product = rgba.copy()
    product.thumbnail((int(size[0] * 0.78), int(size[1] * 0.78)), Image.LANCZOS)
    x = (size[0] - product.width)  // 2
    y = (size[1] - product.height) // 2

    # Shadow: extract alpha, blur, darken
    alpha_ch = product.split()[3]
    shadow   = Image.new("RGBA", size, (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", product.size, (30, 20, 10, 200))
    shadow_layer.putalpha(alpha_ch)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=18))
    shadow.paste(shadow_layer, (x + 16, y + 22), shadow_layer)

    # Compose: bg → shadow → product
    bg_rgba = bg.convert("RGBA")
    bg_rgba = Image.alpha_composite(bg_rgba, shadow)
    bg_rgba.paste(product, (x, y), product)
    return bg_rgba.convert("RGB")


def _compose_on_checkerboard(rgba: Image.Image, size: tuple[int, int]) -> Image.Image:
    bg = Image.new("RGB", size, "#E7E3DA")
    draw = ImageDraw.Draw(bg)
    tile = 96
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            if (x // tile + y // tile) % 2 == 0:
                draw.rectangle([x, y, x + tile, y + tile], fill="#BDB8AD")

    product = rgba.copy()
    product.thumbnail((int(size[0] * 0.82), int(size[1] * 0.82)), Image.LANCZOS)
    x = (size[0] - product.width) // 2
    y = (size[1] - product.height) // 2
    bg_rgba = bg.convert("RGBA")
    bg_rgba.paste(product, (x, y), product)
    return bg_rgba.convert("RGB")


def _compose_on_split_bg(rgba: Image.Image, size: tuple[int, int]) -> Image.Image:
    bg = Image.new("RGB", size, "#FAFAF7")
    draw = ImageDraw.Draw(bg)
    draw.rectangle([0, 0, size[0] // 2, size[1]], fill="#050505")
    draw.line([size[0] // 2, 0, size[0] // 2, size[1]], fill="#C9B79C", width=4)

    product = rgba.copy()
    product.thumbnail((int(size[0] * 0.82), int(size[1] * 0.82)), Image.LANCZOS)
    x = (size[0] - product.width) // 2
    y = (size[1] - product.height) // 2
    bg_rgba = bg.convert("RGBA")
    bg_rgba.paste(product, (x, y), product)
    return bg_rgba.convert("RGB")


def _remove_bg_api(input_path: Path) -> tuple[Image.Image | None, list[str]]:
    import requests
    try:
        from config.settings import REMOVE_BG_API_KEY
    except ImportError:
        import os
        REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY", "")

    warnings = []
    if not REMOVE_BG_API_KEY:
        warnings.append("rembg not available and REMOVE_BG_API_KEY not set")
        return None, warnings

    resp = requests.post(
        "https://api.remove.bg/v1.0/removebg",
        files={"image_file": input_path.open("rb")},
        data={"size": "auto"},
        headers={"X-Api-Key": REMOVE_BG_API_KEY},
        timeout=60,
    )
    if resp.status_code == 200:
        return Image.open(io.BytesIO(resp.content)).convert("RGBA"), warnings
    warnings.append(f"remove.bg API error {resp.status_code}")
    return None, warnings
