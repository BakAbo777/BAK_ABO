from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

BAKABO_STORE_DOMAIN = "bakabo.club"
BKS_TM04_THEME_ID = "202392961362"
BKS_MEMBER_PAGE = f"https://{BAKABO_STORE_DOMAIN}/pages/bks-members"

CRM_FILE = Path("output/growth_crm_member_area_matrix.csv")
# Skill lives in BKS_SKILL alongside all other resident skills
CRM_SKILL = Path("BKS_SKILL/skills/bakabo-growth-crm/SKILL.md")


# Metal tier system: order-count based, computed from Shopify. CSS color used for gold ring and tier badge.
METAL_TIERS: tuple[dict[str, str], ...] = (
    {"tier": "Lead",   "orders_min": "0",  "orders_max": "0",  "color": "#7a7a7a", "unlock": "Size history, AI recommendations.",                               "cta": "Your first BKS piece unlocks the Metal tier and AI size recommendations."},
    {"tier": "Iron",   "orders_min": "1",  "orders_max": "2",  "color": "#8a8a8a", "unlock": "Wishlist, post-purchase cross-sell.",                             "cta": "One more order opens the Camerino and Early Access. You're almost there."},
    {"tier": "Brass",  "orders_min": "3",  "orders_max": "5",  "color": "#c8a96e", "unlock": "Camerino Try-On, +48h drop early access.",                       "cta": "Brass members get Early Access to every new drop 48 hours before the public."},
    {"tier": "Silver", "orders_min": "6",  "orders_max": "10", "color": "#b0b0c8", "unlock": "+24h drop access, full BKS Studio Archive.",                     "cta": "Silver members get exclusive 24h head-start on every new collection drop."},
    {"tier": "Gold",   "orders_min": "11", "orders_max": "",   "color": "#d4a030", "unlock": "VIP private drops, white-glove curation, invitation-only access.", "cta": "Gold is earned through loyalty, never purchased."},
)


# Shopify customer tags for email segmentation (maps to Metal tier logic above)
SEGMENTS: tuple[dict[str, str], ...] = (
    {
        "segment": "BKS Subscriber",
        "tag": "bks-subscriber",
        "metal_tier": "Lead",
        "current_size": "12",
        "trigger": "email subscriber, 0 orders",
        "priority": "P0",
        "action": "Welcome flow: 3 emails in 7 days. Frame around BKS world + Camerino teaser. No coupon, no urgency.",
        "automation": "shopify_email",
        "status": "ready_to_draft",
    },
    {
        "segment": "BKS Drop",
        "tag": "bks-drop",
        "metal_tier": "Iron",
        "current_size": "1",
        "trigger": "1-2 orders",
        "priority": "P1",
        "action": "Post-purchase flow after delivery. Second-purchase cross-sell keyed to collection. Show Brass tier progress bar.",
        "automation": "shopify_flow_ready",
        "status": "ready_to_draft",
    },
    {
        "segment": "BKS Archive",
        "tag": "bks-archive",
        "metal_tier": "Brass+",
        "current_size": "1",
        "trigger": "3+ orders",
        "priority": "P1",
        "action": "Manual Roberto founder email. Archive access unlocked. Permanent free shipping. Show Silver/Gold progress.",
        "automation": "manual",
        "status": "ready_manual",
    },
    {
        "segment": "Dormant",
        "tag": "no marketing tag",
        "metal_tier": "Lead",
        "current_size": "20",
        "trigger": "account with 0 orders, no subscriber tag, no signal in 30 days",
        "priority": "P2",
        "action": "One re-engagement email: 1 wishlist product + Camerino CTA + tier progress bar. Subject: You haven't visited the Camerino yet. Suppress if no response.",
        "automation": "manual_or_shopify_email",
        "status": "approval_required",
    },
)


# Member area features on TM04 — status reflects current build state
MEMBER_FEATURES: tuple[dict[str, str], ...] = (
    {
        "feature": "Gold ring (account icon)",
        "status": "active",
        "theme_dependency": BKS_TM04_THEME_ID,
        "rule": "CSS-only animated gold ring around account icon in header. Tier color from CSS var --bks-tier-color. Must be visible immediately on every page load — no JS dependency.",
        "metric": "belonging signal, upgrade incentive",
    },
    {
        "feature": "Account dashboard / Metal tier card",
        "status": "active",
        "theme_dependency": BKS_TM04_THEME_ID,
        "rule": "Show tier name, tier color badge, order count, progress to next tier. Must deliver value within 60 seconds of page load — no empty state.",
        "metric": "repeat purchase path",
    },
    {
        "feature": "Camerino / Try-On",
        "status": "active",
        "theme_dependency": BKS_TM04_THEME_ID,
        "rule": "Unlocked at Brass tier (3 orders). AI virtual try-on via HeyGen. Gate with tier check before rendering. Tab visible to all; content locked with upgrade CTA for Lead/Iron.",
        "metric": "wishlist-to-purchase conversion",
    },
    {
        "feature": "Tier progress bar",
        "status": "active",
        "theme_dependency": BKS_TM04_THEME_ID,
        "rule": "Visible in member dashboard hero without scrolling. Shows orders to next tier. Use in every re-engagement email.",
        "metric": "tier upgrade rate",
    },
    {
        "feature": "Wishlist",
        "status": "planned",
        "theme_dependency": BKS_TM04_THEME_ID,
        "rule": "Available from Iron tier. Simple heart save, no extra app. Used as signal for drop notifications and Camerino briefs.",
        "metric": "wishlist-to-cart",
    },
    {
        "feature": "Order timeline",
        "status": "planned",
        "theme_dependency": BKS_TM04_THEME_ID,
        "rule": "Made-to-order states: in production → printed → shipped → delivered. Show in dashboard, not just Shopify native.",
        "metric": "support reduction",
    },
    {
        "feature": "Early access (drop gate)",
        "status": "planned",
        "theme_dependency": BKS_TM04_THEME_ID,
        "rule": "Tag-gated Shopify page. Brass+: +48h. Silver+: +24h. No separate portal.",
        "metric": "subscriber engagement",
    },
    {
        "feature": "BKS Studio Archive",
        "status": "planned",
        "theme_dependency": BKS_TM04_THEME_ID,
        "rule": "Gold tier only. Process notes and selected prompt library. Not full private library. Gated by bks-archive tag.",
        "metric": "VIP retention",
    },
    {
        "feature": "Referral",
        "status": "future",
        "theme_dependency": "",
        "rule": "Manual metafields until 50 acquirers. Avoid apps until justified by scale and privacy cost.",
        "metric": "referral conversion",
    },
    {
        "feature": "GDPR profile controls",
        "status": "legal_required",
        "theme_dependency": "",
        "rule": "Export/delete data paths must remain visible and human-reviewed at all times.",
        "metric": "compliance",
    },
)


# Conversion diagnostics — P0 items must resolve before CRM scaling
DIAGNOSTICS: tuple[dict[str, str], ...] = (
    {
        "check": "Gold ring visible on header",
        "status": "needs_review",
        "target": "CSS ring loads on every page, tier color matches Metal tier var, no JS required.",
        "why": "The ring is the primary belonging signal. If it fails, member identity collapses.",
    },
    {
        "check": "Member area 60-second rule",
        "status": "needs_review",
        "target": f"{BKS_MEMBER_PAGE} delivers one clear value signal within 60 seconds of page load.",
        "why": "Empty sections or slow loads cause exit before member engagement. Rule applies to every tab.",
    },
    {
        "check": "TM04 theme active",
        "status": "needs_review",
        "target": f"Shopify published theme ID == {BKS_TM04_THEME_ID}.",
        "why": "All member features, gold ring and dark editorial layout depend on TM04.",
    },
    {
        "check": "PDP made-to-order clarity",
        "status": "needs_review",
        "target": "Made-to-order disclosure visible before add-to-cart.",
        "why": "0 abandoned checkout suggests drop before checkout. Expectation must be set early.",
    },
    {
        "check": "Gallery depth",
        "status": "needs_review",
        "target": "5+ images per PDP including front, back, detail and lifestyle.",
        "why": "Customer needs product reality before purchase. P0 photo shots must be live first.",
    },
    {
        "check": "Size guide",
        "status": "needs_review",
        "target": "Size guide prominent near size selector on all garment PDPs.",
        "why": "Reduces uncertainty and support load for a made-to-order model.",
    },
    {
        "check": "Welcome flow",
        "status": "ready_to_draft",
        "target": ">40% open rate, 2 orders / 30 days from 12 active subscribers.",
        "why": "12 subscribers are the immediate CRM opportunity. Priority action.",
    },
    {
        "check": "Reviews anchor",
        "status": "planned",
        "target": ">8% review rate after delivery.",
        "why": "Transparent social proof supports Google Merchant trust and PDP conversion.",
    },
    {
        "check": "No app bloat",
        "status": "pass",
        "target": "Build for 200 customers, not 2000.",
        "why": "Avoid performance hit, extra data processors and unnecessary cost at current scale.",
    },
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _write_csv(settings: Any, all_rows: list[dict[str, str]]) -> str:
    path = settings.root_dir / CRM_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["type", "name", "status", "priority", "target", "rule", "metric", "action", "automation", "why", "tag", "metal_tier", "current_size", "trigger", "theme_dependency"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in all_rows])
    return _relative(settings.root_dir, path)


def _write_skill(settings: Any) -> str:
    path = settings.root_dir / CRM_SKILL
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "---",
        "name: bakabo-growth-crm",
        "description: Lightweight CRM, Metal tier member area, gold ring identity system, Camerino Try-On gate, welcome/re-engagement flows, PDP conversion diagnostics and loyalty logic for BKS Studio / bakabo.club. Triggers: 'draft welcome email', 'member area health', 'gold ring not showing', 'tier upgrade CTA', 're-engage dormant member', 'Camerino gate logic', 'PDP clarity', 'size guide', 'review anchor', 'loyalty mechanics'. Works with bakabo-members (tier CRM), bakabo-commercial-strategy (drop timing, 60-second rule), bakabo-photo-studio (PDP gallery).",
        "---",
        "",
        "# BKS Growth CRM & Member Area",
        "",
        "Lightweight member system built on TM04 + Shopify tags. No heavy apps. Manual gestures beat automation at current scale.",
        "",
        "---",
        "",
        "## 1. Metal Tier System",
        "",
        "Computed from Shopify order count. CSS color applied to gold ring (`--bks-tier-color`) and tier badge.",
        "",
        "| Tier | Orders | Color | Unlocks | CTA |",
        "|------|--------|-------|---------|-----|",
    ]
    for t in METAL_TIERS:
        orders_range = f"{t['orders_min']}–{t['orders_max']}" if t["orders_max"] else f"{t['orders_min']}+"
        lines.append(f"| **{t['tier']}** | {orders_range} | `{t['color']}` | {t['unlock']} | *{t['cta']}* |")

    lines.extend([
        "",
        "---",
        "",
        "## 2. Email Segments",
        "",
        "| Segment | Tag | Metal tier | Size | Trigger | Action |",
        "|---------|-----|-----------|------|---------|--------|",
    ])
    for seg in SEGMENTS:
        lines.append(f"| {seg['segment']} | `{seg['tag']}` | {seg['metal_tier']} | {seg['current_size']} | {seg['trigger']} | {seg['action']} |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Member Area Features (TM04)",
        "",
        "All active features depend on TM04 theme ID `202392961362` being the published Shopify theme.",
        "",
        "| Feature | Status | Rule | Metric |",
        "|---------|--------|------|--------|",
    ])
    for f in MEMBER_FEATURES:
        lines.append(f"| {f['feature']} | `{f['status']}` | {f['rule']} | {f['metric']} |")

    lines.extend([
        "",
        "---",
        "",
        "## 4. Conversion Diagnostics",
        "",
        "| Check | Status | Target | Why |",
        "|-------|--------|--------|-----|",
    ])
    for d in DIAGNOSTICS:
        lines.append(f"| {d['check']} | `{d['status']}` | {d['target']} | {d['why']} |")

    lines.extend([
        "",
        "---",
        "",
        "## 5. Voice Rules",
        "",
        "- Subject line under 50 characters.",
        "- Email body under 150 words for automated flows.",
        "- No exclamation marks, no emoji, no urgency language.",
        "- No coupon in the first welcome email.",
        "- Use tier progress bar in every re-engagement email.",
        "- Always include unsubscribe link and BKS email footer.",
        "",
        "---",
        "",
        "## 6. Agent Rules",
        "",
        "- Draft welcome/post-purchase/VIP emails; always request Roberto approval before sending.",
        "- Never add fake urgency or coupon pressure in early CRM flows.",
        "- Use Shopify native email first; add apps only when scale justifies cost and privacy impact.",
        "- Gold ring must be CSS-only — no JS dependency. If it fails, flag to Roberto before any member campaign.",
        "- 60-second rule: every tab in the member area must show a value signal within 60s. Empty = broken.",
        "- Record CRM outcomes in Knowledge DB so the agent learns which email and PDP changes convert.",
        "",
        "---",
        "",
        "## Related Skills",
        "",
        "- [[bakabo-members]] — tier CRM detail, email templates, Personal Shopper, Try-On gate",
        "- [[bakabo-commercial-strategy]] — drop timing, 60-second rule, gold ring commercial value",
        "- [[bakabo-photo-studio]] — PDP gallery P0 shots required before conversion diagnostics pass",
        "- [[bakabo-google-trust]] — Google trust P0 must pass before CRM scaling and reviews",
    ])
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return _relative(settings.root_dir, path)


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    member_area = snapshot.get("member_area", {})
    theme_summary = snapshot.get("theme", {}).get("summary", {})
    tm04_active = (
        theme_summary.get("theme_id") == BKS_TM04_THEME_ID
        or theme_summary.get("tm04_active", False)
    )
    member_ok = member_area.get("status") in {"ok", "ready"}

    # Overlay live snapshot into diagnostics
    diagnostics_live: list[dict[str, str]] = []
    for diag in DIAGNOSTICS:
        row = dict(diag)
        if diag["check"] == "TM04 theme active":
            row["status"] = "pass" if tm04_active else "needs_fix"
        elif diag["check"] == "Member area 60-second rule":
            row["status"] = "pass" if member_ok else "needs_review"
        diagnostics_live.append(row)

    all_rows: list[dict[str, str]] = []
    all_rows.extend({"type": "segment", "name": row["segment"], **row} for row in SEGMENTS)
    all_rows.extend({"type": "member_feature", "name": row["feature"], "priority": "P1", **row} for row in MEMBER_FEATURES)
    all_rows.extend({"type": "diagnostic", "name": row["check"], "priority": "P0" if row["status"] in {"needs_review", "needs_fix"} else "P1", **row} for row in diagnostics_live)

    sheet = _write_csv(settings, all_rows)
    skill = _write_skill(settings)

    ready = sum(1 for row in all_rows if row.get("status") in {"pass", "ready_to_draft", "ready_manual", "active"})
    attention = sum(1 for row in all_rows if row.get("status") in {"needs_review", "needs_fix", "approval_required", "legal_required"})
    total = len(all_rows)
    p0_attention = [row["name"] for row in all_rows if row.get("priority") == "P0" and row.get("status") not in {"pass", "active"}]
    next_action = p0_attention[0] if p0_attention else (
        next((row["name"] for row in all_rows if row.get("status") == "ready_to_draft"), "")
    )

    return {
        "summary": {
            "segments": len(SEGMENTS),
            "member_features": len(MEMBER_FEATURES),
            "diagnostics": len(diagnostics_live),
            "ready": ready,
            "attention": attention,
            "percent_complete": round(ready / total * 100) if total else 0,
            "tm04_active": tm04_active,
            "member_area_ok": member_ok,
            "p0_attention": p0_attention,
            "next_action": next_action,
            "sheet": sheet,
            "skill": skill,
        },
        "metal_tiers": list(METAL_TIERS),
        "segments": list(SEGMENTS),
        "member_features": list(MEMBER_FEATURES),
        "diagnostics": diagnostics_live,
        "voice_rules": [
            "Subject line under 50 characters.",
            "Automated email body under 150 words.",
            "No exclamation marks, no emoji, no urgency language.",
            "No coupon in the first welcome flow.",
            "Use tier progress bar in every re-engagement email.",
            "Always include unsubscribe link and BKS email footer.",
        ],
    }
