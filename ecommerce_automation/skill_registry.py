from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any


BAKABO_STORE_DOMAIN = "bakabo.club"
BKS_SKILL_DIR = Path("BKS_SKILL/skills")

SKILL_PATTERN = "*_SKILL.md"
RELATED_SKILL_PATTERN = re.compile(r"`(bakabo-[a-z0-9-]+)`")


def registry_path(root_dir: Path) -> Path:
    return root_dir / "output" / "project_skill_registry.csv"


def index_path(root_dir: Path) -> Path:
    return root_dir / "docs" / "PROJECT_SKILLS_INDEX.md"


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _frontmatter_field(text: str, field: str) -> str:
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    for line in parts[1].splitlines():
        stripped = line.strip()
        if stripped.startswith(f"{field}:"):
            return stripped.split(":", 1)[1].strip().strip('"')
    return ""


def _frontmatter_description(text: str) -> str:
    return _frontmatter_field(text, "description")


def _frontmatter_trust_gate(text: str) -> str:
    return _frontmatter_field(text, "trust_gate")


def _title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _section_names(text: str) -> list[str]:
    return [line[3:].strip() for line in text.splitlines() if line.startswith("## ")]


def _phase_hint(skill_name: str, text: str) -> str:
    haystack = f"{skill_name} {text}".lower()
    if "openai" in haystack or "chatgpt" in haystack:
        return "AI / Agent OS"
    if "canva" in haystack:
        return "Creative connectors"
    if "hyperframes" in haystack or "motion graphics" in haystack or "html-to-video" in haystack:
        return "Motion / Video"
    if "design system" in haystack or "typography" in haystack:
        return "Tema Shopify / Design system"
    if "avatar" in haystack or "heygen" in haystack or "tiktok" in haystack:
        return "Avatar / Social Render"
    if "armocrom" in haystack or "palette" in haystack or "shooting" in haystack:
        return "Image Factory / Direzione artistica"
    if "web experience" in haystack or "homepage" in haystack or "ux" in haystack:
        return "Tema Shopify / UX"
    if "merchant" in haystack or "google" in haystack or "feed" in haystack:
        return "Google Merchant / Trust"
    if "social" in haystack or "campaign" in haystack or "instagram" in haystack:
        return "Social Campaigns"
    if "payment" in haystack or "checkout" in haystack or "stripe" in haystack:
        return "Payments / Checkout"
    if "member" in haystack or "tier" in haystack or "crm" in haystack:
        return "Members / CRM"
    if "inbox" in haystack or "email" in haystack or "smtp" in haystack:
        return "Official Inbox / Email"
    return "Project management"


def _skill_row(root_dir: Path, path: Path, name: str) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    sections = _section_names(text)
    related = sorted(set(RELATED_SKILL_PATTERN.findall(text)))
    return {
        "skill": name,
        "status": "active",
        "title": _title(text, name),
        "file": _relative(root_dir, path),
        "phase_hint": _phase_hint(name, text),
        "trust_gate": _frontmatter_trust_gate(text),
        "sections": len(sections),
        "description": _frontmatter_description(text),
        "related_skills": ";".join(related),
    }


def skill_rows(root_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    # Canonical: BKS_SKILL/skills/<name>/SKILL.md
    bks_root = root_dir / BKS_SKILL_DIR
    if bks_root.exists():
        for path in sorted(bks_root.glob("*/SKILL.md")):
            name = path.parent.name
            seen.add(name)
            rows.append(_skill_row(root_dir, path, name))
    # Legacy: docs/*_SKILL.md (skip if canonical already indexed)
    docs_dir = root_dir / "docs"
    if docs_dir.exists():
        for path in sorted(docs_dir.glob(SKILL_PATTERN)):
            name = path.name.removesuffix("_SKILL.md")
            if name in seen:
                continue
            rows.append(_skill_row(root_dir, path, name))
    return rows


def missing_related_rows(root_dir: Path) -> list[dict[str, Any]]:
    active = {row["skill"] for row in skill_rows(root_dir)}
    related: set[str] = set()
    for row in skill_rows(root_dir):
        related.update(item for item in row["related_skills"].split(";") if item)
    return [
        {
            "skill": name,
            "status": "missing_file",
            "title": name,
            "file": f"docs/{name}_SKILL.md",
            "phase_hint": "Referenced by active skills",
            "trust_gate": "",
            "sections": 0,
            "description": "Referenced by another BKS skill but not present in docs yet.",
            "related_skills": "",
        }
        for name in sorted(related - active)
    ]


def all_skill_rows(root_dir: Path) -> list[dict[str, Any]]:
    return skill_rows(root_dir) + missing_related_rows(root_dir)


def write_registry(root_dir: Path) -> dict[str, Any]:
    rows = all_skill_rows(root_dir)
    path = registry_path(root_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["skill", "status", "title", "file", "phase_hint", "trust_gate", "sections", "description", "related_skills"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    active_rows = [row for row in rows if row["status"] == "active"]
    missing_rows = [row for row in rows if row["status"] != "active"]
    md_lines = [
        "# Project Skill Registry",
        "",
        "Indice operativo delle skill BKS integrate nel Master.",
        "",
        "## Active skills",
        "",
    ]
    for row in active_rows:
        tg = f" `{row['trust_gate']}`" if row.get("trust_gate") else ""
        md_lines.append(f"- `{row['skill']}` - {row['phase_hint']}{tg} - `{row['file']}`")
    md_lines.extend(["", "## Missing referenced skills", ""])
    if missing_rows:
        for row in missing_rows:
            md_lines.append(f"- `{row['skill']}` - expected file `{row['file']}`")
    else:
        md_lines.append("- None")
    index_path(root_dir).write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    return {
        "rows": rows,
        "summary": {
            "active": len(active_rows),
            "missing": len(missing_rows),
            "registry": _relative(root_dir, path),
            "index": _relative(root_dir, index_path(root_dir)),
            "store": BAKABO_STORE_DOMAIN,
            "trust_gate": "trust_foundation",
        },
    }


def payload(root_dir: Path) -> dict[str, Any]:
    return write_registry(root_dir)
