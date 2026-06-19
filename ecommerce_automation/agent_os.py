from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any


CONNECTORS: tuple[dict[str, Any], ...] = (
    {"name": "Shopify Admin", "domain": "Commerce core", "stage": "active", "env": ("SHOPIFY_MYSHOPIFY_DOMAIN", "SHOPIFY_ADMIN_TOKEN"), "autonomy": "supervised_write", "risk": "high", "purpose": "Products, collections, theme, orders, policy pages."},
    {"name": "Printify", "domain": "Production", "stage": "active", "env": ("PRINTIFY_API_TOKEN", "PRINTIFY_SHOP_ID"), "autonomy": "supervised_write", "risk": "medium", "purpose": "Product drafts, publishing, fulfillment sync."},
    {"name": "Catalog Live Sync", "domain": "Commerce core", "stage": "active_partial", "env": ("SHOPIFY_MYSHOPIFY_DOMAIN", "SHOPIFY_ADMIN_TOKEN", "PRINTIFY_API_TOKEN"), "autonomy": "read_first", "risk": "medium", "purpose": "Fetch products from Shopify/Printify, generate CSV snapshots and detect updates/status differences."},
    {"name": "Google Merchant", "domain": "Growth / Compliance", "stage": "active_blocked", "env": ("GOOGLE_MERCHANT_ID",), "autonomy": "read_first", "risk": "high", "purpose": "Shopping feed, diagnostics, account recovery."},
    {"name": "GA4", "domain": "Analytics", "stage": "active", "env": ("GA4_PROPERTY_ID", "GTM_TARGET"), "autonomy": "read_only", "risk": "low", "purpose": "Traffic, events, conversion measurement."},
    {"name": "Google Tag Manager", "domain": "Analytics", "stage": "active", "env": ("GTM_TARGET",), "autonomy": "read_only", "risk": "medium", "purpose": "Tag governance and event routing."},
    {"name": "Google Search Console", "domain": "SEO / AEO", "stage": "planned", "env": ("GOOGLE_SEARCH_CONSOLE_SITE",), "autonomy": "read_only", "risk": "low", "purpose": "Search coverage, indexing, sitemap issues."},
    {"name": "DNS / Domain Trust", "domain": "Network trust", "stage": "active_partial", "env": ("PRIMARY_DOMAIN", "NETWORK_DKIM_SELECTORS"), "autonomy": "read_first", "risk": "high", "purpose": "Apex/www DNS, SPF, DKIM, DMARC and canonical-domain health."},
    {"name": "Google Ads", "domain": "Paid media", "stage": "planned", "env": ("GOOGLE_ADS_CUSTOMER_ID",), "autonomy": "approval_required", "risk": "high", "purpose": "Campaign diagnostics after Merchant recovery."},
    {"name": "OpenAI API", "domain": "AI / Agent reasoning", "stage": "active", "env": ("OPENAI_API_KEY", "OPENAI_PROJECT_ID"), "autonomy": "draft_only", "risk": "medium", "purpose": "Agent reasoning, copy, scripts, image prompts, safety preflight and BKS Master responses."},
    {"name": "OpenAI ChatGPT Project", "domain": "AI / Strategic workspace", "stage": "optional", "env": ("OPENAI_CHATGPT_PROJECT_URL",), "autonomy": "read_first", "risk": "medium", "purpose": "Allied ChatGPT Project for BKS memory, strategy, decisions and cross-tool continuity."},
    {"name": "OpenAI Knowledge Memory", "domain": "AI / Knowledge", "stage": "planned", "env": ("OPENAI_VECTOR_STORE_ID",), "autonomy": "read_first", "risk": "medium", "purpose": "Grounded BKS memory for customer assistant, inbox replies, policy answers and project learning."},
    {"name": "HeyGen", "domain": "Avatar", "stage": "active_partial", "env": ("HEYGEN_API_KEY", "HEYGEN_AVATAR_ID", "HEYGEN_VOICE_ID"), "autonomy": "supervised_write", "risk": "medium", "purpose": "Avatar rendering for social and site video."},
    {"name": "HyperFrames", "domain": "Motion / Video", "stage": "optional", "env": ("HYPERFRAMES_API_KEY", "HYPERFRAMES_PROJECT_ID"), "autonomy": "draft_render_with_approval", "risk": "medium", "purpose": "Animated slides, explainers and motion graphics rendered from HTML projects."},
    {"name": "YouTube", "domain": "Video commerce", "stage": "planned", "env": ("YOUTUBE_CHANNEL_ID", "YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"), "autonomy": "approval_required", "risk": "medium", "purpose": "Shorts publishing and YouTube Shopping."},
    {"name": "Meta / Instagram", "domain": "Social commerce", "stage": "planned", "env": ("META_ACCESS_TOKEN", "INSTAGRAM_BUSINESS_ID", "FACEBOOK_PAGE_ID"), "autonomy": "approval_required", "risk": "medium", "purpose": "Instagram shop, posts, DMs and retargeting."},
    {"name": "WhatsApp Business", "domain": "Messaging", "stage": "future", "env": ("WHATSAPP_BUSINESS_TOKEN", "WHATSAPP_PHONE_NUMBER_ID"), "autonomy": "human_handoff", "risk": "high", "purpose": "Opt-in customer support and order help."},
    {"name": "Telegram Bot", "domain": "Messaging", "stage": "active_partial", "env": ("TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_USERNAME"), "autonomy": "human_handoff", "risk": "medium", "purpose": "Bot links, notifications and internal alerts."},
    {"name": "Email / SMTP", "domain": "Messaging", "stage": "planned", "env": ("SUPPORT_EMAIL", "SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"), "autonomy": "draft_only", "risk": "high", "purpose": "Customer support, weekly updates, launch comms."},
    {"name": "Official Inbox / DSN", "domain": "Messaging", "stage": "planned", "env": ("OFFICIAL_INBOX_EMAIL", "OFFICIAL_INBOX_IMAP_HOST", "OFFICIAL_INBOX_IMAP_USER", "OFFICIAL_INBOX_IMAP_PASSWORD"), "autonomy": "draft_only", "risk": "high", "purpose": "Read official inbox, DSN/bounces and customer replies into Knowledge DB."},
    {"name": "Klaviyo", "domain": "Lifecycle marketing", "stage": "future", "env": ("KLAVIYO_API_KEY",), "autonomy": "approval_required", "risk": "high", "purpose": "Email/SMS lifecycle after consent setup."},
    {"name": "Mailchimp", "domain": "Lifecycle marketing", "stage": "future", "env": ("MAILCHIMP_API_KEY",), "autonomy": "approval_required", "risk": "medium", "purpose": "Newsletter and launch campaigns."},
    {"name": "HubSpot", "domain": "CRM", "stage": "future", "env": ("HUBSPOT_ACCESS_TOKEN",), "autonomy": "human_handoff", "risk": "high", "purpose": "CRM, customer tickets, lead memory."},
    {"name": "Shopify Flow / CRM", "domain": "CRM / Member area", "stage": "planned", "env": ("SHOPIFY_MYSHOPIFY_DOMAIN", "SHOPIFY_ADMIN_TOKEN"), "autonomy": "approval_required", "risk": "medium", "purpose": "Segments, welcome flow, post-purchase flow, tags and member-area metafields."},
    {"name": "Make", "domain": "Automation", "stage": "active", "env": ("MAKE_WEBHOOK_URL", "MAKE_WEBHOOK_SECRET"), "autonomy": "supervised_write", "risk": "medium", "purpose": "Workflow orchestration and event handoff."},
    {"name": "Zapier", "domain": "Automation", "stage": "optional", "env": ("ZAPIER_WEBHOOK_URL",), "autonomy": "supervised_write", "risk": "medium", "purpose": "Alternative app integration layer."},
    {"name": "n8n", "domain": "Automation", "stage": "optional", "env": ("N8N_WEBHOOK_URL",), "autonomy": "supervised_write", "risk": "medium", "purpose": "Self-hosted automation option."},
    {"name": "TikTok Shop", "domain": "Social commerce", "stage": "future", "env": ("TIKTOK_SHOP_ID",), "autonomy": "approval_required", "risk": "medium", "purpose": "Short video commerce after Google recovery."},
    {"name": "Pinterest Catalog", "domain": "Discovery", "stage": "future", "env": ("PINTEREST_BUSINESS_ID",), "autonomy": "approval_required", "risk": "low", "purpose": "Visual discovery catalog."},
    {"name": "Etsy", "domain": "Marketplace", "stage": "future", "env": ("ETSY_SHOP_ID",), "autonomy": "approval_required", "risk": "medium", "purpose": "Curated marketplace test."},
    {"name": "eBay", "domain": "Marketplace", "stage": "future", "env": ("EBAY_SELLER_ID",), "autonomy": "approval_required", "risk": "medium", "purpose": "Secondary marketplace test."},
    {"name": "Amazon SP-API", "domain": "Marketplace", "stage": "future", "env": ("AMAZON_SELLER_ID", "AMAZON_SP_API_CLIENT_ID"), "autonomy": "approval_required", "risk": "high", "purpose": "Amazon listing workflow."},
    {"name": "Canva", "domain": "Creative / Design Agent", "stage": "optional", "env": ("CANVA_API_KEY",), "autonomy": "draft_only", "risk": "low", "purpose": "Brand kits, templates, AI design candidates, social resizes, catalog sheets, comments/review and exports."},
    {"name": "Google Drive", "domain": "Knowledge", "stage": "optional", "env": ("GOOGLE_DRIVE_ENABLED",), "autonomy": "read_first", "risk": "medium", "purpose": "Docs, sheets, briefs, shared archive."},
    {"name": "Stripe", "domain": "Payments", "stage": "future", "env": ("STRIPE_SECRET_KEY",), "autonomy": "approval_required", "risk": "critical", "purpose": "Future agentic commerce/payment telemetry."},
    {"name": "PayPal", "domain": "Payments", "stage": "future", "env": ("PAYPAL_CLIENT_ID",), "autonomy": "approval_required", "risk": "critical", "purpose": "Payment status and commerce readiness."},
    {"name": "Bitcoin / Crypto Payments", "domain": "Payments", "stage": "active", "env": ("BITCOIN_PAYMENTS_ENABLED", "CRYPTO_PAYMENT_PROVIDER"), "autonomy": "read_first", "risk": "critical", "purpose": "Checkout payment availability, refund clarity and trust messaging."},
    {"name": "Search / Trends API", "domain": "Market sensing", "stage": "future", "env": ("SEARCH_API_KEY",), "autonomy": "read_only", "risk": "low", "purpose": "Daily web research and trend monitoring."},
    {"name": "Cloudflare Workers", "domain": "Infrastructure / Edge", "stage": "active", "env": ("CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN"), "autonomy": "supervised_write", "risk": "medium", "purpose": "bks-agent-refresh Worker (daily 12:00 CET agent state reload), edge routing for bakabo.club, caching and security rules."},
    {"name": "BKS Member Area", "domain": "Member / CRM", "stage": "active", "env": ("SHOPIFY_MYSHOPIFY_DOMAIN", "SHOPIFY_ADMIN_TOKEN"), "autonomy": "supervised_write", "risk": "medium", "purpose": "Gold ring (animated metal tier halo), Metal tier system (Lead/Iron/Brass/Silver/Gold), Try-On tab, dark editorial member dashboard. Live on bakabo.club/pages/bks-members via TM04 theme 202392961362."},
    {"name": "Claude AI / Anthropic", "domain": "AI / Agent reasoning", "stage": "active", "env": ("ANTHROPIC_API_KEY",), "autonomy": "draft_only", "risk": "medium", "purpose": "Primary AI reasoning engine for BKS Master. Claude Code CLI active. Powers commercial strategy, photo briefs, member copy, and all supervised agent actions."},
)


ARCHITECTURE_LAYERS: tuple[dict[str, str], ...] = (
    {"layer": "Perception", "purpose": "Ingest live snapshots, Merchant diagnostics, analytics, network monitor, master_actions queue, photo_studio pipeline."},
    {"layer": "Memory", "purpose": "Store checks, decisions, human-verified overrides (_resolve + memory), failed attempts and successful fixes in master_agent_memory.json. bks-agent-refresh Cloudflare Worker reloads state daily at 12:00 CET."},
    {"layer": "Skill Dispatch", "purpose": "Route signals to the correct BKS skill (BKS_SKILL/skills/). Active: commercial-strategy, photo-studio, members, shopify-ops, product-copy, theme-build, avatar-resident, market-intelligence."},
    {"layer": "Planner", "purpose": "Choose next smallest verified action from master_actions. percent_complete + next_action.id drive the progress dashboard."},
    {"layer": "Connector + Skill Registry", "purpose": "Know every API (agent_os.py CONNECTORS) and every skill (BKS_SKILL/skills/). Both are required before acting."},
    {"layer": "Approval Gate", "purpose": "Require human approval for: theme publish, Merchant appeal, Ads activation, customer outreach, payments, .env edits. Never improvise on risky actions."},
    {"layer": "Executor", "purpose": "Run phases, write assets, push Shopify sections via deploy_theme_section.py, trigger Make webhooks, generate photo briefs."},
    {"layer": "Observability", "purpose": "Expose percent_complete, next_action, blockers, trust_pages, feed diagnostics and photo_studio P0 readiness in the master dashboard."},
    {"layer": "Realtime Conversation", "purpose": "Roberto is the only operator. Every turn: snapshot → one-sentence situation → minimum next action → how to verify → confirm if risky → record outcome."},
)


def _env_value(settings: Any, name: str) -> str:
    attr = name.lower()
    aliases = {
        "SHOPIFY_MYSHOPIFY_DOMAIN": "shopify_store",
        "SHOPIFY_ADMIN_TOKEN": "shopify_admin_token",
        "PRINTIFY_API_TOKEN": "printify_api_token",
        "PRINTIFY_SHOP_ID": "printify_shop_id",
        "GOOGLE_MERCHANT_ID": "google_merchant_id",
        "OPENAI_API_KEY": "openai_api_key",
        "OPENAI_PROJECT_ID": "openai_project_id",
        "OPENAI_CHATGPT_PROJECT_URL": "openai_chatgpt_project_url",
        "OPENAI_VECTOR_STORE_ID": "openai_vector_store_id",
        "HEYGEN_API_KEY": "heygen_api_key",
        "HEYGEN_AVATAR_ID": "heygen_avatar_id",
        "HEYGEN_VOICE_ID": "heygen_voice_id",
        "HYPERFRAMES_API_KEY": "hyperframes_api_key",
        "HYPERFRAMES_PROJECT_ID": "hyperframes_project_id",
        "MAKE_WEBHOOK_URL": "make_webhook_url",
        "MAKE_WEBHOOK_SECRET": "make_webhook_secret",
        "GTM_TARGET": "gtm_target",
        "GA4_PROPERTY_ID": "ga4_property_id",
        "BITCOIN_PAYMENTS_ENABLED": "bitcoin_payments_enabled",
        "CRYPTO_PAYMENT_PROVIDER": "crypto_payment_provider",
        "PRIMARY_DOMAIN": "primary_domain",
        "NETWORK_DKIM_SELECTORS": "network_dkim_selectors",
        "OFFICIAL_INBOX_EMAIL": "official_inbox_email",
        "OFFICIAL_INBOX_IMAP_HOST": "official_inbox_imap_host",
        "OFFICIAL_INBOX_IMAP_USER": "official_inbox_imap_user",
        "OFFICIAL_INBOX_IMAP_PASSWORD": "official_inbox_imap_password",
        "SUPPORT_EMAIL": "support_email",
        "SMTP_HOST": "smtp_host",
        "SMTP_USER": "smtp_user",
        "SMTP_PASSWORD": "smtp_password",
        "TELEGRAM_BOT_TOKEN": "telegram_bot_token",
        "TELEGRAM_BOT_USERNAME": "telegram_bot_username",
        "META_ACCESS_TOKEN": "meta_access_token",
        "INSTAGRAM_BUSINESS_ID": "instagram_business_id",
        "FACEBOOK_PAGE_ID": "facebook_page_id",
        "CLOUDFLARE_ACCOUNT_ID": "cloudflare_account_id",
        "CLOUDFLARE_API_TOKEN": "cloudflare_api_token",
        "ANTHROPIC_API_KEY": "anthropic_api_key",
    }
    val = str(getattr(settings, aliases.get(name, attr), "") or "")
    if not val:
        val = str(os.environ.get(name, "") or "")
    return val


def _status(settings: Any, envs: tuple[str, ...], stage: str) -> str:
    present = sum(1 for env in envs if _env_value(settings, env))
    if present == len(envs):
        if stage == "active_blocked":
            return "blocked"
        return "ready"
    if present:
        return "partial"
    if stage in {"future", "optional"}:
        return "planned"
    return "missing"


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def connector_rows(settings: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in CONNECTORS:
        envs = tuple(spec["env"])
        status = _status(settings, envs, spec["stage"])
        rows.append(
            {
                **spec,
                "status": status,
                "required_env": ";".join(envs),
                "configured": sum(1 for env in envs if _env_value(settings, env)),
                "total_env": len(envs),
                "next_action": _next_action(status, spec),
            }
        )
    return rows


def _next_action(status: str, spec: dict[str, Any]) -> str:
    if status == "ready":
        return "Use in supervised workflows and monitor results."
    if status == "blocked":
        return "Repair compliance/account status before using for growth."
    if status == "partial":
        return "Complete missing credentials and run a read-only health check."
    if status == "planned":
        return "Keep in roadmap; do not activate before primary channels are stable."
    return "Add credentials/configuration when this connector becomes priority."


def write_sheet(settings: Any, rows: list[dict[str, Any]]) -> str:
    path = settings.root_dir / "output" / "agent_os_connector_registry.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["name", "domain", "stage", "status", "autonomy", "risk", "required_env", "configured", "total_env", "purpose", "next_action"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in rows])
    return _relative(settings.root_dir, path)


def payload(settings: Any) -> dict[str, Any]:
    rows = connector_rows(settings)
    sheet = write_sheet(settings, rows)
    summary = {
        "ready": sum(1 for row in rows if row["status"] == "ready"),
        "partial": sum(1 for row in rows if row["status"] == "partial"),
        "blocked": sum(1 for row in rows if row["status"] == "blocked"),
        "missing": sum(1 for row in rows if row["status"] == "missing"),
        "planned": sum(1 for row in rows if row["status"] == "planned"),
        "total": len(rows),
        "autonomy": settings.agent_autonomy_level,
        "customer_chat": settings.agent_customer_chat_enabled,
        "sheet": sheet,
    }
    return {
        "summary": summary,
        "layers": list(ARCHITECTURE_LAYERS),
        "connectors": rows,
        "guardrails": [
            "Human approval required for: theme publish, Merchant appeal, Ads activation, customer outreach, payments, .env edits.",
            "Read-only checks always come before write actions. Never improvise on risky steps.",
            "Never modify .env. Printify real shop ID is 12030061 (resolved dynamically). Google Merchant ID 5295165689 is correct.",
            "Google Merchant P0 blockers gate all growth actions: no Ads, no appeal, no aggressive marketing until local_inventory and unavailable_pages are resolved.",
            "TM04 theme ID 202392961362 is the live theme. All changes go through deploy_theme_section.py with human review.",
            "60-second rule: member-facing changes must deliver one clear value signal within 60s. No empty sections.",
            "English names: all skill names, tab names, feature names and app labels in English. Italian in body copy only.",
            "Every verified action writes to master_agent_memory.json so future sessions can _resolve stuck statuses.",
        ],
        "bks_operating_model": {
            "single_operator": "Roberto Picchioni. All decisions, approvals and direction come from Roberto.",
            "primary_store": "bakabo.club — Shopify + Printify print-on-demand, 8 collections, TM04 dark editorial theme.",
            "active_blocker": "Google Merchant suspended (misrepresentation). P0: disable local inventory, fix unavailable pages.",
            "member_system": "Metal tier (Lead/Iron/Brass/Silver/Gold), gold ring CSS animation, Try-On tab — live on TM04.",
            "commercial_sequence": "Trust foundation → Collection identity → Conversion support → Campaign layer → Merchant appeal.",
            "skill_system": "BKS_SKILL/skills/ — 20+ resident skills. Route every signal to the correct skill before acting.",
            "image_pipeline": "photo_studio P0 shots (front, editorial, detail, hero) unlock Collection identity stage.",
            "real_ids": "Printify shop 12030061 · Google Merchant 5295165689 · TM04 theme 202392961362 · GTM GTM-PF5Z85KS",
        },
    }
