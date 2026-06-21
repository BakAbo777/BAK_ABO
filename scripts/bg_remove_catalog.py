"""BKS Studio — Background Removal Pipeline per tema editoriale.

Rimuove lo sfondo dai mockup Printify per uso editoriale (magazine, hero, collection page).

Fonte immagini:
  1. Prima cerca mockup già scaricati: output/printify_library/mockups/{handle}/
  2. Se non trovati, li scarica direttamente dall'API Printify (shop 12030061)

Output:
  output/catalog_images/editorial/{handle}/{handle}_01_cutout.png  (PNG trasparente)
  output/catalog_images/editorial/{handle}/{handle}_01_white.jpg   (JPEG sfondo bianco)

DB:
  assets table — asset_type='editorial_cutout'

Usage:
  python scripts/bg_remove_catalog.py                         # tutti i prodotti
  python scripts/bg_remove_catalog.py --collection bks-hours  # solo una collezione
  python scripts/bg_remove_catalog.py --limit 20              # prime N (test)
  python scripts/bg_remove_catalog.py --dry-run               # solo scan, nessun download/processing
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings()  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# ── env ──────────────────────────────────────────────────────────────────────
_env = ROOT / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        _k = _k.strip()
        if _k not in os.environ:
            os.environ[_k] = _v.strip().strip('"').strip("'")

PTOKEN    = os.environ.get("PRINTIFY_API_TOKEN", "")
SHOP_ID   = "12030061"
EDITORIAL_DIR = ROOT / "output" / "catalog_images" / "editorial"
MOCKUPS_DIR   = ROOT / "output" / "printify_library" / "mockups"

BKS_COLLECTIONS = {
    "bks-hours": "collection:bks-hours",
    "bks-glyph": "collection:bks-glyph",
    "bks-marker": "collection:bks-marker",
    "bks-riviera": "collection:bks-riviera",
    "bks-pulse": "collection:bks-pulse",
    "bks-token": "collection:bks-token",
    "bks-flag": "collection:bks-flag",
    "bks-origin": "collection:bks-origin",
}


def _out(msg: str) -> None:
    sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
    sys.stdout.flush()


def _detect_collection(tags: list[str] | str) -> str:
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]
    for tag in tags:
        t = tag.lower().strip()
        for coll_handle in BKS_COLLECTIONS:
            if coll_handle in t:
                return coll_handle
    return ""


def _detect_collection_from_title(title: str) -> str:
    """Fallback: detect collection from product title."""
    t = title.lower()
    for coll_handle in BKS_COLLECTIONS:
        keyword = coll_handle.replace("bks-", "")  # e.g. "hours", "glyph"
        if keyword in t:
            return coll_handle
    return "uncategorized"


def fetch_printify_products(collection_filter: str | None, limit: int | None) -> list[dict]:
    """Fetch all products from Printify shop 12030061."""
    hdr  = {"Authorization": f"Bearer {PTOKEN}"}
    page = 1
    all_products: list[dict] = []
    _out(f"Fetching Printify products (shop {SHOP_ID})...")
    while True:
        r = requests.get(
            f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json?limit=50&page={page}",
            headers=hdr, verify=False, timeout=30
        )
        if not r.ok:
            _out(f"  Printify API error {r.status_code}: {r.text[:200]}")
            break
        data = r.json()
        items = data.get("data", [])
        if not items:
            break
        for p in items:
            ext = p.get("external", {})
            if not ext.get("id"):
                continue  # not synced to Shopify
            # Extract handle from Shopify URL or direct handle field
            raw_handle = ext.get("handle", "")
            if "/products/" in raw_handle:
                raw_handle = raw_handle.split("/products/")[-1].split("?")[0]
            # Also try title to detect collection if tags empty
            tags = p.get("tags", [])
            title = p.get("title", "")
            coll = _detect_collection(tags)
            if not coll:
                coll = _detect_collection_from_title(title)
            if collection_filter and coll != collection_filter:
                continue
            images = [img.get("src", "") for img in p.get("images", []) if img.get("src")]
            all_products.append({
                "printify_id": p["id"],
                "title": title,
                "handle": raw_handle,
                "shopify_id": ext.get("id", ""),
                "collection": coll,
                "images": images[:3],  # max 3 mockup images
            })
        _out(f"  Page {page}: {len(items)} products fetched (total so far: {len(all_products)})")
        if len(items) < 100:
            break
        page += 1
        time.sleep(0.4)
        if limit and len(all_products) >= limit:
            break
    if limit:
        all_products = all_products[:limit]
    _out(f"Total products to process: {len(all_products)}")
    return all_products


def find_local_mockup(handle: str) -> Path | None:
    """Find first downloaded mockup in output/printify_library/mockups/{handle}/"""
    if not handle:
        return None
    d = MOCKUPS_DIR / handle
    if d.exists():
        imgs = sorted(d.glob("*.jpg")) + sorted(d.glob("*.png")) + sorted(d.glob("*.webp"))
        if imgs:
            return imgs[0]
    return None


def download_image(url: str, session: requests.Session) -> bytes | None:
    try:
        r = session.get(url, timeout=30, verify=False, stream=True)
        r.raise_for_status()
        return r.content
    except Exception as e:
        _out(f"    Download error: {e}")
        return None


def remove_bg(img_bytes: bytes) -> bytes | None:
    """Remove background using rembg. Returns PNG bytes or None on error."""
    try:
        from rembg import remove as rembg_remove
        from PIL import Image
        result = rembg_remove(img_bytes)
        return result
    except Exception as e:
        _out(f"    rembg error: {e}")
        return None


def compose_white_bg(png_bytes: bytes, size: int = 1200) -> bytes | None:
    """Compose cutout on white background, return JPEG bytes."""
    try:
        from PIL import Image
        img = Image.open(BytesIO(png_bytes)).convert("RGBA")
        # Resize
        img.thumbnail((size, size), Image.LANCZOS)
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        out = BytesIO()
        bg.convert("RGB").save(out, format="JPEG", quality=92, optimize=True)
        return out.getvalue()
    except Exception as e:
        _out(f"    Compose error: {e}")
        return None


def register_in_db(
    handle: str, collection: str,
    cutout_path: str, white_path: str,
    w: int, h: int, size_bytes: int
) -> None:
    try:
        from ecommerce_automation import catalog_db
        from bks_assets import active_catalog_db
        db_path = active_catalog_db()
        if not db_path:
            return
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            now = datetime.utcnow().isoformat()
            conn.execute(
                """INSERT OR REPLACE INTO assets
                   (product_handle, asset_type, collection, file_path, url,
                    width, height, file_size, variant, created_at, synced_at, meta_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (handle, "editorial_cutout", collection, cutout_path, "",
                 w, h, size_bytes, "cutout_png", now, now,
                 json.dumps({"white_bg_path": white_path}))
            )
            conn.commit()
    except Exception as e:
        _out(f"    DB error: {e}")


def already_done(handle: str) -> bool:
    out_dir = EDITORIAL_DIR / handle
    cutout = out_dir / f"{handle}_01_cutout.png"
    return cutout.exists()


def process_product(p: dict, session: requests.Session, dry_run: bool, force: bool) -> str:
    handle     = p["handle"] or p["printify_id"]
    collection = p["collection"]
    images     = p["images"]

    if not force and already_done(handle):
        return "skip"

    if dry_run:
        local = find_local_mockup(handle)
        src   = "local" if local else ("api" if images else "no-image")
        _out(f"  DRY  [{collection:12s}] {handle[:50]:50s}  src={src}")
        return "dry"

    # Get image bytes
    img_bytes: bytes | None = None
    local = find_local_mockup(handle)
    if local:
        img_bytes = local.read_bytes()
        _out(f"  ◎    [{collection:12s}] {handle[:50]:50s}  (local mockup)")
    elif images:
        img_bytes = download_image(images[0], session)
        _out(f"  ↓    [{collection:12s}] {handle[:50]:50s}  (download from Printify)")
    else:
        _out(f"  SKIP [{collection:12s}] {handle[:50]:50s}  (no image source)")
        return "no-image"

    if not img_bytes:
        return "error"

    # Remove background
    png_bytes = remove_bg(img_bytes)
    if not png_bytes:
        return "error"

    # Compose white background version
    white_bytes = compose_white_bg(png_bytes)

    # Save output
    out_dir = EDITORIAL_DIR / handle
    out_dir.mkdir(parents=True, exist_ok=True)
    cutout_path = out_dir / f"{handle}_01_cutout.png"
    white_path  = out_dir / f"{handle}_01_white.jpg"
    cutout_path.write_bytes(png_bytes)
    if white_bytes:
        white_path.write_bytes(white_bytes)

    # Get dimensions
    try:
        from PIL import Image
        with Image.open(BytesIO(png_bytes)) as im:
            w, h = im.size
    except Exception:
        w, h = 0, 0

    # Register in DB
    register_in_db(
        handle, collection,
        str(cutout_path), str(white_path) if white_bytes else "",
        w, h, len(png_bytes)
    )

    _out(f"  ✓    [{collection:12s}] {handle[:50]:50s}  {w}×{h}px  {len(png_bytes)//1024}KB")
    return "ok"


def main() -> None:
    parser = argparse.ArgumentParser(description="BKS Editorial Background Removal Pipeline")
    parser.add_argument("--collection", help="Filter by BKS collection (e.g. bks-hours)")
    parser.add_argument("--limit", type=int, help="Process only first N products")
    parser.add_argument("--dry-run", action="store_true", help="Scan only, no processing")
    parser.add_argument("--force", action="store_true", help="Reprocess even if cutout exists")
    args = parser.parse_args()

    _out("=" * 60)
    _out("BKS Editorial Background Removal Pipeline")
    _out(f"Collection filter : {args.collection or 'ALL'}")
    _out(f"Limit             : {args.limit or 'none'}")
    _out(f"Mode              : {'DRY RUN' if args.dry_run else 'PROCESS'}")
    _out("=" * 60)

    EDITORIAL_DIR.mkdir(parents=True, exist_ok=True)

    products = fetch_printify_products(args.collection, args.limit)

    session = requests.Session()
    session.headers.update({"User-Agent": "BKS-Studio/1.0"})

    stats = {"ok": 0, "skip": 0, "error": 0, "dry": 0, "no_image": 0}

    for i, p in enumerate(products, 1):
        _out(f"\n[{i}/{len(products)}]")
        result = process_product(p, session, args.dry_run, args.force)
        if result == "ok":
            stats["ok"] += 1
        elif result == "skip":
            stats["skip"] += 1
        elif result == "error":
            stats["error"] += 1
        elif result == "dry":
            stats["dry"] += 1
        elif result == "no-image":
            stats["no_image"] += 1
        time.sleep(0.1)

    _out("\n" + "=" * 60)
    _out("RISULTATO PIPELINE EDITORIAL CUTOUT")
    _out(f"  Processati (OK)   : {stats['ok']}")
    _out(f"  Già esistenti     : {stats['skip']}")
    _out(f"  Errori            : {stats['error']}")
    _out(f"  Senza immagine    : {stats['no_image']}")
    if args.dry_run:
        _out(f"  Scansionati (dry) : {stats['dry']}")
    _out(f"\nOutput: {EDITORIAL_DIR}")
    _out("=" * 60)


if __name__ == "__main__":
    main()
