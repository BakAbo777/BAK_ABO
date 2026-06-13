from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _score(status: str) -> int:
    return {
        "pass": 100,
        "ready": 90,
        "active": 85,
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


def _signals(settings: Any, snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    google = snapshot.get("google", {})
    marketing = snapshot.get("marketing", {})
    sales = snapshot.get("sales_channels", {})
    avatar = snapshot.get("avatar", {})
    turbobak = snapshot.get("turbobak", {})

    google_summary = google.get("summary", {})
    sales_summary = sales.get("summary", {})
    avatar_summary = avatar.get("summary", {})
    turbo_summary = turbobak.get("summary", {})

    return [
        {
            "signal": "Google trust risk",
            "source": "Merchant diagnostics",
            "status": google_summary.get("status", "unknown"),
            "score": 100 - min(95, int(google_summary.get("blockers", 0)) * 45),
            "meaning": "Merchant recovery is the gating factor for growth.",
        },
        {
            "signal": "Tag and analytics visibility",
            "source": "Live site audit",
            "status": "ready" if google.get("tag_summary", {}).get("expected_gtm_percent", 0) >= 95 else "needs_fix",
            "score": int(google.get("tag_summary", {}).get("expected_gtm_percent", 0)),
            "meaning": "The agent can only adapt if measurement is reliable.",
        },
        {
            "signal": "Timed offer readiness",
            "source": "Marketing offer",
            "status": marketing.get("summary", {}).get("compliance", "unknown"),
            "score": _score(marketing.get("summary", {}).get("compliance", "")),
            "meaning": "Scarcity can be used only when real and clearly disclosed.",
        },
        {
            "signal": "Sales channel spread",
            "source": "Sales channel matrix",
            "status": "partial" if sales_summary.get("active", 0) < 3 else "ready",
            "score": min(100, int(sales_summary.get("active", 0)) * 22 + int(sales_summary.get("partial", 0)) * 10),
            "meaning": "Primary channel remains Shopify until Google/Meta are clean.",
        },
        {
            "signal": "Avatar content capacity",
            "source": "Avatar production",
            "status": "partial" if avatar_summary.get("progress", 0) < 80 else "ready",
            "score": int(avatar_summary.get("progress", 0)),
            "meaning": "Use avatar videos after trust and product pages are stable.",
        },
        {
            "signal": "TurboBAK operational memory",
            "source": settings.turbobak_path,
            "status": "ready" if turbobak.get("exists") else "missing",
            "score": min(100, int(turbo_summary.get("workers", 0)) * 10 + int(turbo_summary.get("pages", 0)) * 3),
            "meaning": "Local worker/dashboard patterns can guide next actions.",
        },
    ]


def _recommendations(signals: list[dict[str, Any]], snapshot: dict[str, Any]) -> list[dict[str, str]]:
    google_status = snapshot.get("google", {}).get("summary", {}).get("status", "")
    blockers = int(snapshot.get("google", {}).get("summary", {}).get("blockers", 0))
    recommendations: list[dict[str, str]] = []
    if google_status == "suspended" or blockers:
        recommendations.append(
            {
                "priority": "P0",
                "recommendation": "Keep site adaptation conservative until Merchant trust passes.",
                "change_type": "trust",
                "site_change": "Light theme, clear policies, no exaggerated discount claims, no fake urgency.",
                "verification": "Merchant P0 actions pass and live audit remains clean.",
            }
        )
    recommendations.append(
        {
            "priority": "P1",
            "recommendation": "Use market signals to rotate collection focus, not to rewrite the whole brand.",
            "change_type": "content",
            "site_change": "Feature one collection at a time in homepage/social based on active campaign and inventory/feed health.",
            "verification": "Collection page HTTP 200, GTM present, product feed available.",
        }
    )
    recommendations.append(
        {
            "priority": "P1",
            "recommendation": "Let the timed offer be a soft launch window.",
            "change_type": "marketing",
            "site_change": "Show countdown with visible terms and no discount percentage until Shopify discount exists.",
            "verification": "Timer compliance checks pass.",
        }
    )
    recommendations.append(
        {
            "priority": "P2",
            "recommendation": "Activate avatar spots after trust repair.",
            "change_type": "social",
            "site_change": "Use HeyGen videos for collection education and YouTube Shorts, not aggressive sales claims.",
            "verification": "Avatar/social render rows ready and Merchant review submitted.",
        }
    )
    return recommendations


def write_sheet(settings: Any, signals: list[dict[str, Any]], recommendations: list[dict[str, str]]) -> str:
    path = settings.root_dir / "output" / "market_sense_matrix.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["type", "priority", "name", "status", "score", "detail"])
        writer.writeheader()
        for row in signals:
            writer.writerow(
                {
                    "type": "signal",
                    "priority": "",
                    "name": row["signal"],
                    "status": row["status"],
                    "score": row["score"],
                    "detail": row["meaning"],
                }
            )
        for row in recommendations:
            writer.writerow(
                {
                    "type": "recommendation",
                    "priority": row["priority"],
                    "name": row["recommendation"],
                    "status": row["change_type"],
                    "score": "",
                    "detail": row["site_change"],
                }
            )
    return _relative(settings.root_dir, path)


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    signals = _signals(settings, snapshot)
    recommendations = _recommendations(signals, snapshot)
    sheet = write_sheet(settings, signals, recommendations)
    average = round(sum(int(row["score"]) for row in signals) / max(len(signals), 1), 1)
    return {
        "summary": {
            "market_sense": average,
            "signals": len(signals),
            "recommendations": len(recommendations),
            "mode": "conservative_adaptation",
            "sheet": sheet,
        },
        "signals": signals,
        "recommendations": recommendations,
    }
