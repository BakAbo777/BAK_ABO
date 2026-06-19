from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


BAKABO_STORE_DOMAIN = "bakabo.club"
BKS_TM04_THEME_ID = "202392961362"
BAKABO_CREW_EMAIL = "crew@bakabo.club"

SOCIAL_SHEET = Path("output/social_campaigns_matrix.csv")
SKILL_DOC = Path("BKS_SKILL/skills/bakabo-social-campaigns/SKILL.md")
PROTOCOL_DOC = Path("docs/bakabo-social-campaigns_SKILL.md")  # legacy


LANGUAGES: tuple[dict[str, str], ...] = (
    {"code": "it", "label": "Italiano", "role": "primary market", "tone": "chiaro, premium, rassicurante"},
    {"code": "en", "label": "English", "role": "international baseline", "tone": "clear, creative, trust-first"},
    {"code": "es", "label": "Espanol", "role": "EU/social expansion", "tone": "directo, visual, transparente"},
    {"code": "fr", "label": "Francais", "role": "EU/social expansion", "tone": "sobre, creatif, fiable"},
    {"code": "de", "label": "Deutsch", "role": "EU/trust market", "tone": "klar, sachlich, verlaesslich"},
)


CHANNELS: tuple[dict[str, str], ...] = (
    {
        "channel": "Instagram Reels",
        "type": "organic_social",
        "asset": "9:16 video + caption",
        "env": "META_ACCESS_TOKEN;INSTAGRAM_BUSINESS_ID",
        "publish_rule": "approval_required",
        "docs": "https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/content-publishing/",
    },
    {
        "channel": "Facebook Page",
        "type": "organic_social",
        "asset": "post/video + product link",
        "env": "META_ACCESS_TOKEN;FACEBOOK_PAGE_ID",
        "publish_rule": "approval_required",
        "docs": "https://developers.facebook.com/docs/graph-api/",
    },
    {
        "channel": "TikTok",
        "type": "organic_social",
        "asset": "9:16 video + caption",
        "env": "TIKTOK_ACCESS_TOKEN;TIKTOK_OPEN_ID",
        "publish_rule": "approval_required_after_app_review",
        "docs": "https://developers.tiktok.com/doc/content-posting-api-get-started/",
    },
    {
        "channel": "YouTube Shorts",
        "type": "organic_video",
        "asset": "short video + title + description",
        "env": "YOUTUBE_CHANNEL_ID;YOUTUBE_CLIENT_ID;YOUTUBE_CLIENT_SECRET;YOUTUBE_REFRESH_TOKEN",
        "publish_rule": "approval_required",
        "docs": "https://developers.google.com/youtube/v3/docs/videos/insert",
    },
    {
        "channel": "Pinterest",
        "type": "visual_discovery",
        "asset": "vertical pin + product/collection URL",
        "env": "PINTEREST_BUSINESS_ID;PINTEREST_ACCESS_TOKEN",
        "publish_rule": "approval_required",
        "docs": "https://developers.pinterest.com/docs/api/v5/",
    },
    {
        "channel": "Telegram",
        "type": "community",
        "asset": "short update + link",
        "env": "TELEGRAM_BOT_TOKEN;TELEGRAM_BOT_USERNAME",
        "publish_rule": "opt_in_only",
        "docs": "https://core.telegram.org/bots/api",
    },
    {
        "channel": "Email crew",
        "type": "owned_marketing",
        "asset": "transparent email + unsubscribe",
        "env": "OFFICIAL_INBOX_EMAIL;SMTP_HOST;SMTP_USER;SMTP_PASSWORD",
        "publish_rule": "consent_and_unsubscribe_required",
        "docs": "https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business",
    },
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _env_value(settings: Any, name: str) -> str:
    aliases = {
        "META_ACCESS_TOKEN": "meta_access_token",
        "INSTAGRAM_BUSINESS_ID": "instagram_business_id",
        "FACEBOOK_PAGE_ID": "facebook_page_id",
        "YOUTUBE_CHANNEL_ID": "youtube_channel_id",
        "YOUTUBE_CLIENT_ID": "youtube_client_id",
        "YOUTUBE_CLIENT_SECRET": "youtube_client_secret",
        "YOUTUBE_REFRESH_TOKEN": "youtube_refresh_token",
        "PINTEREST_BUSINESS_ID": "pinterest_business_id",
        "TELEGRAM_BOT_TOKEN": "telegram_bot_token",
        "TELEGRAM_BOT_USERNAME": "telegram_bot_username",
        "OFFICIAL_INBOX_EMAIL": "official_inbox_email",
        "SMTP_HOST": "smtp_host",
        "SMTP_USER": "smtp_user",
        "SMTP_PASSWORD": "smtp_password",
    }
    return str(getattr(settings, aliases.get(name, name.lower()), "") or "")


def _channel_status(settings: Any, env_string: str) -> tuple[str, str]:
    envs = [item.strip() for item in env_string.split(";") if item.strip()]
    configured = sum(1 for env in envs if _env_value(settings, env))
    if configured == len(envs):
        return "ready_to_draft", f"{configured}/{len(envs)} env"
    if configured:
        return "partial", f"{configured}/{len(envs)} env"
    return "planned", f"0/{len(envs)} env"


def rows(settings: Any, snapshot: dict[str, Any]) -> list[dict[str, str]]:
    google_blocked = snapshot.get("google", {}).get("summary", {}).get("status") == "suspended"
    trust_fixes = int(snapshot.get("trust", {}).get("summary", {}).get("needs_fix", 0))
    result: list[dict[str, str]] = []
    for channel in CHANNELS:
        status, configured = _channel_status(settings, channel["env"])
        if google_blocked or trust_fixes:
            autonomy = "draft_only_until_trust_green"
        elif status == "ready_to_draft":
            autonomy = channel["publish_rule"]
        else:
            autonomy = "prepare_assets_only"
        result.append(
            {
                **channel,
                "status": status,
                "configured": configured,
                "autonomy": autonomy,
                "next_action": _next_action(status, autonomy, channel["channel"]),
            }
        )
    return result


def _next_action(status: str, autonomy: str, channel: str) -> str:
    if autonomy == "draft_only_until_trust_green":
        return f"Prepare multilingual {channel} assets, but wait for Google Trust recovery before campaign push."
    if status == "ready_to_draft":
        return "Generate multilingual draft, run transparency check, request approval before publish."
    if status == "partial":
        return "Complete missing credentials, then run read-only/posting capability check."
    return "Keep in roadmap and prepare reusable copy/asset templates."


def write_sheet(settings: Any, data: list[dict[str, str]]) -> str:
    path = settings.root_dir / SOCIAL_SHEET
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["channel", "type", "status", "configured", "asset", "autonomy", "publish_rule", "env", "next_action", "docs"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in data])
    return _relative(settings.root_dir, path)


def write_protocol(settings: Any) -> str:
    skill_path = settings.root_dir / SKILL_DOC
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        "name: bakabo-social-campaigns",
        "description: Multilingual, transparent, supervised social campaigns for BKS Studio / bakabo.club.",
        "metadata:",
        "  type: skill",
        "  trust_gate: campaign_layer",
        f"  store: {BAKABO_STORE_DOMAIN}",
        "---",
        "",
        "# bakabo-social-campaigns",
        "",
        "Skill for multilingual, transparent, supervised social campaigns.",
        "",
        "## Languages",
        "",
    ]
    lines.extend(f"- `{lang['code']}` {lang['label']}: {lang['tone']} ({lang['role']})" for lang in LANGUAGES)
    lines.extend(
        [
            "",
            "## Autonomy",
            "",
            "The agent may research, draft, translate, adapt, schedule proposals and create campaign packs. Actual publishing, paid campaigns, customer retargeting and direct messages require approval unless an explicit autonomous policy is configured later.",
            "",
            "## Transparency checks",
            "",
            "- Identify BKS/BakAbo clearly.",
            "- Do not invent discounts, certifications, partnerships or scarcity.",
            "- Use product page and checkout as final authority for price and availability.",
            "- Keep unsubscribe/opt-out path for email and direct messaging.",
            "- Do not exploit sensitive data or hidden tracking.",
            "- Pause aggressive campaigns while Google Merchant trust is blocked.",
            "",
            "## Sources",
            "",
            "- [TikTok Content Posting API](https://developers.tiktok.com/doc/content-posting-api-get-started/)",
            "- [YouTube Data API videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert)",
            "- [FTC CAN-SPAM guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)",
        ]
    )
    content = "\n".join(lines) + "\n"
    skill_path.write_text(content, encoding="utf-8")
    legacy_path = settings.root_dir / PROTOCOL_DOC
    legacy_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_path.write_text(content, encoding="utf-8")
    return _relative(settings.root_dir, skill_path)


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    data = rows(settings, snapshot)
    sheet = write_sheet(settings, data)
    protocol = write_protocol(settings)
    return {
        "summary": {
            "channels": len(data),
            "ready": sum(1 for row in data if row["status"] == "ready_to_draft"),
            "partial": sum(1 for row in data if row["status"] == "partial"),
            "planned": sum(1 for row in data if row["status"] == "planned"),
            "languages": len(LANGUAGES),
            "autonomy": "supervised_transparent_campaigns",
            "sheet": sheet,
            "skill": protocol,
            "trust_gate": "campaign_layer",
        },
        "channels": data,
        "languages": list(LANGUAGES),
        "campaign_loop": [
            "Read market signal and Google Trust gate.",
            "Select collection and customer segment.",
            "Generate copy in target languages.",
            "Attach verified asset/video/product URL.",
            "Run transparency and policy checks.",
            "Request approval for publish/send/ad spend.",
            "Record results and customer signals in Knowledge DB.",
        ],
    }
