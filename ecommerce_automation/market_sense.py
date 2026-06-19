from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

BKS_TM04_THEME_ID = "202392961362"
BKS_COLLECTIONS = ("Hours", "Glyph", "Marker", "Riviera", "Pulse", "Token", "Flag", "Origin")

# Commercial stage order — each stage gates the next
COMMERCIAL_STAGES = (
    "trust_foundation",
    "collection_identity",
    "conversion_support",
    "campaign_layer",
    "merchant_appeal",
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _score(status: str) -> int:
    return {
        "pass": 100,
        "ready": 90,
        "active": 88,
        "connected": 88,
        "synced": 85,
        "tm04_live": 85,
        "google_safe": 85,
        "partial": 55,
        "manual_pending": 45,
        "needs_review": 40,
        "needs_fix": 30,
        "needs_build": 30,
        "missing_config": 20,
        "blocked": 10,
        "suspended": 5,
    }.get(status, 50)


def _commercial_stage(snapshot: dict[str, Any]) -> str:
    """Derive which commercial stage BKS is currently in from snapshot data."""
    tc = snapshot.get("trust_contract", {}).get("summary", {})
    ma = snapshot.get("master_actions", {}).get("summary", {})
    theme = snapshot.get("theme", {}).get("summary", {})

    p0_blockers = tc.get("p0_blockers", [])
    merchant_appeal_ready = tc.get("merchant_appeal_ready", False)
    percent_complete = int(ma.get("percent_complete", 0) or 0)
    tm04_active = theme.get("tm04_active", False) or theme.get("theme_id") == BKS_TM04_THEME_ID

    if p0_blockers:
        return "trust_foundation"
    if not tm04_active or percent_complete < 50:
        return "collection_identity"
    if percent_complete < 75:
        return "conversion_support"
    if not merchant_appeal_ready:
        return "campaign_layer"
    return "merchant_appeal"


def _signals(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    google = snapshot.get("google", {})
    marketing = snapshot.get("marketing", {})
    sales = snapshot.get("sales_channels", {})
    avatar = snapshot.get("avatar", {})
    photo_studio = snapshot.get("photo_studio", {})
    trust_contract = snapshot.get("trust_contract", {})
    master_actions = snapshot.get("master_actions", {})
    member_area = snapshot.get("member_area", {})
    theme = snapshot.get("theme", {}).get("summary", {})

    sales_summary = sales.get("summary", {})
    avatar_summary = avatar.get("summary", {})
    photo_summary = photo_studio.get("summary", {})
    tc_summary = trust_contract.get("summary", {})
    ma_summary = master_actions.get("summary", {})

    p0_blockers = tc_summary.get("p0_blockers", [])
    tc_percent = int(tc_summary.get("percent_complete", 0) or 0)
    ma_percent = int(ma_summary.get("percent_complete", 0) or 0)
    tm04_active = theme.get("tm04_active", False) or theme.get("theme_id") == BKS_TM04_THEME_ID
    member_ok = member_area.get("status") in {"ok", "ready"}

    return [
        {
            "signal": "Google trust P0 gate",
            "source": "google_trust_contract + Merchant diagnostics",
            "status": "pass" if not p0_blockers else "needs_fix",
            "score": tc_percent,
            "meaning": f"Trust P0 blockers: {p0_blockers if p0_blockers else 'none'}. All P0 must pass before campaign layer.",
        },
        {
            "signal": "Master actions progress",
            "source": "master_action_queue.csv + master_agent_memory.json",
            "status": "pass" if ma_percent >= 90 else ("partial" if ma_percent >= 50 else "needs_fix"),
            "score": ma_percent,
            "meaning": f"{ma_percent}% of BKS operational actions complete. Blocked: {ma_summary.get('blocked_count', ma_summary.get('blocked', 0))}.",
        },
        {
            "signal": "TM04 theme and member area",
            "source": "ShopifyClient.active_theme_id() + bakabo.club/pages/bks-members",
            "status": "pass" if tm04_active and member_ok else ("partial" if tm04_active or member_ok else "needs_fix"),
            "score": (100 if tm04_active else 0) // 2 + (100 if member_ok else 0) // 2,
            "meaning": f"TM04 live: {tm04_active}. Member area ok: {member_ok}. Gold ring + Camerino + Metal tier depend on both.",
        },
        {
            "signal": "Tag and analytics visibility",
            "source": "Live site audit / GTM",
            "status": "ready" if float(google.get("tag_summary", {}).get("expected_gtm_percent", 0) or 0) >= 95 else "needs_fix",
            "score": int(float(google.get("tag_summary", {}).get("expected_gtm_percent", 0) or 0)),
            "meaning": "The agent can only adapt campaigns if measurement is reliable. Fix before market adaptation decisions.",
        },
        {
            "signal": "Timed offer readiness",
            "source": "Marketing offer / bks-timed-offer section",
            "status": marketing.get("summary", {}).get("compliance", "unknown"),
            "score": _score(marketing.get("summary", {}).get("compliance", "")),
            "meaning": "Scarcity can be used only when real (Shopify discount exists) and terms are clearly disclosed.",
        },
        {
            "signal": "Sales channel spread",
            "source": "Sales channel matrix",
            "status": "partial" if int(sales_summary.get("active", 0) or 0) < 3 else "ready",
            "score": min(100, int(sales_summary.get("active", 0) or 0) * 22 + int(sales_summary.get("partial", 0) or 0) * 10),
            "meaning": "Primary channel remains Shopify + Google Shopping until Meta/TikTok campaigns are trust-gated green.",
        },
        {
            "signal": "Avatar and video capacity",
            "source": "bakabo-avatar-resident + HeyGen",
            "status": "partial" if int(avatar_summary.get("progress", 0) or 0) < 80 else "ready",
            "score": int(avatar_summary.get("progress", 0) or 0),
            "meaning": "15s collection scripts per BKS collection. Activate after P0 photos and trust foundation are stable.",
        },
        {
            "signal": "Global Market System",
            "source": "bakabo-photo-studio + photo_studio_pipeline.csv",
            "status": "ready" if int(photo_summary.get("global_market_contexts", photo_summary.get("world_contexts", 0)) or 0) else "needs_build",
            "score": min(100, int(photo_summary.get("global_market_contexts", photo_summary.get("world_contexts", 0)) or 0) * 12),
            "meaning": "Market-localized product visuals keyed to TM04 accent colors. Enable after trust and shipping gates are green.",
        },
    ]


def _recommendations(signals: list[dict[str, Any]], snapshot: dict[str, Any]) -> list[dict[str, str]]:
    google_status = snapshot.get("google", {}).get("summary", {}).get("status", "")
    google_blockers = int(snapshot.get("google", {}).get("summary", {}).get("blockers", 0) or 0)
    tc_p0 = snapshot.get("trust_contract", {}).get("summary", {}).get("p0_blockers", [])
    ma_percent = int(snapshot.get("master_actions", {}).get("summary", {}).get("percent_complete", 0) or 0)
    theme = snapshot.get("theme", {}).get("summary", {})
    tm04_active = theme.get("tm04_active", False) or theme.get("theme_id") == BKS_TM04_THEME_ID
    member_ok = snapshot.get("member_area", {}).get("status") in {"ok", "ready"}
    stage = _commercial_stage(snapshot)

    recommendations: list[dict[str, str]] = []

    if tc_p0 or google_status == "suspended" or google_blockers:
        recommendations.append({
            "priority": "P0",
            "recommendation": "Clear Trust Contract P0 blockers before any campaign or Merchant appeal.",
            "change_type": "trust",
            "site_change": f"Resolve: {tc_p0 if tc_p0 else 'google_trust_contract.csv p0_blockers'}. Enforce TM04 published, Origin collection live, no folklore in feed.",
            "verification": "google_trust_contract.summary.merchant_appeal_ready == True and p0_blockers == [].",
        })

    if not tm04_active or not member_ok:
        recommendations.append({
            "priority": "P0",
            "recommendation": "Publish TM04 and verify member area before any member-facing campaign.",
            "change_type": "theme",
            "site_change": f"TM04 ({BKS_TM04_THEME_ID}) must be the published Shopify theme. Member area 60-second rule: gold ring, tier card, Camerino tab visible within 60s.",
            "verification": "ShopifyClient.active_theme_id() == '202392961362' and bakabo.club/pages/bks-members loads without empty sections.",
        })

    recommendations.append({
        "priority": "P1",
        "recommendation": "Feature one BKS collection at a time — rotate based on campaign and feed health.",
        "change_type": "content",
        "site_change": f"Current stage: {stage}. Pick one collection from {BKS_COLLECTIONS} and key homepage hero, email and social to its TM04 accent color. Do not change all 8 collections at once.",
        "verification": "Collection page HTTP 200, GTM present, product feed clean for that collection handle.",
    })

    recommendations.append({
        "priority": "P1",
        "recommendation": "Global Market System visuals: adapt by market only after trust and shipping gates are green.",
        "change_type": "creative",
        "site_change": "Use market-localized copy and TM04 accent colors. Keep same product, price, availability and policy evidence. Never invent prints, colors or model likenesses.",
        "verification": "google_trust_contract P0 pass, shipping policy live, landing page language/currency match submitted feed.",
    })

    recommendations.append({
        "priority": "P1",
        "recommendation": "Let the timed offer be a real launch window with visible terms.",
        "change_type": "marketing",
        "site_change": "Show countdown only when a real Shopify discount code exists and expiry is visible. Remove if no code.",
        "verification": "bks-timed-offer section shows real end date; marketing_timer_safe action is pass.",
    })

    if ma_percent >= 75:
        recommendations.append({
            "priority": "P1",
            "recommendation": "Activate avatar + HyperFrames collection drops after trust repair.",
            "change_type": "social",
            "site_change": "Use 15s HeyGen avatar scripts keyed to collection accent. HyperFrames provides the scene. YouTube Shorts, Reels and TikTok. No aggressive claims.",
            "verification": "Avatar script approved, render_id written to metadata, Merchant review submitted or appeal ready.",
        })

    return recommendations


def write_sheet(settings: Any, signals: list[dict[str, Any]], recommendations: list[dict[str, str]]) -> str:
    path = settings.root_dir / "output" / "market_sense_matrix.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["type", "priority", "name", "status", "score", "detail"])
        writer.writeheader()
        for row in signals:
            writer.writerow({
                "type": "signal",
                "priority": "",
                "name": row["signal"],
                "status": row["status"],
                "score": row["score"],
                "detail": row["meaning"],
            })
        for row in recommendations:
            writer.writerow({
                "type": "recommendation",
                "priority": row["priority"],
                "name": row["recommendation"],
                "status": row["change_type"],
                "score": "",
                "detail": row["site_change"],
            })
    return _relative(settings.root_dir, path)


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    signals = _signals(snapshot)
    recommendations = _recommendations(signals, snapshot)
    sheet = write_sheet(settings, signals, recommendations)
    average = round(sum(int(row["score"]) for row in signals) / max(len(signals), 1), 1)
    stage = _commercial_stage(snapshot)
    stage_index = COMMERCIAL_STAGES.index(stage) if stage in COMMERCIAL_STAGES else 0
    return {
        "summary": {
            "market_sense": average,
            "commercial_stage": stage,
            "stage_progress": f"{stage_index + 1}/{len(COMMERCIAL_STAGES)}",
            "signals": len(signals),
            "recommendations": len(recommendations),
            "mode": "conservative_adaptation",
            "sheet": sheet,
        },
        "signals": signals,
        "recommendations": recommendations,
    }
