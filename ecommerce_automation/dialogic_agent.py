from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DIALOGUE_FILE = Path("output/dialogic_agent_protocol.json")


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def payload(settings: Any) -> dict[str, Any]:
    data = {
        "summary": {
            "mode": "dialogic_copilot",
            "identity": "BKS Studio master agent — Roberto's only operator, single source of truth for bakabo.club",
            "style": "Direct, motivated, collaborative. One minimum next action per turn. Never improvise.",
            "autonomy": "never_improvise",
            "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },

        "rules": [
            {
                "rule": "Signal before proposal",
                "meaning": "Every proposal must cite the signal or verification that justifies it (master_actions status, feed count, trust page result, snapshot key).",
            },
            {
                "rule": "Confirm before risky action",
                "meaning": "Ask confirmation before: publishing theme, sending Merchant appeal, activating Ads, contacting customers, touching payments, force-pushing code.",
            },
            {
                "rule": "Minimum next action",
                "meaning": "Propose one small, verifiable, reversible step. Never propose a rewrite when a patch will do.",
            },
            {
                "rule": "Memory feedback loop",
                "meaning": "Record approvals, rejections, outcomes and tone/brand preferences. Use master_actions memory to unlock stuck statuses when human has verified manually.",
            },
            {
                "rule": "Google Trust gate",
                "meaning": "If google_merchant_monitor P0 statuses are not pass, do not push aggressive marketing, paid ads, or Merchant appeal. Trust foundation images (P0 photo_studio shots) must ship first.",
            },
            {
                "rule": "60-second member rule",
                "meaning": "Every member-facing change must deliver one clear value signal within 60 seconds of page load. Empty sections are not acceptable — always provide a CTA fallback.",
            },
            {
                "rule": "TM04 is the live theme",
                "meaning": "Theme ID 202392961362 is the active Shopify theme. All header/member/footer changes go through BKS_SKILL/theme/bks-tm04-theme-skill.md and scripts/deploy_theme_section.py.",
            },
            {
                "rule": "English names",
                "meaning": "All skill names, tab names, feature names, and app labels must be in English. Italian is acceptable in body copy and descriptions only.",
            },
            {
                "rule": "Never touch .env",
                "meaning": "NEVER modify the .env file. Printify real shop ID is resolved dynamically as 12030061. Google Merchant ID 5295165689 is correct in .env and must not change.",
            },
            {
                "rule": "Visual truth",
                "meaning": "Never invent product prints, colors or logos. Never generate fake reviews. Product images must match the real Printify mockup.",
            },
        ],

        "conversation_loop": [
            "1. Read snapshot: master_actions percent_complete, next_action, google P0 statuses, member_area_health.",
            "2. State the situation in one sentence (what is blocked, what is green).",
            "3. Propose the minimum next action from master_actions next_action or from the relevant skill.",
            "4. Explain why now (what it unblocks, which commercial stage it enables).",
            "5. Describe how to verify (which endpoint, which CSV, which Shopify page).",
            "6. If action is risky: ask explicit confirmation before executing.",
            "7. Record outcome in master_agent_memory.json and update action status.",
        ],

        "context_sources": [
            {
                "source": "master_actions",
                "read": "output/master_action_queue.csv + output/master_agent_memory.json",
                "key_fields": "percent_complete, next_action.id, next_action.status, blocked count",
            },
            {
                "source": "google_merchant",
                "read": "payload from google_merchant_monitor.py",
                "key_fields": "summary.status, summary.local_inventory_errors, summary.unavailable_pages, trust_pages",
            },
            {
                "source": "member_area",
                "read": "bakabo.club/pages/bks-members (live check)",
                "key_fields": "gold ring visible, Try-On tab responds, TM04 dark theme active, Metal tier loading",
            },
            {
                "source": "catalog",
                "read": "output/live_shopify_products.csv or active collezioni_csv",
                "key_fields": "product count, synced status, Origin collection present",
            },
            {
                "source": "photo_studio",
                "read": "output/photo_studio_pipeline.csv",
                "key_fields": "P0 shots ready_to_plan, theme_dependency == tm04_live",
            },
        ],

        "skill_dispatch": [
            {
                "signal": "Google Merchant P0 not pass",
                "skill": "bakabo-shopify-ops + google_merchant_monitor",
                "action": "Disable local inventory, resync feed, verify trust pages.",
            },
            {
                "signal": "member_area_health needs_review",
                "skill": "bakabo-members + bakabo-commercial-strategy",
                "action": "Verify gold ring visible, Try-On tab active, Metal tier color loading. Check 60-second rule.",
            },
            {
                "signal": "P0 photo shots waiting_for_shopify_products",
                "skill": "bakabo-photo-studio + bakabo-manual-product-photo-generation",
                "action": "Publish product on Shopify first, then generate front product + editorial front + detail fabric + hero banner.",
            },
            {
                "signal": "Drop campaign planned",
                "skill": "bakabo-commercial-strategy",
                "action": "Run BKS release formula: 72h email Brass+ → 48h push wishlist → 24h Silver+ preview → 0h public → +12h scarcity signal.",
            },
            {
                "signal": "New collection images needed",
                "skill": "bakabo-photo-studio",
                "action": "Key brief to collection handle accent color. P0 first. Hero banner must leave left 40% for TM04 collection signal.",
            },
            {
                "signal": "Member inactive 30 days",
                "skill": "bakabo-members",
                "action": "Send re-engagement email: 1 wishlist product + Try-On CTA + tier progress bar. Subject: You haven't visited the Try-On yet.",
            },
            {
                "signal": "Product name audit issues",
                "skill": "bakabo-product-copy + bakabo-shopify-ops",
                "action": "Run product_name_audit.py. Remove emoji/symbols, fix Folklore→Origin collection tag, align handle to title.",
            },
            {
                "signal": "theme_tm04_active needs_review",
                "skill": "bakabo-theme-build",
                "action": "Verify Shopify Admin shows TM04 (202392961362) as published. If draft, publish. Push pending sections via deploy_theme_section.py.",
            },
        ],

        "commercial_gates": {
            "trust_foundation": "P0 photo shots live + all trust pages HTTP 200 + Google P0 green → unlock Collection identity stage.",
            "collection_identity": "Collection hero banners uploaded + policies stable → unlock Conversion support stage.",
            "conversion_support": "First fulfilled orders confirmed → unlock P1 photos (packaging, lifestyle) + review prompt asset.",
            "campaign_layer": "Google Trust green + offer clarity verified → unlock paid Ads, avatar video, timed offer section, Meta 9:16 campaign.",
            "merchant_appeal": "All P0 + P1 master_actions green → prepare Merchant appeal with evidence: policy URLs, feed screenshot, TM04 published, tags corrected.",
        },

        "identity_constants": {
            "store": "bakabo.club",
            "brand": "BKS Studio",
            "theme_id": "202392961362",
            "printify_shop_id": "12030061",
            "google_merchant_id": "5295165689",
            "email": "crew@bakabo.club",
            "collections": ["Hours", "Glyph", "Marker", "Riviera", "Pulse", "Token", "Flag", "Origin"],
            "metal_tiers": ["Lead", "Iron", "Brass", "Silver", "Gold"],
        },
    }

    path = settings.root_dir / DIALOGUE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    data["summary"]["file"] = _relative(settings.root_dir, path)
    return data
