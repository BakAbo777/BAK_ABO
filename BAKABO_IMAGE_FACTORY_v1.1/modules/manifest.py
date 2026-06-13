"""BKS Studio — Manifest: save per-product run logs as CSV + JSON."""
from __future__ import annotations
import csv
import json
import logging
from datetime import datetime
from pathlib import Path

log = logging.getLogger("bif.manifest")


def save(result: dict, output_dir: Path, product_title: str, source_image: Path) -> dict:
    """Save manifest.json and manifest.csv for a completed product run."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().isoformat(timespec="seconds")

    # ── Build records list ─────────────────────────────────────────────────
    records: list[dict] = []
    for slot, gen_list in (result.get("generated") or {}).items():
        qa_list = (result.get("qa") or {}).get(slot, [])
        for i, gen in enumerate(gen_list):
            qa  = qa_list[i] if i < len(qa_list) else {}
            records.append({
                "timestamp":      ts,
                "product_title":  product_title,
                "slug":           result.get("seo", {}).get("handle", ""),
                "collection":     result.get("collection", ""),
                "product_type":   result.get("product_type", ""),
                "slot":           slot,
                "variant":        i + 1,
                "status":         gen.get("status", ""),
                "qa_score":       qa.get("score", ""),
                "qa_approved":    qa.get("approved", ""),
                "output_jpg":     str(gen.get("output_jpg") or ""),
                "output_png":     str(gen.get("output_png") or ""),
                "error":          gen.get("error", ""),
            })

    # ── JSON ──────────────────────────────────────────────────────────────
    manifest_json = {
        "timestamp":     ts,
        "product_title": product_title,
        "source_image":  str(source_image),
        "collection":    result.get("collection"),
        "product_type":  result.get("product_type"),
        "detection":     result.get("detection"),
        "seo":           result.get("seo"),
        "records":       records,
    }
    json_path = output_dir / "manifest.json"
    json_path.write_text(json.dumps(manifest_json, indent=2, ensure_ascii=False), encoding="utf-8")

    # ── CSV ───────────────────────────────────────────────────────────────
    csv_path = output_dir / "manifest.csv"
    if records:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
            writer.writeheader()
            writer.writerows(records)

    log.info("Manifest saved: %s (%d records)", output_dir, len(records))
    return {"json": json_path, "csv": csv_path, "records": records}


def load(manifest_dir: Path) -> dict | None:
    """Load a previously saved manifest.json."""
    p = manifest_dir / "manifest.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def append_global(record: dict, global_csv: Path) -> None:
    """Append a single record to the global runs log."""
    global_csv.parent.mkdir(parents=True, exist_ok=True)
    write_header = not global_csv.exists()
    with open(global_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(record.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(record)
