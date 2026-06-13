#!/usr/bin/env python3
"""
BKS Studio - Fase 1
Fix non-standard series tags and write BKS_COLLEZIONE_26_v5.csv.

Rules:
- If a product has collection:<name>, series must be the canonical editorial series.
- Existing canonical series tags are kept.
- Non-standard series tags are removed and replaced from collection:<name>.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = BASE_DIR / "BKS_COLLEZIONE_26_v4.csv"
DEFAULT_OUTPUT = BASE_DIR / "BKS_COLLEZIONE_26_v5.csv"
DEFAULT_REPORT = BASE_DIR / "output" / "series_tag_fix_report.csv"

COLLECTION_TO_SERIES = {
    "folklore": "naif",
    "glyph": "brut",
    "marker": "neo-expressionism",
    "riviera": "islands",
    "pulse": "optical",
    "token": "arcade",
    "flag": "neo-dada",
    "hours": "hyperrealism",
}

CANONICAL_SERIES_TAGS = {f"series:{value}" for value in COLLECTION_TO_SERIES.values()}


def split_tags(value: str) -> list[str]:
    return [tag.strip() for tag in (value or "").split(",") if tag.strip()]


def normalize_tags(tags: list[str]) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for tag in tags:
        key = tag.lower()
        if key not in seen:
            normalized.append(tag)
            seen.add(key)
    return normalized


def collection_key_from_tags(tags: list[str]) -> str:
    for tag in tags:
        if tag.startswith("collection:"):
            return tag.split(":", 1)[1].strip().lower()
    return ""


def fix_product_tags(tags_value: str) -> tuple[str, list[str], str]:
    tags = split_tags(tags_value)
    collection_key = collection_key_from_tags(tags)
    canonical_series = COLLECTION_TO_SERIES.get(collection_key, "")

    old_series_tags = [tag for tag in tags if tag.startswith("series:")]
    if not canonical_series:
        return ", ".join(normalize_tags(tags)), [], ""

    desired_series_tag = f"series:{canonical_series}"
    changed = [
        tag
        for tag in old_series_tags
        if tag != desired_series_tag or tag not in CANONICAL_SERIES_TAGS
    ]

    if not changed and desired_series_tag in old_series_tags:
        return ", ".join(normalize_tags(tags)), [], desired_series_tag

    fixed_tags = [tag for tag in tags if not tag.startswith("series:")]
    fixed_tags.append(desired_series_tag)
    return ", ".join(normalize_tags(fixed_tags)), old_series_tags, desired_series_tag


def run(input_path: Path, output_path: Path, report_path: Path) -> tuple[int, int]:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames:
            raise ValueError(f"CSV senza header: {input_path}")

        rows = list(reader)
        fieldnames = reader.fieldnames

    changed_products: dict[str, dict[str, str]] = {}
    output_rows: list[dict[str, str]] = []

    for row in rows:
        fixed_row = dict(row)
        title = (row.get("Title") or "").strip()
        handle = (row.get("Handle") or "").strip()

        if title and handle:
            fixed_tags, old_series, new_series = fix_product_tags(row.get("Tags") or "")
            fixed_row["Tags"] = fixed_tags

            if old_series and old_series != [new_series]:
                changed_products[handle] = {
                    "Handle": handle,
                    "Title": title,
                    "Old series tags": "; ".join(old_series),
                    "New series tag": new_series,
                }

        output_rows.append(fixed_row)

    with output_path.open("w", encoding="utf-8-sig", newline="") as dest:
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    with report_path.open("w", encoding="utf-8-sig", newline="") as report_file:
        writer = csv.DictWriter(
            report_file,
            fieldnames=["Handle", "Title", "Old series tags", "New series tag"],
        )
        writer.writeheader()
        writer.writerows(changed_products.values())

    return len(rows), len(changed_products)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fix BKS non-standard series tags.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    total_rows, changed_products = run(args.input, args.output, args.report)
    print(f"Rows written: {total_rows}")
    print(f"Products fixed: {changed_products}")
    print(f"Output: {args.output}")
    print(f"Report: {args.report}")


if __name__ == "__main__":
    main()
