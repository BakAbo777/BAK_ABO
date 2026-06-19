from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BAKABO_STORE_DOMAIN = "bakabo.club"
BKS_TM04_THEME_ID = "202392961362"
BKS_PRINTIFY_SHOP_ID = "12030061"

BKS_COLLECTIONS = frozenset(("Hours", "Glyph", "Marker", "Riviera", "Pulse", "Token", "Flag", "Origin"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def split_tags(value: str) -> list[str]:
    return [tag.strip() for tag in (value or "").split(",") if tag.strip()]


def tag_value(tags: list[str], prefix: str) -> str:
    prefix_lower = prefix.lower()
    for tag in tags:
        if tag.lower().startswith(prefix_lower):
            return tag.split(":", 1)[1].strip()
    return ""


def stable_hash(data: dict[str, Any]) -> str:
    raw = json.dumps(data, ensure_ascii=True, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _normalize_collection(raw: str) -> str:
    """Title-case and validate against BKS_COLLECTIONS; map Folklore→Origin."""
    if not raw:
        return raw
    candidate = raw.strip().title()
    if candidate.lower() == "folklore":
        return "Origin"
    return candidate if candidate in BKS_COLLECTIONS else raw.strip()


class ExternalReferenceStore:
    """Ledger connecting bakabo.club catalog products to external platform IDs (Printify, Shopify)."""

    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.database_path)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        with self.connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS external_references (
                    handle TEXT PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT '',
                    vendor TEXT NOT NULL DEFAULT '',
                    product_type TEXT NOT NULL DEFAULT '',
                    bks_collection TEXT NOT NULL DEFAULT '',
                    bks_design TEXT NOT NULL DEFAULT '',
                    bks_series TEXT NOT NULL DEFAULT '',
                    bks_drop TEXT NOT NULL DEFAULT '',
                    local_status TEXT NOT NULL DEFAULT '',
                    local_catalog_path TEXT NOT NULL DEFAULT '',
                    variant_count INTEGER NOT NULL DEFAULT 0,
                    sample_sku TEXT NOT NULL DEFAULT '',
                    printify_shop_id TEXT NOT NULL DEFAULT '',
                    printify_product_id TEXT NOT NULL DEFAULT '',
                    shopify_product_id TEXT NOT NULL DEFAULT '',
                    shopify_gid TEXT NOT NULL DEFAULT '',
                    publish_status TEXT NOT NULL DEFAULT 'unmapped',
                    last_sync_status TEXT NOT NULL DEFAULT 'catalog_seen',
                    last_error TEXT NOT NULL DEFAULT '',
                    source_hash TEXT NOT NULL DEFAULT '',
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_external_refs_publish ON external_references (publish_status)")
            con.execute("CREATE INDEX IF NOT EXISTS idx_external_refs_collection ON external_references (bks_collection)")

    # ── catalog ingestion ─────────────────────────────────────────────────────

    def seed_from_catalog(self, catalog_path: Path) -> dict[str, Any]:
        rows = list(csv.DictReader(catalog_path.open("r", encoding="utf-8-sig", newline="")))
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            handle = (row.get("Handle") or "").strip()
            if handle:
                grouped[handle].append(row)

        now = utc_now()
        inserted = 0
        updated = 0
        unchanged = 0
        folklore_fixed = 0
        with self.connect() as con:
            for handle, product_rows in sorted(grouped.items()):
                first = next((row for row in product_rows if (row.get("Title") or "").strip()), product_rows[0])
                tags = split_tags(first.get("Tags", ""))
                raw_collection = (
                    first.get("BKS Collection (product.metafields.bks.collection)")
                    or tag_value(tags, "collection:")
                ).strip()
                normalized_collection = _normalize_collection(raw_collection)
                if raw_collection.lower() == "folklore":
                    folklore_fixed += 1
                payload = {
                    "handle": handle,
                    "title": (first.get("Title") or "").strip(),
                    "vendor": (first.get("Vendor") or "").strip(),
                    "product_type": (first.get("Type") or "").strip(),
                    "bks_collection": normalized_collection,
                    "bks_design": (first.get("BKS Design (product.metafields.bks.design)") or "").strip(),
                    "bks_series": (first.get("BKS Series (product.metafields.bks.series)") or tag_value(tags, "series:")).strip(),
                    "bks_drop": (first.get("BKS Drop (product.metafields.bks.drop)") or tag_value(tags, "drop:")).strip(),
                    "local_status": (first.get("Status") or tag_value(tags, "status:")).strip(),
                    "local_catalog_path": str(catalog_path),
                    "variant_count": len({(row.get("Variant SKU") or f"row-{index}").strip() for index, row in enumerate(product_rows)}),
                    "sample_sku": (first.get("Variant SKU") or "").strip(),
                }
                payload["source_hash"] = stable_hash(payload)
                existing = con.execute(
                    "SELECT source_hash FROM external_references WHERE handle = ?",
                    (handle,),
                ).fetchone()
                if existing is None:
                    con.execute(
                        """
                        INSERT INTO external_references (
                            handle, title, vendor, product_type, bks_collection, bks_design,
                            bks_series, bks_drop, local_status, local_catalog_path,
                            variant_count, sample_sku, source_hash,
                            first_seen_at, last_seen_at, updated_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            payload["handle"],
                            payload["title"],
                            payload["vendor"],
                            payload["product_type"],
                            payload["bks_collection"],
                            payload["bks_design"],
                            payload["bks_series"],
                            payload["bks_drop"],
                            payload["local_status"],
                            payload["local_catalog_path"],
                            payload["variant_count"],
                            payload["sample_sku"],
                            payload["source_hash"],
                            now, now, now,
                        ),
                    )
                    inserted += 1
                elif existing["source_hash"] != payload["source_hash"]:
                    con.execute(
                        """
                        UPDATE external_references
                        SET title = ?, vendor = ?, product_type = ?, bks_collection = ?,
                            bks_design = ?, bks_series = ?, bks_drop = ?, local_status = ?,
                            local_catalog_path = ?, variant_count = ?, sample_sku = ?,
                            source_hash = ?, last_seen_at = ?, updated_at = ?,
                            last_sync_status = 'catalog_updated'
                        WHERE handle = ?
                        """,
                        (
                            payload["title"],
                            payload["vendor"],
                            payload["product_type"],
                            payload["bks_collection"],
                            payload["bks_design"],
                            payload["bks_series"],
                            payload["bks_drop"],
                            payload["local_status"],
                            payload["local_catalog_path"],
                            payload["variant_count"],
                            payload["sample_sku"],
                            payload["source_hash"],
                            now, now,
                            handle,
                        ),
                    )
                    updated += 1
                else:
                    con.execute(
                        "UPDATE external_references SET last_seen_at = ?, last_sync_status = 'catalog_seen' WHERE handle = ?",
                        (now, handle),
                    )
                    unchanged += 1

        return {
            "catalog_path": str(catalog_path),
            "catalog_rows": len(rows),
            "products_seen": len(grouped),
            "inserted": inserted,
            "updated": updated,
            "unchanged": unchanged,
            "folklore_fixed": folklore_fixed,
            "summary": self.summary(),
        }

    # ── platform link writes ──────────────────────────────────────────────────

    def link_printify(self, handle: str, shop_id: str, product_id: str) -> None:
        with self.connect() as con:
            con.execute(
                """
                UPDATE external_references
                SET printify_shop_id = ?, printify_product_id = ?,
                    updated_at = ?, last_sync_status = 'printify_linked'
                WHERE handle = ?
                """,
                (shop_id, product_id, utc_now(), handle),
            )

    def link_shopify(self, handle: str, product_id: str, gid: str) -> None:
        with self.connect() as con:
            con.execute(
                """
                UPDATE external_references
                SET shopify_product_id = ?, shopify_gid = ?,
                    updated_at = ?, last_sync_status = 'shopify_linked'
                WHERE handle = ?
                """,
                (product_id, gid, utc_now(), handle),
            )

    def mark_published(self, handle: str, publish_status: str, *, error: str = "") -> None:
        sync_status = "publish_error" if error else "published"
        with self.connect() as con:
            con.execute(
                """
                UPDATE external_references
                SET publish_status = ?, last_error = ?,
                    updated_at = ?, last_sync_status = ?
                WHERE handle = ?
                """,
                (publish_status, error, utc_now(), sync_status, handle),
            )

    # ── reads ─────────────────────────────────────────────────────────────────

    def summary(self) -> dict[str, Any]:
        with self.connect() as con:
            total = con.execute("SELECT COUNT(*) FROM external_references").fetchone()[0]
            mapped_printify = con.execute(
                "SELECT COUNT(*) FROM external_references WHERE printify_product_id != ''"
            ).fetchone()[0]
            mapped_shopify = con.execute(
                "SELECT COUNT(*) FROM external_references WHERE shopify_product_id != '' OR shopify_gid != ''"
            ).fetchone()[0]
            folklore_count = con.execute(
                "SELECT COUNT(*) FROM external_references WHERE bks_collection = 'Folklore'"
            ).fetchone()[0]
            statuses = con.execute(
                "SELECT publish_status, COUNT(*) AS count FROM external_references GROUP BY publish_status ORDER BY count DESC"
            ).fetchall()
            collections = con.execute(
                """
                SELECT bks_collection, COUNT(*) AS count
                FROM external_references
                GROUP BY bks_collection
                ORDER BY count DESC
                LIMIT 12
                """
            ).fetchall()
        unknown_collections = sum(
            row["count"] for row in collections
            if row["bks_collection"] and row["bks_collection"] not in BKS_COLLECTIONS
        )
        return {
            "total_products": int(total),
            "mapped_printify": int(mapped_printify),
            "mapped_shopify": int(mapped_shopify),
            "missing_printify": int(total - mapped_printify),
            "missing_shopify": int(total - mapped_shopify),
            "folklore_detected": int(folklore_count),
            "unknown_collections": unknown_collections,
            "publish_statuses": {row["publish_status"] or "unknown": row["count"] for row in statuses},
            "collections": {row["bks_collection"] or "unassigned": row["count"] for row in collections},
            "trust_gate": "trust_foundation",
        }

    def list_references(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        search: str = "",
        collection: str = "",
        publish_status: str = "",
    ) -> list[dict[str, Any]]:
        limit = max(1, min(250, int(limit)))
        offset = max(0, int(offset))
        conditions: list[str] = []
        params: list[Any] = []
        if search:
            conditions.append("(handle LIKE ? OR title LIKE ? OR bks_collection LIKE ?)")
            needle = f"%{search}%"
            params.extend([needle, needle, needle])
        if collection:
            conditions.append("bks_collection = ?")
            params.append(_normalize_collection(collection))
        if publish_status:
            conditions.append("publish_status = ?")
            params.append(publish_status)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.extend([limit, offset])
        with self.connect() as con:
            rows = con.execute(
                f"SELECT * FROM external_references {where} ORDER BY updated_at DESC, handle LIMIT ? OFFSET ?",
                params,
            ).fetchall()
        return [dict(row) for row in rows]

    def get_reference(self, handle: str) -> dict[str, Any] | None:
        with self.connect() as con:
            row = con.execute(
                "SELECT * FROM external_references WHERE handle = ?", (handle,)
            ).fetchone()
        return dict(row) if row else None
