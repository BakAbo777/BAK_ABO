"""BKS Studio — Prepare catalog images from Printify mockups.

Uses the original Printify mockup images (downloaded by sync_printify_library.py)
as catalog images. NO creative changes, NO AI generation, NO text added.

Operations performed:
  - Rename to BKS handle convention: {handle}_{n:02d}.jpg
  - Resize to catalog target: 2000×2000 px max (Shopify recommended)
  - Convert to JPEG at 90% quality (catalog standard)
  - Record output in DB as asset_type='catalog_mockup'
  - Optionally upload directly to Shopify product media

Rules (immutable — never override):
  - Mockup images used AS-IS: zero content changes.
  - Artwork/texture NOT modified.
  - Product model NOT modified.
  - NO text added at any stage.
  - Shape and dimensions come from Printify blueprint only.

Usage:
  python scripts/prepare_catalog_images.py
  python scripts/prepare_catalog_images.py --collection bks-hours
  python scripts/prepare_catalog_images.py --upload-to-shopify
  python scripts/prepare_catalog_images.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings()  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_env = ROOT / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        if _k.strip() not in os.environ:
            os.environ[_k.strip()] = _v.strip().strip('"').strip("'")

from ecommerce_automation import catalog_db
from bks_assets import active_catalog_db

CATALOG_TARGET = ROOT / "output" / "catalog_images"
CATALOG_MAX_PX  = 2000
CATALOG_QUALITY = 90

# Shopify
DOMAIN  = os.environ.get("SHOPIFY_MYSHOPIFY_DOMAIN", "")
TOKEN   = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-01")
REST_BASE = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR_REST  = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}


def _out(msg: str) -> None:
    sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
    sys.stdout.flush()


def _ensure_pil() -> bool:
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


def _process_image(src: Path, dest: Path, max_px: int, quality: int) -> Path | None:
    """Resize image, preserving PNG transparency when present.
    Returns the actual saved path (may differ from dest if PNG), or None on error.
    """
    try:
        from PIL import Image
        with Image.open(src) as img:
            has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
            w, h = img.size
            if w > max_px or h > max_px:
                ratio = min(max_px / w, max_px / h)
                new_size = (int(w * ratio), int(h * ratio))
            else:
                new_size = None

            dest.parent.mkdir(parents=True, exist_ok=True)

            if has_alpha:
                out_path = dest.with_suffix(".png")
                img_out = img.convert("RGBA")
                if new_size:
                    img_out = img_out.resize(new_size, Image.LANCZOS)
                img_out.save(out_path, "PNG", optimize=True)
                return out_path
            else:
                img_out = img.convert("RGB")
                if new_size:
                    img_out = img_out.resize(new_size, Image.LANCZOS)
                img_out.save(dest, "JPEG", quality=quality, optimize=True)
                return dest
    except Exception as exc:
        _out(f"    ✗ image processing error: {exc}")
        return None


def _shopify_upload_product_image(
    shopify_product_id: str, image_path: Path, alt: str = ""
) -> str:
    """Upload image to Shopify product media via GraphQL staged upload."""
    if not DOMAIN or not TOKEN:
        return ""
    try:
        import base64
        data = image_path.read_bytes()
        b64 = base64.b64encode(data).decode()
        # Use REST product images endpoint (simpler than GraphQL for product images)
        url = f"{REST_BASE}/products/{shopify_product_id}/images.json"
        payload = {"image": {"attachment": b64, "filename": image_path.name, "alt": alt}}
        r = requests.post(url, headers=HDR_REST, json=payload, timeout=60, verify=False)
        if r.ok:
            return r.json().get("image", {}).get("src", "")
    except Exception as exc:
        _out(f"    ✗ Shopify upload error: {exc}")
    return ""


def prepare_collection(
    db_path: Path,
    collection: str,
    dry_run: bool,
    upload_to_shopify: bool,
    has_pil: bool,
) -> dict:
    products = catalog_db.list_printify_products(db_path, collection=collection)
    processed = 0
    skipped = 0
    errors = 0

    for prod in products:
        pid = prod["printify_product_id"]
        title = prod["title"]
        col = prod["collection"] or "uncategorized"
        shopify_id = prod["shopify_product_id"]

        local_paths = json.loads(prod.get("local_mockup_paths_json") or "[]")
        if not local_paths:
            _out(f"  ⚪ {title[:40]} — no local mockups, run sync first")
            skipped += 1
            continue

        # Build BKS handle from title
        handle = title.lower().replace(" ", "-").replace("/", "-")
        handle = "".join(c for c in handle if c.isalnum() or c == "-")[:40]
        out_dir = CATALOG_TARGET / col / handle
        out_dir.mkdir(parents=True, exist_ok=True)

        _out(f"  → {handle} ({len(local_paths)} mockups)")

        for idx, rel_path in enumerate(local_paths):
            src = ROOT / rel_path
            if not src.exists():
                _out(f"    ✗ missing: {rel_path}")
                errors += 1
                continue

            dest_name = f"{handle}_{idx+1:02d}.jpg"
            dest = out_dir / dest_name

            # Check for existing processed file (may be .png if transparent)
            existing = dest if dest.exists() else dest.with_suffix(".png")
            if existing.exists() and not dry_run:
                skipped += 1
                continue

            if dry_run:
                _out(f"    [DRY] {src.name} → {dest.relative_to(ROOT)}")
                skipped += 1
                continue

            if has_pil:
                saved_path = _process_image(src, dest, CATALOG_MAX_PX, CATALOG_QUALITY)
            else:
                import shutil
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                saved_path = dest

            if not saved_path:
                errors += 1
                continue

            dest = saved_path  # use actual saved path (may be .png)

            # Record in assets DB
            catalog_db.upsert_asset(
                db_path,
                product_handle=handle,
                asset_type="catalog_mockup",
                file_path=str(dest.relative_to(ROOT)),
                collection=col,
                variant=f"mockup_{idx+1:02d}",
                width=CATALOG_MAX_PX,
                meta={
                    "printify_product_id": pid,
                    "source_mockup": rel_path,
                    "no_text": True,
                    "no_creative_changes": True,
                    "source": "printify_original_mockup",
                },
            )

            if upload_to_shopify and shopify_id and idx == 0:
                alt = f"{title} — {col.replace('bks-', '').title()} collection"
                cdn_url = _shopify_upload_product_image(shopify_id, dest, alt)
                if cdn_url:
                    _out(f"    ✓ Shopify: {cdn_url[:60]}...")
                    catalog_db.upsert_asset(
                        db_path,
                        product_handle=handle,
                        asset_type="catalog_mockup",
                        file_path=str(dest.relative_to(ROOT)),
                        collection=col,
                        url=cdn_url,
                        variant=f"mockup_{idx+1:02d}",
                    )
                time.sleep(0.5)

            processed += 1

    return {"processed": processed, "skipped": skipped, "errors": errors}


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare BKS catalog images from Printify mockups")
    parser.add_argument("--collection", default="", help="Filter by collection handle")
    parser.add_argument("--upload-to-shopify", action="store_true",
                        help="Upload prepared images to Shopify product media")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    db_path = active_catalog_db()
    has_pil = _ensure_pil()

    if not has_pil:
        _out("⚠ Pillow not installed — images will be copied without resizing")
        _out("  Install: pip install Pillow")

    _out(f"=== BKS Catalog Image Preparation ({'DRY RUN' if args.dry_run else 'LIVE'}) ===")
    _out(f"  DB: {db_path.name}  |  Output: output/catalog_images/")

    lib_summary = catalog_db.printify_library_summary(db_path)
    if not lib_summary.get("ok") or lib_summary.get("products", 0) == 0:
        _out("✗ No Printify products in DB. Run sync_printify_library.py first.")
        sys.exit(1)

    collections: list[str] = []
    if args.collection:
        collections = [args.collection]
    else:
        by_col = lib_summary.get("by_collection") or {}
        collections = list(by_col.keys()) if by_col else [""]

    total = {"processed": 0, "skipped": 0, "errors": 0}
    for col in collections:
        _out(f"\n── {col or 'all'} ──────────────────────────────────")
        result = prepare_collection(db_path, col, args.dry_run,
                                    args.upload_to_shopify, has_pil)
        for k in total:
            total[k] += result[k]

    _out(f"\n=== DONE === processed={total['processed']} skipped={total['skipped']} errors={total['errors']}")
    _out(f"  Catalog images: {CATALOG_TARGET}")


if __name__ == "__main__":
    main()
