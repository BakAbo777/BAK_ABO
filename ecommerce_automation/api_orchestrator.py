from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


API_SPECS: tuple[dict[str, Any], ...] = (
    {"api": "Shopify Admin", "phase": "05 Shopify publish / Deploy", "purpose": "Theme, products, collections, metafields, live checks.", "env": ("SHOPIFY_MYSHOPIFY_DOMAIN", "SHOPIFY_ADMIN_TOKEN", "SHOPIFY_API_VERSION"), "service_key": "shopify"},
    {"api": "Printify", "phase": "02 Import / 05 Publish", "purpose": "Product drafts, publish flow, order sync.", "env": ("PRINTIFY_API_TOKEN", "PRINTIFY_SHOP_ID"), "service_key": "printify"},
    {"api": "OpenAI", "phase": "04 AI content / images", "purpose": "Copy, prompts, image/content generation support.", "env": ("OPENAI_API_KEY",), "service_key": "openai"},
    {"api": "HeyGen", "phase": "09 Avatar / Social Render", "purpose": "Avatar videos, voice, portrait exports.", "env": ("HEYGEN_API_KEY", "HEYGEN_AVATAR_ID", "HEYGEN_VOICE_ID"), "service_key": "heygen"},
    {"api": "Make", "phase": "01 Config / 07 Social", "purpose": "Outbound/inbound automation events and social render handoff.", "env": ("MAKE_WEBHOOK_URL", "MAKE_WEBHOOK_SECRET"), "service_key": "make"},
    {"api": "Meta / Instagram", "phase": "Communications / Social", "purpose": "Instagram DM, Facebook page messaging, human handoff.", "env": ("META_ACCESS_TOKEN", "INSTAGRAM_BUSINESS_ID", "FACEBOOK_PAGE_ID"), "service_key": "meta"},
    {"api": "Telegram Bot", "phase": "Communications / Bot", "purpose": "Opt-in bot entry point for direct customer conversations.", "env": ("TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_USERNAME", "TELEGRAM_BOT_URL"), "service_key": "telegram"},
    {"api": "Email / SMTP", "phase": "Communications", "purpose": "Customer support, launch emails, agent handoff.", "env": ("SUPPORT_EMAIL", "SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"), "service_key": "email"},
    {"api": "Google Merchant", "phase": "Sales Channels", "purpose": "Shopping feed, free listings and product diagnostics.", "env": ("GOOGLE_MERCHANT_ID",), "service_key": "google_merchant"},
    {"api": "TikTok Shop", "phase": "Sales Channels", "purpose": "Short-form commerce tests and product sync.", "env": ("TIKTOK_SHOP_ID",), "service_key": "tiktok_shop"},
    {"api": "Pinterest Catalog", "phase": "Sales Channels", "purpose": "Visual discovery catalog and product pins.", "env": ("PINTEREST_BUSINESS_ID",), "service_key": "pinterest"},
    {"api": "Etsy", "phase": "Sales Channels", "purpose": "Curated marketplace tests for graphic/art-led products.", "env": ("ETSY_SHOP_ID",), "service_key": "etsy"},
    {"api": "eBay", "phase": "Sales Channels", "purpose": "Secondary marketplace testing.", "env": ("EBAY_SELLER_ID",), "service_key": "ebay"},
    {"api": "YouTube", "phase": "Social Render", "purpose": "YouTube Shorts upload path for avatar videos.", "env": ("YOUTUBE_CHANNEL_ID", "YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"), "service_key": "youtube"},
    {"api": "Image Factory", "phase": "03 Images / 09 Avatar assets", "purpose": "Local image generation, contact sheets, source previews.", "env": ("IMAGE_FACTORY_DIR", "IMAGE_FACTORY_URL"), "service_key": "image_factory"},
    {"api": "Amazon SP-API", "phase": "08 Amazon", "purpose": "Future listing and marketplace workflow.", "env": ("AMAZON_SP_API_CLIENT_ID",), "service_key": "amazon"},
)


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
    if status in {"online", "configured", "render_ready"}:
        return "ready"
    if status in {"suspended", "needs_review", "limited"}:
        return "partial"
    if status == "key_ready":
        return "partial"
    if configured and status not in {"offline", "missing_key", "missing_token", "missing_webhook_url", "missing_oauth", "error"}:
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
                "status": status,
                "phase": spec["phase"],
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
    return {
        "rows": data,
        "summary": {
            "ready": sum(1 for row in data if row["status"] == "ready"),
            "partial": sum(1 for row in data if row["status"] == "partial"),
            "missing": sum(1 for row in data if row["status"] == "missing"),
            "matrix": _relative(root_dir, path),
        },
    }
