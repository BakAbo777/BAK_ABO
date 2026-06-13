#!/usr/bin/env python3
"""
BKS Studio - Fase 2b
Populate product metafields from BKS_COLLEZIONE_26_v6.csv.

Run:
  python tools/populate_metafields.py --no-verify-ssl
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from pathlib import Path

from bks_shopify_api import ShopifyGraphQL, add_shopify_args


BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from bks_assets import active_catalog_csv  # noqa: E402


DEFAULT_CSV = active_catalog_csv()
LOG_PATH = BASE_DIR / "output" / "populate_metafields_log.csv"
LOG_FIELDS = ["status", "handle", "id", "message"]

COLLECTION_NAMES = {
    "folklore": "Folklore",
    "glyph": "Glyph",
    "marker": "Marker",
    "riviera": "Riviera",
    "pulse": "Pulse",
    "token": "Token",
    "flag": "Flag",
    "hours": "Hours",
}


GET_PRODUCT = """
query ProductByHandle($handle: String!) {
  productByHandle(handle: $handle) {
    id
    title
    handle
  }
}
"""

SET_METAFIELDS = """
mutation SetMetafields($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields {
      id
      namespace
      key
      value
    }
    userErrors {
      field
      message
    }
  }
}
"""


def split_tags(value: str) -> list[str]:
    return [tag.strip() for tag in (value or "").split(",") if tag.strip()]


def extract_tag_value(tags: list[str], prefix: str) -> str:
    for tag in tags:
        if tag.startswith(prefix):
            return tag.split(":", 1)[1].strip()
    return ""


def extract_design_name(title: str) -> str:
    match = re.match(
        r"^BKS\s+(?:Folklore|Glyph|Marker|Riviera|Pulse|Token|Flag|Hours)\s+(.+?)(?:[™(]|$)",
        title,
    )
    if match:
        return match.group(1).strip()
    standalone = re.match(r"^BKS\s+(.+?)(?:[™(]|$)", title)
    return standalone.group(1).strip() if standalone else ""


def unique_products(csv_path: Path) -> dict[str, dict[str, str]]:
    products: dict[str, dict[str, str]] = {}
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            handle = (row.get("Handle") or "").strip()
            title = (row.get("Title") or "").strip()
            if handle and title and handle not in products:
                products[handle] = {"title": title, "tags": row.get("Tags") or ""}
    return products


def product_values(handle: str, data: dict[str, str]) -> dict[str, str]:
    tags = split_tags(data["tags"])
    collection_key = extract_tag_value(tags, "collection:")
    return {
        "handle": handle,
        "title": data["title"],
        "collection": COLLECTION_NAMES.get(collection_key, collection_key.capitalize()),
        "design": extract_design_name(data["title"]),
        "series": extract_tag_value(tags, "series:"),
        "drop": extract_tag_value(tags, "drop:") or "catalog-reset-2026",
    }


def completed_handles(log_path: Path) -> set[str]:
    if not log_path.exists():
        return set()
    completed: set[str] = set()
    with log_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            status = (row.get("status") or "").strip()
            handle = (row.get("handle") or "").strip()
            if handle and status in {"updated", "skipped", "missing"}:
                completed.add(handle)
    return completed


def reset_log(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=LOG_FIELDS)
        writer.writeheader()


def ensure_log(log_path: Path) -> None:
    if not log_path.exists() or log_path.stat().st_size == 0:
        reset_log(log_path)


def append_log(log_path: Path, result: dict[str, str]) -> None:
    ensure_log(log_path)
    with log_path.open("a", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=LOG_FIELDS)
        writer.writerow({field: result.get(field, "") for field in LOG_FIELDS})


def apply_start_after(
    items: list[tuple[str, dict[str, str]]],
    start_after: str,
) -> list[tuple[str, dict[str, str]]]:
    if not start_after:
        return items
    for index, (handle, _) in enumerate(items):
        if handle == start_after:
            return items[index + 1 :]
    raise RuntimeError(f"--start-after handle not found in CSV: {start_after}")


def set_product_metafields(client: ShopifyGraphQL, values: dict[str, str]) -> dict[str, str]:
    product_data = client.query(GET_PRODUCT, {"handle": values["handle"]})
    product = product_data["data"].get("productByHandle")
    if not product:
        return {"status": "missing", "handle": values["handle"], "id": "", "message": "Product not found"}

    metafields = [
        {
            "ownerId": product["id"],
            "namespace": "bks",
            "key": "collection",
            "type": "single_line_text_field",
            "value": values["collection"],
        },
        {
            "ownerId": product["id"],
            "namespace": "bks",
            "key": "design",
            "type": "single_line_text_field",
            "value": values["design"],
        },
        {
            "ownerId": product["id"],
            "namespace": "bks",
            "key": "series",
            "type": "single_line_text_field",
            "value": values["series"],
        },
        {
            "ownerId": product["id"],
            "namespace": "bks",
            "key": "drop",
            "type": "single_line_text_field",
            "value": values["drop"],
        },
    ]
    result = client.query(SET_METAFIELDS, {"metafields": metafields})
    payload = result["data"]["metafieldsSet"]
    errors = payload.get("userErrors") or []
    if errors:
        return {
            "status": "error",
            "handle": values["handle"],
            "id": product["id"],
            "message": "; ".join(error.get("message", "") for error in errors),
        }
    return {"status": "updated", "handle": values["handle"], "id": product["id"], "message": ""}


def main() -> None:
    parser = argparse.ArgumentParser(description="Populate BKS product metafields.")
    add_shopify_args(parser)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--resume", action="store_true", help="Skip handles already logged as updated/skipped/missing.")
    parser.add_argument("--start-after", default="", help="Start after this handle in CSV order.")
    parser.add_argument("--continue-on-error", action="store_true", help="Keep going after a product-level error.")
    args = parser.parse_args()

    client = ShopifyGraphQL.from_args(args)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    products = unique_products(args.csv)
    items = list(products.items())
    items = apply_start_after(items, args.start_after.strip())
    if args.resume:
        done = completed_handles(LOG_PATH)
        items = [(handle, data) for handle, data in items if handle not in done]
        ensure_log(LOG_PATH)
        print(f"Resume: skipping {len(done)} handles already logged.")
    else:
        reset_log(LOG_PATH)
    if args.limit:
        items = items[: args.limit]

    print(f"Store: {client.shop}")
    print(f"Products: {len(items)}")
    if args.start_after:
        print(f"Start after: {args.start_after}")

    for handle, data in items:
        values = product_values(handle, data)
        if not values["collection"] or not values["series"]:
            result = {
                "status": "skipped",
                "handle": handle,
                "id": "",
                "message": "Missing collection or series tag",
            }
        else:
            try:
                result = set_product_metafields(client, values)
            except Exception as exc:
                result = {
                    "status": "error",
                    "handle": handle,
                    "id": "",
                    "message": f"{type(exc).__name__}: {exc}",
                }
                append_log(LOG_PATH, result)
                print(f"{result['status']:7} {handle} {result['message']}")
                print(f"Log: {LOG_PATH}")
                if not args.continue_on_error:
                    print("Stopped on first error. Re-run with --resume or --start-after after the network is stable.")
                    raise SystemExit(1) from exc
                time.sleep(0.4)
                continue
        append_log(LOG_PATH, result)
        print(f"{result['status']:7} {handle} {result['message']}")
        time.sleep(0.4)

    print(f"Log: {LOG_PATH}")


if __name__ == "__main__":
    main()
