#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bks_assets import active_catalog_csv, active_catalog_db, relative_to_base, save_active_assets  # noqa: E402
from ecommerce_automation.catalog_db import export_csv_for_shopify, migrate_rows  # noqa: E402


COLLECTION_TO_SERIES = {
    "hours": "hyperrealism",
    "glyph": "brut",
    "marker": "neo-expressionism",
    "riviera": "islands",
    "pulse": "optical",
    "token": "arcade",
    "flag": "neo-dada",
    "folklore": "naif",
}

COLLECTION_LABELS = {key: key.capitalize() for key in COLLECTION_TO_SERIES}
CONTROLLED_TAG_PREFIXES = (
    "brand:",
    "collection:",
    "series:",
    "type:",
    "drop:",
    "status:",
    "print-type:",
    "macro:",
)

TYPE_CATEGORY = {
    "sneakers": "Apparel & Accessories > Shoes > Sneakers",
    "swim-trunks": "Apparel & Accessories > Clothing > Swimwear > Swim Boxers",
    "one-piece-swimsuit": "Apparel & Accessories > Clothing > Swimwear > One-Piece Swimsuits",
    "puffer-jacket": "Apparel & Accessories > Clothing > Outerwear > Coats & Jackets > Puffer Jackets",
    "windbreaker": "Apparel & Accessories > Clothing > Outerwear > Coats & Jackets > Windbreakers",
    "athletic-shorts": "Apparel & Accessories > Clothing > Shorts",
    "lounge-pants": "Apparel & Accessories > Clothing > Sleepwear & Loungewear > Loungewear Bottoms",
    "pullover-hoodie": "Apparel & Accessories > Clothing > Clothing Tops > Hoodies",
    "racerback-dress": "Apparel & Accessories > Clothing > Dresses",
    "travel-bag": "Luggage & Bags > Duffel Bags",
    "backpack": "Luggage & Bags > Backpacks",
    "flip-flop": "Apparel & Accessories > Shoes > Sandals",
    "cozy-slipper": "Apparel & Accessories > Shoes > Slippers",
    "womens-tee": "Apparel & Accessories > Clothing > Tops & Tees > T-Shirts",
    "camp-shirt": "Apparel & Accessories > Clothing > Shirts & Tops",
    "shirt": "Apparel & Accessories > Clothing > Shirts & Tops",
}

TYPE_LABEL = {
    "sneakers": "Sneakers",
    "swim-trunks": "Swim Trunks",
    "one-piece-swimsuit": "One-Piece Swimsuit",
    "puffer-jacket": "Puffer Jacket",
    "windbreaker": "Windbreaker",
    "athletic-shorts": "Athletic Shorts",
    "lounge-pants": "Lounge Pants",
    "pullover-hoodie": "Pullover Hoodie",
    "racerback-dress": "Racerback Dress",
    "travel-bag": "Travel Bag",
    "backpack": "Backpack",
    "flip-flop": "Flip Flop",
    "cozy-slipper": "Cozy Slipper",
    "womens-tee": "Women's Tee",
    "camp-shirt": "Camp Shirt",
    "shirt": "Shirt",
}


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    return " ".join(value.replace("™", "").split())


def slug(value: str) -> str:
    value = (value or "").replace("™", "").lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-{2,}", "-", value).strip("-")


def split_tags(value: str) -> list[str]:
    return [tag.strip() for tag in (value or "").split(",") if tag.strip()]


def normalize_tags(tags: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for tag in tags:
        cleaned = " ".join(tag.strip().split())
        if not cleaned:
            continue
        key = cleaned.lower()
        if key not in seen:
            seen.add(key)
            out.append(cleaned)
    return out


def remove_controlled_tags(tags: list[str]) -> list[str]:
    out: list[str] = []
    for tag in tags:
        key = tag.strip().lower()
        if any(key.startswith(prefix) for prefix in CONTROLLED_TAG_PREFIXES):
            continue
        out.append(tag)
    return out


def tag_value(tags: list[str], prefix: str) -> str:
    prefix_l = prefix.lower()
    for tag in tags:
        if tag.lower().startswith(prefix_l):
            return tag.split(":", 1)[1].strip().lower()
    return ""


def infer_collection(row: dict[str, str], tags: list[str]) -> str:
    field = (row.get("BKS Collection (product.metafields.bks.collection)") or "").strip().lower()
    if field in COLLECTION_TO_SERIES:
        return field

    from_tag = tag_value(tags, "collection:")
    if from_tag in COLLECTION_TO_SERIES:
        return from_tag

    haystack = " ".join(
        [
            row.get("Title", ""),
            row.get("Handle", ""),
            row.get("Body (HTML)", ""),
            row.get("Tags", ""),
        ]
    ).lower()
    for key in COLLECTION_TO_SERIES:
        if re.search(rf"\b{re.escape(key)}\b", haystack):
            return key

    keyword_map = {
        "riviera": ["resort", "beach", "coast", "hawaiian", "aloha", "tropical", "summer"],
        "glyph": ["glyph", "symbol", "code", "circuit", "blueprint"],
        "marker": ["marker", "street", "urban", "drip", "spray", "face"],
        "token": ["token", "pixel", "arcade", "maze", "mosaic", "digital"],
        "flag": ["flag", "collage", "dada", "burst", "banner"],
        "pulse": ["pulse", "optical", "prism", "vibration", "shard"],
        "folklore": ["folklore", "floral", "velvet", "garden", "bestiary"],
        "hours": ["hours", "brocade", "pane", "monochrome", "nocturne"],
    }
    for collection, words in keyword_map.items():
        if any(word in haystack for word in words):
            return collection
    return "glyph"


def infer_product_type(row: dict[str, str], tags: list[str]) -> str:
    raw = " ".join([tag_value(tags, "type:"), row.get("Type", ""), row.get("Title", ""), row.get("Handle", "")]).lower()
    checks = [
        ("one-piece-swimsuit", ["one-piece", "one piece"]),
        ("swim-trunks", ["swim trunks", "swim boxers"]),
        ("puffer-jacket", ["puffer"]),
        ("windbreaker", ["windbreaker"]),
        ("pullover-hoodie", ["hoodie", "pullover"]),
        ("athletic-shorts", ["athletic long shorts", "athletics shorts", "athletic shorts", "long shorts"]),
        ("lounge-pants", ["lounge pants", "pajama", "pyjama"]),
        ("racerback-dress", ["racerback dress", "dress"]),
        ("travel-bag", ["travel bag", "duffel", "duffle"]),
        ("backpack", ["backpack"]),
        ("flip-flop", ["flip flop", "flip-flop"]),
        ("cozy-slipper", ["slipper"]),
        ("womens-tee", ["women's tee", "womens tee", "t-shirt", "tee"]),
        ("sneakers", ["sneaker", "sneakers", "shoes", "shoe"]),
        ("camp-shirt", ["hawaiian shirt", "camp shirt", "aloha"]),
        ("shirt", ["shirt"]),
    ]
    for canonical, needles in checks:
        if any(needle in raw for needle in needles):
            return canonical
    return slug(row.get("Type", "")) or "aop"


def infer_gender(row: dict[str, str], product_type: str, tags: list[str]) -> str:
    raw = " ".join([row.get("Title", ""), row.get("Handle", ""), row.get("Tags", "")]).lower()
    if "macro:woman" in [tag.lower() for tag in tags] or product_type in {"one-piece-swimsuit", "racerback-dress", "womens-tee"}:
        return "female"
    if "macro:man" in [tag.lower() for tag in tags] or " men" in raw or "mens" in raw or "men's" in raw:
        return "male"
    return "unisex"


def extract_design(title: str, collection: str, product_type: str) -> str:
    value = clean_text(title)
    value = re.sub(r"^BKS\s+", "", value, flags=re.IGNORECASE)
    value = re.sub(rf"^{collection}\s+", "", value, flags=re.IGNORECASE)
    label = TYPE_LABEL.get(product_type, product_type.replace("-", " ").title())
    value = re.sub(re.escape(label) + r"$", "", value, flags=re.IGNORECASE).strip(" -—")
    if "—" in value and not value.lower().startswith("abstract"):
        value = value.split("—", 1)[0].strip()
    return value or collection.capitalize()


def canonical_public_title(title: str, collection: str, product_type: str, design: str) -> str:
    if title.strip().lower().startswith("bks "):
        return title
    raw = title.lower()
    if "face" in raw:
        design = "Faces"
    elif "mosaic" in raw:
        design = "Mosaic"
    elif len(design) > 28:
        design = COLLECTION_LABELS[collection]
    label = TYPE_LABEL.get(product_type, product_type.replace("-", " ").title())
    return f"BKS {COLLECTION_LABELS[collection]} {design.replace('™', '').strip()}™ {label}"


def concise_title(title: str, collection: str, product_type: str, limit: int = 70) -> str:
    cleaned = clean_text(title)
    base = f"{cleaned} | BKS Studio"
    if len(base) <= limit:
        return base
    label = TYPE_LABEL.get(product_type, product_type.replace("-", " ").title())
    fallback = f"BKS {COLLECTION_LABELS[collection]} {label} | AI-Art Print"
    if len(fallback) <= limit:
        return fallback
    return fallback[: limit - 1].rstrip(" -|") + "…"


def concise_description(title: str, collection: str, product_type: str, limit: int = 160) -> str:
    label = TYPE_LABEL.get(product_type, product_type.replace("-", " ").title()).lower()
    desc = (
        f"AI-generated all-over print {label} from BKS {COLLECTION_LABELS[collection]}. "
        "Made to order, edge-to-edge printed and curated by BKS Studio at bakabo.club."
    )
    if len(desc) <= limit:
        return desc
    return desc[: limit - 1].rstrip(" .,") + "."


def is_bad_category(value: str) -> bool:
    stripped = (value or "").strip()
    return not stripped or len(stripped) > 120 or "✅" in stripped or "Torno al" in stripped


def enrich(input_path: Path, output_path: Path, report_path: Path) -> tuple[int, int]:
    with input_path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, restval='')
        if not reader.fieldnames:
            raise ValueError(f"CSV senza header: {input_path}")
        fieldnames = reader.fieldnames
        # Righe con tag HTML nell'Handle sono frammenti del blocco di compliance
        # GPSR (Printify) finiti fuori posto per virgolette CSV perse a monte,
        # non prodotti reali: scartarle evita sia righe spazzatura in output
        # sia il crash di DictWriter sui campi extra che generano.
        rows = [row for row in reader if "<" not in (row.get("Handle") or "")]

    product_titles: dict[str, str] = {}
    for row in rows:
        handle = (row.get("Handle") or "").strip()
        title = (row.get("Title") or "").strip()
        if handle and title:
            product_titles[handle] = title

    report_rows: list[dict[str, str]] = []
    output_rows: list[dict[str, str]] = []

    for row in rows:
        fixed = {k: ('' if v is None else v) for k, v in row.items()}
        handle = (row.get("Handle") or "").strip()
        title = (row.get("Title") or "").strip()
        changes: list[str] = []

        if title:
            tags = split_tags(row.get("Tags", ""))
            collection = infer_collection(row, tags)
            product_type = infer_product_type(row, tags)
            series = COLLECTION_TO_SERIES[collection]
            design = extract_design(title, collection, product_type)
            category = TYPE_CATEGORY.get(product_type, "Apparel & Accessories > Clothing")
            gender = infer_gender(row, product_type, tags)
            status = (row.get("Status") or "active").strip().lower() or "active"

            required_tags = [
                "brand:bks",
                f"collection:{collection}",
                f"series:{series}",
                f"type:{product_type}",
                "drop:catalog-reset-2026",
                f"status:{status}",
                "print-type:aop",
                "made-to-order",
                "ai-art",
                "bakabo-enriched",
            ]
            if gender == "female":
                required_tags.append("macro:woman")
            elif gender == "male":
                required_tags.append("macro:man")
            else:
                required_tags.extend(["macro:man", "macro:woman"])

            normalized = normalize_tags(remove_controlled_tags(tags) + required_tags)
            new_tags = ", ".join(normalized)
            if new_tags != (row.get("Tags") or ""):
                fixed["Tags"] = new_tags
                changes.append("tags")

            canonical_title = canonical_public_title(title, collection, product_type, design)
            if canonical_title != title:
                fixed["Title"] = canonical_title
                title = canonical_title
                changes.append("Title")

            fill_values = {
                "SEO Title": concise_title(title, collection, product_type),
                "SEO Description": concise_description(title, collection, product_type),
                "BKS Collection (product.metafields.bks.collection)": COLLECTION_LABELS[collection],
                "BKS Design (product.metafields.bks.design)": design,
                "BKS Drop (product.metafields.bks.drop)": "catalog-reset-2026",
                "BKS Series (product.metafields.bks.series)": series,
                "Google Product Category (product.metafields.custom.google_product_category)": category,
                "Google Shopping / Gender": gender,
                "Google Shopping / Age Group": "adult",
                "Google Shopping / Condition": "new",
                "Google Shopping / Custom Product": "TRUE",
                "Google Shopping / Custom Label 0": "no-gtin",
                "Google Shopping / Custom Label 1": TYPE_LABEL.get(product_type, product_type.replace("-", " ").title()),
            }

            for field, value in fill_values.items():
                if field not in fixed:
                    continue
                old_value = (fixed.get(field) or "").strip()
                should_fill = not old_value
                if field == "SEO Description" and len(old_value) > 160:
                    should_fill = True
                if field == "SEO Title" and (len(old_value) > 70 or "bakabo" in old_value.lower()):
                    should_fill = True
                if field == "BKS Series (product.metafields.bks.series)" and old_value and old_value != series:
                    should_fill = True
                if field == "Google Product Category (product.metafields.custom.google_product_category)" and is_bad_category(old_value):
                    should_fill = True
                if should_fill and old_value != value:
                    fixed[field] = value
                    changes.append(field)

            if (fixed.get("Image Src") or "").strip():
                value = f"{clean_text(title)} - BKS {COLLECTION_LABELS[collection]} {TYPE_LABEL.get(product_type, 'product')}"
                if (fixed.get("Image Alt Text") or "").strip() != value:
                    fixed["Image Alt Text"] = value
                    changes.append("Image Alt Text")

        elif handle and (fixed.get("Image Src") or "").strip() and not (fixed.get("Image Alt Text") or "").strip() and handle in product_titles:
            fixed["Image Alt Text"] = f"{clean_text(product_titles[handle])} - BKS Studio product image"
            changes.append("Image Alt Text")

        if not (fixed.get("Image Src") or "").strip():
            for field in ("Image Position", "Image Alt Text"):
                if (fixed.get(field) or "").strip():
                    fixed[field] = ""
                    changes.append(field)

        if changes:
            report_rows.append(
                {
                    "Handle": handle,
                    "Title": title or product_titles.get(handle, ""),
                    "Changed fields": "; ".join(sorted(set(changes))),
                }
            )
        output_rows.append(fixed)

    db_path = active_catalog_db()
    migrate_rows(output_rows, fieldnames, db_path, source=input_path.name)
    save_active_assets(catalog_db=db_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    export_csv_for_shopify(db_path, output_path)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8-sig", newline="") as report:
        writer = csv.DictWriter(report, fieldnames=["Handle", "Title", "Changed fields"])
        writer.writeheader()
        writer.writerows(report_rows)

    return len(output_rows), len(report_rows)


def default_output_path(input_path: Path) -> Path:
    stem = input_path.stem
    if stem.endswith("_SEO_TAGS_READY"):
        stem = stem.removesuffix("_SEO_TAGS_READY")
    return input_path.with_name(f"{stem}_SEO_TAGS_READY.csv")


def main() -> int:
    parser = argparse.ArgumentParser(description="Completa e ottimizza SEO/tag/metafield del CSV Shopify BKS.")
    parser.add_argument("--input", type=Path, default=active_catalog_csv())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--set-active", action="store_true", help="Imposta il CSV generato come catalogo attivo.")
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output or default_output_path(input_path)
    report_path = args.report or ROOT / "output" / f"catalog_enrichment_report_{datetime.now():%Y%m%d_%H%M%S}.csv"

    total_rows, changed_rows = enrich(input_path, output_path, report_path)
    if args.set_active:
        save_active_assets(catalog_csv=output_path)

    print(f"Rows written: {total_rows}")
    print(f"Rows changed: {changed_rows}")
    print(f"Output: {relative_to_base(output_path)}")
    print(f"Report: {relative_to_base(report_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
