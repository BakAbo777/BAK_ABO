"""Catalog helpers for Image Factory automation."""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
ACTIVE_ASSETS = ROOT_DIR / "output" / "bks_active_assets.json"
CATALOG_DIR = ROOT_DIR / "collezioni_csv"


@dataclass(frozen=True)
class ProductMatch:
    handle: str
    title: str
    tags: str
    collection: str
    product_type: str
    source: str


def safe_slug(value: str) -> str:
    value = re.sub(r"[™®©]", "", value or "")
    value = re.sub(r"[^a-zA-Z0-9\s\-]", "", value)
    value = re.sub(r"\s+", "-", value.strip()).lower()
    return value[:80]


def split_tags(value: str) -> list[str]:
    return [tag.strip() for tag in (value or "").split(",") if tag.strip()]


def tag_value(tags: list[str], prefix: str) -> str:
    prefix_lower = prefix.lower()
    for tag in tags:
        if tag.lower().startswith(prefix_lower):
            return tag.split(":", 1)[1].strip()
    return ""


def active_catalog_path() -> Path | None:
    if ACTIVE_ASSETS.exists():
        try:
            data = json.loads(ACTIVE_ASSETS.read_text(encoding="utf-8"))
            configured = data.get("catalog_csv")
            if configured:
                path = Path(configured)
                if not path.is_absolute():
                    path = ROOT_DIR / path
                if path.exists():
                    return path
        except json.JSONDecodeError:
            pass
    files = sorted(CATALOG_DIR.glob("*.csv"), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def product_type_from_row(row: dict[str, str]) -> str:
    tags = split_tags(row.get("Tags", ""))
    raw = (tag_value(tags, "type:") or row.get("Type") or row.get("Product Category") or "").lower()
    handle = (row.get("Handle") or "").lower()
    title = (row.get("Title") or "").lower()
    haystack = " ".join([raw, handle, title])

    mapping = [
        ("lounge-pants", ["lounge-pants", "pajama", "sleepwear", "pants"]),
        ("swim-trunks", ["swim-trunks", "trunks"]),
        ("one-piece-swimsuit", ["one-piece", "swimsuit"]),
        ("puffer-jacket", ["puffer"]),
        ("windbreaker", ["windbreaker"]),
        ("pullover-hoodie", ["hoodie"]),
        ("racerback-dress", ["racerback", "dress"]),
        ("athletic-shorts", ["athletic-shorts", "shorts"]),
        ("sneakers", ["sneakers", "shoes"]),
        ("backpack", ["backpack"]),
        ("travel-bag", ["travel-bag", "duffle", "duffel"]),
        ("flip-flop", ["flip-flop", "flip flops"]),
        ("cozy-slipper", ["slipper"]),
        ("womens-tee", ["womens-tee", "women's tee", "tee", "shirt", "camp-shirt"]),
    ]
    for product_type, needles in mapping:
        if any(needle in haystack for needle in needles):
            return product_type
    return "lounge-pants"


def load_products() -> list[dict[str, str]]:
    path = active_catalog_path()
    if not path:
        return []
    rows = list(csv.DictReader(path.open("r", encoding="utf-8-sig", newline="")))
    products: dict[str, dict[str, str]] = {}
    for row in rows:
        handle = (row.get("Handle") or "").strip()
        title = (row.get("Title") or "").strip()
        if not handle or not title:
            continue
        products.setdefault(handle, row)
    return list(products.values())


def _match_from_row(row: dict[str, str]) -> ProductMatch:
    handle = (row.get("Handle") or "").strip()
    title = (row.get("Title") or "").strip()
    tags = row.get("Tags") or ""
    collection = (
        row.get("BKS Collection (product.metafields.bks.collection)")
        or tag_value(split_tags(tags), "collection:")
        or "folklore"
    ).strip().lower()
    return ProductMatch(
        handle=handle,
        title=title,
        tags=tags,
        collection=collection,
        product_type=product_type_from_row(row),
        source="catalog",
    )


def find_product_for_slug(slug: str, products: list[dict[str, str]] | None = None) -> ProductMatch | None:
    products = products if products is not None else load_products()
    slug = safe_slug(slug)
    for row in products:
        handle = (row.get("Handle") or "").strip()
        title = (row.get("Title") or "").strip()
        if slug in {safe_slug(handle), safe_slug(title)}:
            return _match_from_row(row)
    return None


def match_product_for_image(image_path: Path, products: list[dict[str, str]] | None = None) -> ProductMatch | None:
    parent_slug = image_path.parent.name
    file_slug = re.sub(r"_mockup_\d+.*$", "", image_path.stem)
    return find_product_for_slug(parent_slug, products) or find_product_for_slug(file_slug, products)


def source_image_options(source_dir: Path) -> dict[str, Path]:
    images = sorted(
        [
            *source_dir.rglob("*.jpg"),
            *source_dir.rglob("*.jpeg"),
            *source_dir.rglob("*.png"),
            *source_dir.rglob("*.webp"),
        ],
        key=lambda item: (item.parent.name, item.name),
    )
    products = load_products()
    options: dict[str, Path] = {}
    for image in images:
        match = match_product_for_image(image, products)
        title = match.title if match else image.parent.name
        label = f"{title} / {image.name}"
        options[label] = image
    return options
