from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROUTINE_SHEET = Path("output/agent_routine_queue.csv")
COST_SHEET = Path("output/api_cost_guard_matrix.csv")
ROUTINE_DOC = Path("docs/BKS_AGENT_ROUTINE.md")


ROUTINE_STEPS: tuple[dict[str, str], ...] = (
    {
        "step": "Refresh local truth",
        "cadence": "dashboard refresh",
        "automation": "automatic",
        "cost_level": "free_local",
        "inputs": "SQLite, CSV, theme files, generated reports",
        "output": "Updated snapshot and Knowledge DB seed",
        "approval": "none",
    },
    {
        "step": "Check Google trust gate",
        "cadence": "daily 12:00 + before campaigns",
        "automation": "automatic_read",
        "cost_level": "free_low",
        "inputs": "live audit, Merchant status notes, policy pages, feed matrix",
        "output": "P0 blockers and first recovery action",
        "approval": "none for checks; human for appeal",
    },
    {
        "step": "Check network trust gate",
        "cadence": "realtime snapshot + before email/social campaigns",
        "automation": "automatic_read",
        "cost_level": "free_low",
        "inputs": "DNS, MX, SPF, DKIM, DMARC, DSN/bounce, HTTPS endpoints, tracking suffix rules",
        "output": "network blockers, delivery risk and data-suffix guardrails",
        "approval": "none for checks; human for DNS/email infrastructure changes",
    },
    {
        "step": "Monitor official inbox",
        "cadence": "continuous when IMAP enabled",
        "automation": "read_and_draft",
        "cost_level": "low",
        "inputs": "crew@bakabo.club, categories, Knowledge DB",
        "output": "classified email, draft reply, escalation flag",
        "approval": "required before send for risky cases",
    },
    {
        "step": "Evaluate customer/social signals",
        "cadence": "daily/weekly",
        "automation": "automatic_read",
        "cost_level": "low_medium",
        "inputs": "GA4/GTM aggregate, email consented open/click, social metrics",
        "output": "transparent marketing recommendation",
        "approval": "none for read; required for retarget/send/ad spend",
    },
    {
        "step": "Prepare next action",
        "cadence": "after every check",
        "automation": "automatic",
        "cost_level": "free_local",
        "inputs": "Master action queue, weekly goals, market sense, legal guardrails",
        "output": "one suggested action with reason and verification",
        "approval": "depends on action risk",
    },
    {
        "step": "Generate assets/copy",
        "cadence": "on demand / campaign window",
        "automation": "draft_automatic",
        "cost_level": "medium_controlled",
        "inputs": "OpenAI, HeyGen, image/archive assets, Photo Studio plan",
        "output": "multilingual copy, scripts, image/video plan",
        "approval": "required before public use",
    },
    {
        "step": "Publish or send",
        "cadence": "only after approval",
        "automation": "supervised_write",
        "cost_level": "variable",
        "inputs": "Shopify, Meta, YouTube, TikTok, email, Telegram",
        "output": "published theme/social/email action",
        "approval": "explicit human approval",
    },
    {
        "step": "Verify result and learn",
        "cadence": "after action",
        "automation": "automatic_read",
        "cost_level": "low",
        "inputs": "HTTP checks, platform status, Knowledge DB, customer feedback",
        "output": "memory update, next step or rollback recommendation",
        "approval": "none unless rollback/publish needed",
    },
)


COST_GUARDS: tuple[dict[str, str], ...] = (
    {
        "api": "Local files / SQLite",
        "cost": "free",
        "rule": "Use first for every answer and routine update.",
        "approval": "none",
    },
    {
        "api": "Google/Shopify read checks",
        "cost": "low",
        "rule": "Batch reads; avoid repeated live calls during one dashboard refresh.",
        "approval": "none for read-only",
    },
    {
        "api": "OpenAI reasoning/copy",
        "cost": "metered",
        "rule": "Use concise prompts, reuse Knowledge DB summaries, generate drafts in batches.",
        "approval": "none for internal draft; approval before publication",
    },
    {
        "api": "HeyGen rendering",
        "cost": "credit_metered",
        "rule": "Render pilot first, then batch only approved scripts/images.",
        "approval": "required before render batch",
    },
    {
        "api": "Social publishing APIs",
        "cost": "low_variable",
        "rule": "Prepare posts locally; publish only after trust and approval gates.",
        "approval": "required before publish",
    },
    {
        "api": "Paid Ads APIs",
        "cost": "ad_spend",
        "rule": "Never autonomous while Merchant is suspended or trust is red.",
        "approval": "explicit budget approval",
    },
    {
        "api": "Email campaigns",
        "cost": "deliverability_reputation",
        "rule": "Segment by consent; include opt-out; do not use deceptive urgency.",
        "approval": "required before campaign send",
    },
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _step_status(step: dict[str, str], snapshot: dict[str, Any]) -> str:
    name = step["step"]
    if name == "Check Google trust gate":
        return "attention" if int(snapshot.get("trust", {}).get("summary", {}).get("needs_fix", 0)) else "ready"
    if name == "Check network trust gate":
        return "attention" if int(snapshot.get("network", {}).get("summary", {}).get("needs_fix", 0)) else "ready"
    if name == "Monitor official inbox":
        summary = snapshot.get("official_inbox", {}).get("summary", {})
        return "ready" if summary.get("status") == "ready_for_drafts" else "needs_config"
    if name == "Evaluate customer/social signals":
        social = snapshot.get("social_campaigns", {}).get("summary", {})
        return "ready" if int(social.get("ready", 0)) else "prepare"
    if name == "Generate assets/copy":
        photo = snapshot.get("photo_studio", {}).get("summary", {})
        return "ready" if int(photo.get("ready", 0)) else "prepare"
    if name == "Publish or send":
        google_status = snapshot.get("google", {}).get("summary", {}).get("status")
        return "blocked" if google_status == "suspended" else "approval_required"
    return "ready"


def build_rows(snapshot: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, step in enumerate(ROUTINE_STEPS, start=1):
        status = _step_status(step, snapshot)
        rows.append(
            {
                **step,
                "priority": str(index),
                "status": status,
                "updated_at": _now(),
            }
        )
    return rows


def write_outputs(settings: Any, rows: list[dict[str, str]]) -> tuple[str, str, str]:
    routine_path = settings.root_dir / ROUTINE_SHEET
    routine_path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["priority", "step", "status", "cadence", "automation", "cost_level", "inputs", "output", "approval", "updated_at"]
    with routine_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fields} for row in rows])

    cost_path = settings.root_dir / COST_SHEET
    cost_path.parent.mkdir(parents=True, exist_ok=True)
    cost_fields = ["api", "cost", "rule", "approval"]
    with cost_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=cost_fields)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in cost_fields} for row in COST_GUARDS])

    doc_path = settings.root_dir / ROUTINE_DOC
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# BKS Agent Routine",
        "",
        "Routine: si attiva, aggiorna, suggerisce, verifica e passa avanti.",
        "",
        "## Cost principle",
        "",
        "Use local data first, batch read-only API calls, estimate cost before metered work, and require approval for paid, public, customer-facing or irreversible actions.",
        "",
        "## Steps",
        "",
    ]
    lines.extend(f"{row['priority']}. {row['step']} - {row['automation']} - {row['cost_level']} - {row['approval']}." for row in rows)
    lines.extend(
        [
            "",
            "## Cost guards",
            "",
        ]
    )
    lines.extend(f"- {row['api']}: {row['rule']} Approval: {row['approval']}." for row in COST_GUARDS)
    doc_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return _relative(settings.root_dir, routine_path), _relative(settings.root_dir, cost_path), _relative(settings.root_dir, doc_path)


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    rows = build_rows(snapshot)
    routine_sheet, cost_sheet, doc = write_outputs(settings, rows)
    next_step = next((row for row in rows if row["status"] in {"attention", "needs_config", "prepare", "blocked", "approval_required"}), rows[0] if rows else {})
    return {
        "summary": {
            "steps": len(rows),
            "ready": sum(1 for row in rows if row["status"] == "ready"),
            "attention": sum(1 for row in rows if row["status"] in {"attention", "needs_config", "blocked"}),
            "next_step": next_step.get("step", ""),
            "routine_sheet": routine_sheet,
            "cost_sheet": cost_sheet,
            "doc": doc,
        },
        "rows": rows,
        "cost_guards": list(COST_GUARDS),
        "next_step": next_step,
    }
