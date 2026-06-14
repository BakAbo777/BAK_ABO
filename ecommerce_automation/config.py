from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
ROOT_DIR = PACKAGE_DIR.parent
ENV_PATH = ROOT_DIR / ".env"


def _load_env_file(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        k = key.strip()
        v = value.strip().strip('"').strip("'")
        if k not in os.environ or not os.environ[k]:
            os.environ[k] = v


def _env(*names: str, default: str = "") -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return default


_load_env_file()


@dataclass(frozen=True)
class Settings:
    app_name: str = "ECAMP - Ecommerce Automation Master Panel"
    root_dir: Path = ROOT_DIR
    package_dir: Path = PACKAGE_DIR
    env_path: Path = ENV_PATH
    database_path: Path = Path(_env("ECAMP_DATABASE_PATH", default=str(PACKAGE_DIR / "database.db")))
    secret_key: str = _env("ECAMP_SECRET_KEY", default="dev-local-only")

    shopify_store: str = _env("SHOPIFY_MYSHOPIFY_DOMAIN", "SHOPIFY_STORE", "SHOP", default="")
    shopify_public_domain: str = _env("SHOPIFY_STORE", default="")
    primary_domain: str = _env("PRIMARY_DOMAIN", "PUBLIC_DOMAIN", default="bakabo.club")
    shopify_admin_token: str = _env("SHOPIFY_ADMIN_TOKEN", "SHOPIFY_TOKEN", "TOKEN", default="")
    shopify_api_version: str = _env("SHOPIFY_API_VERSION", default="2025-01")

    printify_api_token: str = _env("PRINTIFY_API_TOKEN", default="")
    printify_shop_id: str = _env("PRINTIFY_SHOP_ID", default="")
    printify_shop_title: str = _env("PRINTIFY_SHOP_TITLE", default="bakabo.club")

    make_webhook_url: str = _env("MAKE_WEBHOOK_URL", default="")
    make_webhook_secret: str = _env("MAKE_WEBHOOK_SECRET", default="")
    make_api_key: str = _env("MAKE_API_KEY", default="")
    meta_business_id: str = _env("META_BUSINESS_ID", default="")
    meta_access_token: str = _env("META_ACCESS_TOKEN", default="")
    facebook_page_id: str = _env("FACEBOOK_PAGE_ID", default="")
    instagram_business_id: str = _env("INSTAGRAM_BUSINESS_ID", default="")
    meta_commerce_account_id: str = _env("META_COMMERCE_ACCOUNT_ID", default="")

    openai_api_key: str = _env("OPENAI_API_KEY", default="")
    openai_project_id: str = _env("OPENAI_PROJECT_ID", default="")
    openai_organization_id: str = _env("OPENAI_ORGANIZATION_ID", "OPENAI_ORG_ID", default="")
    openai_chatgpt_project_url: str = _env("OPENAI_CHATGPT_PROJECT_URL", "CHATGPT_PROJECT_URL", default="")
    openai_vector_store_id: str = _env("OPENAI_VECTOR_STORE_ID", default="")
    openai_default_model: str = _env("OPENAI_DEFAULT_MODEL", default="")
    openai_realtime_enabled: str = _env("OPENAI_REALTIME_ENABLED", default="")
    heygen_api_key: str = _env("HEYGEN_API_KEY", default="")
    heygen_avatar_id: str = _env("HEYGEN_AVATAR_ID", default="")
    heygen_voice_id: str = _env("HEYGEN_VOICE_ID", default="")
    hyperframes_api_key: str = _env("HYPERFRAMES_API_KEY", default="")
    hyperframes_project_id: str = _env("HYPERFRAMES_PROJECT_ID", default="")
    hyperframes_default_format: str = _env("HYPERFRAMES_DEFAULT_FORMAT", default="1080x1920")
    youtube_channel_id: str = _env("YOUTUBE_CHANNEL_ID", default="")
    youtube_channel_url: str = _env("YOUTUBE_CHANNEL_URL", default="")
    youtube_client_id: str = _env("YOUTUBE_CLIENT_ID", default="")
    youtube_client_secret: str = _env("YOUTUBE_CLIENT_SECRET", default="")
    youtube_refresh_token: str = _env("YOUTUBE_REFRESH_TOKEN", default="")
    support_email: str = _env("SUPPORT_EMAIL", default="crew@bakabo.club")
    official_inbox_email: str = _env("OFFICIAL_INBOX_EMAIL", "CREW_EMAIL", default="crew@bakabo.club")
    official_inbox_imap_host: str = _env("OFFICIAL_INBOX_IMAP_HOST", "IMAP_HOST", default="")
    official_inbox_imap_port: str = _env("OFFICIAL_INBOX_IMAP_PORT", "IMAP_PORT", default="993")
    official_inbox_imap_user: str = _env("OFFICIAL_INBOX_IMAP_USER", "IMAP_USER", default="")
    official_inbox_imap_password: str = _env("OFFICIAL_INBOX_IMAP_PASSWORD", "IMAP_PASSWORD", default="")
    official_inbox_provider: str = _env("OFFICIAL_INBOX_PROVIDER", default="")
    official_email_tracking_provider: str = _env("OFFICIAL_EMAIL_TRACKING_PROVIDER", default="")
    official_email_tracking_enabled: str = _env("OFFICIAL_EMAIL_TRACKING_ENABLED", default="false")
    official_email_tracking_consent_mode: str = _env("OFFICIAL_EMAIL_TRACKING_CONSENT_MODE", default="transparent_opt_in")
    official_email_unsubscribe_url: str = _env("OFFICIAL_EMAIL_UNSUBSCRIBE_URL", default="https://bakabo.club/pages/contact")
    network_dkim_selectors: str = _env("NETWORK_DKIM_SELECTORS", default="google")
    smtp_host: str = _env("SMTP_HOST", default="")
    smtp_port: str = _env("SMTP_PORT", default="")
    smtp_user: str = _env("SMTP_USER", default="")
    smtp_password: str = _env("SMTP_PASSWORD", default="")
    telegram_bot_token: str = _env("TELEGRAM_BOT_TOKEN", default="")
    telegram_bot_username: str = _env("TELEGRAM_BOT_USERNAME", default="")
    telegram_bot_url: str = _env("TELEGRAM_BOT_URL", default="")
    customer_bot_url: str = _env("CUSTOMER_BOT_URL", default="")
    google_merchant_id: str = _env("GOOGLE_MERCHANT_ID", "MERCHANT_CENTER_ID", default="5295165689")
    google_merchant_status: str = _env("GOOGLE_MERCHANT_STATUS", default="suspended")
    google_merchant_reason: str = _env("GOOGLE_MERCHANT_REASON", default="misrepresentation")
    gtm_target: str = _env("GTM_TARGET", default="GTM-PF5Z85KS")
    ga4_property_id: str = _env("GA4_PROPERTY_ID", default="")
    google_ads_customer_id: str = _env("GOOGLE_ADS_CUSTOMER_ID", default="")
    google_search_console_site: str = _env("GOOGLE_SEARCH_CONSOLE_SITE", default="")
    shop_app_enabled: str = _env("SHOP_APP_ENABLED", default="")
    tiktok_shop_id: str = _env("TIKTOK_SHOP_ID", default="")
    tiktok_access_token: str = _env("TIKTOK_ACCESS_TOKEN", default="")
    tiktok_open_id: str = _env("TIKTOK_OPEN_ID", default="")
    pinterest_business_id: str = _env("PINTEREST_BUSINESS_ID", default="")
    pinterest_access_token: str = _env("PINTEREST_ACCESS_TOKEN", default="")
    amazon_seller_id: str = _env("AMAZON_SELLER_ID", default="")
    etsy_shop_id: str = _env("ETSY_SHOP_ID", default="")
    ebay_seller_id: str = _env("EBAY_SELLER_ID", default="")
    whatsapp_business_token: str = _env("WHATSAPP_BUSINESS_TOKEN", default="")
    whatsapp_phone_number_id: str = _env("WHATSAPP_PHONE_NUMBER_ID", default="")
    klaviyo_api_key: str = _env("KLAVIYO_API_KEY", default="")
    mailchimp_api_key: str = _env("MAILCHIMP_API_KEY", default="")
    hubspot_access_token: str = _env("HUBSPOT_ACCESS_TOKEN", default="")
    canva_api_key: str = _env("CANVA_API_KEY", default="")
    google_drive_enabled: str = _env("GOOGLE_DRIVE_ENABLED", default="")
    zapier_webhook_url: str = _env("ZAPIER_WEBHOOK_URL", default="")
    n8n_webhook_url: str = _env("N8N_WEBHOOK_URL", default="")
    stripe_secret_key: str = _env("STRIPE_SECRET_KEY", default="")
    paypal_client_id: str = _env("PAYPAL_CLIENT_ID", default="")
    crypto_payments_enabled: str = _env("CRYPTO_PAYMENTS_ENABLED", default="true")
    bitcoin_payments_enabled: str = _env("BITCOIN_PAYMENTS_ENABLED", default="true")
    crypto_payment_provider: str = _env("CRYPTO_PAYMENT_PROVIDER", default="Shopify/third-party checkout")
    crypto_refund_policy_url: str = _env("CRYPTO_REFUND_POLICY_URL", default="https://bakabo.club/policies/refund-policy")
    search_api_key: str = _env("SEARCH_API_KEY", default="")
    agent_autonomy_level: str = _env("AGENT_AUTONOMY_LEVEL", default="supervised")
    agent_customer_chat_enabled: str = _env("AGENT_CUSTOMER_CHAT_ENABLED", default="false")
    bks_assistant_theme_enabled: str = _env("BKS_ASSISTANT_THEME_ENABLED", default="false")
    bks_assistant_public_endpoint: str = _env("BKS_ASSISTANT_PUBLIC_ENDPOINT", default="")
    bks_assistant_public_token: str = _env("BKS_ASSISTANT_PUBLIC_TOKEN", default="")
    turbobak_path: str = _env("TURBOBAK_PATH", default="E:/TurboBAK")
    turbobak_github_repo: str = _env("TURBOBAK_GITHUB_REPO", default="https://github.com/BakAbo777/TURBOBAK.git")
    marketing_offer_enabled: str = _env("MARKETING_OFFER_ENABLED", default="true")
    marketing_offer_name: str = _env("MARKETING_OFFER_NAME", default="BKS Launch Window")
    marketing_offer_url: str = _env("MARKETING_OFFER_URL", default="https://bakabo.club/collections/new-arrivals")
    marketing_offer_code: str = _env("MARKETING_OFFER_CODE", default="")
    marketing_offer_ends_at: str = _env("MARKETING_OFFER_ENDS_AT", default="2026-06-20T23:59:59+02:00")
    image_factory_url: str = _env("IMAGE_FACTORY_URL", default="http://127.0.0.1:8503")
    image_factory_dir: Path = Path(_env("IMAGE_FACTORY_DIR", default=str(ROOT_DIR / "BAKABO_IMAGE_FACTORY_v1.1")))
    amazon_sp_api_client_id: str = _env("AMAZON_SP_API_CLIENT_ID", default="")


settings = Settings()
