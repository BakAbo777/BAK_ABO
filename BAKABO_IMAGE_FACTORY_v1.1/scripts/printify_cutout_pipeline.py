"""BKS Studio — Printify → Cutout → Collection Overlay pipeline.

Fetches ALL products from Printify, removes backgrounds with maximum precision,
then generates one overlay per BKS collection accent color + paper/dark standard.

Outputs per product (in output/cutout/{product_slug}/):
  {slug}_cutout_safe.png          — RGBA transparent (Shopify-ready)
  {slug}_salt_commercial_bg.jpg   — product on #FAFAF7 paper
  {slug}_onyx_commercial_bg.jpg   — product on #0A0A0A cinema dark
  {slug}_{collection}_overlay.jpg — one per BKS collection accent (8 files)
  {slug}_edge_review.jpg          — QA split BG
  {slug}_checkerboard_review.jpg  — QA checkerboard
  manifest.csv                    — full path/URL index for all products
"""
from __future__ import annotations

import csv
import io
import logging
import sys
import time
from pathlib import Path

import requests

# ── Setup paths ────────────────────────────────────────────────────────────────
FACTORY_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(FACTORY_ROOT))

from config.settings import CUTOUT_DIR, SOURCE_DIR
from modules.background_remover import remove_background_safe
from modules.printify_client import load_products, resolve_shop_id

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger("bks.cutout_pipeline")

# ── BKS collection accent palette ─────────────────────────────────────────────
BKS_COLLECTION_PALETTE: dict[str, str] = {
    "hours":   "#c8c4be",
    "glyph":   "#d4a030",
    "marker":  "#c04418",
    "riviera": "#0ca898",
    "pulse":   "#8888cc",
    "token":   "#9828d8",
    "flag":    "#c82020",
    "origin":  "#489808",
}

STANDARD_BACKGROUNDS: dict[str, str] = {
    "salt":  "#FAFAF7",   # editorial paper
    "onyx":  "#0A0A0A",   # cinema dark
}

ALL_BACKGROUNDS = {**STANDARD_BACKGROUNDS, **BKS_COLLECTION_PALETTE}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _slug(text: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def _primary_image_url(product: dict) -> str | None:
    images = product.get("images") or []
    for img in images:
        if isinstance(img, dict) and img.get("is_default"):
            return img.get("src") or img.get("url")
    if images and isinstance(images[0], dict):
        return images[0].get("src") or images[0].get("url")
    return None


def _download(url: str, dest: Path) -> bool:
    import urllib3
    for verify in (True, False):
        try:
            if not verify:
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            r = requests.get(url, timeout=60, stream=True, verify=verify)
            r.raise_for_status()
            dest.write_bytes(r.content)
            return True
        except requests.exceptions.SSLError:
            if not verify:
                log.warning("Download SSL failed even without verify: %s", url)
                return False
            continue  # retry without SSL verify
        except Exception as exc:
            log.warning("Download failed %s: %s", url, exc)
            return False
    return False


def _collection_from_product(product: dict) -> str | None:
    tags = " ".join(product.get("tags", [])).lower()
    title = product.get("title", "").lower()
    for col in BKS_COLLECTION_PALETTE:
        if col in tags or col in title:
            return col
    return None


# ── Per-product pipeline ──────────────────────────────────────────────────────

def _shopify_id_from_product(product: dict) -> str | None:
    """Extract the linked Shopify product ID from a Printify product."""
    ext = product.get("external") or {}
    if isinstance(ext, dict):
        sid = ext.get("id") or ext.get("shopify_id") or ext.get("shopify_product_id")
        if sid:
            return str(sid)
    return None


def process_product(product: dict, force: bool = False, upload_to_shopify: bool = False) -> dict:
    pid   = product.get("id", "unknown")
    title = product.get("title", f"product-{pid}")
    slug  = _slug(title)

    product_dir = CUTOUT_DIR / slug
    product_dir.mkdir(parents=True, exist_ok=True)

    cutout_path = product_dir / f"{slug}_cutout_safe.png"
    if cutout_path.exists() and not force:
        log.info("SKIP (cached)  %s", slug)
        return {"product_id": pid, "slug": slug, "status": "cached",
                "cutout": str(cutout_path)}

    image_url = _primary_image_url(product)
    if not image_url:
        log.warning("NO IMAGE  %s (%s)", slug, pid)
        return {"product_id": pid, "slug": slug, "status": "no_image"}

    # Download source
    source_path = SOURCE_DIR / f"{slug}_source.jpg"
    if not source_path.exists() or force:
        ok = _download(image_url, source_path)
        if not ok:
            return {"product_id": pid, "slug": slug, "status": "download_failed"}

    log.info("PROCESSING  %s", slug)

    # Detect which collection this product belongs to (for primary overlay)
    primary_col = _collection_from_product(product)

    # Run background removal — conservative mode, max edge preservation
    result = remove_background_safe(
        input_path=source_path,
        output_dir=product_dir,
        product_slug=slug,
        preserve_edges=True,
        fallback_original=True,
    )

    if not result["success"]:
        log.error("CUTOUT FAILED  %s: %s", slug, result.get("error"))
        return {"product_id": pid, "slug": slug, "status": "cutout_failed",
                "error": result.get("error")}

    if result.get("warnings"):
        for w in result["warnings"]:
            if "⚠️" in w or "❌" in w:
                log.warning("  %s", w)

    # Generate all collection overlays from the cutout
    from PIL import Image
    from modules.background_remover import _compose_on_bg, _compose_with_shadow

    cutout = Image.open(cutout_path).convert("RGBA")
    overlay_paths: dict[str, str] = {}

    for bg_name, bg_hex in ALL_BACKGROUNDS.items():
        out_path = product_dir / f"{slug}_{bg_name}_overlay.jpg"
        if not out_path.exists() or force:
            composed = _compose_with_shadow(cutout, bg_hex, (2000, 2000))
            composed.save(out_path, "JPEG", quality=92)
        overlay_paths[bg_name] = str(out_path)

    log.info("  OK  %s → %d overlays", slug, len(overlay_paths))

    # ── Optional: upload clean salt background version to Shopify ─────────
    shopify_upload = None
    if upload_to_shopify:
        shopify_product_id = _shopify_id_from_product(product)
        salt_path = Path(overlay_paths.get("salt", ""))
        if not shopify_product_id:
            log.warning("UPLOAD SKIP  %s — no Shopify product ID in Printify external field", slug)
        elif not salt_path.exists():
            log.warning("UPLOAD SKIP  %s — salt overlay not found at %s", slug, salt_path)
        else:
            try:
                from modules.shopify_client import upload_image
                alt_text = f"{title} — BKS Studio cutout (no background)"
                img_data = upload_image(shopify_product_id, salt_path, alt=alt_text, position=2)
                shopify_upload = {
                    "shopify_product_id": shopify_product_id,
                    "shopify_image_id": img_data.get("id"),
                    "shopify_image_src": img_data.get("src"),
                }
                log.info("  UPLOADED  %s → Shopify product %s (image id: %s)",
                         slug, shopify_product_id, img_data.get("id"))
            except Exception as exc:
                log.error("  UPLOAD FAILED  %s: %s", slug, exc)
                shopify_upload = {"error": str(exc)}

    return {
        "product_id":      pid,
        "slug":            slug,
        "title":           title,
        "status":          "ok",
        "primary_collection": primary_col or "",
        "source_url":      image_url,
        "cutout":          str(cutout_path),
        "overlays":        overlay_paths,
        "shopify_upload":  shopify_upload,
        "warnings":        result.get("warnings", []),
    }


# ── Manifest writer ───────────────────────────────────────────────────────────

def write_manifest(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bg_keys = list(ALL_BACKGROUNDS.keys())
    fieldnames = ["product_id", "slug", "title", "status", "primary_collection",
                  "source_url", "cutout"] + [f"overlay_{k}" for k in bg_keys] + ["warnings"]
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            flat = {k: v for k, v in row.items() if k != "overlays" and k != "warnings"}
            if "overlays" in row:
                for k in bg_keys:
                    flat[f"overlay_{k}"] = row["overlays"].get(k, "")
            flat["warnings"] = " | ".join(row.get("warnings", []))
            writer.writerow(flat)
    log.info("Manifest written: %s (%d rows)", path, len(rows))


# ── Main ──────────────────────────────────────────────────────────────────────

def run(max_products: int = 0, force: bool = False, upload_to_shopify: bool = False) -> None:
    log.info("Resolving Printify shop ID...")
    shop_id = resolve_shop_id()
    log.info("Shop ID: %s", shop_id)

    all_products: list[dict] = []
    page = 1
    page_limit = 50  # Printify max
    while True:
        batch = load_products(page=page, limit=page_limit)
        if not batch:
            break
        all_products.extend(batch)
        log.info("  Page %d: %d products (total so far: %d)", page, len(batch), len(all_products))
        if len(batch) < page_limit:
            break
        if max_products and len(all_products) >= max_products:
            all_products = all_products[:max_products]
            break
        page += 1
        time.sleep(0.3)

    if max_products:
        all_products = all_products[:max_products]

    log.info("Total products to process: %d", len(all_products))

    results = []
    for i, product in enumerate(all_products, 1):
        log.info("[%d/%d]", i, len(all_products))
        row = process_product(product, force=force, upload_to_shopify=upload_to_shopify)
        results.append(row)
        time.sleep(0.3)

    manifest_path = FACTORY_ROOT / "output" / "cutout_manifest.csv"
    write_manifest(results, manifest_path)

    ok    = sum(1 for r in results if r["status"] == "ok")
    skip  = sum(1 for r in results if r["status"] == "cached")
    fail  = sum(1 for r in results if r["status"] not in ("ok", "cached"))
    log.info("Done. OK=%d  CACHED=%d  FAILED=%d", ok, skip, fail)
    log.info("Manifest: %s", manifest_path)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="BKS Printify → Cutout pipeline")
    parser.add_argument("--max",   type=int, default=0,    help="Limit number of products (0=all)")
    parser.add_argument("--force",  action="store_true", help="Re-process even if cached")
    parser.add_argument("--upload", action="store_true", help="Upload salt-bg cutout to Shopify product (requires linked Shopify ID in Printify external field)")
    args = parser.parse_args()
    run(max_products=args.max, force=args.force, upload_to_shopify=args.upload)
