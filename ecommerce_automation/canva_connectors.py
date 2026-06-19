from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

BAKABO_STORE_DOMAIN = "bakabo.club"
BKS_TM04_THEME_ID = "202392961362"
BKS_COLLECTIONS = ("Hours", "Glyph", "Marker", "Riviera", "Pulse", "Token", "Flag", "Origin")

TOOLSET_CSV = Path("output/canva_connector_toolset.csv")
# Skill lives alongside other resident skills — not in docs/
SKILL_DOC = Path("BKS_SKILL/skills/bakabo-canva-connectors/SKILL.md")


TOOL_GROUPS: tuple[dict[str, str], ...] = (
    {
        "group": "Interactive AI",
        "trust_gate": "collection_identity",
        "tools": "Generate Design with AI; Generate Structured Design with AI; Request User Review of Presentation Outline; Search Designs",
        "use": "Create candidate visuals, structured documents and presentation outlines from BKS briefs.",
        "agent_rule": "Use for drafts and candidates; request review before converting into official assets. Key visual to target collection accent color.",
    },
    {
        "group": "Discovery / Read",
        "trust_gate": "trust_foundation",
        "tools": "Search Designs; Search Brand Templates; Search Folders; List Folder Items; Resolve Shortlink",
        "use": "Find existing BKS designs, folders, brand templates and shared links.",
        "agent_rule": "Use Search Brand Templates for templates/autofill; use Search Designs only for existing designs.",
    },
    {
        "group": "Brand / Dataset",
        "trust_gate": "trust_foundation",
        "tools": "List Brand Kits; Get Brand Template Dataset; Get Assets Metadata",
        "use": "Understand BKS brand kits, fillable template fields and reusable assets.",
        "agent_rule": "Prefer Brand Kit and dataset-backed templates before free generation.",
    },
    {
        "group": "Design Readback",
        "trust_gate": "trust_foundation",
        "tools": "Get Design Information; Get Design Text Content; Get Design Pages; Get Design Page Thumbnail; Get Presenter Notes; Get Export Formats",
        "use": "Audit text, pages, thumbnails, notes and export options before editing or exporting.",
        "agent_rule": "Read design content before making edits; preserve BKS naming, series and typography.",
    },
    {
        "group": "Collaboration",
        "trust_gate": "collection_identity",
        "tools": "List Design Comments; List Comment Replies; Add Comment To Design; Reply To Comment; Resolve Comment",
        "use": "Run human review loops on campaigns, presentations and social packs.",
        "agent_rule": "Use comments for approvals and change requests; never silently overwrite reviewed work.",
    },
    {
        "group": "Create / Edit",
        "trust_gate": "collection_identity",
        "tools": "Create Design From Candidate; Create Design from Brand Template; Create Brand Template Draft; Start Editing Design; Edit Design; Save Design Edits; Discard Design Edits",
        "use": "Turn candidates/templates into editable BKS assets, edit them and save only approved changes.",
        "agent_rule": "A generated candidate must become a design before edit/export/resize; official saves require review.",
    },
    {
        "group": "Asset / Layout Ops",
        "trust_gate": "collection_identity",
        "tools": "Copy Design; Merge Designs; Resize Design; Import Design From Public HTTPS URL; Upload Asset From URL; Move Item To Folder; Create Folder",
        "use": "Build campaign packs, adapt formats and organize Canva assets by collection/channel.",
        "agent_rule": "Resize for each channel after source approval; keep one folder per BKS collection.",
    },
    {
        "group": "Output",
        "trust_gate": "conversion_support",
        "tools": "Export Design; Publish Brand Template",
        "use": "Export approved visuals or publish reusable BKS brand templates.",
        "agent_rule": "Export is allowed after review and trust_gate: conversion_support. Publishing brand templates requires explicit approval.",
    },
)


WORKFLOWS: tuple[dict[str, str], ...] = (
    {
        "workflow": "BKS Social Pack",
        "trust_gate": "collection_identity",
        "input": "Collection name, product URL, approved image/video, caption brief, language.",
        "sequence": "Brand Kit -> brand template search -> dataset/autofill or AI candidate -> review -> resize per channel -> export.",
        "output": "Instagram, TikTok, YouTube Shorts thumbnail/story, Pinterest pin and email visual.",
    },
    {
        "workflow": "Avatar Campaign Visual",
        "trust_gate": "collection_identity",
        "input": "HeyGen render MP4, 9:16 hero image, collection identity, TM04 accent hex, CTA.",
        "sequence": "Read social render sheet -> generate/resize Canva layouts keyed to collection accent -> comment review -> export.",
        "output": "Video cover, thumbnail, story frame and post carousel.",
    },
    {
        "workflow": "BKS Presentation / Pitch",
        "trust_gate": "trust_foundation",
        "input": "Campaign brief, product logic, Google trust status, catalog metrics.",
        "sequence": "Request outline review -> generate structured design -> readback -> comment review -> export.",
        "output": "Pitch deck, internal report or partner presentation.",
    },
    {
        "workflow": "Catalog / Collection Sheet",
        "trust_gate": "collection_identity",
        "input": "Shopify/Printify CSV, product titles, collection images, price/status data.",
        "sequence": "Search template -> get dataset -> autofill -> inspect pages/text -> save approved design.",
        "output": "Collection catalogue, product one-pager or sales sheet.",
    },
    {
        "workflow": "BKS Drop Release Pack",
        "trust_gate": "collection_identity",
        "input": "Drop collection (one of 8 BKS collections), TM04 accent hex, BKS release formula stage, Shopify discount code if active.",
        "sequence": "Pick collection accent -> generate hero banner (left 40% clear for TM04 signal) -> resize for email/story/post -> add countdown or discount block -> comment review -> export.",
        "output": "Hero banner, email header, story countdown, social announcement post.",
    },
)


GUARDRAILS: tuple[str, ...] = (
    "Read before write: inspect designs, templates and datasets before editing.",
    "Use Brand Kit when available; otherwise use bakabo-design-system tokens.",
    "Generated designs are candidates until converted and reviewed.",
    "Use templates/autofill for repeated catalog and campaign formats.",
    "Do not invent discounts, partnerships, certifications, awards or product claims.",
    "Do not publish brand templates, overwrite official designs or export public campaign assets without approval.",
    "Preserve BKS plus collection/series naming and remove emoji/decorative symbols from public titles.",
    "Never use 'Folklore' as a collection name or folder name — the collection is named Origin.",
    "Key each design's dominant accent color to the target BKS collection (from hyperframes_connectors.COLLECTION_ACCENTS). Do not mix accents across collections in a single asset.",
    "Hero banners for collection drops must leave the left 40% of the image clear — TM04 editorial signal space.",
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _configured(settings: Any) -> bool:
    return bool(str(getattr(settings, "canva_api_key", "") or "").strip())


_READ_ONLY_GROUPS = {"Discovery / Read", "Brand / Dataset", "Design Readback"}
_OUTPUT_GROUPS = {"Output"}


def rows(settings: Any) -> list[dict[str, Any]]:
    status = "configured" if _configured(settings) else "connector_available"
    return [
        {
            **group,
            "status": status,
            "autonomy": "approval_required" if group["group"] in _OUTPUT_GROUPS else "draft_only",
            "risk": "low" if group["group"] in _READ_ONLY_GROUPS else "medium",
        }
        for group in TOOL_GROUPS
    ]


def write_sheet(settings: Any, data: list[dict[str, Any]]) -> str:
    path = settings.root_dir / TOOLSET_CSV
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["group", "trust_gate", "status", "autonomy", "risk", "tools", "use", "agent_rule"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in data])
    return _relative(settings.root_dir, path)


def write_skill(settings: Any) -> str:
    path = settings.root_dir / SKILL_DOC
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        "name: bakabo-canva-connectors",
        "description: Canva connector operating skill for BakAbo/BKS. Use when creating or managing Canva social posts, presentations, catalog sheets, brand templates, resize workflows, asset upload, comments/review, exports, or AI-generated Canva designs from BKS briefs.",
        f"store: {BAKABO_STORE_DOMAIN}",
        f"theme_id: {BKS_TM04_THEME_ID}",
        "related: [[bakabo-hyperframes-video]], [[bakabo-avatar-resident]], [[bakabo-commercial-strategy]]",
        "---",
        "",
        "# BakAbo / BKS Canva Connectors",
        "",
        "## Operating Rule",
        "",
        "Treat Canva as a native design connector inside the BKS workflow, not as a separate design island.",
        "The Master prepares drafts, reviews evidence and asks approval before public output.",
        "All designs for public campaigns are gated at `trust_gate: conversion_support` — do not export before then.",
        "",
        "## Collections",
        "",
        f"BKS collections (8): {', '.join(BKS_COLLECTIONS)}. Never use 'Folklore'.",
        "Key each design to one collection at a time. Accent colors in hyperframes_connectors.COLLECTION_ACCENTS.",
        "",
        "## Tool Groups",
        "",
    ]
    for group in TOOL_GROUPS:
        lines.extend([
            f"### {group['group']}",
            f"- Trust gate: {group['trust_gate']}",
            f"- Tools: {group['tools']}",
            f"- Use: {group['use']}",
            f"- Agent rule: {group['agent_rule']}",
            "",
        ])
    lines.extend(["## Workflows", ""])
    for workflow in WORKFLOWS:
        lines.extend([
            f"### {workflow['workflow']}",
            f"- Trust gate: {workflow['trust_gate']}",
            f"- Input: {workflow['input']}",
            f"- Sequence: {workflow['sequence']}",
            f"- Output: {workflow['output']}",
            "",
        ])
    lines.extend(["## Guardrails", ""])
    lines.extend(f"- {item}" for item in GUARDRAILS)
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return _relative(settings.root_dir, path)


def payload(settings: Any) -> dict[str, Any]:
    data = rows(settings)
    sheet = write_sheet(settings, data)
    skill = write_skill(settings)
    return {
        "summary": {
            "status": "configured" if _configured(settings) else "connector_available",
            "groups": len(data),
            "workflows": len(WORKFLOWS),
            "guardrails": len(GUARDRAILS),
            "autonomy": "draft_only_supervised_output",
            "trust_gate": "collection_identity",
            "sheet": sheet,
            "skill": skill,
        },
        "tool_groups": data,
        "workflows": list(WORKFLOWS),
        "guardrails": list(GUARDRAILS),
    }
