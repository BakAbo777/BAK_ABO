import csv
import json
import re
import shutil
import unicodedata
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = Path(r"I:\BAKABO_CATALOG\collezioni")
WORK_DIR = ROOT / ".codex_work" / "collections_cleaning"
OUT_DIR = ROOT / "output" / "bks_clean_collections"
OUT_CSV_DIR = OUT_DIR / "csv"
REPORT_PATH = OUT_DIR / "bks_collection_cleaning_report.csv"
MANIFEST_PATH = OUT_DIR / "bks_collection_manifest.json"
ZIP_PATH = OUT_DIR / "bks_clean_collections_package.zip"

SOURCE_ZIPS = [
    "Women's Tee.csv.zip",
    "Collection_Dress_v04.zip",
    "collezione_backpack_v04.zip",
    "collezione_flip_flop_v01 (1).csv.zip",
    "Collezione_One-Piece_Swimsuit_v04.csv.zip",
    "collezione_puffer_v04.zip",
    "collezione_sneakers_v04.zip",
    "collezione_swim_trunks_final.zip",
    "collezione_travel_bag_final.zip",
    "collezione_windbreaker_v04.zip",
    "Cozy Slipper.csv.zip",
    "hawaiian.csv.zip",
    "pajama_pants.csv.zip",
    "Pullover_Hoodie_fixed.zip",
]

TYPE_RULES = {
    "Women's Tee.csv.zip": ("tee", "woman"),
    "Collection_Dress_v04.zip": ("cut-dress", "woman"),
    "collezione_backpack_v04.zip": ("backpack", "accessories"),
    "collezione_flip_flop_v01 (1).csv.zip": ("flip-flop", "man,woman"),
    "Collezione_One-Piece_Swimsuit_v04.csv.zip": ("one-piece-swimsuit", "woman"),
    "collezione_puffer_v04.zip": ("puffer-jacket", "man,woman"),
    "collezione_sneakers_v04.zip": ("sneakers", "man,woman"),
    "collezione_swim_trunks_final.zip": ("swim-trunks", "man"),
    "collezione_travel_bag_final.zip": ("travel-bag", "accessories"),
    "collezione_windbreaker_v04.zip": ("windbreaker", "man,woman"),
    "Cozy Slipper.csv.zip": ("slipper", "accessories"),
    "hawaiian.csv.zip": ("hawaiian-shirt", "man"),
    "pajama_pants.csv.zip": ("pajama-pants", "woman"),
    "Pullover_Hoodie_fixed.zip": ("pullover-hoodie", "man,woman"),
}

SERIES_RULES = [
    ("riviera", ["riviera", "beach", "aqua", "siren", "zora", "hawaiian", "swim", "one-piece", "flip"]),
    ("token", ["token", "pixel", "arcade", "digital", "low-bit"]),
    ("pulse", ["pulse", "optic", "tile", "kinetic", "geo", "matrix"]),
    ("marker", ["marker", "brush", "gesture", "paint", "expression"]),
    ("glyph", ["glyph", "symbol", "alphabet", "brut", "code"]),
    ("flag", ["flag", "block", "field", "dada"]),
    ("folklore", ["folklore", "garden", "animal", "naif"]),
    ("hours", ["hours", "urban", "material", "shadow", "montclair"]),
]

REQUIRED_COLUMNS = [
    "Handle",
    "Title",
    "Body (HTML)",
    "Vendor",
    "Product Category",
    "Type",
    "Tags",
    "Published",
    "Image Src",
    "Image Position",
    "Image Alt Text",
    "SEO Title",
    "SEO Description",
    "Status",
]

OLD_PATCH_TAG_PREFIXES = (
    "brand:",
    "collection:",
    "series:",
    "macro:",
    "type:",
    "visual:",
    "use-case:",
    "status:",
    "curation:",
    "drop:",
    "print-type:",
)

EU_REP = (
    "<p><strong>EU Representative:</strong> HONSON VENTURES LIMITED, "
    "gpsr@honsonventures.com, Gnaftis House flat 102, Limassol, "
    "Mesa Geitonia, 4003, CY.</p>"
)
MTO = (
    "<p><strong>Made to order.</strong> Each BKS Studio piece is produced after "
    "purchase to reduce overproduction. Production time comes before shipping time.</p>"
)


def safe_name(value: str) -> str:
    value = value.replace(".zip", "")
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")


def strip_symbols(value: str) -> str:
    out = []
    for ch in str(value or ""):
        cat = unicodedata.category(ch)
        if cat == "So" or ch in {"️"}:
            continue
        out.append(ch)
    return "".join(out)


def clean_public_text(value: str) -> str:
    text = strip_symbols(value)
    protected = {
        "__BKS_DOMAIN__": "bakabo.club",
        "__BKS_ENRICHED__": "bakabo-enriched",
    }
    text = re.sub(r"bakabo\.club", "__BKS_DOMAIN__", text, flags=re.I)
    text = re.sub(r"\bbakabo-enriched\b", "__BKS_ENRICHED__", text, flags=re.I)
    text = re.sub(r"BAK\s*\|\s*ABO|BAK\s+ABO|BAKABO|BakAbo|Bakabo", "BKS Studio", text)
    text = re.sub(
        r"\b(?:brand|collection|series|macro|type|visual|use-case|status|curation|drop|print-type):[A-Za-z0-9._-]+,?\s*",
        "",
        text,
        flags=re.I,
    )
    for marker, replacement in protected.items():
        text = text.replace(marker, replacement)
    return re.sub(r"\s+", " ", text).strip()


def slugify(value: str) -> str:
    text = strip_symbols(value).lower()
    text = re.sub(r"bakabo|bks studio", "bks", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-") or "bks-product"


def read_csv(path: Path):
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            with path.open("r", encoding=enc, newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                return reader.fieldnames or [], rows, enc
        except UnicodeDecodeError:
            continue
    raise UnicodeError(f"Cannot read {path}")


def write_csv(path: Path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def infer_series(row):
    blob = " ".join([row.get("Handle", ""), row.get("Title", ""), row.get("Tags", "")]).lower()
    for collection, keys in SERIES_RULES:
        if f"collection:{collection}" in blob or any(k in blob for k in keys):
            return collection
    return "hours"


def merge_tags(existing, additions):
    out = []
    seen = set()
    for tag in list(existing) + list(additions):
        cleaned = clean_public_text(tag.strip())
        if not cleaned:
            continue
        key = cleaned.lower()
        if key.startswith(OLD_PATCH_TAG_PREFIXES):
            continue
        if key in {"bakabo-enriched", "ai-generated wearable art", "bks studio"}:
            continue
        if key not in seen:
            seen.add(key)
            out.append(cleaned)
    return ", ".join(out)


def title_from_row(row):
    title = clean_public_text(row.get("Title") or row.get("Handle") or "BKS Studio Product")
    title = title.replace("(BKS)", "").replace(" BKS ", " ")
    return re.sub(r"\s+", " ", title).strip()


def ensure_body(row):
    body = clean_public_text(row.get("Body (HTML)", ""))
    low = body.lower()
    additions = []
    if "made to order" not in low and "made-to-order" not in low:
        additions.append(MTO)
    if "honson ventures limited" not in low:
        additions.append(EU_REP)
    return (body + "\n" + "\n".join(additions)).strip()


def clean_rows(source_zip, csv_path, fieldnames, rows):
    type_tag, nav_tags = TYPE_RULES[source_zip]
    final_fields = list(fieldnames)
    for col in REQUIRED_COLUMNS:
        if col not in final_fields:
            final_fields.append(col)

    cleaned = []
    report = {
        "source_zip": source_zip,
        "csv_file": str(csv_path),
        "input_rows": len(rows),
        "input_products": len({r.get("Handle", "") for r in rows if r.get("Handle", "")}),
        "emoji_cleaned": 0,
        "brand_cleaned": 0,
        "handles_changed": 0,
        "missing_columns_added": ",".join([c for c in REQUIRED_COLUMNS if c not in fieldnames]),
    }

    for row in rows:
        original_blob = " ".join(str(v) for v in row.values())
        if re.search(r"[\U00010000-\U0010ffff]|️", original_blob):
            report["emoji_cleaned"] += 1
        if re.search(r"BAK\s*\|\s*ABO|BAK\s+ABO|BAKABO|BakAbo|Bakabo", original_blob):
            report["brand_cleaned"] += 1

        out = {field: clean_public_text(row.get(field, "")) for field in final_fields}
        old_handle = out.get("Handle", "")
        if old_handle:
            out["Handle"] = slugify(old_handle)
            if out["Handle"] != old_handle:
                report["handles_changed"] += 1

        title = title_from_row(out)
        collection = infer_series(out)
        nav_list = [m.strip() for m in nav_tags.split(",") if m.strip()]
        bks_tags = [
            "bks",
            collection,
            type_tag,
            *nav_list,
            "print-on-demand",
            "made-to-order",
            "active",
        ]

        out["Title"] = title
        out["Vendor"] = out.get("Vendor") or "MWW On Demand"
        out["Type"] = type_tag
        out["Tags"] = merge_tags((out.get("Tags") or "").split(","), bks_tags)
        out["Body (HTML)"] = ensure_body(out)
        out["SEO Title"] = f"{title} | BKS Studio"[:70]
        out["SEO Description"] = (
            f"{title} by BKS Studio. AI-generated wearable art, printed on demand "
            f"and made to order to reduce overproduction."
        )[:160]
        if out.get("Image Src") and not out.get("Image Alt Text"):
            out["Image Alt Text"] = f"BKS Studio {title} {type_tag}, front view on Bone background"
        elif out.get("Image Alt Text"):
            out["Image Alt Text"] = clean_public_text(out["Image Alt Text"])
        out["Status"] = out.get("Status") or "active"
        out["Published"] = out.get("Published") or "TRUE"
        cleaned.append(out)

    report["output_rows"] = len(cleaned)
    report["output_products"] = len({r.get("Handle", "") for r in cleaned if r.get("Handle", "")})
    return final_fields, cleaned, report


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUT_CSV_DIR.mkdir(parents=True, exist_ok=True)

    reports = []
    manifest = {"sources": [], "visual_standard": {
        "product_mockup_ratio": "4:5",
        "editorial_ratio": "16:9",
        "compact_ratio": "1:1",
        "backgrounds": {"bone": "#EFEAE0", "salt": "#FAFAF7", "shadow": "#242833", "onyx": "#0A0A0A"},
        "temperature": "5500-6000K",
        "forbidden": ["third-party overlays", "Printify watermarks", "commercial smile poses", "oversaturation", "cold blue cast"],
    }}

    for source_zip in SOURCE_ZIPS:
        src = SOURCE_DIR / source_zip
        target = WORK_DIR / safe_name(source_zip)
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(src) as zf:
            zf.extractall(target)
        csvs = sorted(target.rglob("*.csv"))
        if not csvs:
            reports.append({"source_zip": source_zip, "csv_file": "", "input_rows": 0, "input_products": 0, "error": "no csv"})
            continue
        for csv_path in csvs:
            fieldnames, rows, enc = read_csv(csv_path)
            final_fields, cleaned, report = clean_rows(source_zip, csv_path, fieldnames, rows)
            out_name = safe_name(source_zip) + "__" + csv_path.stem.replace(" ", "_") + "__clean.csv"
            out_path = OUT_CSV_DIR / out_name
            write_csv(out_path, final_fields, cleaned)
            report["encoding"] = enc
            report["output_csv"] = str(out_path)
            reports.append(report)
            manifest["sources"].append(report)

    report_fields = sorted({k for report in reports for k in report})
    write_csv(REPORT_PATH, report_fields, reports)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in OUT_CSV_DIR.rglob("*.csv"):
            zf.write(path, path.relative_to(OUT_DIR))
        zf.write(REPORT_PATH, REPORT_PATH.relative_to(OUT_DIR))
        zf.write(MANIFEST_PATH, MANIFEST_PATH.relative_to(OUT_DIR))

    print(json.dumps({"reports": len(reports), "package": str(ZIP_PATH), "report": str(REPORT_PATH)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
