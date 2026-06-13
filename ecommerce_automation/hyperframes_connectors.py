from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


TOOLSET_CSV = Path("output/hyperframes_connector_toolset.csv")
PROTOCOL_DOC = Path("docs/bakabo-hyperframes-video_SKILL.md")


TOOLS: tuple[dict[str, str], ...] = (
    {
        "tool": "Compose HyperFrames Video",
        "mode": "interactive_write",
        "use": "Create an HTML-based motion video project from a BKS storyboard, script or explainer brief.",
        "agent_rule": "Use after copy/storyboard approval; keep claims transparent and collection naming intact.",
    },
    {
        "tool": "Get HyperFrames Project",
        "mode": "interactive_read",
        "use": "Inspect project structure, scenes and assets before editing or rendering.",
        "agent_rule": "Read project state before any render or iteration.",
    },
    {
        "tool": "Render HyperFrames Video",
        "mode": "interactive_write",
        "use": "Render the approved HTML motion project into video.",
        "agent_rule": "Render only draft/approved projects and track cost/time before repeated renders.",
    },
    {
        "tool": "Check HyperFrames Project Status",
        "mode": "read_only",
        "use": "Check project generation, validation or composition state.",
        "agent_rule": "Poll lightly; do not create duplicate projects when a project is still processing.",
    },
    {
        "tool": "Check HyperFrames Render Status",
        "mode": "read_only",
        "use": "Monitor render progress and final output readiness.",
        "agent_rule": "Use status checks for visible progress in the Master dashboard.",
    },
)


WORKFLOWS: tuple[dict[str, str], ...] = (
    {
        "workflow": "Animated Collection Explainer",
        "input": "BKS collection name, 35-50 word script, product/collection images, CTA.",
        "sequence": "Storyboard -> HTML scenes -> compose project -> check project -> render -> check render -> attach to Social Render.",
        "output": "9:16 explainer video for Reels, TikTok, YouTube Shorts and homepage section.",
    },
    {
        "workflow": "Motion Presentation",
        "input": "Pitch outline, metrics, Google trust status, product visuals.",
        "sequence": "Approved outline -> animated HTML slides -> render preview -> review -> export video.",
        "output": "Animated founder/customer presentation or internal progress video.",
    },
    {
        "workflow": "Product Trust Clip",
        "input": "Made-to-order explanation, shipping/returns clarity, product photo, trust strip copy.",
        "sequence": "Compliance copy -> short motion graphic -> render -> review with Google-safe checklist.",
        "output": "Transparent product/trust clip for PDP, email or social.",
    },
)


GUARDRAILS: tuple[str, ...] = (
    "Use HyperFrames for motion from approved HTML/storyboards, not for unverified product claims.",
    "Keep render loops cost-aware: compose once, check status, render only after review.",
    "Use 9:16 as the default social format unless the channel requires another format.",
    "Do not hide terms, prices, delivery expectations or AI disclosure in motion graphics.",
    "Every rendered video should write metadata: script, collection, source assets, render ID, channel and approval state.",
    "Avatar/HeyGen and HyperFrames are complementary: avatar speaks; HyperFrames visualizes.",
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
    fieldnames = ["tool", "mode", "status", "autonomy", "risk", "use", "agent_rule"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in data])
    return _relative(settings.root_dir, path)


def write_protocol(settings: Any) -> str:
    path = settings.root_dir / PROTOCOL_DOC
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        "name: bakabo-hyperframes-video",
        "description: HyperFrames operating skill for BakAbo/BKS motion graphics. Use when composing animated slides, explainer videos, HTML-to-video scenes, motion product trust clips, checking HyperFrames project/render status, or rendering social videos from approved BKS storyboards.",
        "---",
        "",
        "# BakAbo / BKS HyperFrames Video",
        "",
        "## Operating Rule",
        "",
        "Use HyperFrames as the motion layer of the BKS Master: HTML scenes become explainers, animated slides and social videos. Compose and render only with approval gates and metadata.",
        "",
        "## Tools",
        "",
    ]
    for tool in TOOLS:
        lines.extend(
            [
                f"### {tool['tool']}",
                f"- Mode: {tool['mode']}",
                f"- Use: {tool['use']}",
                f"- Agent rule: {tool['agent_rule']}",
                "",
            ]
        )
    lines.extend(["## Workflows", ""])
    for workflow in WORKFLOWS:
        lines.extend(
            [
                f"### {workflow['workflow']}",
                f"- Input: {workflow['input']}",
                f"- Sequence: {workflow['sequence']}",
                f"- Output: {workflow['output']}",
                "",
            ]
        )
    lines.extend(["## Guardrails", ""])
    lines.extend(f"- {item}" for item in GUARDRAILS)
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return _relative(settings.root_dir, path)


def payload(settings: Any) -> dict[str, Any]:
    data = rows(settings)
    sheet = write_sheet(settings, data)
    protocol = write_protocol(settings)
    return {
        "summary": {
            "status": "configured" if _configured(settings) else "connector_available",
            "tools": len(data),
            "workflows": len(WORKFLOWS),
            "default_format": getattr(settings, "hyperframes_default_format", "1080x1920"),
            "autonomy": "draft_render_with_approval",
            "sheet": sheet,
            "protocol": protocol,
        },
        "tools": data,
        "workflows": list(WORKFLOWS),
        "guardrails": list(GUARDRAILS),
    }
