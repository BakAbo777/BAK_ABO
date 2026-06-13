"""Audit BKS files for legal/copy references that need review before launch."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "output" / "legal_reference_audit_v20.csv"
OUT_MD = ROOT / "output" / "legal_reference_audit_v20.md"

TEXT_SUFFIXES = {".csv", ".md", ".html", ".txt", ".json", ".liquid"}
SCAN_ROOTS = [
    ROOT / "docs",
    ROOT / "output",
    ROOT / "tools",
    ROOT / ".codex_work" / "BKS_V20_collections_theme" / "BKS_V19_work" / "templates",
    ROOT / ".codex_work" / "BKS_V20_collections_theme" / "BKS_V19_work" / "sections",
    ROOT / ".codex_work" / "BKS_V20_collections_theme" / "BKS_V19_work" / "snippets",
]

PATTERNS = {
    "legacy_warranty_directive": re.compile(r"Directive\s+1999/44/EC", re.I),
    "broad_gdpr_claim": re.compile(r"GDPR compliant", re.I),
    "generic_newsletter_subscribe": re.compile(r"Button:\s+Subscribe|>\s*Subscribe\s*<", re.I),
    "review_placeholder_risk": re.compile(r"fake review|placeholder review|testimonial placeholder", re.I),
}


def iter_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        if root.is_file():
            candidates = [root]
        else:
            candidates = list(root.rglob("*"))
        for path in candidates:
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            if ".zip" in path.suffixes:
                continue
            files.append(path)
    return sorted(set(files))


def main() -> None:
    rows: list[dict[str, str | int]] = []
    for path in iter_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for key, pattern in PATTERNS.items():
                if pattern.search(line):
                    rows.append(
                        {
                            "issue": key,
                            "file": str(path.relative_to(ROOT)),
                            "line": line_no,
                            "excerpt": line.strip()[:280],
                        }
                    )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["issue", "file", "line", "excerpt"])
        writer.writeheader()
        writer.writerows(rows)

    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["issue"])] = counts.get(str(row["issue"]), 0) + 1

    lines = [
        "# BKS Legal Reference Audit V20",
        "",
        "This audit finds copy/legal references that should be reviewed before import or publication.",
        "",
        "| Issue | Count | Action |",
        "|---|---:|---|",
    ]
    actions = {
        "legacy_warranty_directive": "Replace with Directive (EU) 2019/771 and applicable national consumer law before publishing/importing.",
        "broad_gdpr_claim": "Avoid broad compliance claims; use privacy-rights wording unless legal counsel approves.",
        "generic_newsletter_subscribe": "Use `Join the archive` for the BKS Archive newsletter CTA.",
        "review_placeholder_risk": "Do not publish placeholder/fake review content; use verified review data only.",
    }
    for key in PATTERNS:
        lines.append(f"| {key} | {counts.get(key, 0)} | {actions[key]} |")
    lines.extend(
        [
            "",
            f"Detailed CSV: `{OUT_CSV.relative_to(ROOT)}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Audited {len(iter_files())} files")
    print(f"Findings: {len(rows)}")
    for key in PATTERNS:
        print(f"{key}: {counts.get(key, 0)}")


if __name__ == "__main__":
    main()
