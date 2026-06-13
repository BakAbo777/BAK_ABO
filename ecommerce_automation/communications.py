from __future__ import annotations

from typing import Any


def payload(settings: Any) -> dict[str, Any]:
    telegram_link = f"https://t.me/{settings.telegram_bot_username}" if settings.telegram_bot_username else settings.telegram_bot_url
    channels = [
        {
            "channel": "Email",
            "status": "configured" if settings.support_email and settings.smtp_host else "missing_config",
            "purpose": "Customer support, launch email, handoff from agent.",
            "required_env": "SUPPORT_EMAIL;SMTP_HOST;SMTP_PORT;SMTP_USER;SMTP_PASSWORD",
            "link": f"mailto:{settings.support_email}" if settings.support_email else "",
            "consent": "required for marketing email",
        },
        {
            "channel": "Instagram DM",
            "status": "configured" if settings.instagram_business_id and settings.meta_access_token else "missing_meta",
            "purpose": "Customer DM, social follow-up, human handoff.",
            "required_env": "INSTAGRAM_BUSINESS_ID;META_ACCESS_TOKEN",
            "link": "https://www.instagram.com/bakabofirm/",
            "consent": "required before automated conversation",
        },
        {
            "channel": "Telegram Bot",
            "status": "configured" if settings.telegram_bot_token and (settings.telegram_bot_username or settings.telegram_bot_url) else "missing_bot",
            "purpose": "Bot entry point for direct assistant/customer conversations.",
            "required_env": "TELEGRAM_BOT_TOKEN;TELEGRAM_BOT_USERNAME;TELEGRAM_BOT_URL",
            "link": telegram_link,
            "consent": "explicit opt-in required",
        },
        {
            "channel": "Facebook / Meta",
            "status": "configured" if settings.facebook_page_id and settings.meta_access_token else "missing_meta",
            "purpose": "Page messaging, catalog retargeting, bot routing.",
            "required_env": "FACEBOOK_PAGE_ID;META_BUSINESS_ID;META_ACCESS_TOKEN",
            "link": "https://www.facebook.com/bakabofirm/",
            "consent": "required before automated conversation",
        },
        {
            "channel": "YouTube",
            "status": "configured" if settings.youtube_channel_id else "missing_channel",
            "purpose": "Shorts comments, video discovery, future routing.",
            "required_env": "YOUTUBE_CHANNEL_ID",
            "link": settings.youtube_channel_url,
            "consent": "public comments only unless user opts in",
        },
        {
            "channel": "Customer Bot Link",
            "status": "planned" if not settings.customer_bot_url else "configured",
            "purpose": "Single opt-in entry point for assistant conversation.",
            "required_env": "CUSTOMER_BOT_URL",
            "link": settings.customer_bot_url,
            "consent": "explicit opt-in required",
        },
    ]
    return {
        "channels": channels,
        "summary": {
            "configured": sum(1 for row in channels if row["status"] == "configured"),
            "missing": sum(1 for row in channels if row["status"].startswith("missing")),
            "planned": sum(1 for row in channels if row["status"] == "planned"),
        },
    }
