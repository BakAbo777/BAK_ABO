from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ecommerce_automation.product_name_audit import payload as product_name_audit_payload


SHOPIFY_CSV = Path("output/live_shopify_products.csv")
PRINTIFY_CSV = Path("output/live_printify_products.csv")
DIFF_CSV = Path("output/catalog_platform_diff.csv")
REPORT_JSON = Path("output/catalog_live_sync_report.json")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _split_tags(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value or "").split(",") if item.strip()]


def _tag_value(tags: list[str], prefix: str) -> str:
    prefix_lower = prefix.lower()
    for tag in tags:
        if tag.lower().startswith(prefix_lower):
            return tag.split(":", 1)[1].strip()
    return ""


def _shopify_rows(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for product in products:
        tags = _split_tags(product.get("tags", ""))
        variants = [item for item in product.get("variants", []) if isinstance(item, dict)]
        images = [item for item in product.get("images", []) if isinstance(item, dict)]
        rows.append(
            {
                "handle": product.get("handle", ""),
                "title": product.get("title", ""),
                "shopify_product_id": str(product.get("id", "") or ""),
                "shopify_gid": f"gid://shopify/Product/{product.get('id')}" if product.get("id") else "",
                "vendor": product.get("vendor", ""),
                "product_type": product.get("product_type", ""),
                "status": product.get("status", ""),
                "published_at": product.get("published_at", "") or "",
                "updated_at": product.get("updated_at", "") or "",
                "variant_count": len(variants),
                "image_count": len(images),
                "sample_sku": str((variants[0].get("sku", "") if variants else "") or ""),
                "bks_collection": _tag_value(tags, "collection:"),
                "bks_series": _tag_value(tags, "series:"),
                "bks_drop": _tag_value(tags, "drop:"),
                "tags": ",".join(tags),
            }
        )
    return rows


def _printify_rows(products: list[dict[str, Any]], shop_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for product in products:
        external = product.get("external") if isinstance(product.get("external"), dict) else {}
        variants = [item for item in product.get("variants", []) if isinstance(item, dict)]
        images = [item for item in product.get("images", []) if isinstance(item, dict)]
        tags = _split_tags(product.get("tags", []))
        rows.append(
            {
                "handle": str(external.get("handle", "") or product.get("slug", "") or ""),
                "title": product.get("title", ""),
                "printify_shop_id": shop_id,
                "printify_product_id": str(product.get("id", "") or ""),
                "shopify_product_id": str(external.get("id", "") or ""),
                "visible": str(product.get("visible", "")),
                "status": "published" if product.get("visible") or external.get("id") else "draft",
                "updated_at": product.get("updated_at", "") or "",
                "variant_count": len(variants),
                "image_count": len(images),
                "tags": ",".join(tags),
            }
        )
    return rows


def _write_csv(root_dir: Path, relative_path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> str:
    path = root_dir / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in rows])
    return _relative(root_dir, path)


def _update_references_from_shopify(references: Any, rows: list[dict[str, Any]], root_dir: Path) -> dict[str, int]:
    inserted = 0
    updated = 0
    now = _now()
    with references.connect() as con:
        for row in rows:
            handle = str(row.get("handle") or "").strip()
            if not handle:
                continue
            existing = con.execute("SELECT handle, shopify_product_id, updated_at FROM external_references WHERE handle = ?", (handle,)).fetchone()
            publish_status = "published" if row.get("published_at") or row.get("status") == "active" else str(row.get("status") or "shopify_seen")
            if existing is None:
                con.execute(
                    """
                    INSERT INTO external_references (
                        handle, title, vendor, product_type, bks_collection, bks_series, bks_drop,
                        local_status, local_catalog_path, variant_count, sample_sku,
                        shopify_product_id, shopify_gid, publish_status, last_sync_status,
                        first_seen_at, last_seen_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        handle,
                        row.get("title", ""),
                        row.get("vendor", ""),
                        row.get("product_type", ""),
                        row.get("bks_collection", ""),
                        row.get("bks_series", ""),
                        row.get("bks_drop", ""),
                        row.get("status", ""),
                        str(root_dir / SHOPIFY_CSV),
                        int(row.get("variant_count", 0) or 0),
                        row.get("sample_sku", ""),
                        row.get("shopify_product_id", ""),
                        row.get("shopify_gid", ""),
                        publish_status,
                        "shopify_live_inserted",
                        now,
                        now,
                        now,
                    ),
                )
                inserted += 1
            else:
                con.execute(
                    """
                    UPDATE external_references
                    SET title = ?, vendor = ?, product_type = ?, bks_collection = ?,
                        bks_series = ?, bks_drop = ?, local_status = ?, local_catalog_path = ?,
                        variant_count = ?, sample_sku = ?, shopify_product_id = ?, shopify_gid = ?,
                        publish_status = ?, last_sync_status = 'shopify_live_updated',
                        last_seen_at = ?, updated_at = ?
                    WHERE handle = ?
                    """,
                    (
                        row.get("title", ""),
                        row.get("vendor", ""),
                        row.get("product_type", ""),
                        row.get("bks_collection", ""),
                        row.get("bks_series", ""),
                        row.get("bks_drop", ""),
                        row.get("status", ""),
                        str(root_dir / SHOPIFY_CSV),
                        int(row.get("variant_count", 0) or 0),
                        row.get("sample_sku", ""),
                        row.get("shopify_product_id", ""),
                        row.get("shopify_gid", ""),
                        publish_status,
                        now,
                        now,
                        handle,
                    ),
                )
                updated += 1
    return {"shopify_inserted": inserted, "shopify_updated": updated}


def _update_references_from_printify(references: Any, rows: list[dict[str, Any]]) -> dict[str, int]:
    updated = 0
    unmatched = 0
    now = _now()
    with references.connect() as con:
        for row in rows:
            handle = str(row.get("handle") or "").strip()
            title = str(row.get("title") or "").strip()
            existing = None
            if handle:
                existing = con.execute("SELECT handle FROM external_references WHERE handle = ?", (handle,)).fetchone()
            if existing is None and title:
                existing = con.execute("SELECT handle FROM external_references WHERE lower(title) = lower(?) LIMIT 1", (title,)).fetchone()
            if existing is None:
                unmatched += 1
                continue
            con.execute(
                """
                UPDATE external_references
                SET printify_shop_id = ?, printify_product_id = ?,
                    shopify_product_id = COALESCE(NULLIF(shopify_product_id, ''), ?),
                    last_sync_status = 'printify_live_updated',
                    last_seen_at = ?, updated_at = ?
                WHERE handle = ?
                """,
                (
                    row.get("printify_shop_id", ""),
                    row.get("printify_product_id", ""),
                    row.get("shopify_product_id", ""),
                    now,
                    now,
                    existing["handle"],
                ),
            )
            updated += 1
    return {"printify_updated": updated, "printify_unmatched": unmatched}


def _diff_rows(shopify: list[dict[str, Any]], printify: list[dict[str, Any]]) -> list[dict[str, Any]]:
    shopify_by_handle = {str(row.get("handle", "")).strip().lower(): row for row in shopify if row.get("handle")}
    shopify_by_id = {str(row.get("shopify_product_id", "")).strip(): row for row in shopify if row.get("shopify_product_id")}
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for row in printify:
        handle_key = str(row.get("handle", "")).strip().lower()
        shopify_id = str(row.get("shopify_product_id", "")).strip()
        shopify_row = shopify_by_handle.get(handle_key) or shopify_by_id.get(shopify_id)
        if shopify_row:
            seen.add(str(shopify_row.get("handle", "")).strip().lower())
            status = "matched"
            if str(row.get("status")) == "draft":
                status = "printify_draft"
            elif str(shopify_row.get("status")) != "active":
                status = "shopify_not_active"
            rows.append(
                {
                    "status": status,
                    "handle": shopify_row.get("handle", row.get("handle", "")),
                    "title": shopify_row.get("title", row.get("title", "")),
                    "shopify_id": shopify_row.get("shopify_product_id", ""),
                    "printify_id": row.get("printify_product_id", ""),
                    "shopify_updated_at": shopify_row.get("updated_at", ""),
                    "printify_updated_at": row.get("updated_at", ""),
                    "next_action": "No action" if status == "matched" else "Review publication/status mismatch.",
                }
            )
        else:
            rows.append(
                {
                    "status": "printify_not_in_shopify",
                    "handle": row.get("handle", ""),
                    "title": row.get("title", ""),
                    "shopify_id": "",
                    "printify_id": row.get("printify_product_id", ""),
                    "shopify_updated_at": "",
                    "printify_updated_at": row.get("updated_at", ""),
                    "next_action": "Publish or map product if it should be live.",
                }
            )
    for handle_key, row in shopify_by_handle.items():
        if handle_key not in seen:
            rows.append(
                {
                    "status": "shopify_not_in_printify",
                    "handle": row.get("handle", ""),
                    "title": row.get("title", ""),
                    "shopify_id": row.get("shopify_product_id", ""),
                    "printify_id": "",
                    "shopify_updated_at": row.get("updated_at", ""),
                    "printify_updated_at": "",
                    "next_action": "Confirm source/fulfillment or remove from Printify-required checks.",
                }
            )
    return rows


def payload(settings: Any, services: dict[str, Any], references: Any, *, live: bool = False) -> dict[str, Any]:
    shopify_client = services["shopify"]
    printify_client = services["printify"]
    if not live:
        report_path = settings.root_dir / REPORT_JSON
        if report_path.exists():
            try:
                return json.loads(report_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        return {
            "summary": {
                "status": "ready_for_live_sync",
                "live": False,
                "shopify_configured": shopify_client.configured,
                "printify_configured": printify_client.configured,
                "next_action": "Run live sync to fetch Shopify/Printify products and update references.",
            },
            "diff": [],
            "shopify": [],
            "printify": [],
        }

    errors: list[str] = []
    shopify_products: list[dict[str, Any]] = []
    printify_products: list[dict[str, Any]] = []
    shop_id = ""

    if shopify_client.configured:
        try:
            shopify_products = shopify_client.iter_products()
        except Exception as exc:  # noqa: BLE001
            errors.append(f"shopify:{type(exc).__name__}:{exc}")
    else:
        errors.append("shopify:missing_credentials")

    if printify_client.configured:
        try:
            shop_id = printify_client.resolve_shop_id(settings.printify_shop_title)
            printify_products = printify_client.iter_products(shop_id)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"printify:{type(exc).__name__}:{exc}")
    else:
        errors.append("printify:missing_token")

    shopify_rows = _shopify_rows(shopify_products)
    printify_rows = _printify_rows(printify_products, shop_id)
    diff = _diff_rows(shopify_rows, printify_rows)

    shopify_sheet = _write_csv(
        settings.root_dir,
        SHOPIFY_CSV,
        shopify_rows,
        ["handle", "title", "shopify_product_id", "shopify_gid", "vendor", "product_type", "status", "published_at", "updated_at", "variant_count", "image_count", "sample_sku", "bks_collection", "bks_series", "bks_drop", "tags"],
    )
    printify_sheet = _write_csv(
        settings.root_dir,
        PRINTIFY_CSV,
        printify_rows,
        ["handle", "title", "printify_shop_id", "printify_product_id", "shopify_product_id", "visible", "status", "updated_at", "variant_count", "image_count", "tags"],
    )
    diff_sheet = _write_csv(
        settings.root_dir,
        DIFF_CSV,
        diff,
        ["status", "handle", "title", "shopify_id", "printify_id", "shopify_updated_at", "printify_updated_at", "next_action"],
    )

    updates = {}
    if shopify_rows:
        updates.update(_update_references_from_shopify(references, shopify_rows, settings.root_dir))
    if printify_rows:
        updates.update(_update_references_from_printify(references, printify_rows))

    attention = sum(1 for row in diff if row["status"] != "matched")
    name_audit = product_name_audit_payload(settings, products=shopify_rows if shopify_rows else None)
    report = {
        "summary": {
            "status": "attention" if errors or attention else "synced",
            "live": True,
            "checked_at": _now(),
            "shopify_products": len(shopify_rows),
            "printify_products": len(printify_rows),
            "matched": sum(1 for row in diff if row["status"] == "matched"),
            "attention": attention,
            "errors": len(errors),
            "error_messages": errors[:6],
            "shopify_sheet": shopify_sheet,
            "printify_sheet": printify_sheet,
            "diff_sheet": diff_sheet,
            **updates,
            "references": references.summary(),
            "name_audit_status": name_audit.get("summary", {}).get("status", ""),
            "name_audit_needs_fix": name_audit.get("summary", {}).get("needs_fix", 0),
            "name_audit_needs_review": name_audit.get("summary", {}).get("needs_review", 0),
            "name_audit_sheet": name_audit.get("summary", {}).get("sheet", ""),
        },
        "diff": diff[:250],
        "name_audit": name_audit.get("rows", [])[:80],
        "shopify": shopify_rows[:100],
        "printify": printify_rows[:100],
    }
    report_path = settings.root_dir / REPORT_JSON
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    report["summary"]["report"] = _relative(settings.root_dir, report_path)
    return report
