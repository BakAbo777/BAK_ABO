from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

BAKABO_STORE_DOMAIN = "bakabo.club"
BKS_TM04_THEME_ID = "202392961362"

PAYMENTS_SHEET = Path("output/payments_matrix.csv")


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _enabled(value: str) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def rows(settings: Any) -> list[dict[str, str]]:
    bitcoin_enabled = _enabled(settings.bitcoin_payments_enabled)
    crypto_enabled = _enabled(settings.crypto_payments_enabled)
    provider = settings.crypto_payment_provider or "Shopify/third-party checkout"
    return [
        {
            "method": "Bitcoin",
            "status": "active" if bitcoin_enabled else "planned",
            "provider": provider,
            "customer_message": "Bitcoin is available where shown at checkout. Final order total and refund terms are handled by the checkout/policy flow.",
            "risk": "Do not present Bitcoin as investment advice, price protection, or guaranteed saving.",
            "verification": "Confirm Bitcoin/crypto badge or payment option is visible in Shopify checkout and policies explain refunds.",
            "trust_gate": "trust_foundation",
        },
        {
            "method": "USDC / stablecoin",
            "status": "active" if crypto_enabled else "planned",
            "provider": provider,
            "customer_message": "Crypto payment availability depends on the checkout provider and customer region.",
            "risk": "Avoid promises about fees, exchange rates, settlement time or availability unless checkout proves it.",
            "verification": "Confirm payment method appears in checkout for enabled markets.",
            "trust_gate": "trust_foundation",
        },
        {
            "method": "PayPal",
            "status": "configured" if settings.paypal_client_id else "visible_on_site",
            "provider": "PayPal / Shopify payments",
            "customer_message": "PayPal appears as a familiar trust option for customers.",
            "risk": "Keep refunds aligned with site refund policy.",
            "verification": "Confirm PayPal logo/payment option is visible in checkout.",
            "trust_gate": "trust_foundation",
        },
        {
            "method": "Card / wallets",
            "status": "visible_on_site",
            "provider": "Shopify checkout",
            "customer_message": "Cards and wallets stay the default low-friction checkout path.",
            "risk": "Do not push crypto at the expense of familiar payment choices.",
            "verification": "Confirm cards/wallets remain visible and clear.",
            "trust_gate": "trust_foundation",
        },
    ]


def write_sheet(settings: Any, data: list[dict[str, str]]) -> str:
    path = settings.root_dir / PAYMENTS_SHEET
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["method", "status", "provider", "trust_gate", "customer_message", "risk", "verification"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in data])
    return _relative(settings.root_dir, path)


def payload(settings: Any) -> dict[str, Any]:
    data = rows(settings)
    sheet = write_sheet(settings, data)
    return {
        "summary": {
            "active": sum(1 for row in data if row["status"] in {"active", "configured", "visible_on_site"}),
            "planned": sum(1 for row in data if row["status"] == "planned"),
            "bitcoin": "active" if _enabled(settings.bitcoin_payments_enabled) else "planned",
            "provider": settings.crypto_payment_provider,
            "sheet": sheet,
            "trust_gate": "trust_foundation",
        },
        "rows": data,
        "agent_skill": "bakabo-bitcoin-payments",
        "guardrails": [
            "Frame Bitcoin as payment optionality, not investment opportunity.",
            "Customer total, taxes, shipping and refunds must be governed by checkout and policy pages.",
            "Do not claim lower fees, faster delivery or special guarantees unless verified.",
            "Keep card, wallet and PayPal choices prominent to avoid frightening mainstream shoppers.",
        ],
    }
