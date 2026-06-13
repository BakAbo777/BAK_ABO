from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS_FILE = Path("output/always_on_agent_status.json")
DRIVE_MANIFEST = Path("output/drive_sync_manifest.csv")


DRIVE_ITEMS: tuple[dict[str, str], ...] = (
    {"artifact": "Master memory", "path": "output/master_agent_memory.json", "drive_type": "json/file", "purpose": "Agent learning and verification history."},
    {"artifact": "Daily web update", "path": "output/daily_web_update.json", "drive_type": "json/file", "purpose": "Daily live/local monitoring report."},
    {"artifact": "Weekly goals", "path": "output/weekly_minimum_goals.csv", "drive_type": "sheet", "purpose": "Minimum weekly verification discipline."},
    {"artifact": "Google trust contract", "path": "output/google_trust_contract.csv", "drive_type": "sheet", "purpose": "Trust requirements and evidence."},
    {"artifact": "Google Merchant matrix", "path": "output/google_merchant_analytics_matrix.csv", "drive_type": "sheet", "purpose": "Merchant recovery actions."},
    {"artifact": "Agent OS connectors", "path": "output/agent_os_connector_registry.csv", "drive_type": "sheet", "purpose": "All current and future API connections."},
    {"artifact": "Market sense", "path": "output/market_sense_matrix.csv", "drive_type": "sheet", "purpose": "Signals and conservative site adaptations."},
    {"artifact": "Payments matrix", "path": "output/payments_matrix.csv", "drive_type": "sheet", "purpose": "Bitcoin, crypto and payment trust checks."},
    {"artifact": "Official inbox matrix", "path": "output/official_inbox_matrix.csv", "drive_type": "sheet", "purpose": "crew@bakabo.club monitoring, categories and transparent email rules."},
    {"artifact": "Social campaigns matrix", "path": "output/social_campaigns_matrix.csv", "drive_type": "sheet", "purpose": "Multilingual supervised social campaign readiness."},
    {"artifact": "Legal guardrails", "path": "output/legal_guardrails_matrix.csv", "drive_type": "sheet", "purpose": "Customer legal guarantees and compliance gates."},
    {"artifact": "Supplier contract matrix", "path": "output/supplier_contract_matrix.csv", "drive_type": "sheet", "purpose": "Producer/supplier minimum terms and risk checks."},
    {"artifact": "Photo studio pipeline", "path": "output/photo_studio_pipeline.csv", "drive_type": "sheet", "purpose": "Product/collection photography and theme composition pipeline."},
    {"artifact": "Theme AI assistant note", "path": "04_TEMA_SHOPIFY/BKS_AI_ASSISTANT_GOOGLE_TRUST_NOTE.md", "drive_type": "doc", "purpose": "Google-facing explanation of customer AI assistant guardrails."},
    {"artifact": "Agent routine queue", "path": "output/agent_routine_queue.csv", "drive_type": "sheet", "purpose": "Automatic update/suggest/verify routine."},
    {"artifact": "API cost guard matrix", "path": "output/api_cost_guard_matrix.csv", "drive_type": "sheet", "purpose": "Cost-aware API usage and approval gates."},
    {"artifact": "Network monitor report", "path": "output/network_monitor_report.json", "drive_type": "json/file", "purpose": "DNS, DMARC, DSN, endpoint and tracking suffix health."},
    {"artifact": "Network DNS matrix", "path": "output/network_dns_matrix.csv", "drive_type": "sheet", "purpose": "Domain DNS records and trust checks."},
    {"artifact": "Network email auth matrix", "path": "output/network_email_auth_matrix.csv", "drive_type": "sheet", "purpose": "SPF, DKIM, DMARC, SMTP TLS, DSN/bounce and unsubscribe checks."},
    {"artifact": "Realtime control status", "path": "output/realtime_control_status.json", "drive_type": "json/file", "purpose": "Live-light agent processing progression."},
    {"artifact": "Realtime processing timeline", "path": "output/realtime_processing_timeline.csv", "drive_type": "sheet", "purpose": "Visible processing stages for the conversational agent."},
    {"artifact": "Growth CRM matrix", "path": "output/growth_crm_member_area_matrix.csv", "drive_type": "sheet", "purpose": "Customer segments, member area, PDP diagnostics and CRM flow."},
    {"artifact": "Catalog live sync report", "path": "output/catalog_live_sync_report.json", "drive_type": "json/file", "purpose": "Shopify/Printify live catalog sync summary."},
    {"artifact": "Shopify live products", "path": "output/live_shopify_products.csv", "drive_type": "sheet", "purpose": "Products fetched directly from Shopify Admin API."},
    {"artifact": "Printify live products", "path": "output/live_printify_products.csv", "drive_type": "sheet", "purpose": "Products fetched directly from Printify API."},
    {"artifact": "Catalog platform diff", "path": "output/catalog_platform_diff.csv", "drive_type": "sheet", "purpose": "Product mapping/status differences between Shopify and Printify."},
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _drive_manifest(settings: Any) -> tuple[list[dict[str, str]], str]:
    rows: list[dict[str, str]] = []
    drive_enabled = settings.google_drive_enabled.lower() in {"1", "true", "yes", "on"}
    for item in DRIVE_ITEMS:
        path = settings.root_dir / item["path"]
        rows.append(
            {
                **item,
                "exists": "yes" if path.exists() else "no",
                "drive_status": "ready_to_sync" if drive_enabled and path.exists() else ("prepared" if path.exists() else "waiting_for_artifact"),
                "last_modified": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(timespec="seconds") if path.exists() else "",
            }
        )

    manifest_path = settings.root_dir / DRIVE_MANIFEST
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["artifact", "path", "drive_type", "purpose", "exists", "drive_status", "last_modified"]
    with manifest_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return rows, _relative(settings.root_dir, manifest_path)


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    drive_rows, drive_manifest = _drive_manifest(settings)
    actions = snapshot.get("actions", {})
    trust = snapshot.get("trust", {})
    daily = snapshot.get("daily", {})
    weekly = snapshot.get("weekly", {})
    next_action = actions.get("next_action", {})
    blockers = int(trust.get("summary", {}).get("needs_fix", 0)) + int(actions.get("summary", {}).get("blocked", 0))
    drive_ready = sum(1 for row in drive_rows if row["drive_status"] == "ready_to_sync")
    report = {
        "summary": {
            "mode": "always_on_supervised",
            "autonomy": settings.agent_autonomy_level,
            "customer_chat": settings.agent_customer_chat_enabled,
            "status": "attention" if blockers else "watching",
            "blockers": blockers,
            "next_action": next_action.get("title", ""),
            "daily_mode": daily.get("summary", {}).get("mode", ""),
            "weekly_attention": weekly.get("summary", {}).get("needs_attention", 0),
            "drive_ready": drive_ready,
            "drive_manifest": drive_manifest,
            "updated_at": _now(),
        },
        "loops": [
            {"loop": "Daily web update", "cadence": "daily 12:00", "status": "active", "approval": "none for read checks"},
            {"loop": "Google trust gate", "cadence": "every dashboard refresh", "status": "active", "approval": "required before appeal"},
            {"loop": "Weekly minimum goals", "cadence": "weekly", "status": "active", "approval": "none for checks"},
            {"loop": "Theme/offer patching", "cadence": "on demand", "status": "prepared", "approval": "required before publish"},
            {"loop": "Customer messaging", "cadence": "on opt-in", "status": "guarded", "approval": "human handoff required"},
            {"loop": "Official inbox crew@bakabo.club", "cadence": "continuous when IMAP configured", "status": "prepared", "approval": "human review for risky replies"},
            {"loop": "Social campaigns", "cadence": "weekly planning + launch windows", "status": "prepared", "approval": "required before publish/ad spend"},
            {"loop": "Photo studio / reviews", "cadence": "after product realization and delivery", "status": "prepared", "approval": "required before customer review asks if incentive exists"},
            {"loop": "Routine and cost guard", "cadence": "every agent cycle", "status": "active", "approval": "required for metered/public/risky actions"},
            {"loop": "Network trust monitor", "cadence": "realtime snapshot + manual live check", "status": "prepared", "approval": "required before DNS/email infrastructure changes"},
            {"loop": "Growth CRM / member area", "cadence": "weekly and after order events", "status": "prepared", "approval": "required before customer sends"},
            {"loop": "Real-time control", "cadence": "8 second dashboard heartbeat", "status": "active", "approval": "none for status display"},
            {"loop": "Catalog Shopify/Printify sync", "cadence": "manual live button + scheduled later", "status": "prepared", "approval": "none for read; required before product writes"},
        ],
        "drive": drive_rows,
        "next_action": next_action,
        "guardrails": [
            "Monitor always; write only when approved or low-risk local artifact.",
            "Google trust gate blocks growth actions when red.",
            "Drive mirror is a copy of memory/report artifacts, not the only source of truth.",
            "Customer-facing messages require consent and human escalation path.",
        ],
    }
    path = settings.root_dir / STATUS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    report["summary"]["status_file"] = _relative(settings.root_dir, path)
    return report
