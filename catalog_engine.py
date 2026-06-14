from __future__ import annotations

import csv
import shutil
import threading
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

from bks_assets import active_catalog_csv, relative_to_base, save_active_assets
from tools.enrich_shopify_catalog import enrich


BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
CATALOG_DIR = BASE_DIR / "collezioni_csv"
UPDATED_CSV = OUTPUT_DIR / "products_export_updated.csv"
SEO_REPORT = OUTPUT_DIR / "seo_report.csv"
PACKAGE_ZIP = OUTPUT_DIR / "bakabo_export_package.zip"

app = Flask(__name__, template_folder="templates", static_folder="static")

PROGRESS: dict[str, Any] = {
    "active": False,
    "progress": 0,
    "total": 0,
    "current": "Pronto",
    "errors": [],
}


def read_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        return [], []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), reader.fieldnames or []


def split_tags(value: str) -> list[str]:
    return [tag.strip() for tag in (value or "").split(",") if tag.strip()]


def tag_value(tags: list[str], prefix: str) -> str:
    for tag in tags:
        if tag.lower().startswith(prefix.lower()):
            return tag.split(":", 1)[1].strip()
    return ""


def product_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if (row.get("Title") or "").strip()]


def catalog_summary(path: Path) -> dict[str, Any]:
    rows, _ = read_rows(path)
    products = product_rows(rows)
    image_rows = [row for row in rows if (row.get("Image Src") or "").strip()]
    return {
        "ok": path.exists(),
        "file": relative_to_base(path),
        "rows": len(rows),
        "handles": len({(row.get("Handle") or "").strip() for row in rows if (row.get("Handle") or "").strip()}),
        "products": len(products),
        "image_rows": len(image_rows),
        "rembg_available": False,
        "missing_seo_title": sum(1 for row in products if not (row.get("SEO Title") or "").strip()),
        "missing_seo_description": sum(1 for row in products if not (row.get("SEO Description") or "").strip()),
        "missing_alt": sum(1 for row in image_rows if not (row.get("Image Alt Text") or "").strip()),
        "types": dict(Counter((row.get("Type") or "Unspecified").strip() for row in products).most_common(12)),
        "vendors": dict(Counter((row.get("Vendor") or "Unspecified").strip() for row in products).most_common(8)),
    }


def curation_stats(path: Path) -> dict[str, Any]:
    rows, fieldnames = read_rows(path)
    products = product_rows(rows)
    keep_counts = Counter()
    active_by_series = Counter()
    active_by_type = Counter()
    series_counts = Counter()
    status_counts = Counter()

    for row in products:
        tags = split_tags(row.get("Tags", ""))
        status = (row.get("Status") or "").strip().lower() or "empty"
        status_counts[status] += 1
        series = tag_value(tags, "collection:") or tag_value(tags, "series:") or "unassigned"
        product_type = tag_value(tags, "type:") or (row.get("Type") or "unassigned")
        series_counts[series] += 1

        if "curation:keep" in {tag.lower() for tag in tags} or status == "active":
            keep_counts["Yes"] += 1
            active_by_series[series] += 1
            active_by_type[product_type] += 1
        elif status == "draft":
            keep_counts["No"] += 1
        else:
            keep_counts["Empty"] += 1

    return {
        "ok": path.exists(),
        "products": len(products),
        "keep_counts": dict(keep_counts),
        "active_by_series": dict(active_by_series.most_common(20)),
        "active_by_type": dict(active_by_type.most_common(20)),
        "series_counts": dict(series_counts.most_common(20)),
        "status_counts": dict(status_counts.most_common(12)),
        "target": {"min_total": 90, "max_total": 150, "min_per_collection": 8, "max_per_collection": 22},
        "columns": {
            "keep": "Tags/curation:keep" if "Tags" in fieldnames else "",
            "series": "Tags/collection:*" if "Tags" in fieldnames else "",
        },
    }


def package_outputs(csv_path: Path, report_path: Path) -> None:
    PACKAGE_ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(PACKAGE_ZIP, "w", zipfile.ZIP_DEFLATED) as package:
        if csv_path.exists():
            package.write(csv_path, arcname=csv_path.name)
        if report_path.exists():
            package.write(report_path, arcname=report_path.name)


def run_enrichment(source: Path) -> None:
    try:
        PROGRESS.update({"active": True, "progress": 0, "total": 3, "current": "Lettura CSV", "errors": []})
        CATALOG_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        stem = source.stem.removesuffix("_SEO_TAGS_READY")
        ready_csv = CATALOG_DIR / f"{stem}_SEO_TAGS_READY.csv"
        PROGRESS.update({"progress": 1, "current": "Completo SEO, tag e metafield"})
        enrich(source, ready_csv, SEO_REPORT)

        PROGRESS.update({"progress": 2, "current": "Creo export e ZIP"})
        shutil.copy2(ready_csv, UPDATED_CSV)
        package_outputs(ready_csv, SEO_REPORT)
        save_active_assets(catalog_csv=ready_csv)

        PROGRESS.update({"progress": 3, "current": "Completato", "active": False})
    except Exception as exc:  # noqa: BLE001
        PROGRESS["errors"].append(f"{type(exc).__name__}: {exc}")
        PROGRESS.update({"current": "Errore", "active": False})


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/summary")
def api_summary():
    path = active_catalog_csv()
    summary = catalog_summary(path)
    if not summary["ok"]:
        return jsonify({"ok": False, "error": f"CSV non trovato: {relative_to_base(path)}"}), 404
    return jsonify(summary)


@app.get("/api/curation/stats")
def api_curation_stats():
    path = active_catalog_csv()
    stats = curation_stats(path)
    if not stats["ok"]:
        return jsonify({"ok": False, "error": f"CSV non trovato: {relative_to_base(path)}"}), 404
    return jsonify(stats)


@app.post("/api/upload")
def api_upload():
    file = request.files.get("csv")
    if not file or not file.filename:
        return jsonify({"ok": False, "error": "CSV mancante"}), 400
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = secure_filename(file.filename) or "catalog_upload.csv"
    target = INPUT_DIR / filename
    file.save(target)
    save_active_assets(catalog_csv=target)
    return jsonify(catalog_summary(target))


@app.post("/api/process")
def api_process():
    if PROGRESS.get("active"):
        return jsonify({"ok": False, "error": "Elaborazione gia' in corso"}), 409
    source = active_catalog_csv()
    if source is None or not source.exists():
        return jsonify({"ok": False, "error": f"CSV non trovato: {relative_to_base(source)}"}), 404
    threading.Thread(target=run_enrichment, args=(source,), daemon=True).start()
    return jsonify({"ok": True, "message": "Elaborazione avviata."})


@app.get("/api/progress")
def api_progress():
    return jsonify(PROGRESS)


@app.get("/api/preview")
def api_preview():
    path = active_catalog_csv()
    rows, _ = read_rows(path)
    products = product_rows(rows)[:6]
    preview = []
    for row in products:
        tags = split_tags(row.get("Tags", ""))
        collection = tag_value(tags, "collection:") or "glyph"
        product_type = (row.get("Type") or "").strip() or "AOP"
        preview.append({
            "title": (row.get("Title") or "").strip()[:48],
            "handle": (row.get("Handle") or "").strip(),
            "collection": collection,
            "type": product_type,
            "image": (row.get("Image Src") or "").strip(),
            "price": (row.get("Variant Price") or "").strip(),
        })
    return jsonify({"ok": bool(preview), "products": preview})


@app.get("/download/csv")
def download_csv():
    path = active_catalog_csv()
    if UPDATED_CSV.exists():
        path = UPDATED_CSV
    if path is None or not path.exists():
        return jsonify({"ok": False, "error": "CSV non trovato"}), 404
    return send_file(path, as_attachment=True)


@app.get("/download/seo")
def download_seo():
    if not SEO_REPORT.exists():
        return jsonify({"ok": False, "error": "SEO report non ancora generato"}), 404
    return send_file(SEO_REPORT, as_attachment=True)


@app.get("/download/zip")
def download_zip():
    if not PACKAGE_ZIP.exists():
        return jsonify({"ok": False, "error": "Pacchetto ZIP non ancora generato"}), 404
    return send_file(PACKAGE_ZIP, as_attachment=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
