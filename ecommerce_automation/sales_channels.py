from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


CHANNEL_SPECS: tuple[dict[str, str], ...] = (
    {
        "channel": "Shopify Online Store",
        "type": "storefront",
        "priority": "primary",
        "purpose": "Main ecommerce site and checkout.",
        "required": "SHOPIFY_MYSHOPIFY_DOMAIN;SHOPIFY_ADMIN_TOKEN",
        "status_key": "shopify",
    },
    {
        "channel": "Shop App",
        "type": "marketplace",
        "priority": "secondary",
        "purpose": "Shopify customer discovery and account reorders.",
        "required": "SHOP_APP_ENABLED",
        "status_key": "shop_app",
    },
    {
        "channel": "Instagram Shop",
        "type": "social commerce",
        "priority": "primary",
        "purpose": "Visual product discovery through Instagram.",
        "required": "META_ACCESS_TOKEN;INSTAGRAM_BUSINESS_ID;META_COMMERCE_ACCOUNT_ID",
        "status_key": "instagram_shop",
    },
    {
        "channel": "Facebook Shop",
        "type": "social commerce",
        "priority": "secondary",
        "purpose": "Meta catalog, page shop and retargeting.",
        "required": "META_ACCESS_TOKEN;FACEBOOK_PAGE_ID;META_COMMERCE_ACCOUNT_ID",
        "status_key": "facebook_shop",
    },
    {
        "channel": "Google Merchant / Shopping",
        "type": "search commerce",
        "priority": "primary",
        "purpose": "Free listings, Shopping feed and product validation.",
        "required": "GOOGLE_MERCHANT_ID",
        "status_key": "google_merchant",
    },
    {
        "channel": "YouTube Shopping",
        "type": "video commerce",
        "priority": "secondary",
        "purpose": "Product discovery from Shorts and videos.",
        "required": "YOUTUBE_CHANNEL_ID;GOOGLE_MERCHANT_ID",
        "status_key": "youtube_shopping",
    },
    {
        "channel": "TikTok Shop",
        "type": "social commerce",
        "priority": "test",
        "purpose": "Short-form commerce tests for avatar and product videos.",
        "required": "TIKTOK_SHOP_ID",
        "status_key": "tiktok_shop",
    },
    {
        "channel": "Pinterest Catalog",
        "type": "visual discovery",
        "priority": "test",
        "purpose": "Evergreen visual search and collection discovery.",
        "required": "PINTEREST_BUSINESS_ID",
        "status_key": "pinterest",
    },
    {
        "channel": "Amazon Marketplace",
        "type": "marketplace",
        "priority": "future",
        "purpose": "Marketplace extension after Shopify catalog stability.",
        "required": "AMAZON_SELLER_ID;AMAZON_SP_API_CLIENT_ID",
        "status_key": "amazon_marketplace",
    },
    {
        "channel": "Etsy",
        "type": "marketplace",
        "priority": "future",
        "purpose": "Limited curated tests for graphic/art-led products.",
        "required": "ETSY_SHOP_ID",
        "status_key": "etsy",
    },
    {
        "channel": "eBay",
        "type": "marketplace",
        "priority": "future",
        "purpose": "Secondary marketplace testing only after ops are stable.",
        "required": "EBAY_SELLER_ID",
        "status_key": "ebay",
    },
    {
        "channel": "Assisted Sales",
        "type": "direct",
        "priority": "support",
        "purpose": "Email, Instagram DM and Telegram bot handoff with consent.",
        "required": "SUPPORT_EMAIL;TELEGRAM_BOT_TOKEN;INSTAGRAM_BUSINESS_ID",
        "status_key": "assisted_sales",
    },
)


def sheet_path(root_dir: Path) -> Path:
    return root_dir / "output" / "sales_channels_matrix.csv"


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _statuses(settings: Any) -> dict[str, str]:
    meta_ready = bool(settings.meta_access_token)
    merchant_status = str(settings.google_merchant_status or "").lower()
    merchant_usable = bool(settings.google_merchant_id) and merchant_status not in {"suspended", "blocked", "needs_review", "limited"}
    merchant_partial = bool(settings.google_merchant_id) and not merchant_usable
    return {
        "shopify": "active" if settings.shopify_store and settings.shopify_admin_token else "missing_config",
        "shop_app": "planned" if not settings.shop_app_enabled else "active",
        "instagram_shop": "active" if meta_ready and settings.instagram_business_id and settings.meta_commerce_account_id else "missing_config",
        "facebook_shop": "active" if meta_ready and settings.facebook_page_id and settings.meta_commerce_account_id else "missing_config",
        "google_merchant": "active" if merchant_usable else ("partial" if merchant_partial else "missing_config"),
        "youtube_shopping": "active" if settings.youtube_channel_id and merchant_usable else ("partial" if settings.youtube_channel_id and merchant_partial else "missing_config"),
        "tiktok_shop": "planned" if not settings.tiktok_shop_id else "active",
        "pinterest": "planned" if not settings.pinterest_business_id else "active",
        "amazon_marketplace": "planned" if not (settings.amazon_seller_id and settings.amazon_sp_api_client_id) else "active",
        "etsy": "planned" if not settings.etsy_shop_id else "active",
        "ebay": "planned" if not settings.ebay_seller_id else "active",
        "assisted_sales": "partial" if settings.support_email or settings.telegram_bot_token or settings.instagram_business_id else "missing_config",
    }


def rows(settings: Any) -> list[dict[str, str]]:
    statuses = _statuses(settings)
    result: list[dict[str, str]] = []
    for spec in CHANNEL_SPECS:
        status = statuses.get(spec["status_key"], "missing_config")
        next_action = {
            "active": "Monitor feed/orders and keep product data aligned.",
            "partial": "Complete missing messaging credentials and consent routing.",
            "planned": "Keep in roadmap; activate after primary channels are stable.",
            "missing_config": "Add credentials/configuration and validate catalog feed.",
        }.get(status, "Review configuration.")
        result.append({**spec, "status": status, "next_action": next_action})
    return result


def write_sheet(settings: Any) -> dict[str, Any]:
    data = rows(settings)
    path = sheet_path(settings.root_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["channel", "status", "type", "priority", "purpose", "required", "next_action"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row[key] for key in fieldnames} for row in data])
    return {
        "rows": data,
        "summary": {
            "active": sum(1 for row in data if row["status"] == "active"),
            "partial": sum(1 for row in data if row["status"] == "partial"),
            "planned": sum(1 for row in data if row["status"] == "planned"),
            "missing": sum(1 for row in data if row["status"] == "missing_config"),
            "sheet": _relative(settings.root_dir, path),
        },
    }


def payload(settings: Any) -> dict[str, Any]:
    return write_sheet(settings)
