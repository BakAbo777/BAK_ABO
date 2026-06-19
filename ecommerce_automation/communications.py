from __future__ import annotations

from typing import Any

BAKABO_STORE_DOMAIN = "bakabo.club"
BAKABO_CREW_EMAIL = "crew@bakabo.club"
BAKABO_INSTAGRAM = "https://www.instagram.com/bakabofirm/"
BAKABO_FACEBOOK = "https://www.facebook.com/bakabofirm/"

# trust_gate: minimum commercial stage before this channel can be used autonomously
# scope: member (Metal tier members only), public (all visitors), internal (Roberto/ops only)
CHANNEL_SPECS: tuple[dict[str, str], ...] = (
    {
        "channel": "Email SMTP",
        "priority": "p0",
        "scope": "both",
        "trust_gate": "trust_foundation",
        "purpose": "Transactional email, member tier updates, drop campaigns, agent handoff drafts.",
        "required_env": "SMTP_HOST;SMTP_PORT;SMTP_USER;SMTP_PASSWORD;SUPPORT_EMAIL",
        "consent": "required for marketing; transactional is implicit post-purchase",
        "bks_note": "Primary outbound channel. Use crew@bakabo.club. Require unsubscribe link for all marketing sends.",
    },
    {
        "channel": "Email IMAP",
        "priority": "p0",
        "scope": "internal",
        "trust_gate": "trust_foundation",
        "purpose": "Inbox monitoring, customer classification, draft generation, escalation routing.",
        "required_env": "OFFICIAL_INBOX_IMAP_HOST;OFFICIAL_INBOX_IMAP_USER;OFFICIAL_INBOX_IMAP_PASSWORD",
        "consent": "n/a — operator inbox",
        "bks_note": "crew@bakabo.club IMAP. Enables agent to read incoming email and draft replies. Required before member re-engagement workflows.",
    },
    {
        "channel": "Telegram Bot",
        "priority": "p0",
        "scope": "both",
        "trust_gate": "trust_foundation",
        "purpose": "Primary async customer chat, BKS assistant entry point, human escalation path.",
        "required_env": "TELEGRAM_BOT_TOKEN;TELEGRAM_BOT_USERNAME;TELEGRAM_BOT_URL",
        "consent": "explicit opt-in required before automated conversation",
        "bks_note": "Highest-value direct channel for BKS. Roberto can receive escalations here. Link from member area and contact page.",
    },
    {
        "channel": "WhatsApp Business",
        "priority": "p1",
        "scope": "both",
        "trust_gate": "collection_identity",
        "purpose": "Order updates, human handoff from assistant, high-intent member follow-up.",
        "required_env": "WHATSAPP_BUSINESS_TOKEN;WHATSAPP_PHONE_NUMBER_ID",
        "consent": "explicit opt-in required; do not initiate unless customer messaged first",
        "bks_note": "Use after Telegram is fully live. Never send marketing without explicit prior consent.",
    },
    {
        "channel": "Instagram DM",
        "priority": "p1",
        "scope": "public",
        "trust_gate": "collection_identity",
        "purpose": "Customer DM from social discovery, brand inquiry, human handoff.",
        "required_env": "INSTAGRAM_BUSINESS_ID;META_ACCESS_TOKEN",
        "consent": "required before automated response; human reply always allowed",
        "bks_note": "bakabofirm. Activate Meta Graph API for DM routing. Do not automate without opt-in.",
    },
    {
        "channel": "Facebook / Meta",
        "priority": "p1",
        "scope": "public",
        "trust_gate": "collection_identity",
        "purpose": "Page messaging, catalog retargeting, drop campaign distribution.",
        "required_env": "FACEBOOK_PAGE_ID;META_BUSINESS_ID;META_ACCESS_TOKEN",
        "consent": "required before automated conversation",
        "bks_note": "bakabofirm. Catalog retargeting requires Google Trust P0 green + Meta Commerce account.",
    },
    {
        "channel": "YouTube",
        "priority": "p1",
        "scope": "public",
        "trust_gate": "conversion_support",
        "purpose": "Shorts comments, collection video discovery, 15s avatar scripts (HeyGen).",
        "required_env": "YOUTUBE_CHANNEL_ID;YOUTUBE_CLIENT_ID;YOUTUBE_CLIENT_SECRET;YOUTUBE_REFRESH_TOKEN",
        "consent": "public comments only; no DM automation",
        "bks_note": "BKS avatar 15s scripts per collection (Hours/Glyph/Marker… etc). HeyGen generates, YouTube distributes. Enable after P0 photo shots are live.",
    },
    {
        "channel": "TikTok Shop",
        "priority": "p2",
        "scope": "public",
        "trust_gate": "campaign_layer",
        "purpose": "Short video product discovery, shoppable content, new audience acquisition.",
        "required_env": "TIKTOK_SHOP_ID;TIKTOK_ACCESS_TOKEN",
        "consent": "public content; no automated DM",
        "bks_note": "Activate only after Google Trust P0 green and catalog is clean. Shares feed with Shopify.",
    },
    {
        "channel": "BKS Assistant (Public)",
        "priority": "p1",
        "scope": "public",
        "trust_gate": "trust_foundation",
        "purpose": "Embedded AI assistant on bakabo.club for product discovery, sizing, member routing.",
        "required_env": "BKS_ASSISTANT_PUBLIC_ENDPOINT;BKS_ASSISTANT_PUBLIC_TOKEN;AGENT_CUSTOMER_CHAT_ENABLED",
        "consent": "explicit opt-in before storing conversation",
        "bks_note": "Embed via bks-ai-assistant.liquid section (TM04). Requires AGENT_CUSTOMER_CHAT_ENABLED=true. Never store PII without consent.",
    },
    {
        "channel": "Customer Bot Link",
        "priority": "p1",
        "scope": "both",
        "trust_gate": "trust_foundation",
        "purpose": "Single canonical URL for opt-in entry to assistant conversation.",
        "required_env": "CUSTOMER_BOT_URL",
        "consent": "explicit opt-in required",
        "bks_note": "Set CUSTOMER_BOT_URL to the Telegram bot link or assistant page. Used in member area CTA and email footers.",
    },
)


def _channel_status(ch: dict[str, str], settings: Any) -> tuple[str, str]:
    name = ch["channel"]
    if name == "Email SMTP":
        ok = bool(settings.support_email and settings.smtp_host and settings.smtp_port and settings.smtp_user and settings.smtp_password)
        return ("configured" if ok else "missing_config", f"mailto:{settings.support_email}" if settings.support_email else "")
    if name == "Email IMAP":
        ok = bool(settings.official_inbox_imap_host and settings.official_inbox_imap_user and settings.official_inbox_imap_password)
        email = settings.official_inbox_email or BAKABO_CREW_EMAIL
        return ("configured" if ok else "missing_config", f"mailto:{email}")
    if name == "Telegram Bot":
        ok = bool(settings.telegram_bot_token and (settings.telegram_bot_username or settings.telegram_bot_url))
        link = (f"https://t.me/{settings.telegram_bot_username}" if settings.telegram_bot_username else settings.telegram_bot_url) or ""
        return ("configured" if ok else "missing_bot", link)
    if name == "WhatsApp Business":
        ok = bool(settings.whatsapp_business_token and settings.whatsapp_phone_number_id)
        return ("configured" if ok else "missing_config", "https://business.whatsapp.com/")
    if name == "Instagram DM":
        ok = bool(settings.instagram_business_id and settings.meta_access_token)
        return ("configured" if ok else "missing_meta", BAKABO_INSTAGRAM)
    if name == "Facebook / Meta":
        ok = bool(settings.facebook_page_id and settings.meta_access_token)
        return ("configured" if ok else "missing_meta", BAKABO_FACEBOOK)
    if name == "YouTube":
        ok = bool(settings.youtube_channel_id and settings.youtube_client_id and settings.youtube_refresh_token)
        return ("configured" if ok else "missing_channel", settings.youtube_channel_url or "")
    if name == "TikTok Shop":
        ok = bool(settings.tiktok_shop_id and settings.tiktok_access_token)
        return ("configured" if ok else "missing_config", "")
    if name == "BKS Assistant (Public)":
        ok = bool(settings.bks_assistant_public_endpoint and settings.bks_assistant_public_token and settings.agent_customer_chat_enabled == "true")
        link = settings.bks_assistant_public_endpoint or f"https://{BAKABO_STORE_DOMAIN}/pages/bks-assistant"
        return ("configured" if ok else "missing_config", link)
    if name == "Customer Bot Link":
        ok = bool(settings.customer_bot_url)
        return ("configured" if ok else "planned", settings.customer_bot_url or "")
    return "unknown", ""


def payload(settings: Any) -> dict[str, Any]:
    channels = []
    for spec in CHANNEL_SPECS:
        status, link = _channel_status(spec, settings)
        channels.append({**spec, "status": status, "link": link})

    configured_count = sum(1 for ch in channels if ch["status"] == "configured")
    missing_count = sum(1 for ch in channels if ch["status"].startswith("missing"))
    planned_count = sum(1 for ch in channels if ch["status"] == "planned")

    p0_channels = [ch for ch in channels if ch.get("priority") == "p0"]
    p0_configured = [ch["channel"] for ch in p0_channels if ch["status"] == "configured"]
    p0_missing = [ch["channel"] for ch in p0_channels if ch["status"] != "configured"]

    first_unconfigured = next((ch["channel"] for ch in channels if ch["status"] != "configured"), "")
    campaign_ready = [ch["channel"] for ch in channels if ch["status"] == "configured" and ch.get("trust_gate") in {"trust_foundation", "collection_identity"}]

    return {
        "channels": channels,
        "summary": {
            "configured": configured_count,
            "missing": missing_count,
            "planned": planned_count,
            "total": len(channels),
            "p0_configured": p0_configured,
            "p0_missing": p0_missing,
            "campaign_ready_channels": campaign_ready,
            "first_unconfigured": first_unconfigured,
            "agent_rule": "Do not initiate automated customer conversations on any channel without explicit opt-in. P0 channels must be configured before member re-engagement workflows.",
        },
    }
