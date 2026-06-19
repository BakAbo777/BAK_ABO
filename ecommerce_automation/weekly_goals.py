from __future__ import annotations

import csv
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


BAKABO_STORE_DOMAIN = "bakabo.club"
BKS_TM04_THEME_ID = "202392961362"

GOALS_FILE = Path("output/weekly_minimum_goals.csv")


GOAL_SPECS: tuple[dict[str, str], ...] = (
    {
        "id": "weekly_google_status",
        "area": "Google Merchant",
        "minimum": "Merchant status reviewed and P0 blockers documented.",
        "verify_from": "google.summary.blockers",
        "target": "0 P0 blockers before appeal",
    },
    {
        "id": "weekly_tags",
        "area": "Analytics",
        "minimum": "GTM target and GA4 coverage checked.",
        "verify_from": "google.tag_summary",
        "target": "GTM/GA4 coverage >= 95%",
    },
    {
        "id": "weekly_network",
        "area": "Network Trust",
        "minimum": "DNS, DMARC, DKIM/SPF, DSN/bounce and endpoint status reviewed.",
        "verify_from": "network.summary",
        "target": "0 network/email blockers before scaling campaigns",
    },
    {
        "id": "weekly_feed",
        "area": "Feed",
        "minimum": "Product feed scanned for missing attributes and risky claims.",
        "verify_from": "google.feed.summary",
        "target": "0 missing required fields on product rows, 0 unreviewed risky claims",
    },
    {
        "id": "weekly_catalog_sync",
        "area": "Catalog Sync",
        "minimum": "Shopify and Printify product snapshots compared for updates and status mismatch.",
        "verify_from": "catalog_sync.summary",
        "target": "0 catalog sync attention items",
    },
    {
        "id": "weekly_product_names",
        "area": "Product Names",
        "minimum": "Online/local product names checked for emoji, symbols, typos, duplicates and handle mismatch.",
        "verify_from": "product_names.summary",
        "target": "0 needs_fix product name issues",
    },
    {
        "id": "weekly_offer",
        "area": "Marketing",
        "minimum": "Timed offer date, terms and landing page verified.",
        "verify_from": "marketing.summary",
        "target": "compliance google_safe",
    },
    {
        "id": "weekly_theme",
        "area": "Theme",
        "minimum": "TM04 live theme reviewed: trust strip, editorial grid, Metal tier, timed offer.",
        "verify_from": "theme.summary",
        "target": "TM04 live on bakabo.club — status ready",
    },
    {
        "id": "weekly_market",
        "area": "Market Sense",
        "minimum": "Market signals reviewed before changing homepage/copy.",
        "verify_from": "market.summary",
        "target": "conservative_adaptation mode",
    },
    {
        "id": "weekly_agent_memory",
        "area": "Agent",
        "minimum": "Master action queue checked and memory updated.",
        "verify_from": "actions.summary",
        "target": "next action selected and verified when possible",
    },
    {
        "id": "weekly_growth_crm",
        "area": "Growth CRM",
        "minimum": "PDP clarity and welcome/post-purchase CRM priorities reviewed.",
        "verify_from": "growth_crm.summary",
        "target": "PDP clarity before heavier CRM automation",
    },
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _week_id() -> str:
    today = date.today()
    year, week, _ = today.isocalendar()
    return f"{year}-W{week:02d}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _status(goal_id: str, snapshot: dict[str, Any]) -> tuple[str, str]:
    google = snapshot.get("google", {})
    marketing = snapshot.get("marketing", {})
    theme = snapshot.get("theme", {})
    market = snapshot.get("market", {})
    actions = snapshot.get("actions", {})
    network = snapshot.get("network", {})
    growth_crm = snapshot.get("growth_crm", {})
    catalog_sync = snapshot.get("catalog_sync", {})
    product_names = snapshot.get("product_names", {})
    if goal_id == "weekly_google_status":
        blockers = int(google.get("summary", {}).get("blockers", 0))
        return ("pass" if blockers == 0 else "needs_fix", f"{blockers} P0 blockers")
    if goal_id == "weekly_tags":
        tag = google.get("tag_summary", {})
        gtm = float(tag.get("expected_gtm_percent", 0))
        ga = float(tag.get("ga4_percent", 0))
        return ("pass" if gtm >= 95 and ga >= 95 else "needs_fix", f"GTM {gtm}% / GA4 {ga}%")
    if goal_id == "weekly_network":
        summary = network.get("summary", {})
        needs = int(summary.get("needs_fix", 0) or 0)
        return ("pass" if needs == 0 and summary.get("status") == "pass" else "needs_fix", f"{needs} network blockers")
    if goal_id == "weekly_feed":
        feed = google.get("feed", {}).get("summary", {})
        missing = int(feed.get("missing_required", 0))
        claims = int(feed.get("claim_review", 0))
        return ("pass" if missing == 0 and claims == 0 else "needs_review", f"missing {missing}, claims {claims}")
    if goal_id == "weekly_catalog_sync":
        summary = catalog_sync.get("summary", {})
        attention = int(summary.get("attention", 0) or 0) + int(summary.get("errors", 0) or 0)
        return ("pass" if summary.get("status") == "synced" and attention == 0 else "needs_review", f"{attention} catalog attention items")
    if goal_id == "weekly_product_names":
        summary = product_names.get("summary", {})
        fix = int(summary.get("needs_fix", 0) or 0)
        review = int(summary.get("needs_review", 0) or 0)
        return ("pass" if fix == 0 and review == 0 else ("needs_fix" if fix else "needs_review"), f"{fix} fix, {review} review")
    if goal_id == "weekly_offer":
        compliance = marketing.get("summary", {}).get("compliance", "")
        return ("pass" if compliance == "google_safe" else "needs_fix", compliance or "unknown")
    if goal_id == "weekly_theme":
        status = theme.get("summary", {}).get("status", "")
        return ("pass" if status == "ready" else "needs_build", status or "unknown")
    if goal_id == "weekly_market":
        mode = market.get("summary", {}).get("mode", "")
        return ("pass" if mode == "conservative_adaptation" else "needs_review", mode or "unknown")
    if goal_id == "weekly_agent_memory":
        next_action = actions.get("next_action", {}).get("id", "")
        return ("pass" if next_action else "needs_review", next_action or "no next action")
    if goal_id == "weekly_growth_crm":
        summary = growth_crm.get("summary", {})
        attention = int(summary.get("attention", 0) or 0)
        return ("pass" if attention <= 2 else "needs_review", f"{attention} CRM/PDP attention items")
    return "needs_review", "unknown"


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, str]] = []
    for spec in GOAL_SPECS:
        status, evidence = _status(spec["id"], snapshot)
        rows.append(
            {
                **spec,
                "week": _week_id(),
                "status": status,
                "evidence": evidence,
                "updated_at": _now(),
            }
        )

    path = settings.root_dir / GOALS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["week", "id", "area", "status", "minimum", "target", "evidence", "verify_from", "updated_at"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in rows])

    return {
        "summary": {
            "week": _week_id(),
            "total": len(rows),
            "pass": sum(1 for row in rows if row["status"] == "pass"),
            "needs_attention": sum(1 for row in rows if row["status"] != "pass"),
            "sheet": _relative(settings.root_dir, path),
            "store": BAKABO_STORE_DOMAIN,
            "trust_gate": "trust_foundation",
        },
        "rows": rows,
    }
