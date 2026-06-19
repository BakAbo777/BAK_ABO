"""sync_bks_database.py — Indicizza I:\\BKS database nella tabella assets di catalog_db.

Uso:
    python scripts/sync_bks_database.py                 # sincronizzazione incrementale
    python scripts/sync_bks_database.py --full          # reindicizza tutto (ignora timestamp)
    python scripts/sync_bks_database.py --dry-run       # mostra solo i conteggi
    python scripts/sync_bks_database.py --root "D:/altro/archivio"  # root alternativo
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bks_assets import active_catalog_db, bks_media_root, save_active_assets
from ecommerce_automation.catalog_db import upsert_asset, _ensure_assets_table, _get_meta, _set_meta

import sqlite3
from contextlib import closing
import json


# ── Mappatura directory → asset_type ──────────────────────────────────────────

DIR_TYPE_MAP: dict[str, str] = {
    "01_NFT": "nft",
    "02_IMMAGINI_AI": "ai_image",
    "03_BAKSITO_WEB_SHOPIFY": "shopify_web",
    "04_BAKSITO_ASSETS": "asset",
    "05_BAKABO_WEB_2017": "archive_web",
    "20_VIDEO_SOCIAL_FB_META": "video_social",
    "22_VIDEO_GENERICI": "video",
    "23_AUDIO_VOICEOVER": "audio_voiceover",
    "24_AUDIO_MUSIC_SOUNDTRACK": "audio_music",
    "25_AUDIO_GENERICI": "audio",
    "42_SHOPIFY_PATCHES_PEZZE": "mockup",
    "43_APP_VIDEO_MANIPOLAZIONE": "video_edit",
    "00_MANIFESTI": "manifest",
}

AVATAR_DIR_MAP: dict[str, str] = {
    "foto avatar": "avatar_photo",
    "video avatar": "avatar",
}

MEDIA_EXTENSIONS: frozenset[str] = frozenset({
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".tiff", ".tif", ".bmp", ".avif",
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v",
    ".mp3", ".wav", ".aac", ".m4a", ".flac", ".ogg",
    ".pdf", ".svg",
})

COLLECTION_MAP: dict[str, str] = {
    "bks_flag": "Flag",
    "bks_folklore": "Folklore",
    "bks_glyph": "Glyph",
    "bks_hours": "Hours",
    "bks_marker": "Marker",
    "bks_pulse": "Pulse",
    "bks_riviera": "Riviera",
    "bks_token": "Token",
}

_HANDLE_RE = re.compile(r"^(bks-[a-z0-9-]+?)(?:_mockup_\d+|_contact[_-]sheet.*|_social.*|_hero.*)?$")


def _extract_collection(parts: tuple[str, ...]) -> str:
    for part in parts:
        key = part.lower()
        if key in COLLECTION_MAP:
            return COLLECTION_MAP[key]
    return ""


def _extract_handle(stem: str) -> str:
    stem_lower = stem.lower()
    m = _HANDLE_RE.match(stem_lower)
    if m:
        return m.group(1)
    if stem_lower.startswith("bks-"):
        return stem_lower.split("_mockup_")[0].split("_contact")[0]
    return ""


def _extract_variant(parts: tuple[str, ...], asset_type: str) -> str:
    for part in parts:
        if part.lower() not in COLLECTION_MAP and part not in ("_Senza_collezione",):
            return part
    return ""


def _walk_organized(base: Path, organized_dir: Path, since_ts: float) -> list[dict]:
    records: list[dict] = []
    top = organized_dir.name  # e.g. BKS_ORGANIZED_20260615_225737

    for category_dir in organized_dir.iterdir():
        if not category_dir.is_dir():
            continue
        asset_type = DIR_TYPE_MAP.get(category_dir.name)
        if not asset_type:
            continue

        for file in category_dir.rglob("*"):
            if not file.is_file():
                continue
            if file.suffix.lower() not in MEDIA_EXTENSIONS:
                continue
            if file.stat().st_mtime <= since_ts:
                continue

            rel_parts = file.relative_to(category_dir).parts
            collection = _extract_collection(tuple(p.lower() for p in rel_parts))
            variant = _extract_variant(rel_parts[:-1], asset_type) if len(rel_parts) > 1 else ""
            handle = _extract_handle(file.stem)

            records.append({
                "product_handle": handle,
                "asset_type": asset_type,
                "collection": collection,
                "file_path": str(file),
                "variant": variant,
                "meta": {"source_dir": top, "category": category_dir.name},
            })

    return records


def _walk_avatar(avatar_dir: Path, since_ts: float) -> list[dict]:
    records: list[dict] = []
    for sub in avatar_dir.iterdir():
        if not sub.is_dir():
            continue
        asset_type = AVATAR_DIR_MAP.get(sub.name.lower(), "avatar_asset")
        for file in sub.rglob("*"):
            if not file.is_file():
                continue
            if file.suffix.lower() not in MEDIA_EXTENSIONS:
                continue
            if file.stat().st_mtime <= since_ts:
                continue
            handle = _extract_handle(file.stem)
            collection_guess = ""
            for coll in COLLECTION_MAP.values():
                if coll.lower() in file.name.lower():
                    collection_guess = coll
                    break
            records.append({
                "product_handle": handle,
                "asset_type": asset_type,
                "collection": collection_guess,
                "file_path": str(file),
                "variant": "",
                "meta": {"source_dir": "AVATAR"},
            })
    return records


def sync(media_root: Path, db_path: Path, *, full: bool = False, dry_run: bool = False) -> dict:
    since_ts: float = 0.0

    with closing(sqlite3.connect(db_path)) as conn:
        _ensure_assets_table(conn)
        if not full:
            meta = _get_meta(conn)
            since_str = meta.get("bks_database_sync_at", "")
            if since_str:
                try:
                    from datetime import timezone
                    since_ts = datetime.fromisoformat(since_str).timestamp()
                except Exception:
                    since_ts = 0.0

    records: list[dict] = []

    for entry in media_root.iterdir():
        if not entry.is_dir():
            continue
        if entry.name.startswith("BKS_ORGANIZED_"):
            records.extend(_walk_organized(media_root, entry, since_ts))
        elif entry.name == "AVATAR":
            records.extend(_walk_avatar(entry, since_ts))

    if dry_run:
        by_type: dict[str, int] = {}
        for r in records:
            by_type[r["asset_type"]] = by_type.get(r["asset_type"], 0) + 1
        return {"dry_run": True, "found": len(records), "by_type": by_type}

    inserted = 0
    updated = 0
    now = datetime.now().isoformat()

    with closing(sqlite3.connect(db_path)) as conn:
        _ensure_assets_table(conn)
        conn.execute("BEGIN")
        for r in records:
            existing = conn.execute(
                "SELECT id FROM assets WHERE file_path = ?", (r["file_path"],)
            ).fetchone()
            meta_json = json.dumps(r["meta"], ensure_ascii=False)
            if existing:
                conn.execute(
                    "UPDATE assets SET product_handle=?, asset_type=?, collection=?, variant=?, synced_at=?, meta_json=? WHERE id=?",
                    (r["product_handle"], r["asset_type"], r["collection"], r["variant"], now, meta_json, existing[0]),
                )
                updated += 1
            else:
                conn.execute(
                    "INSERT INTO assets (product_handle, asset_type, collection, file_path, variant, synced_at, meta_json) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (r["product_handle"], r["asset_type"], r["collection"], r["file_path"], r["variant"], now, meta_json),
                )
                inserted += 1
        _set_meta(conn, "bks_database_sync_at", now)
        _set_meta(conn, "bks_database_root", str(media_root))
        conn.commit()

    return {
        "ok": True,
        "inserted": inserted,
        "updated": updated,
        "total_processed": len(records),
        "media_root": str(media_root),
        "db": str(db_path),
        "synced_at": now,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync I:\\BKS database → catalog_db assets table")
    parser.add_argument("--root", type=Path, help="Media root override")
    parser.add_argument("--full", action="store_true", help="Full re-index (ignore last sync timestamp)")
    parser.add_argument("--dry-run", action="store_true", help="Count files without writing to DB")
    args = parser.parse_args()

    media_root = args.root or bks_media_root()
    if not media_root.exists():
        sys.exit(f"ERROR: media root not found: {media_root}")

    db_path = active_catalog_db()
    print(f"Media root : {media_root}")
    print(f"Database   : {db_path}")
    print(f"Mode       : {'DRY RUN' if args.dry_run else ('FULL' if args.full else 'INCREMENTAL')}")
    print()

    result = sync(media_root, db_path, full=args.full, dry_run=args.dry_run)

    if result.get("dry_run"):
        print(f"Files found: {result['found']}")
        for t, c in sorted(result["by_type"].items(), key=lambda x: -x[1]):
            print(f"  {t:25s} {c:5d}")
    else:
        print(f"Inserted : {result['inserted']}")
        print(f"Updated  : {result['updated']}")
        print(f"Total    : {result['total_processed']}")
        print(f"Synced at: {result['synced_at']}")

        # Salva il media_root in active_assets.json per le sessioni future
        save_active_assets(media_root=media_root)
        print(f"\nMedia root registrato in output/bks_active_assets.json")


if __name__ == "__main__":
    main()
