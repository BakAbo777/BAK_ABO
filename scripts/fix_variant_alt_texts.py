"""Fix Shopify variant image alt texts that contain 'Printify'.

Strategy:
  - Pass 1: collect the correct alt text for each product from Image Position == 1
  - Pass 2: for every variant row whose alt text contains 'Printify', replace it
            with the position-1 alt text for that product.

Input:  output/products_export_updated.csv  (or pass --input <path>)
Output: output/products_export_alt_fixed.csv
"""
from __future__ import annotations
import argparse
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def cli() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--input",  default=str(ROOT / "output" / "products_export_updated.csv"))
    p.add_argument("--output", default=str(ROOT / "output" / "products_export_alt_fixed.csv"))
    return p.parse_args()


def clean_alt(text: str) -> str:
    text = text.replace("™", "")          # remove ™
    text = re.sub(r"\s*Printify\s+bakabo\.club", "", text)
    text = re.sub(r"\s*Printify\s+BKS\s+Studio", "", text)
    text = re.sub(r"\s*Printify\b", "", text)
    return text.strip()


def main() -> None:
    args = cli()
    src = Path(args.input)
    dst = Path(args.output)

    if not src.exists():
        print(f"ERROR: input not found: {src}")
        return

    # Pass 1 — build handle → correct alt text from Image Position 1
    main_alts: dict[str, str] = {}
    with src.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            handle = (row.get("Handle") or "").strip()
            pos    = (row.get("Image Position") or "").strip()
            alt    = (row.get("Image Alt Text") or "").strip()
            if handle and pos == "1" and alt and "Printify" not in alt:
                main_alts[handle] = alt

    print(f"Products with clean position-1 alt: {len(main_alts)}")

    # Pass 2 — rewrite, replacing bad alt texts
    fixed = 0
    current_handle = ""

    with src.open(encoding="utf-8-sig", newline="") as fi, \
         dst.open("w", encoding="utf-8-sig", newline="") as fo:

        reader = csv.DictReader(fi)
        fieldnames = [f for f in reader.fieldnames if f is not None]
        writer = csv.DictWriter(fo, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        for row in reader:
            row.pop(None, None)  # drop extra columns beyond header count
            h = (row.get("Handle") or "").strip()
            if h:
                current_handle = h

            alt = row.get("Image Alt Text") or ""
            if "Printify" in alt:
                if current_handle in main_alts:
                    row["Image Alt Text"] = main_alts[current_handle]
                else:
                    row["Image Alt Text"] = clean_alt(alt)
                fixed += 1

            writer.writerow(row)

    print(f"Alt texts fixed : {fixed}")
    print(f"Output          : {dst}")


if __name__ == "__main__":
    main()
