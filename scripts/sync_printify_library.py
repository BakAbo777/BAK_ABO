"""BKS Studio — Sync Printify Library to local DB + disk.

Downloads and catalogs:
  1. All uploaded artwork/textures  → output/printify_library/textures/
  2. Product blueprints (model info) → DB  (catalog/printify_blueprints)
  3. Product mockup images (originals, unchanged) → output/printify_library/mockups/{handle}/

Rules (immutable):
  - Mockup images are used AS-IS — zero creative modifications.
  - Artwork/texture files are sacred — never altered.
  - Shape and dimensions come from blueprint data only.
  - No text is added to any image at any stage.

Usage:
  python scripts/sync_printify_library.py
  python scripts/sync_printify_library.py --skip-download   # catalog only, skip file download
  python scripts/sync_printify_library.py --collection bks-hours
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
        _k = _k.strip()
        _v = _v.strip().strip('"').strip("'")
        if _k not in os.environ:
            os.environ[_k] = _v

from ecommerce_automation.services.printify_client import PrintifyClient
from ecommerce_automation import catalog_db
from bks_assets import active_catalog_db

PRINTIFY_SHOP_ID = "12030061"
LIB_DIR = ROOT / "output" / "printify_library"
TEXTURES_DIR = LIB_DIR / "textures"
MOCKUPS_DIR  = LIB_DIR / "mockups"

# BKS collection tags in Shopify → handle mapping
COLLECTION_TAG_MAP: dict[str, str] = {
    "bks-hours":   "collection:bks-hours",
    "bks-glyph":   "collection:bks-glyph",
    "bks-marker":  "collection:bks-marker",
    "bks-riviera": "collection:bks-riviera",
    "bks-pulse":   "collection:bks-pulse",
    "bks-token":   "collection:bks-token",
    "bks-flag":    "collection:bks-flag",
    "bks-origin":  "collection:bks-origin",
}


def _out(msg: str) -> None:
    sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
    sys.stdout.flush()


def _download(url: str, dest: Path, session: requests.Session) -> bool:
    """Download a file to dest. Returns True on success."""
    if dest.exists():
        return True
    try:
        r = session.get(url, timeout=60, verify=False, stream=True)
        r.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
        return True
    except Exception as exc:
        _out(f"    ✗ download error: {exc}")
        return False


_COLLECTION_NAMES = {
    "hours": "bks-hours", "glyph": "bks-glyph", "marker": "bks-marker",
    "riviera": "bks-riviera", "pulse": "bks-pulse", "token": "bks-token",
    "flag": "bks-flag", "origin": "bks-origin",
}


def _tag_to_collection(tags_str: str) -> str:
    """Extract BKS collection handle from tags (supports both collection:bks-hours and collection:hours)."""
    tags = [t.strip().lower() for t in (tags_str or "").split(",")]
    for col, tag in COLLECTION_TAG_MAP.items():
        if tag.lower() in tags:
            return col
    # fallback: collection:hours (without bks- prefix)
    for tag in tags:
        if tag.startswith("collection:"):
            name = tag[len("collection:"):]
            if name in _COLLECTION_NAMES:
                return _COLLECTION_NAMES[name]
            name_stripped = name.replace("bks-", "")
            if name_stripped in _COLLECTION_NAMES:
                return _COLLECTION_NAMES[name_stripped]
    return ""


_TITLE_ALIASES = {"folklore": "bks-origin"}


def _title_to_collection(title: str) -> str:
    """Derive BKS collection from product title (e.g. 'BKS Hours ...' → 'bks-hours')."""
    title_lower = title.lower()
    # aliases first (e.g. Folklore → Origin)
    for alias, handle in _TITLE_ALIASES.items():
        if alias in title_lower:
            return handle
    # standard: "BKS Hours" or "BKS-Hours" prefix
    for name, handle in _COLLECTION_NAMES.items():
        if f"bks {name}" in title_lower or f"bks-{name}" in title_lower:
            return handle
    # fallback: just the collection name anywhere in title (e.g. "Pulse Grid Travel Bag")
    for name, handle in _COLLECTION_NAMES.items():
        if name in title_lower:
            return handle
    return ""


def _extract_upload_ids(product: dict) -> list[str]:
    """Extract all artwork/upload IDs referenced in a Printify product."""
    ids: set[str] = set()
    for area in (product.get("print_areas") or []):
        for layer in (area.get("layers") or []):
            img_id = layer.get("image_id") or layer.get("id") or ""
            if img_id:
                ids.add(str(img_id))
    # also check images array for src that look like upload IDs
    for img in (product.get("images") or []):
        vid = img.get("variant_ids") or []
        # images in product.images are mockup renders, not upload IDs
        _ = vid  # not upload IDs
    return sorted(ids)


def sync_uploads(client: PrintifyClient, db_path: Path, session: requests.Session,
                 skip_download: bool) -> int:
    _out("\n=== Phase 1: Uploaded textures/artwork ===")
    uploads = client.iter_uploads()
    _out(f"  Found {len(uploads)} uploads in Printify account")

    TEXTURES_DIR.mkdir(parents=True, exist_ok=True)
    saved = 0
    for u in uploads:
        pid = str(u.get("id") or "")
        if not pid:
            continue
        filename = u.get("file_name") or u.get("filename") or f"{pid}.png"
        url = u.get("preview_url") or u.get("url") or ""
        width = u.get("width")
        height = u.get("height")
        file_size = u.get("size") or u.get("file_size")
        mime_type = u.get("mime_type") or ""
        upload_time = str(u.get("upload_time") or "")

        local_path = ""
        if not skip_download and url:
            dest = TEXTURES_DIR / f"{pid}_{filename}"
            ok = _download(url, dest, session)
            if ok:
                local_path = str(dest.relative_to(ROOT))

        catalog_db.upsert_printify_upload(
            db_path,
            printify_id=pid,
            filename=filename,
            url=url,
            local_path=local_path,
            width=int(width) if width else None,
            height=int(height) if height else None,
            file_size=int(file_size) if file_size else None,
            mime_type=mime_type,
            upload_time=upload_time,
        )
        saved += 1

    _out(f"  ✓ {saved} uploads cataloged")
    return saved


def sync_products(client: PrintifyClient, db_path: Path, session: requests.Session,
                  skip_download: bool, collection_filter: str) -> tuple[int, set[int]]:
    _out("\n=== Phase 2: Products + mockup images ===")
    products = client.iter_products(PRINTIFY_SHOP_ID)
    _out(f"  Found {len(products)} products in shop {PRINTIFY_SHOP_ID}")

    blueprint_ids: set[int] = set()
    saved = 0

    for p in products:
        pid = str(p.get("id") or "")
        title = p.get("title") or ""
        blueprint_id = int(p.get("blueprint_id") or 0)
        print_provider_id = int(p.get("print_provider_id") or 0)

        # Shopify product ID from external field
        external = p.get("external") or {}
        shopify_id = str(external.get("id") or "")

        # Derive collection from tags, fallback to title
        tags_str = p.get("tags") or ""
        if isinstance(tags_str, list):
            tags_str = ", ".join(str(t) for t in tags_str)
        collection = _tag_to_collection(tags_str) or _title_to_collection(title)

        if collection_filter and collection != collection_filter:
            continue

        if blueprint_id:
            blueprint_ids.add(blueprint_id)

        upload_ids = _extract_upload_ids(p)

        # Mockup images: product.images[] with is_default=True first
        raw_images = p.get("images") or []
        mockup_urls = [img.get("src") for img in raw_images if img.get("src")]

        local_mockup_paths: list[str] = []
        if not skip_download and mockup_urls:
            import re as _re
            handle = _re.sub(r'[\\/:*?"<>|]', "", title.lower()).replace(" ", "-")[:40].strip("-")
            mockup_dir = MOCKUPS_DIR / (collection or "uncategorized") / handle
            mockup_dir.mkdir(parents=True, exist_ok=True)
            for idx, url in enumerate(mockup_urls[:5]):  # first 5 mockups per product
                ext = url.split("?")[0].rsplit(".", 1)[-1] or "png"
                dest = mockup_dir / f"mockup_{idx+1:02d}.{ext}"
                ok = _download(url, dest, session)
                if ok:
                    local_mockup_paths.append(str(dest.relative_to(ROOT)))
                time.sleep(0.1)

        catalog_db.upsert_printify_product(
            db_path,
            printify_product_id=pid,
            shopify_product_id=shopify_id,
            title=title,
            blueprint_id=blueprint_id or None,
            print_provider_id=print_provider_id or None,
            collection=collection,
            upload_ids=upload_ids,
            mockup_urls=mockup_urls,
            local_mockup_paths=local_mockup_paths,
            meta={
                "tags": tags_str,
                "visible": p.get("visible"),
                "variants_count": len(p.get("variants") or []),
            },
        )
        saved += 1

    _out(f"  ✓ {saved} products cataloged, {len(blueprint_ids)} unique blueprints to fetch")
    return saved, blueprint_ids


def sync_blueprints(client: PrintifyClient, db_path: Path, blueprint_ids: set[int]) -> int:
    _out("\n=== Phase 3: Blueprints (product models) ===")
    saved = 0
    for bp_id in sorted(blueprint_ids):
        try:
            bp = client.get_blueprint(bp_id)
            catalog_db.upsert_printify_blueprint(
                db_path,
                blueprint_id=bp_id,
                title=bp.get("title") or "",
                brand=bp.get("brand") or "",
                model=bp.get("model") or "",
                description=bp.get("description") or "",
                images=[img.get("src") for img in (bp.get("images") or []) if img.get("src")],
                meta={"variants_count": len(bp.get("variants") or [])},
            )
            saved += 1
            _out(f"  ✓ blueprint {bp_id}: {bp.get('brand')} {bp.get('model')}")
            time.sleep(0.3)
        except Exception as exc:
            _out(f"  ✗ blueprint {bp_id}: {exc}")
    return saved


def backfill_collections(db_path: Path) -> int:
    """Update existing DB products with empty collection using title-based detection."""
    import sqlite3
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT id, title FROM printify_products WHERE collection IS NULL OR collection = ''"
    ).fetchall()
    updated = 0
    for row_id, title in rows:
        col = _title_to_collection(title or "")
        if col:
            conn.execute("UPDATE printify_products SET collection = ? WHERE id = ?", (col, row_id))
            updated += 1
    conn.commit()
    conn.close()
    return updated


def print_summary(db_path: Path) -> None:
    summary = catalog_db.printify_library_summary(db_path)
    _out("\n── Library Summary ──────────────────────────────")
    _out(f"  Uploads (textures):     {summary['uploads']} total, {summary['uploads_downloaded']} downloaded")
    _out(f"  Blueprints (models):    {summary['blueprints']}")
    _out(f"  Products:               {summary['products']} total, {summary['products_with_mockups']} with mockups")
    if summary.get("by_collection"):
        _out("  By collection:")
        for col, count in summary["by_collection"].items():
            _out(f"    {col}: {count}")
    _out(f"\n  Library dir: {LIB_DIR}")
    _out(f"  DB: {db_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync Printify library to local DB + disk")
    parser.add_argument("--skip-download", action="store_true",
                        help="Only catalog metadata, skip downloading files")
    parser.add_argument("--collection", default="",
                        help="Filter by BKS collection handle (e.g. bks-hours)")
    parser.add_argument("--uploads-only", action="store_true",
                        help="Only sync uploaded textures, skip products+blueprints")
    parser.add_argument("--products-only", action="store_true",
                        help="Only sync products+blueprints, skip uploads")
    args = parser.parse_args()

    token = os.environ.get("PRINTIFY_API_TOKEN", "")
    if not token:
        _out("✗ PRINTIFY_API_TOKEN not set")
        sys.exit(1)

    db_path = active_catalog_db()
    client = PrintifyClient(token=token, shop_id=PRINTIFY_SHOP_ID)
    session = requests.Session()
    session.verify = False

    _out(f"=== BKS Printify Library Sync ({'catalog only' if args.skip_download else 'download + catalog'}) ===")
    _out(f"  Shop: {PRINTIFY_SHOP_ID}  |  DB: {db_path.name}")

    blueprint_ids: set[int] = set()

    if not args.products_only:
        sync_uploads(client, db_path, session, args.skip_download)

    if not args.uploads_only:
        _, blueprint_ids = sync_products(client, db_path, session,
                                         args.skip_download, args.collection)
        sync_blueprints(client, db_path, blueprint_ids)

    # Cross-reference: tag each patch with the collections where it's used
    _out("\n=== Phase 4: Patch → collection cross-reference ===")
    xref = catalog_db.sync_upload_collections(db_path)
    if xref.get("ok"):
        _out(f"  ✓ {xref['updated']} patches tagged with collection(s)  "
             f"(from {xref['upload_ids_found']} upload refs in products)")
    else:
        _out("  ⚪ cross-reference skipped (no products with upload refs)")

    # Backfill collections for products with empty collection field
    _out("\n=== Phase 5: Backfill collections from titles ===")
    n = backfill_collections(db_path)
    _out(f"  ✓ {n} products updated with collection from title")

    print_summary(db_path)
    _out("\n=== DONE ===")


if __name__ == "__main__":
    main()
