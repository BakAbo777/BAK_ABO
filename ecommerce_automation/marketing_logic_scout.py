from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

BKS_TM04_THEME_ID = "202392961362"
BKS_COLLECTIONS = ("Hours", "Glyph", "Marker", "Riviera", "Pulse", "Token", "Flag", "Origin")

# Readiness rank for sorting (lower = more urgent)
_READINESS_RANK = {"do_now": 0, "recommended": 1, "prepare_only": 2, "needs_fix": 3, "blocked": 4}


PLAYBOOKS: tuple[dict[str, Any], ...] = (
    {
        "logic": "Trust-first Merchant recovery",
        "trust_gate": "trust_foundation",
        "already_active": "Google rewards accurate product data, matching landing pages, crawlable images and clear policies.",
        "best_for_bks": "Foundation for all paid acquisition, Google Shopping, YouTube Shopping. Unblocks merchant_appeal_ready.",
        "product_quality_need": "Accurate product descriptions, real images, HTTP 200 product pages, no promo text in feed descriptions, Origin not Folklore.",
        "brand_fit": 100,
        "google_risk": 10,
        "first_action": "Open google_trust_contract.csv → check p0_blockers. Resolve in order: Business identity → Product truth → Collection identity → Returns → Secure checkout.",
        "source": "Google product data specification",
        "source_url": "https://support.google.com/merchants/answer/7052112",
    },
    {
        "logic": "BKS Metal tier member retention",
        "trust_gate": "trust_foundation",
        "already_active": "Loyalty tiers (Lead/Iron/Brass/Silver/Gold) are built on Shopify order count. Gold ring + Camerino are live on TM04.",
        "best_for_bks": "Re-engage 12 subscribers and 20 dormant accounts. Tier upgrade CTAs drive repeat purchases and Camerino Try-On activation.",
        "product_quality_need": "TM04 published, gold ring CSS loading, Camerino tab responding, 60-second rule met on /pages/bks-members.",
        "brand_fit": 97,
        "google_risk": 5,
        "first_action": "Verify member area health: gold ring visible, tier card loads within 60s. Then draft welcome flow for 12 BKS Subscribers.",
        "source": "bakabo-members skill",
        "source_url": "BKS_SKILL/skills/bakabo-members/SKILL.md",
    },
    {
        "logic": "BKS collection drop mechanics",
        "trust_gate": "collection_identity",
        "already_active": "BKS release formula: 72h Brass+ email → 48h wishlist push → 24h Silver+ preview → 0h public → +12h scarcity signal.",
        "best_for_bks": "Structured drops create urgency without fake timers. Each collection has its own TM04 accent color and editorial identity.",
        "product_quality_need": "P0 photos live for drop collection, hero banner with left 40% clear for TM04 signal, real Shopify discount code if offering one.",
        "brand_fit": 95,
        "google_risk": 20,
        "first_action": "Pick one collection (recommend Glyph or Hours for first drop). Run P0 photo brief. Set up BKS release formula email sequence in Shopify Email.",
        "source": "bakabo-commercial-strategy skill",
        "source_url": "BKS_SKILL/skills/bakabo-commercial-strategy/SKILL.md",
    },
    {
        "logic": "Creator-led social commerce",
        "trust_gate": "collection_identity",
        "already_active": "Instagram/TikTok/YouTube creators tag or link products directly from content.",
        "best_for_bks": "Founder-led avatar clips (HeyGen 15s), styling reels keyed to collection accent color, artist/process stories for Glyph and Marker.",
        "product_quality_need": "P0 hero images live, product pages HTTP 200, size/fit guide visible, fast visual recognition for each of 8 collections.",
        "brand_fit": 92,
        "google_risk": 35,
        "first_action": "Use Glyph (#2e1a1a) or Riviera (#1a2a3e) as first creator-style test. Key visual to TM04 accent. Wait for Google trust P0 green.",
        "source": "Shopify social commerce",
        "source_url": "https://www.shopify.com/enterprise/blog/social-commerce-trends",
    },
    {
        "logic": "Shoppable short video",
        "trust_gate": "conversion_support",
        "already_active": "YouTube Shopping and Shorts let merchants connect stores and tag products in content.",
        "best_for_bks": "15-second HeyGen avatar scripts per BKS collection. HyperFrames provides the scene. Distribute via YouTube Shorts, Reels, TikTok.",
        "product_quality_need": "Avatar script approved, render_id logged, collection landing page HTTP 200, Merchant P0 green, no aggressive claims in video.",
        "brand_fit": 88,
        "google_risk": 40,
        "first_action": "Prepare collection scripts using COLLECTION_VIDEO_BRIEFS accents. Publish only after merchant_appeal_ready or Merchant review submitted.",
        "source": "YouTube Shopping Help",
        "source_url": "https://support.google.com/youtube/answer/12257682",
    },
    {
        "logic": "Pinterest visual discovery",
        "trust_gate": "collection_identity",
        "already_active": "Pinterest acts as visual search for unbranded product discovery and mood-board intent.",
        "best_for_bks": "TM04 accent-keyed editorial boards per collection. Origin (earth, linen), Riviera (coastal), Glyph (type as texture).",
        "product_quality_need": "Clean vertical images (P0 front product shot), product titles aligned to collection handle, no misleading claims.",
        "brand_fit": 86,
        "google_risk": 25,
        "first_action": "Create board concepts for 3 collections. Activate Shopify–Pinterest catalog sync after Google feed is clean.",
        "source": "Shopify social commerce",
        "source_url": "https://www.shopify.com/enterprise/blog/social-commerce-trends",
    },
    {
        "logic": "Global checkout and payment optionality",
        "trust_gate": "trust_foundation",
        "already_active": "Global ecommerce growth is tied to localized checkout, wallets, payments, shipping and returns clarity.",
        "best_for_bks": "Bitcoin/crypto as modern checkout signal plus PayPal/card/wallet. Position as optionality, never financial promise.",
        "product_quality_need": "crypto_refund_policy_url set and live, no investment language anywhere, payment options visible at checkout.",
        "brand_fit": 80,
        "google_risk": 55,
        "first_action": "Verify crypto_refund_policy_url is set. Check 'Secure checkout' row in legal_guardrails. Bitcoin is optional payment only.",
        "source": "Shopify global ecommerce",
        "source_url": "https://www.shopify.com/enterprise/blog/global-ecommerce-statistics",
    },
    {
        "logic": "Soft limited drop / launch window",
        "trust_gate": "collection_identity",
        "already_active": "Time-limited product windows build real urgency when the scarcity is genuine.",
        "best_for_bks": "BKS timed offer section on TM04. Real Shopify discount code, visible expiry, countdown keyed to drop collection.",
        "product_quality_need": "Real end date/time, matching Shopify discount code active, terms paragraph visible, no fake percentage discount.",
        "brand_fit": 78,
        "google_risk": 60,
        "first_action": "Set real end date in bks-timed-offer section. Link to drop collection page. Verify timer compliance in marketing_logic_scout.",
        "source": "Google trust + offer clarity",
        "source_url": "https://support.google.com/merchants/answer/6150127?hl=it",
    },
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _readiness(snapshot: dict[str, Any], playbook: dict[str, Any]) -> tuple[str, str]:
    tc = snapshot.get("trust_contract", {}).get("summary", {})
    google = snapshot.get("google", {}).get("summary", {})
    marketing = snapshot.get("marketing", {}).get("summary", {})
    avatar = snapshot.get("avatar", {}).get("summary", {})
    member_area = snapshot.get("member_area", {})
    theme = snapshot.get("theme", {}).get("summary", {})

    p0_blockers: list[str] = tc.get("p0_blockers", [])
    merchant_appeal_ready: bool = tc.get("merchant_appeal_ready", False)
    merchant_suspended: bool = google.get("status") == "suspended"
    tm04_active: bool = theme.get("tm04_active", False) or theme.get("theme_id") == BKS_TM04_THEME_ID
    member_ok: bool = member_area.get("status") in {"ok", "ready"}

    logic = playbook["logic"]

    if logic == "Trust-first Merchant recovery":
        if not p0_blockers and merchant_appeal_ready:
            return "recommended", "P0 clear — Merchant appeal can now be submitted."
        return "do_now", f"P0 blockers: {p0_blockers if p0_blockers else 'checking...'}. This gates all growth actions."

    if logic == "BKS Metal tier member retention":
        if not tm04_active:
            return "needs_fix", f"TM04 ({BKS_TM04_THEME_ID}) is not the published theme. Gold ring and Camerino will not load."
        if not member_ok:
            return "needs_fix", "Member area failed 60-second test. Fix before launching re-engagement email."
        return "do_now", "12 subscribers ready for welcome flow. Member area healthy. Highest-ROI action at current scale."

    if p0_blockers or merchant_suspended:
        if logic in {"Creator-led social commerce", "Shoppable short video", "Soft limited drop / launch window", "BKS collection drop mechanics"}:
            return "prepare_only", f"Prepare assets. Wait for Google trust P0 green. Blockers: {p0_blockers}."

    if logic == "BKS collection drop mechanics":
        return "recommended", "Trust foundation clear. Draft BKS release formula email sequence. Pick one collection."

    if logic == "Shoppable short video":
        if int(avatar.get("progress", 0) or 0) < 70:
            return "prepare_only", "Avatar production < 70% — prepare scripts but do not publish until complete."
        if not merchant_appeal_ready:
            return "prepare_only", "Prepare scripts. Publish after Merchant review submitted."
        return "recommended", "Avatar ready and trust green. Activate YouTube Shorts pipeline."

    if logic == "Soft limited drop / launch window":
        if marketing.get("compliance") != "google_safe":
            return "needs_fix", "Timer terms/deadline must be Google-safe. Set real end date and visible terms."
        return "recommended", "Timer is Google-safe. Activate as real launch window."

    if logic == "Global checkout and payment optionality":
        bitcoin_refund_set = bool(snapshot.get("settings_crypto_refund_url", ""))
        if not bitcoin_refund_set:
            return "prepare_only", "Set crypto_refund_policy_url before promoting Bitcoin payment."
        return "recommended", "Payment optionality is clean. Keep Bitcoin as checkout signal only."

    return "recommended", "Fit is good once current blockers are handled."


def rows(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for playbook in PLAYBOOKS:
        readiness, note = _readiness(snapshot, playbook)
        quality_score = int(playbook["brand_fit"]) - int(playbook["google_risk"] * 0.25)
        result.append({
            **playbook,
            "readiness": readiness,
            "agent_note": note,
            "quality_fit_score": max(0, min(100, round(quality_score))),
        })
    return sorted(
        result,
        key=lambda row: (
            _READINESS_RANK.get(str(row["readiness"]), 5),
            -int(row["quality_fit_score"]),
        ),
    )


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    data = rows(snapshot)
    path = settings.root_dir / "output" / "marketing_logic_scout.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "logic",
        "trust_gate",
        "readiness",
        "quality_fit_score",
        "brand_fit",
        "google_risk",
        "already_active",
        "best_for_bks",
        "product_quality_need",
        "first_action",
        "agent_note",
        "source",
        "source_url",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in data])

    best = data[0] if data else {}
    next_playbook = next((row for row in data if row["readiness"] == "recommended"), best)
    p0_blocked = [row["logic"] for row in data if row["readiness"] in {"blocked", "needs_fix"}]

    return {
        "summary": {
            "playbooks": len(data),
            "do_now": sum(1 for row in data if row["readiness"] == "do_now"),
            "recommended": sum(1 for row in data if row["readiness"] == "recommended"),
            "prepare_only": sum(1 for row in data if row["readiness"] == "prepare_only"),
            "needs_fix": sum(1 for row in data if row["readiness"] == "needs_fix"),
            "best_logic": best.get("logic", ""),
            "next_playbook": next_playbook.get("logic", ""),
            "p0_blocked_playbooks": p0_blocked,
            "sheet": _relative(settings.root_dir, path),
        },
        "rows": data,
        "sources": [
            {"label": "Google Merchant product data specification", "url": "https://support.google.com/merchants/answer/7052112"},
            {"label": "Shopify social commerce trends", "url": "https://www.shopify.com/enterprise/blog/social-commerce-trends"},
            {"label": "YouTube Shopping Help", "url": "https://support.google.com/youtube/answer/12257682"},
            {"label": "Shopify global ecommerce trends", "url": "https://www.shopify.com/enterprise/blog/global-ecommerce-statistics"},
            {"label": "Google Merchant offer clarity", "url": "https://support.google.com/merchants/answer/6150127?hl=it"},
        ],
    }
