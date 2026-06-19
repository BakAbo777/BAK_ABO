from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

# priority: p0 = blocks core BKS operations; p1 = important, enable when ready; p2 = future channel
# trust_gate: minimum commercial stage before this service can be used for campaigns
API_SPECS: tuple[dict[str, Any], ...] = (
    # --- Core infrastructure (p0) ---
    {
        "api": "Shopify Admin",
        "priority": "p0",
        "phase": "05 Shopify publish / Deploy",
        "trust_gate": "trust_foundation",
        "purpose": "Theme, products, collections, metafields, TM04 publish, live checks.",
        "env": ("SHOPIFY_MYSHOPIFY_DOMAIN", "SHOPIFY_ADMIN_TOKEN", "SHOPIFY_API_VERSION"),
        "service_key": "shopify",
    },
    {
        "api": "Printify",
        "priority": "p0",
        "phase": "02 Import / 05 Publish",
        "trust_gate": "trust_foundation",
        "purpose": "Product drafts, publish flow, order sync. Real shop ID: 12030061 (resolved dynamically).",
        "env": ("PRINTIFY_API_TOKEN", "PRINTIFY_SHOP_ID"),
        "service_key": "printify",
    },
    {
        "api": "Email / SMTP",
        "priority": "p0",
        "phase": "Communications",
        "trust_gate": "trust_foundation",
        "purpose": "Transactional email, drop campaigns, member tier updates via crew@bakabo.club.",
        "env": ("SUPPORT_EMAIL", "SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD"),
        "service_key": "email",
    },
    {
        "api": "Email / IMAP",
        "priority": "p0",
        "phase": "Communications / Inbox",
        "trust_gate": "trust_foundation",
        "purpose": "Inbox monitor, customer classification, draft replies, member re-engagement trigger.",
        "env": ("OFFICIAL_INBOX_IMAP_HOST", "OFFICIAL_INBOX_IMAP_USER", "OFFICIAL_INBOX_IMAP_PASSWORD"),
        "service_key": "email_imap",
    },
    {
        "api": "Telegram Bot",
        "priority": "p0",
        "phase": "Communications / Bot",
        "trust_gate": "trust_foundation",
        "purpose": "Primary async customer chat, BKS assistant entry point, Roberto escalation path.",
        "env": ("TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_USERNAME", "TELEGRAM_BOT_URL"),
        "service_key": "telegram",
    },
    {
        "api": "Google Merchant",
        "priority": "p0",
        "phase": "Sales Channels",
        "trust_gate": "trust_foundation",
        "purpose": "Shopping feed, free listings, product diagnostics. ID: 5295165689.",
        "env": ("GOOGLE_MERCHANT_ID",),
        "service_key": "google_merchant",
    },
    {
        "api": "Cloudflare Workers",
        "priority": "p0",
        "phase": "Infrastructure / Edge",
        "trust_gate": "trust_foundation",
        "purpose": "bks-agent-refresh Worker: cron 12:00 CET daily refresh, edge routing, API gateway.",
        "env": ("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID"),
        "service_key": "cloudflare",
    },
    # --- AI services (p0 for content, p1 for avatar) ---
    {
        "api": "OpenAI",
        "priority": "p0",
        "phase": "04 AI content / images",
        "trust_gate": "trust_foundation",
        "purpose": "Copy, prompts, image generation, product descriptions, skill reasoning.",
        "env": ("OPENAI_API_KEY",),
        "service_key": "openai",
    },
    {
        "api": "Claude AI / Anthropic",
        "priority": "p0",
        "phase": "04 AI / Agent reasoning",
        "trust_gate": "trust_foundation",
        "purpose": "Master agent reasoning, skill dispatch, dialogic copilot, snapshot analysis.",
        "env": ("ANTHROPIC_API_KEY",),
        "service_key": "anthropic",
    },
    {
        "api": "HeyGen",
        "priority": "p1",
        "phase": "09 Avatar / Social Render",
        "trust_gate": "collection_identity",
        "purpose": "Avatar videos, 15s collection scripts per BKS collection, voice and portrait exports.",
        "env": ("HEYGEN_API_KEY", "HEYGEN_AVATAR_ID", "HEYGEN_VOICE_ID"),
        "service_key": "heygen",
    },
    {
        "api": "Image Factory",
        "priority": "p0",
        "phase": "03 Images / 09 Avatar assets",
        "trust_gate": "trust_foundation",
        "purpose": "Local image generation, P0 photo briefs, contact sheets, source previews.",
        "env": ("IMAGE_FACTORY_DIR", "IMAGE_FACTORY_URL"),
        "service_key": "image_factory",
    },
    # --- Communications (p1) ---
    {
        "api": "WhatsApp Business",
        "priority": "p1",
        "phase": "Communications",
        "trust_gate": "collection_identity",
        "purpose": "Order updates, human handoff, high-intent member follow-up after Telegram is live.",
        "env": ("WHATSAPP_BUSINESS_TOKEN", "WHATSAPP_PHONE_NUMBER_ID"),
        "service_key": "whatsapp",
    },
    {
        "api": "Meta / Instagram",
        "priority": "p1",
        "phase": "Communications / Social",
        "trust_gate": "collection_identity",
        "purpose": "Instagram DM @bakabofirm, Facebook page messaging, catalog retargeting.",
        "env": ("META_ACCESS_TOKEN", "INSTAGRAM_BUSINESS_ID", "FACEBOOK_PAGE_ID"),
        "service_key": "meta",
    },
    {
        "api": "Make",
        "priority": "p1",
        "phase": "01 Config / 07 Social",
        "trust_gate": "collection_identity",
        "purpose": "Outbound/inbound automation events, social render handoff, webhook routing.",
        "env": ("MAKE_WEBHOOK_URL", "MAKE_WEBHOOK_SECRET"),
        "service_key": "make",
    },
    # --- Social distribution (p1) ---
    {
        "api": "YouTube",
        "priority": "p1",
        "phase": "Social Render",
        "trust_gate": "conversion_support",
        "purpose": "Shorts upload for HeyGen avatar scripts, 15s per BKS collection.",
        "env": ("YOUTUBE_CHANNEL_ID", "YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"),
        "service_key": "youtube",
    },
    # --- Sales channels (p1/p2) ---
    {
        "api": "TikTok Shop",
        "priority": "p1",
        "phase": "Sales Channels",
        "trust_gate": "campaign_layer",
        "purpose": "Short-form commerce, shoppable content, new audience acquisition.",
        "env": ("TIKTOK_SHOP_ID", "TIKTOK_ACCESS_TOKEN"),
        "service_key": "tiktok_shop",
    },
    {
        "api": "Pinterest Catalog",
        "priority": "p1",
        "phase": "Sales Channels",
        "trust_gate": "collection_identity",
        "purpose": "Visual discovery catalog, product pins for editorial/lifestyle shots.",
        "env": ("PINTEREST_BUSINESS_ID", "PINTEREST_ACCESS_TOKEN"),
        "service_key": "pinterest",
    },
    {
        "api": "Etsy",
        "priority": "p2",
        "phase": "Sales Channels",
        "trust_gate": "campaign_layer",
        "purpose": "Curated marketplace for graphic/art-led BKS products.",
        "env": ("ETSY_SHOP_ID",),
        "service_key": "etsy",
    },
    {
        "api": "eBay",
        "priority": "p2",
        "phase": "Sales Channels",
        "trust_gate": "campaign_layer",
        "purpose": "Secondary marketplace testing.",
        "env": ("EBAY_SELLER_ID",),
        "service_key": "ebay",
    },
    {
        "api": "Amazon SP-API",
        "priority": "p2",
        "phase": "08 Amazon",
        "trust_gate": "campaign_layer",
        "purpose": "Future Merch on Demand and marketplace listing workflow.",
        "env": ("AMAZON_SP_API_CLIENT_ID",),
        "service_key": "amazon",
    },
)

# Statuses from connected services that map to "ready"
_READY_STATUSES = frozenset({"online", "configured", "render_ready", "connected", "pass", "synced"})
# Statuses that mean configured but limited — not a blocker, but not full green
_PARTIAL_STATUSES = frozenset({"suspended", "needs_review", "limited", "key_ready", "manual_pending"})
# Statuses that override "configured=True" to partial/missing
_BROKEN_STATUSES = frozenset({"offline", "missing_key", "missing_token", "missing_webhook_url", "missing_oauth", "error"})


def matrix_path(root_dir: Path) -> Path:
    return root_dir / "output" / "api_orchestration_matrix.csv"


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _service_status(service: Any) -> str:
    if isinstance(service, bool):
        return "ready" if service else "missing"
    if not isinstance(service, dict):
        return "missing"
    status = str(service.get("status", ""))
    configured = bool(service.get("configured", False))
    if status in _READY_STATUSES:
        return "ready"
    if status in _PARTIAL_STATUSES:
        return "partial"
    if configured and status not in _BROKEN_STATUSES:
        return "ready"
    if configured:
        return "partial"
    return "missing"


def rows(root_dir: Path, services: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for spec in API_SPECS:
        service = services.get(spec["service_key"], {})
        status = _service_status(service)
        result.append(
            {
                "api": spec["api"],
                "priority": spec["priority"],
                "status": status,
                "phase": spec["phase"],
                "trust_gate": spec["trust_gate"],
                "purpose": spec["purpose"],
                "required_env": ";".join(spec["env"]),
                "service_status": service.get("status", "") if isinstance(service, dict) else status,
            }
        )
    return result


def write_matrix(root_dir: Path, services: dict[str, Any]) -> dict[str, Any]:
    data = rows(root_dir, services)
    path = matrix_path(root_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)

    total = len(data)
    ready_count = sum(1 for row in data if row["status"] == "ready")
    p0_rows = [row for row in data if row.get("priority") == "p0"]
    p0_missing = [row["api"] for row in p0_rows if row["status"] == "missing"]
    first_missing = next((row["api"] for row in data if row["status"] == "missing"), "")

    return {
        "rows": data,
        "summary": {
            "ready": ready_count,
            "partial": sum(1 for row in data if row["status"] == "partial"),
            "missing": sum(1 for row in data if row["status"] == "missing"),
            "total": total,
            "percent_complete": round(ready_count / total * 100) if total else 0,
            "p0_missing": p0_missing,
            "first_missing": first_missing,
            "matrix": _relative(root_dir, path),
        },
    }
