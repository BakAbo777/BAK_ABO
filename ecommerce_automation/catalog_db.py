from __future__ import annotations

import csv
import json
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import Any


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS catalog_meta (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS rows (
    row_index INTEGER PRIMARY KEY,
    handle TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    product_type TEXT NOT NULL DEFAULT '',
    collection TEXT NOT NULL DEFAULT '',
    series TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '',
    image_src TEXT NOT NULL DEFAULT '',
    image_position TEXT NOT NULL DEFAULT '',
    image_alt TEXT NOT NULL DEFAULT '',
    variant_sku TEXT NOT NULL DEFAULT '',
    variant_price REAL,
    variant_compare_at_price REAL,
    seo_title TEXT NOT NULL DEFAULT '',
    seo_description TEXT NOT NULL DEFAULT '',
    is_product_row INTEGER NOT NULL DEFAULT 0,
    raw_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_rows_handle ON rows(handle);
CREATE INDEX IF NOT EXISTS idx_rows_collection ON rows(collection);

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_handle TEXT NOT NULL DEFAULT '',
    asset_type TEXT NOT NULL DEFAULT '',
    collection TEXT NOT NULL DEFAULT '',
    file_path TEXT NOT NULL,
    url TEXT NOT NULL DEFAULT '',
    width INTEGER,
    height INTEGER,
    file_size INTEGER,
    variant TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT '',
    synced_at TEXT NOT NULL DEFAULT '',
    meta_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_assets_handle ON assets(product_handle);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_assets_collection ON assets(collection);

CREATE TABLE IF NOT EXISTS rejected_assets (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path        TEXT,
    shopify_url      TEXT,
    shopify_filename TEXT,
    collection       TEXT,
    reason           TEXT,
    defect_type      TEXT,
    notes            TEXT,
    reported_at      TEXT
);
CREATE INDEX IF NOT EXISTS idx_rejected_collection ON rejected_assets(collection);
CREATE INDEX IF NOT EXISTS idx_rejected_defect ON rejected_assets(defect_type);
"""


def _split_tags(value: str) -> list[str]:
    return [tag.strip() for tag in (value or "").split(",") if tag.strip()]


def _tag_value(tags: list[str], prefix: str) -> str:
    prefix_l = prefix.lower()
    for tag in tags:
        if tag.lower().startswith(prefix_l):
            return tag.split(":", 1)[1].strip()
    return ""


def _to_float(value: str) -> float | None:
    try:
        return float(value) if (value or "").strip() else None
    except ValueError:
        return None


def _set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO catalog_meta (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def _get_meta(conn: sqlite3.Connection) -> dict[str, str]:
    return dict(conn.execute("SELECT key, value FROM catalog_meta").fetchall())


def migrate_rows(rows: list[dict[str, str]], fieldnames: list[str], db_path: Path, *, source: str = "") -> dict[str, Any]:
    """Sostituisce il contenuto del DB con `rows` in una singola transazione.

    Ogni riga viene salvata sia come colonne tipizzate (per query agili) sia come
    `raw_json` integrale (per export CSV lossless senza dover ri-mappare 115 colonne).
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as conn:
        try:
            conn.execute("BEGIN")
            conn.executescript(SCHEMA_SQL)
            conn.execute("DELETE FROM rows")
            for idx, row in enumerate(rows):
                tags = _split_tags(row.get("Tags", ""))
                handle = (row.get("Handle") or "").strip()
                title = (row.get("Title") or "").strip()
                conn.execute(
                    """INSERT INTO rows (
                        row_index, handle, title, product_type, collection, series, status, tags,
                        image_src, image_position, image_alt, variant_sku, variant_price,
                        variant_compare_at_price, seo_title, seo_description, is_product_row, raw_json
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        idx,
                        handle,
                        title,
                        (row.get("Type") or "").strip(),
                        _tag_value(tags, "collection:"),
                        _tag_value(tags, "series:"),
                        (row.get("Status") or "").strip(),
                        row.get("Tags") or "",
                        (row.get("Image Src") or "").strip(),
                        (row.get("Image Position") or "").strip(),
                        (row.get("Image Alt Text") or "").strip(),
                        (row.get("Variant SKU") or "").strip(),
                        _to_float(row.get("Variant Price") or ""),
                        _to_float(row.get("Variant Compare At Price") or ""),
                        (row.get("SEO Title") or "").strip(),
                        (row.get("SEO Description") or "").strip(),
                        1 if title else 0,
                        json.dumps(row, ensure_ascii=False),
                    ),
                )
            _set_meta(conn, "fieldnames", json.dumps(fieldnames, ensure_ascii=False))
            _set_meta(conn, "source", source)
            _set_meta(conn, "generated_at", datetime.now().isoformat())
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    handles = {(row.get("Handle") or "").strip() for row in rows if (row.get("Handle") or "").strip()}
    return {"rows": len(rows), "handles": len(handles)}


def migrate_from_csv(csv_path: Path, db_path: Path) -> dict[str, Any]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, restval="")
        if not reader.fieldnames:
            raise ValueError(f"CSV senza header: {csv_path}")
        fieldnames = reader.fieldnames
        # Righe-fantasma con tag HTML nell'Handle sono frammenti del blocco di
        # compliance GPSR/Printify senza virgolette CSV a monte: non sono prodotti.
        rows = [row for row in reader if "<" not in (row.get("Handle") or "")]
    return migrate_from_rows(rows, fieldnames, db_path, source=csv_path.name)


def migrate_from_rows(rows: list[dict[str, str]], fieldnames: list[str], db_path: Path, *, source: str = "") -> dict[str, Any]:
    return migrate_rows(rows, fieldnames, db_path, source=source)


def export_csv_for_shopify(db_path: Path, output_path: Path) -> int:
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        meta = _get_meta(conn)
        fieldnames = json.loads(meta.get("fieldnames", "[]"))
        if not fieldnames:
            raise ValueError(f"Nessun fieldnames salvato nel DB: {db_path}")
        cursor = conn.execute("SELECT raw_json FROM rows ORDER BY row_index")
        out_rows = [json.loads(record["raw_json"]) for record in cursor.fetchall()]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as dest:
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)
    return len(out_rows)


def meta(db_path: Path) -> dict[str, str]:
    if not db_path.exists():
        return {}
    with closing(sqlite3.connect(db_path)) as conn:
        return _get_meta(conn)


def fetch_all_rows(db_path: Path) -> list[dict[str, str]]:
    """Ritorna le righe originali (decodificate da raw_json) nell'ordine del CSV."""
    if not db_path.exists():
        return []
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.execute("SELECT raw_json FROM rows ORDER BY row_index")
        return [json.loads(record[0]) for record in cursor.fetchall()]


def fetch_products(db_path: Path, *, collection: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
    if not db_path.exists():
        return []
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        query = "SELECT * FROM rows WHERE is_product_row = 1"
        params: list[Any] = []
        if collection:
            query += " AND collection = ?"
            params.append(collection)
        query += " ORDER BY row_index"
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        cursor = conn.execute(query, params)
        return [dict(record) for record in cursor.fetchall()]


def summary(db_path: Path) -> dict[str, Any]:
    if not db_path.exists():
        return {"ok": False, "rows": 0, "products": 0, "handles": 0, "error": f"DB non trovato: {db_path}"}
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        total_rows = conn.execute("SELECT COUNT(*) AS c FROM rows").fetchone()["c"]
        products = conn.execute("SELECT COUNT(*) AS c FROM rows WHERE is_product_row = 1").fetchone()["c"]
        handles = conn.execute("SELECT COUNT(DISTINCT handle) AS c FROM rows WHERE handle != ''").fetchone()["c"]
        image_rows = conn.execute("SELECT COUNT(*) AS c FROM rows WHERE image_src != ''").fetchone()["c"]
        missing_seo_title = conn.execute(
            "SELECT COUNT(*) AS c FROM rows WHERE is_product_row = 1 AND seo_title = ''"
        ).fetchone()["c"]
        missing_seo_description = conn.execute(
            "SELECT COUNT(*) AS c FROM rows WHERE is_product_row = 1 AND seo_description = ''"
        ).fetchone()["c"]
        missing_alt = conn.execute(
            "SELECT COUNT(*) AS c FROM rows WHERE image_src != '' AND image_alt = ''"
        ).fetchone()["c"]
        by_collection = conn.execute(
            "SELECT collection, COUNT(*) AS c FROM rows WHERE is_product_row = 1 GROUP BY collection ORDER BY c DESC"
        ).fetchall()
        by_type = conn.execute(
            "SELECT product_type, COUNT(*) AS c FROM rows WHERE is_product_row = 1 GROUP BY product_type ORDER BY c DESC LIMIT 12"
        ).fetchall()
        meta = _get_meta(conn)
    return {
        "ok": True,
        "rows": total_rows,
        "products": products,
        "handles": handles,
        "image_rows": image_rows,
        "missing_seo_title": missing_seo_title,
        "missing_seo_description": missing_seo_description,
        "missing_alt": missing_alt,
        "by_collection": {(record["collection"] or "unassigned"): record["c"] for record in by_collection},
        "types": {(record["product_type"] or "Unspecified"): record["c"] for record in by_type},
        "generated_at": meta.get("generated_at", ""),
        "source": meta.get("source", ""),
        "db_file": str(db_path),
    }


def _ensure_assets_table(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_handle TEXT NOT NULL DEFAULT '',
            asset_type TEXT NOT NULL DEFAULT '',
            collection TEXT NOT NULL DEFAULT '',
            file_path TEXT NOT NULL,
            url TEXT NOT NULL DEFAULT '',
            width INTEGER,
            height INTEGER,
            file_size INTEGER,
            variant TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT '',
            synced_at TEXT NOT NULL DEFAULT '',
            meta_json TEXT NOT NULL DEFAULT '{}'
        );
        CREATE INDEX IF NOT EXISTS idx_assets_handle ON assets(product_handle);
        CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(asset_type);
        CREATE INDEX IF NOT EXISTS idx_assets_collection ON assets(collection);
        """
    )


def sync_cutout_manifest(db_path: Path, manifest_path: Path) -> dict[str, Any]:
    """Importa cutout_manifest.csv (output della printify_cutout_pipeline) nella tabella assets.

    Ogni riga del manifest diventa un asset di tipo 'cutout' o 'overlay'.
    Usa product_handle come chiave idempotente: righe già presenti vengono
    aggiornate, non duplicate.
    """
    if not manifest_path.exists():
        return {"ok": False, "error": f"manifest non trovato: {manifest_path}"}
    with manifest_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        return {"ok": True, "inserted": 0, "updated": 0}

    now = datetime.now().isoformat()
    inserted = 0
    updated = 0
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as conn:
        _ensure_assets_table(conn)
        conn.execute("BEGIN")
        for row in rows:
            handle = (row.get("product_handle") or row.get("handle") or "").strip()
            file_path = (row.get("file_path") or row.get("path") or "").strip()
            if not file_path:
                continue
            asset_type = (row.get("asset_type") or ("cutout" if "cutout" in file_path.lower() else "source")).strip()
            collection = (row.get("collection") or "").strip()
            variant = (row.get("variant") or row.get("background") or "").strip()
            url = (row.get("url") or "").strip()
            meta = json.dumps({k: v for k, v in row.items() if k not in (
                "product_handle", "handle", "file_path", "path", "asset_type",
                "collection", "variant", "background", "url",
            )}, ensure_ascii=False)
            existing = conn.execute(
                "SELECT id FROM assets WHERE product_handle = ? AND file_path = ?",
                (handle, file_path),
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE assets SET asset_type=?, collection=?, variant=?, url=?, synced_at=?, meta_json=? WHERE id=?",
                    (asset_type, collection, variant, url, now, meta, existing[0]),
                )
                updated += 1
            else:
                conn.execute(
                    "INSERT INTO assets (product_handle, asset_type, collection, file_path, url, variant, synced_at, meta_json) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (handle, asset_type, collection, file_path, url, variant, now, meta),
                )
                inserted += 1
        conn.commit()
    return {"ok": True, "inserted": inserted, "updated": updated, "total": len(rows)}


def upsert_asset(
    db_path: Path,
    *,
    product_handle: str,
    asset_type: str,
    file_path: str,
    collection: str = "",
    url: str = "",
    variant: str = "",
    width: int | None = None,
    height: int | None = None,
    file_size: int | None = None,
    meta: dict | None = None,
) -> int:
    """Inserisce o aggiorna un singolo asset. Ritorna l'id della riga."""
    now = datetime.now().isoformat()
    meta_json = json.dumps(meta or {}, ensure_ascii=False)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as conn:
        _ensure_assets_table(conn)
        existing = conn.execute(
            "SELECT id FROM assets WHERE product_handle = ? AND file_path = ?",
            (product_handle, file_path),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE assets SET asset_type=?, collection=?, url=?, variant=?, "
                "width=?, height=?, file_size=?, synced_at=?, meta_json=? WHERE id=?",
                (asset_type, collection, url, variant, width, height, file_size, now, meta_json, existing[0]),
            )
            conn.commit()
            return existing[0]
        cursor = conn.execute(
            "INSERT INTO assets (product_handle, asset_type, collection, file_path, url, variant, "
            "width, height, file_size, created_at, synced_at, meta_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (product_handle, asset_type, collection, file_path, url, variant,
             width, height, file_size, now, now, meta_json),
        )
        conn.commit()
        return cursor.lastrowid


def list_assets(
    db_path: Path,
    *,
    asset_type: str | None = None,
    collection: str | None = None,
    product_handle: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    if not db_path.exists():
        return []
    with closing(sqlite3.connect(db_path)) as conn:
        _ensure_assets_table(conn)
        conn.row_factory = sqlite3.Row
        query = "SELECT * FROM assets WHERE 1=1"
        params: list[Any] = []
        if asset_type:
            query += " AND asset_type = ?"
            params.append(asset_type)
        if collection:
            query += " AND collection = ?"
            params.append(collection)
        if product_handle:
            query += " AND product_handle = ?"
            params.append(product_handle)
        query += " ORDER BY id DESC"
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        return [dict(r) for r in conn.execute(query, params).fetchall()]


def assets_summary(db_path: Path) -> dict[str, Any]:
    if not db_path.exists():
        return {"ok": False, "total": 0}
    with closing(sqlite3.connect(db_path)) as conn:
        _ensure_assets_table(conn)
        conn.row_factory = sqlite3.Row
        total = conn.execute("SELECT COUNT(*) AS c FROM assets").fetchone()["c"]
        by_type = conn.execute(
            "SELECT asset_type, COUNT(*) AS c FROM assets GROUP BY asset_type ORDER BY c DESC"
        ).fetchall()
        by_collection = conn.execute(
            "SELECT collection, COUNT(*) AS c FROM assets WHERE collection != '' GROUP BY collection ORDER BY c DESC"
        ).fetchall()
    return {
        "ok": True,
        "total": total,
        "by_type": {r["asset_type"]: r["c"] for r in by_type},
        "by_collection": {(r["collection"] or "unassigned"): r["c"] for r in by_collection},
    }


REJECTED_ASSETS_DDL = """
CREATE TABLE IF NOT EXISTS rejected_assets (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path        TEXT,
    shopify_url      TEXT,
    shopify_filename TEXT,
    collection       TEXT,
    reason           TEXT,
    defect_type      TEXT,
    notes            TEXT,
    reported_at      TEXT
);
CREATE INDEX IF NOT EXISTS idx_rejected_collection ON rejected_assets(collection);
CREATE INDEX IF NOT EXISTS idx_rejected_defect ON rejected_assets(defect_type);
"""

_DEFECT_TYPES = (
    "anatomy_extra_limb",   # extra arms / legs / fingers
    "anatomy_merged",       # two bodies merged
    "anatomy_distorted",    # face / hands deformed
    "color_wrong",          # wrong dominant color / clipping
    "composition_off",      # framing / crop / ratio issue
    "blur",                 # insufficient sharpness
    "watermark",            # watermark or overlay artifact
    "other",
)


def _ensure_rejected_table(conn: sqlite3.Connection) -> None:
    for stmt in REJECTED_ASSETS_DDL.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            conn.execute(stmt)
    conn.commit()


def reject_asset(
    db_path: Path,
    *,
    shopify_filename: str = "",
    file_path: str = "",
    shopify_url: str = "",
    collection: str = "",
    reason: str = "",
    defect_type: str = "other",
    notes: str = "",
) -> int:
    """Add an image to rejected_assets. Returns the new row id."""
    now = datetime.now().isoformat()
    with closing(sqlite3.connect(db_path)) as conn:
        _ensure_rejected_table(conn)
        cur = conn.execute(
            """INSERT INTO rejected_assets
               (file_path, shopify_url, shopify_filename, collection,
                reason, defect_type, notes, reported_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (file_path, shopify_url, shopify_filename, collection,
             reason, defect_type, notes, now),
        )
        conn.commit()
        return cur.lastrowid


def list_rejected(db_path: Path, collection: str = "", defect_type: str = "") -> list[dict]:
    """Return all rejected assets, optionally filtered."""
    if not db_path.exists():
        return []
    with closing(sqlite3.connect(db_path)) as conn:
        _ensure_rejected_table(conn)
        conn.row_factory = sqlite3.Row
        q = "SELECT * FROM rejected_assets WHERE 1=1"
        params: list = []
        if collection:
            q += " AND collection = ?"
            params.append(collection)
        if defect_type:
            q += " AND defect_type = ?"
            params.append(defect_type)
        q += " ORDER BY reported_at DESC"
        return [dict(r) for r in conn.execute(q, params).fetchall()]


def is_rejected(db_path: Path, shopify_filename: str = "", file_path: str = "") -> bool:
    """Return True if the asset is already in the rejected table."""
    if not db_path.exists():
        return False
    with closing(sqlite3.connect(db_path)) as conn:
        _ensure_rejected_table(conn)
        if shopify_filename:
            r = conn.execute(
                "SELECT 1 FROM rejected_assets WHERE shopify_filename = ? LIMIT 1",
                (shopify_filename,),
            ).fetchone()
            if r:
                return True
        if file_path:
            r = conn.execute(
                "SELECT 1 FROM rejected_assets WHERE file_path = ? LIMIT 1",
                (file_path,),
            ).fetchone()
            if r:
                return True
    return False


# ─────────────────────────── PRINTIFY LIBRARY TABLES ────────────────────────

PRINTIFY_DDL = """
CREATE TABLE IF NOT EXISTS printify_uploads (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    printify_id          TEXT NOT NULL UNIQUE,
    filename             TEXT NOT NULL DEFAULT '',
    url                  TEXT NOT NULL DEFAULT '',
    local_path           TEXT NOT NULL DEFAULT '',
    width                INTEGER,
    height               INTEGER,
    file_size            INTEGER,
    mime_type            TEXT NOT NULL DEFAULT '',
    upload_time          TEXT NOT NULL DEFAULT '',
    used_in_collections  TEXT NOT NULL DEFAULT '[]',
    synced_at            TEXT NOT NULL DEFAULT '',
    meta_json            TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_pfy_up_id ON printify_uploads(printify_id);

CREATE TABLE IF NOT EXISTS printify_blueprints (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    blueprint_id  INTEGER NOT NULL UNIQUE,
    title         TEXT NOT NULL DEFAULT '',
    brand         TEXT NOT NULL DEFAULT '',
    model         TEXT NOT NULL DEFAULT '',
    description   TEXT NOT NULL DEFAULT '',
    images_json   TEXT NOT NULL DEFAULT '[]',
    synced_at     TEXT NOT NULL DEFAULT '',
    meta_json     TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_pfy_bp_id ON printify_blueprints(blueprint_id);

CREATE TABLE IF NOT EXISTS printify_products (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    printify_product_id     TEXT NOT NULL UNIQUE,
    shopify_product_id      TEXT NOT NULL DEFAULT '',
    title                   TEXT NOT NULL DEFAULT '',
    blueprint_id            INTEGER,
    print_provider_id       INTEGER,
    collection              TEXT NOT NULL DEFAULT '',
    upload_ids_json         TEXT NOT NULL DEFAULT '[]',
    mockup_urls_json        TEXT NOT NULL DEFAULT '[]',
    local_mockup_paths_json TEXT NOT NULL DEFAULT '[]',
    synced_at               TEXT NOT NULL DEFAULT '',
    meta_json               TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_pfy_prod_id  ON printify_products(printify_product_id);
CREATE INDEX IF NOT EXISTS idx_pfy_prod_col ON printify_products(collection);
"""


def _ensure_printify_tables(conn: sqlite3.Connection) -> None:
    for stmt in PRINTIFY_DDL.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            conn.execute(stmt)
    # Migrations for existing DBs that predate schema changes
    existing_cols = {
        row[1] for row in conn.execute("PRAGMA table_info(printify_uploads)").fetchall()
    }
    if "used_in_collections" not in existing_cols:
        conn.execute(
            "ALTER TABLE printify_uploads ADD COLUMN used_in_collections TEXT NOT NULL DEFAULT '[]'"
        )
    conn.commit()


def upsert_printify_upload(
    db_path: Path,
    *,
    printify_id: str,
    filename: str = "",
    url: str = "",
    local_path: str = "",
    width: int | None = None,
    height: int | None = None,
    file_size: int | None = None,
    mime_type: str = "",
    upload_time: str = "",
    used_in_collections: list | None = None,
    meta: dict | None = None,
) -> int:
    now = datetime.now().isoformat()
    meta_json = json.dumps(meta or {}, ensure_ascii=False)
    cols_json = json.dumps(used_in_collections or [], ensure_ascii=False)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as conn:
        _ensure_printify_tables(conn)
        existing = conn.execute(
            "SELECT id FROM printify_uploads WHERE printify_id = ?", (printify_id,)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE printify_uploads SET filename=?, url=?, local_path=?, width=?, height=?, "
                "file_size=?, mime_type=?, upload_time=?, used_in_collections=?, synced_at=?, meta_json=? WHERE id=?",
                (filename, url, local_path, width, height, file_size, mime_type,
                 upload_time, cols_json, now, meta_json, existing[0]),
            )
            conn.commit()
            return existing[0]
        cur = conn.execute(
            "INSERT INTO printify_uploads (printify_id, filename, url, local_path, width, height, "
            "file_size, mime_type, upload_time, used_in_collections, synced_at, meta_json) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (printify_id, filename, url, local_path, width, height, file_size,
             mime_type, upload_time, cols_json, now, meta_json),
        )
        conn.commit()
        return cur.lastrowid


def sync_upload_collections(db_path: Path) -> dict:
    """Cross-reference: for each upload, compute which collections use it.

    Reads printify_products.upload_ids_json and updates
    printify_uploads.used_in_collections with the list of distinct collection handles.
    """
    if not db_path.exists():
        return {"ok": False, "updated": 0}
    now = datetime.now().isoformat()
    with closing(sqlite3.connect(db_path)) as conn:
        _ensure_printify_tables(conn)
        conn.row_factory = sqlite3.Row
        products = conn.execute(
            "SELECT collection, upload_ids_json FROM printify_products WHERE upload_ids_json != '[]'"
        ).fetchall()

        # Build map: upload_id → set of collection handles
        upload_cols: dict[str, set[str]] = {}
        for prod in products:
            col = prod["collection"] or ""
            ids = json.loads(prod["upload_ids_json"] or "[]")
            for uid in ids:
                uid = str(uid)
                if uid not in upload_cols:
                    upload_cols[uid] = set()
                if col:
                    upload_cols[uid].add(col)

        updated = 0
        for printify_id, collections in upload_cols.items():
            cols_json = json.dumps(sorted(collections), ensure_ascii=False)
            result = conn.execute(
                "UPDATE printify_uploads SET used_in_collections=?, synced_at=? WHERE printify_id=?",
                (cols_json, now, printify_id),
            )
            if result.rowcount > 0:
                updated += 1

        conn.commit()
    return {"ok": True, "updated": updated, "upload_ids_found": len(upload_cols)}


def upsert_printify_blueprint(
    db_path: Path,
    *,
    blueprint_id: int,
    title: str = "",
    brand: str = "",
    model: str = "",
    description: str = "",
    images: list | None = None,
    meta: dict | None = None,
) -> int:
    now = datetime.now().isoformat()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as conn:
        _ensure_printify_tables(conn)
        existing = conn.execute(
            "SELECT id FROM printify_blueprints WHERE blueprint_id = ?", (blueprint_id,)
        ).fetchone()
        args = (title, brand, model, description,
                json.dumps(images or [], ensure_ascii=False),
                now, json.dumps(meta or {}, ensure_ascii=False))
        if existing:
            conn.execute(
                "UPDATE printify_blueprints SET title=?, brand=?, model=?, description=?, "
                "images_json=?, synced_at=?, meta_json=? WHERE id=?",
                args + (existing[0],),
            )
            conn.commit()
            return existing[0]
        cur = conn.execute(
            "INSERT INTO printify_blueprints (blueprint_id, title, brand, model, description, "
            "images_json, synced_at, meta_json) VALUES (?,?,?,?,?,?,?,?)",
            (blueprint_id,) + args,
        )
        conn.commit()
        return cur.lastrowid


def upsert_printify_product(
    db_path: Path,
    *,
    printify_product_id: str,
    shopify_product_id: str = "",
    title: str = "",
    blueprint_id: int | None = None,
    print_provider_id: int | None = None,
    collection: str = "",
    upload_ids: list | None = None,
    mockup_urls: list | None = None,
    local_mockup_paths: list | None = None,
    meta: dict | None = None,
) -> int:
    now = datetime.now().isoformat()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as conn:
        _ensure_printify_tables(conn)
        existing = conn.execute(
            "SELECT id FROM printify_products WHERE printify_product_id = ?", (printify_product_id,)
        ).fetchone()
        vals = (
            shopify_product_id, title, blueprint_id, print_provider_id, collection,
            json.dumps(upload_ids or [], ensure_ascii=False),
            json.dumps(mockup_urls or [], ensure_ascii=False),
            json.dumps(local_mockup_paths or [], ensure_ascii=False),
            now, json.dumps(meta or {}, ensure_ascii=False),
        )
        if existing:
            conn.execute(
                "UPDATE printify_products SET shopify_product_id=?, title=?, blueprint_id=?, "
                "print_provider_id=?, collection=?, upload_ids_json=?, mockup_urls_json=?, "
                "local_mockup_paths_json=?, synced_at=?, meta_json=? WHERE id=?",
                vals + (existing[0],),
            )
            conn.commit()
            return existing[0]
        cur = conn.execute(
            "INSERT INTO printify_products (printify_product_id, shopify_product_id, title, "
            "blueprint_id, print_provider_id, collection, upload_ids_json, mockup_urls_json, "
            "local_mockup_paths_json, synced_at, meta_json) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (printify_product_id,) + vals,
        )
        conn.commit()
        return cur.lastrowid


def list_printify_uploads(db_path: Path, limit: int | None = None) -> list[dict]:
    if not db_path.exists():
        return []
    with closing(sqlite3.connect(db_path)) as conn:
        _ensure_printify_tables(conn)
        conn.row_factory = sqlite3.Row
        q = "SELECT * FROM printify_uploads ORDER BY id DESC"
        if limit:
            q += f" LIMIT {limit}"
        return [dict(r) for r in conn.execute(q).fetchall()]


def list_printify_products(db_path: Path, collection: str = "") -> list[dict]:
    if not db_path.exists():
        return []
    with closing(sqlite3.connect(db_path)) as conn:
        _ensure_printify_tables(conn)
        conn.row_factory = sqlite3.Row
        q = "SELECT * FROM printify_products WHERE 1=1"
        params: list = []
        if collection:
            q += " AND collection = ?"
            params.append(collection)
        q += " ORDER BY id"
        return [dict(r) for r in conn.execute(q, params).fetchall()]


def printify_library_summary(db_path: Path) -> dict:
    if not db_path.exists():
        return {"ok": False, "uploads": 0, "blueprints": 0, "products": 0}
    with closing(sqlite3.connect(db_path)) as conn:
        _ensure_printify_tables(conn)
        conn.row_factory = sqlite3.Row
        uploads = conn.execute("SELECT COUNT(*) AS c FROM printify_uploads").fetchone()["c"]
        uploads_dl = conn.execute(
            "SELECT COUNT(*) AS c FROM printify_uploads WHERE local_path != ''"
        ).fetchone()["c"]
        blueprints = conn.execute("SELECT COUNT(*) AS c FROM printify_blueprints").fetchone()["c"]
        products = conn.execute("SELECT COUNT(*) AS c FROM printify_products").fetchone()["c"]
        products_with_mockups = conn.execute(
            "SELECT COUNT(*) AS c FROM printify_products WHERE local_mockup_paths_json != '[]'"
        ).fetchone()["c"]
        by_col = conn.execute(
            "SELECT collection, COUNT(*) AS c FROM printify_products "
            "WHERE collection != '' GROUP BY collection ORDER BY c DESC"
        ).fetchall()
    return {
        "ok": True,
        "uploads": uploads,
        "uploads_downloaded": uploads_dl,
        "blueprints": blueprints,
        "products": products,
        "products_with_mockups": products_with_mockups,
        "by_collection": {r["collection"]: r["c"] for r in by_col},
    }


# ─────────────────────────── PUBLIC PAYLOAD ──────────────────────────────────

def payload(settings: Any = None) -> dict[str, Any]:
    from bks_assets import active_catalog_db

    db_path = active_catalog_db()
    summ = summary(db_path)
    if not summ.get("ok"):
        return {"summary": summ, "products": []}
    products = fetch_products(db_path, limit=500)
    rows = [
        {
            "handle": record["handle"],
            "title": record["title"],
            "collection": record["collection"],
            "type": record["product_type"],
            "status": record["status"],
            "price": record["variant_price"],
            "image": record["image_src"],
        }
        for record in products
    ]
    return {"summary": summ, "products": rows}
