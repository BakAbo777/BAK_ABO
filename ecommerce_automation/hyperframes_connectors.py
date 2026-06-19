from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

BAKABO_STORE_DOMAIN = "bakabo.club"
BKS_TM04_THEME_ID = "202392961362"

TOOLSET_CSV = Path("output/hyperframes_connector_toolset.csv")
# Skill lives in BKS_SKILL alongside the other resident skills
SKILL_DOC = Path("BKS_SKILL/skills/bakabo-hyperframes-video/SKILL.md")

# Per-collection motion brief: accent color from TM04, narrative direction, social hook.
# All 8 BKS collections — NEVER use "Folklore" (renamed to Origin).
COLLECTION_VIDEO_BRIEFS: tuple[dict[str, str], ...] = (
    {"collection": "Hours",   "handle": "bks-hours",   "accent": "#1a1a2e", "narrative": "Time as identity. Quiet luxury. Slow reveal.",         "hook": "Some pieces are worth the wait."},
    {"collection": "Glyph",   "handle": "bks-glyph",   "accent": "#2e1a1a", "narrative": "Symbol, mark, signature. Type as texture.",            "hook": "Wear the mark."},
    {"collection": "Marker",  "handle": "bks-marker",  "accent": "#1a2e1a", "narrative": "Urban, street, drawn lines. Hand-made feel.",           "hook": "Drawn by hand. Built to last."},
    {"collection": "Riviera", "handle": "bks-riviera", "accent": "#1a2a3e", "narrative": "Mediterranean light. Holiday ease. Relaxed confidence.", "hook": "The coast, distilled."},
    {"collection": "Pulse",   "handle": "bks-pulse",   "accent": "#2e1a2e", "narrative": "Energy, movement, frequency. Athletic edge.",            "hook": "Move on your terms."},
    {"collection": "Token",   "handle": "bks-token",   "accent": "#2e2a1a", "narrative": "Collectible, limited, earned. Membership signal.",       "hook": "Not everyone gets one."},
    {"collection": "Flag",    "handle": "bks-flag",    "accent": "#1a1e2e", "narrative": "National code, graphic identity. Bold statement.",       "hook": "Show your colours."},
    {"collection": "Origin",  "handle": "bks-origin",  "accent": "#489808", "narrative": "Roots, naive art, earth tones. Honest materials.",      "hook": "Back to where it started."},
)


TOOLS: tuple[dict[str, str], ...] = (
    {
        "tool": "Compose HyperFrames Video",
        "mode": "interactive_write",
        "trust_gate": "collection_identity",
        "use": "Create an HTML-based motion video project from a BKS collection brief, storyboard or explainer script.",
        "agent_rule": "Use after copy/storyboard approval. Key accent color and narrative to the target collection brief. Keep collection naming exact — never use 'Folklore'.",
    },
    {
        "tool": "Get HyperFrames Project",
        "mode": "interactive_read",
        "trust_gate": "trust_foundation",
        "use": "Inspect project structure, scenes and assets before editing or rendering.",
        "agent_rule": "Read project state before any render or iteration. Record project_id in video metadata.",
    },
    {
        "tool": "Render HyperFrames Video",
        "mode": "interactive_write",
        "trust_gate": "collection_identity",
        "use": "Render the approved HTML motion project to MP4/WebM.",
        "agent_rule": "Render only after Roberto approval. Track credit cost. Write render_id, collection handle, script hash and channel to metadata. Do not render the same project twice without review.",
    },
    {
        "tool": "Check HyperFrames Project Status",
        "mode": "read_only",
        "trust_gate": "trust_foundation",
        "use": "Check project generation, validation or composition state.",
        "agent_rule": "Poll at most once per 30 seconds. Do not create duplicate projects while one is still processing.",
    },
    {
        "tool": "Check HyperFrames Render Status",
        "mode": "read_only",
        "trust_gate": "trust_foundation",
        "use": "Monitor render progress and final output URL readiness.",
        "agent_rule": "Surface render status in the Master dashboard. Report output URL when ready.",
    },
)


WORKFLOWS: tuple[dict[str, str], ...] = (
    {
        "workflow": "Collection Drop Video",
        "trust_gate": "collection_identity",
        "input": "Collection name (from BKS 8), accent color from COLLECTION_VIDEO_BRIEFS, P0 hero product image, 35-50 word drop script, CTA.",
        "sequence": "Brief → accent-keyed storyboard → Compose (HTML scenes) → Check project → Roberto approval → Render → Check render status → attach to Social Render pipeline.",
        "output": "9:16 drop announcement video for Reels, TikTok Shorts, YouTube Shorts and TM04 homepage section.",
    },
    {
        "workflow": "Member Re-engagement Clip",
        "trust_gate": "trust_foundation",
        "input": "Member tier (Metal system), wishlist item image, progress-to-next-tier copy, Camerino CTA.",
        "sequence": "bakabo-members skill → tier color + wishlist data → motion brief → Compose → Check → render → email embed or member area hero.",
        "output": "15s personalised re-engagement clip. Must deliver value signal within 60 seconds of play — no long intros.",
    },
    {
        "workflow": "Trust Transparency Clip",
        "trust_gate": "trust_foundation",
        "input": "Made-to-order disclosure, shipping/returns clarity, product photo, Google-safe trust strip copy.",
        "sequence": "google_trust_contract P0 check → compliance copy → short motion graphic → Render → review against Google-safe checklist.",
        "output": "Transparent product/trust clip for PDP, email or social. Required before campaign layer activation.",
    },
    {
        "workflow": "Avatar + HyperFrames Composite",
        "trust_gate": "collection_identity",
        "input": "HeyGen rendered avatar clip (15s), collection background HTML scene, overlay copy.",
        "sequence": "HeyGen avatar render complete → BKS scene composed in HyperFrames → merge layers → render composite → Check render status.",
        "output": "Combined avatar + motion backdrop video. Avatar speaks; HyperFrames provides the collection world.",
    },
    {
        "workflow": "Progress Presentation",
        "trust_gate": "trust_foundation",
        "input": "master_actions percent_complete, trust contract P0 status, product count, Google Merchant status.",
        "sequence": "Snapshot data → animated HTML slides → render preview → Roberto review → export.",
        "output": "Internal animated progress video or founder update for investors/partners.",
    },
)


GUARDRAILS: tuple[str, ...] = (
    "Compose only from approved storyboards or BKS collection briefs — never invent product prints, colors or model looks.",
    "Key every composition to the collection's accent color from COLLECTION_VIDEO_BRIEFS. Wrong accent = wrong identity.",
    "Never use 'Folklore' in scripts, overlays or titles — the collection is 'Origin'.",
    "Keep render loops cost-aware: compose once, check status, render only after Roberto approval.",
    "9:16 is the default social format (Reels/TikTok/Shorts). 16:9 for presentations. 1:1 for email hero.",
    "Do not hide terms, prices, delivery expectations or AI disclosure in motion graphics.",
    "Every rendered video writes metadata: collection handle, accent color, script, render_id, channel, approval state.",
    "Member clips must deliver a clear value signal within 60 seconds — no decorative intros.",
    "Avatar/HeyGen and HyperFrames are complementary: avatar speaks; HyperFrames builds the world around them.",
    "Do not render campaign videos while google_trust_contract P0 blockers are non-empty.",
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _configured(settings: Any) -> bool:
    return bool(str(getattr(settings, "hyperframes_api_key", "") or "").strip())


def rows(settings: Any) -> list[dict[str, str]]:
    status = "configured" if _configured(settings) else "connector_available"
    return [
        {
            **tool,
            "status": status,
            "autonomy": "draft_render_with_approval",
            "risk": "medium" if "Render" in tool["tool"] or "Compose" in tool["tool"] else "low",
        }
        for tool in TOOLS
    ]


def write_sheet(settings: Any, data: list[dict[str, str]]) -> str:
    path = settings.root_dir / TOOLSET_CSV
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["tool", "mode", "trust_gate", "status", "autonomy", "risk", "use", "agent_rule"]
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
        "name: bakabo-hyperframes-video",
        "description: HyperFrames motion skill for BKS Studio. Use when composing collection drop videos, member re-engagement clips, trust transparency clips, avatar+background composites, or checking HyperFrames project/render status. Triggers: 'make a drop video', 'animate the collection', 'render the explainer', 'create a motion clip for Origin/Hours/Glyph…', 'avatar background scene', 'trust clip'. Works with bakabo-photo-studio (source images), bakabo-avatar-resident (HeyGen avatar clips), bakabo-commercial-strategy (drop timing), bakabo-members (tier data for member clips).",
        "---",
        "",
        "# BKS HyperFrames Video Skill",
        "",
        "HyperFrames is the **motion layer** of the BKS Master system. HTML scenes become collection explainers, member clips, trust transparencies and social drops.",
        "",
        "---",
        "",
        "## 1. Collection Video Briefs",
        "",
        "Key every composition to the collection's accent color. Wrong accent = wrong collection identity.",
        "",
        "| Collection | Handle | Accent | Narrative | Hook |",
        "|------------|--------|--------|-----------|------|",
    ]
    for brief in COLLECTION_VIDEO_BRIEFS:
        lines.append(f"| {brief['collection']} | `{brief['handle']}` | `{brief['accent']}` | {brief['narrative']} | *{brief['hook']}* |")

    lines.extend([
        "",
        "---",
        "",
        "## 2. Tools",
        "",
    ])
    for tool in TOOLS:
        lines.extend([
            f"### {tool['tool']}",
            f"- Mode: `{tool['mode']}` — Trust gate: `{tool['trust_gate']}`",
            f"- Use: {tool['use']}",
            f"- Agent rule: {tool['agent_rule']}",
            "",
        ])

    lines.extend(["---", "", "## 3. Workflows", ""])
    for wf in WORKFLOWS:
        lines.extend([
            f"### {wf['workflow']}",
            f"- Trust gate: `{wf['trust_gate']}`",
            f"- Input: {wf['input']}",
            f"- Sequence: {wf['sequence']}",
            f"- Output: {wf['output']}",
            "",
        ])

    lines.extend(["---", "", "## 4. Guardrails", ""])
    lines.extend(f"- {item}" for item in GUARDRAILS)

    lines.extend([
        "",
        "---",
        "",
        "## 5. Related Skills",
        "",
        "- [[bakabo-avatar-resident]] — HeyGen avatar scripts (15s per collection); avatar speaks, HyperFrames provides the world",
        "- [[bakabo-photo-studio]] — P0/P1 source images; hero banner left 40% must clear for TM04 collection signal",
        "- [[bakabo-commercial-strategy]] — drop timing gates; trust_foundation must pass before campaign renders",
        "- [[bakabo-members]] — Metal tier data for personalised member re-engagement clips",
        "- [[bakabo-google-trust]] — P0 blockers gate; do not render campaign videos while p0_blockers is non-empty",
    ])
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return _relative(settings.root_dir, path)


def payload(settings: Any) -> dict[str, Any]:
    data = rows(settings)
    sheet = write_sheet(settings, data)
    skill = write_skill(settings)
    configured = _configured(settings)
    project_id = str(getattr(settings, "hyperframes_project_id", "") or "")
    return {
        "summary": {
            "status": "configured" if configured else "connector_available",
            "tools": len(data),
            "workflows": len(WORKFLOWS),
            "collections": len(COLLECTION_VIDEO_BRIEFS),
            "default_format": getattr(settings, "hyperframes_default_format", "1080x1920"),
            "project_id": project_id,
            "autonomy": "draft_render_with_approval",
            "trust_gate": "collection_identity",
            "sheet": sheet,
            "skill": skill,
        },
        "tools": data,
        "workflows": list(WORKFLOWS),
        "collection_briefs": list(COLLECTION_VIDEO_BRIEFS),
        "guardrails": list(GUARDRAILS),
    }
