#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export the BKS V19 collection plan as operational files."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bks_collection_specs import (  # noqa: E402
    ALL_COLLECTIONS,
    LEGACY_COLLECTION_METAFIELDS,
    MISSING_COLLECTION_HANDLES,
    TEMPLATE_EXCLUDED_HANDLES,
    collection_to_payload,
)


DOCS_PATH = ROOT / "docs" / "BKS_Collections_Complete_v1.md"
EXTERNAL_DOCS_PATH = Path("I:/BAKABO_CATALOG/CREAZIONE/COLLEZIONI FOTO/BKS_Collections_Complete_v1.md")
OUTPUT_DIR = ROOT / "output"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def source_markdown() -> str:
    path = DOCS_PATH if DOCS_PATH.exists() else EXTERNAL_DOCS_PATH
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def extract_between(text: str, start_marker: str, end_marker: str | None = None) -> str:
    if start_marker not in text:
        return ""
    chunk = text.split(start_marker, 1)[1]
    if end_marker and end_marker in chunk:
        chunk = chunk.split(end_marker, 1)[0]
    return f"{start_marker}{chunk}".strip() + "\n"


def export_plan() -> list[Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    plan_rows = [spec.to_row() for spec in ALL_COLLECTIONS]
    plan_path = OUTPUT_DIR / "bks_collection_plan_v20.csv"
    write_csv(plan_path, plan_rows)
    written.append(plan_path)

    template_rows = [
        {
            "collection": spec.title,
            "handle": spec.handle,
            "base_template": spec.template,
            "template": spec.effective_template,
            "template_suffix": spec.template_suffix or "",
            "template_scope": spec.template_scope,
            "batch": "missing-16" if spec.handle in MISSING_COLLECTION_HANDLES else "existing/core",
        }
        for spec in ALL_COLLECTIONS
    ]
    template_path = OUTPUT_DIR / "bks_collection_template_assignment_v20.csv"
    write_csv(template_path, template_rows)
    written.append(template_path)

    exclusions_path = OUTPUT_DIR / "bks_collection_template_exclusions_v20.csv"
    write_csv(
        exclusions_path,
        [
            {
                "handle": handle,
                "template": "collection",
                "reason": "Default collection: system/automatic collection excluded from BKS custom templates",
            }
            for handle in sorted(TEMPLATE_EXCLUDED_HANDLES)
        ],
    )
    written.append(exclusions_path)

    payload_path = OUTPUT_DIR / "bks_collection_payloads_v20.json"
    payload_path.write_text(
        json.dumps(
            {
                spec.handle: collection_to_payload(spec)["smart_collection"]
                for spec in ALL_COLLECTIONS
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    written.append(payload_path)

    audit_path = OUTPUT_DIR / "bks_collection_legacy_metafields_audit_v20.csv"
    write_csv(audit_path, list(LEGACY_COLLECTION_METAFIELDS))
    written.append(audit_path)

    checklist_path = OUTPUT_DIR / "bks_collection_legacy_metafields_delete_checklist_v20.md"
    checklist_lines = [
        "# BKS Collection Legacy Metafields — Delete Checklist",
        "",
        "Percorso Shopify: Settings -> Custom data -> Metafields -> Collections.",
        "Eliminare solo le definizioni legacy con emoji o naming non più coerente.",
        "",
    ]
    for item in LEGACY_COLLECTION_METAFIELDS:
        checklist_lines.append(f"- [ ] `{item['label']}` — {item['problem']} — {item['action']}")
    checklist_path.write_text("\n".join(checklist_lines) + "\n", encoding="utf-8")
    written.append(checklist_path)

    md = source_markdown()
    prompts = extract_between(md, "# PARTE 3 — PROMPT IMMAGINI CATEGORY COVERS", "# APPENDICE")
    prompts_path = OUTPUT_DIR / "bks_collection_image_prompts_v20.md"
    if prompts:
        prompts_path.write_text(prompts, encoding="utf-8")
    else:
        prompts_path.write_text(
            "# BKS Collection Image Prompts V19\n\nFonte markdown non trovata. Copiare `BKS_Collections_Complete_v1.md` in `docs/` e rilanciare.\n",
            encoding="utf-8",
        )
    written.append(prompts_path)

    return written


def main() -> int:
    for path in export_plan():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
