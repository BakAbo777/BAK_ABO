from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any


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


def _frontmatter_description(text: str) -> str:
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    for line in parts[1].splitlines():
        if line.strip().startswith("description:"):
            return line.split(":", 1)[1].strip().strip('"')
    return ""


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
    return "Project management"


def skill_rows(root_dir: Path) -> list[dict[str, Any]]:
    docs_dir = root_dir / "docs"
    rows: list[dict[str, Any]] = []
    if not docs_dir.exists():
        return rows
    for path in sorted(docs_dir.glob(SKILL_PATTERN)):
        text = path.read_text(encoding="utf-8")
        name = path.name.removesuffix("_SKILL.md")
        sections = _section_names(text)
        related = sorted(set(RELATED_SKILL_PATTERN.findall(text)))
        rows.append(
            {
                "skill": name,
                "status": "active",
                "title": _title(text, name),
                "file": _relative(root_dir, path),
                "phase_hint": _phase_hint(name, text),
                "sections": len(sections),
                "description": _frontmatter_description(text),
                "related_skills": ";".join(related),
            }
        )
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
    fieldnames = ["skill", "status", "title", "file", "phase_hint", "sections", "description", "related_skills"]
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
        md_lines.append(f"- `{row['skill']}` - {row['phase_hint']} - `{row['file']}`")
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
        },
    }


def payload(root_dir: Path) -> dict[str, Any]:
    return write_registry(root_dir)
