from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


CRM_FILE = Path("output/growth_crm_member_area_matrix.csv")
CRM_SKILL = Path("docs/bakabo-growth-crm-member-area_SKILL.md")


SEGMENTS: tuple[dict[str, str], ...] = (
    {
        "segment": "BKS Archive",
        "tag": "bks-archive",
        "current_size": "1",
        "trigger": "2+ orders",
        "priority": "P1",
        "action": "Manual founder email, archive access, permanent free shipping.",
        "automation": "manual",
        "status": "ready_manual",
    },
    {
        "segment": "BKS Drop",
        "tag": "bks-drop",
        "current_size": "1",
        "trigger": "1 order",
        "priority": "P1",
        "action": "Post-purchase flow after delivery, second-purchase cross-sell.",
        "automation": "shopify_flow_ready",
        "status": "ready_to_draft",
    },
    {
        "segment": "BKS Subscriber",
        "tag": "bks-subscriber",
        "current_size": "12",
        "trigger": "email subscriber, 0 orders",
        "priority": "P0",
        "action": "Welcome flow: 3 emails in 7 days, no coupon, no urgency.",
        "automation": "shopify_email",
        "status": "ready_to_draft",
    },
    {
        "segment": "Dormant",
        "tag": "no marketing tag",
        "current_size": "20",
        "trigger": "account, no subscriber, no orders",
        "priority": "P2",
        "action": "One re-engagement email; suppress if no signal in 30 days.",
        "automation": "manual_or_shopify_email",
        "status": "approval_required",
    },
)


MEMBER_FEATURES: tuple[dict[str, str], ...] = (
    {"feature": "Account dashboard", "status": "planned", "rule": "Show tier, order shortcuts, wishlist/early access only when useful.", "metric": "repeat purchase path"},
    {"feature": "Order timeline", "status": "planned", "rule": "Made-to-order states: in production, printed, shipped, delivered.", "metric": "support reduction"},
    {"feature": "Wishlist", "status": "planned", "rule": "Available from bks-subscriber; simple gifting/share link later.", "metric": "wishlist-to-cart"},
    {"feature": "Early access", "status": "planned", "rule": "Tag-gated Shopify page, no separate portal.", "metric": "subscriber engagement"},
    {"feature": "BKS Studio Archive", "status": "planned", "rule": "Only bks-archive; process notes and selected prompt library, not full private library.", "metric": "VIP retention"},
    {"feature": "Referral", "status": "future", "rule": "Manual metafields until 50 acquirers; avoid extra apps too early.", "metric": "referral conversion"},
    {"feature": "GDPR profile controls", "status": "legal_required", "rule": "Export/delete data paths must stay visible and human-reviewed.", "metric": "compliance"},
)


DIAGNOSTICS: tuple[dict[str, str], ...] = (
    {"check": "PDP made-to-order clarity", "status": "needs_review", "target": "Visible before add-to-cart.", "why": "0 abandoned checkout suggests drop before checkout."},
    {"check": "Gallery depth", "status": "needs_review", "target": "5+ images per PDP.", "why": "Customer needs product reality before purchase."},
    {"check": "Size guide", "status": "needs_review", "target": "Prominent near size selector.", "why": "Reduces uncertainty and support load."},
    {"check": "Reviews anchor", "status": "planned", "target": ">8% review rate after delivery.", "why": "Transparent social proof supports Merchant trust."},
    {"check": "Welcome flow", "status": "ready_to_draft", "target": ">40% open, 2 orders/30 days.", "why": "12 subscribers are the immediate CRM opportunity."},
    {"check": "No app bloat", "status": "pass", "target": "Build for 200 customers, not 2000.", "why": "Avoid cost, performance hit and extra processors."},
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _write_csv(settings: Any, rows: list[dict[str, str]]) -> str:
    path = settings.root_dir / CRM_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["type", "name", "status", "priority", "target", "rule", "metric", "action", "automation", "why", "tag", "current_size", "trigger"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in rows])
    return _relative(settings.root_dir, path)


def _write_skill(settings: Any) -> str:
    path = settings.root_dir / CRM_SKILL
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# bakabo-growth-crm-member-area",
        "",
        "Skill for lightweight CRM, member area, social proof, reviews, wishlist and loyalty logic.",
        "",
        "## Core constraints",
        "",
        "- Voice is editorial, cool, no urgency, no exclamation marks, no emoji in body copy.",
        "- Current scale is small: manual gestures beat heavy automation.",
        "- Build for 200 customers, not 2000.",
        "- PDP clarity comes before abandoned checkout or aggressive email flows.",
        "",
        "## Segments",
        "",
    ]
    lines.extend(f"- {row['segment']} ({row['tag']}): {row['action']}" for row in SEGMENTS)
    lines.extend(
        [
            "",
            "## Agent rules",
            "",
            "- Draft welcome/post-purchase/manual VIP email, but request approval before sending.",
            "- Never use fake urgency or coupon pressure in early CRM.",
            "- Use Shopify native tools first; add apps only when scale justifies cost and privacy impact.",
            "- Save CRM signals into Knowledge DB so the agent learns which PDP and email changes work.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return _relative(settings.root_dir, path)


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, str]] = []
    rows.extend({"type": "segment", "name": row["segment"], **row} for row in SEGMENTS)
    rows.extend({"type": "member_feature", "name": row["feature"], "priority": "P1", **row} for row in MEMBER_FEATURES)
    rows.extend({"type": "diagnostic", "name": row["check"], "priority": "P0" if row["status"] == "needs_review" else "P1", **row} for row in DIAGNOSTICS)
    sheet = _write_csv(settings, rows)
    skill = _write_skill(settings)
    ready = sum(1 for row in rows if row.get("status") in {"pass", "ready_to_draft", "ready_manual"})
    attention = sum(1 for row in rows if row.get("status") in {"needs_review", "approval_required", "legal_required"})
    return {
        "summary": {
            "segments": len(SEGMENTS),
            "member_features": len(MEMBER_FEATURES),
            "diagnostics": len(DIAGNOSTICS),
            "ready": ready,
            "attention": attention,
            "primary_action": "Fix PDP clarity and draft welcome flow before heavier CRM.",
            "sheet": sheet,
            "skill": skill,
        },
        "segments": list(SEGMENTS),
        "member_features": list(MEMBER_FEATURES),
        "diagnostics": list(DIAGNOSTICS),
        "voice_rules": [
            "Subject under 50 characters.",
            "Automatic email body under 150 words.",
            "No exclamation marks, no emoji, no urgency.",
            "No coupon in the first welcome flow.",
        ],
    }
