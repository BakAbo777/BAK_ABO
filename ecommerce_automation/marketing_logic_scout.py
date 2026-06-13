from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


PLAYBOOKS: tuple[dict[str, Any], ...] = (
    {
        "logic": "Creator-led social commerce",
        "already_active": "Instagram/TikTok/YouTube creators tag or link products directly from content.",
        "best_for_bks": "Avatar videos, founder-led clips, styling reels, artist/process stories.",
        "product_quality_need": "Hero images, clear product pages, size/fit confidence, fast visual recognition.",
        "brand_fit": 92,
        "google_risk": 35,
        "first_action": "Use Glyph or Riviera as first creator-style test after trust pages pass.",
        "source": "Shopify social commerce",
        "source_url": "https://www.shopify.com/enterprise/blog/social-commerce-trends",
    },
    {
        "logic": "Shoppable short video",
        "already_active": "YouTube Shopping and Shorts let merchants connect stores and tag products in content.",
        "best_for_bks": "15-second HeyGen collection explainers and product close-up Shorts.",
        "product_quality_need": "Video-ready collection story, product landing page, clear terms and returns.",
        "brand_fit": 88,
        "google_risk": 40,
        "first_action": "Prepare YouTube Shorts metadata but publish only after Merchant trust P0 is green.",
        "source": "YouTube Shopping Help",
        "source_url": "https://support.google.com/youtube/answer/12257682",
    },
    {
        "logic": "Pinterest visual discovery",
        "already_active": "Pinterest acts as visual search for unbranded product discovery and mood-board intent.",
        "best_for_bks": "Pattern-led collections, backpacks, sneakers, swimwear, gift boards.",
        "product_quality_need": "Clean vertical images, product titles, collection boards, no misleading claims.",
        "brand_fit": 86,
        "google_risk": 25,
        "first_action": "Create board concepts by collection; activate catalog after Google feed is clean.",
        "source": "Shopify social commerce",
        "source_url": "https://www.shopify.com/enterprise/blog/social-commerce-trends",
    },
    {
        "logic": "Trust-first Merchant recovery",
        "already_active": "Google rewards accurate product data, matching landing pages, crawlable images and clear policies.",
        "best_for_bks": "Foundation for Google Shopping, YouTube Shopping and all paid acquisition.",
        "product_quality_need": "Accurate product descriptions, real images, available pages, no promo text in feed descriptions.",
        "brand_fit": 100,
        "google_risk": 10,
        "first_action": "Fix About/FAQ 404, stale products, risky claim tokens and feed attributes.",
        "source": "Google product data specification",
        "source_url": "https://support.google.com/merchants/answer/7052112",
    },
    {
        "logic": "Global checkout and payment optionality",
        "already_active": "Global ecommerce growth is tied to localized checkout, wallets, payments, shipping and returns clarity.",
        "best_for_bks": "Bitcoin/crypto as modern checkout option plus traditional wallets and PayPal.",
        "product_quality_need": "Clear refund policy, no investment language, payment availability visible at checkout.",
        "brand_fit": 80,
        "google_risk": 55,
        "first_action": "Keep Bitcoin as optional payment trust asset, not a promotional headline.",
        "source": "Shopify global ecommerce",
        "source_url": "https://www.shopify.com/enterprise/blog/global-ecommerce-statistics",
    },
    {
        "logic": "Soft limited drop / launch window",
        "already_active": "Time-limited product windows are common, but need real availability and terms.",
        "best_for_bks": "Launch Window timer for current BKS Studio drop.",
        "product_quality_need": "Real expiry, visible terms, matching landing page, no fake discount.",
        "brand_fit": 78,
        "google_risk": 60,
        "first_action": "Use countdown only as real campaign window with terms, not urgency pressure.",
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
    trust = snapshot.get("trust", {}).get("summary", {})
    google = snapshot.get("google", {}).get("summary", {})
    marketing = snapshot.get("marketing", {}).get("summary", {})
    avatar = snapshot.get("avatar", {}).get("summary", {})
    payments = snapshot.get("payments", {}).get("summary", {})
    trust_red = int(trust.get("needs_fix", 0))
    merchant_suspended = google.get("status") == "suspended"

    logic = playbook["logic"]
    if logic == "Trust-first Merchant recovery":
        return ("do_now", "This is the gate for all growth actions.")
    if trust_red or merchant_suspended:
        if logic in {"Creator-led social commerce", "Shoppable short video", "Soft limited drop / launch window"}:
            return ("prepare_only", "Prepare assets, but wait for Google trust repair before aggressive activation.")
    if logic == "Shoppable short video" and int(avatar.get("progress", 0)) < 70:
        return ("prepare_only", "Avatar/social production is not complete enough for publish.")
    if logic == "Soft limited drop / launch window" and marketing.get("compliance") != "google_safe":
        return ("needs_fix", "Timer terms/deadline must be Google-safe.")
    if logic == "Global checkout and payment optionality" and payments.get("bitcoin") != "active":
        return ("prepare_only", "Payment method still needs checkout verification.")
    return ("recommended", "Fit is good once current blockers are handled.")


def rows(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for playbook in PLAYBOOKS:
        readiness, note = _readiness(snapshot, playbook)
        quality_score = int(playbook["brand_fit"]) - int(playbook["google_risk"] * 0.25)
        result.append(
            {
                **playbook,
                "readiness": readiness,
                "agent_note": note,
                "quality_fit_score": max(0, min(100, round(quality_score))),
            }
        )
    return sorted(result, key=lambda row: (row["readiness"] != "do_now", -row["quality_fit_score"]))


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    data = rows(snapshot)
    path = settings.root_dir / "output" / "marketing_logic_scout.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "logic",
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
    return {
        "summary": {
            "playbooks": len(data),
            "do_now": sum(1 for row in data if row["readiness"] == "do_now"),
            "recommended": sum(1 for row in data if row["readiness"] == "recommended"),
            "prepare_only": sum(1 for row in data if row["readiness"] == "prepare_only"),
            "best_logic": best.get("logic", ""),
            "sheet": _relative(settings.root_dir, path),
        },
        "rows": data,
        "sources": [
            {"label": "Shopify social commerce trends", "url": "https://www.shopify.com/enterprise/blog/social-commerce-trends"},
            {"label": "Google Merchant product data specification", "url": "https://support.google.com/merchants/answer/7052112"},
            {"label": "YouTube Shopping Help", "url": "https://support.google.com/youtube/answer/12257682"},
            {"label": "Shopify global ecommerce trends", "url": "https://www.shopify.com/enterprise/blog/global-ecommerce-statistics"},
        ],
    }
