from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def rows(settings: Any) -> list[dict[str, str]]:
    bitcoin_enabled = settings.bitcoin_payments_enabled.lower() in {"1", "true", "yes", "on"}
    crypto_enabled = settings.crypto_payments_enabled.lower() in {"1", "true", "yes", "on"}
    provider = settings.crypto_payment_provider or "Shopify/third-party checkout"
    return [
        {
            "method": "Bitcoin",
            "status": "active" if bitcoin_enabled else "planned",
            "provider": provider,
            "customer_message": "Bitcoin is available where shown at checkout. Final order total and refund terms are handled by the checkout/policy flow.",
            "risk": "Do not present Bitcoin as investment advice, price protection, or guaranteed saving.",
            "verification": "Confirm Bitcoin/crypto badge or payment option is visible in Shopify checkout and policies explain refunds.",
        },
        {
            "method": "USDC / stablecoin",
            "status": "active" if crypto_enabled else "planned",
            "provider": provider,
            "customer_message": "Crypto payment availability depends on the checkout provider and customer region.",
            "risk": "Avoid promises about fees, exchange rates, settlement time or availability unless checkout proves it.",
            "verification": "Confirm payment method appears in checkout for enabled markets.",
        },
        {
            "method": "PayPal",
            "status": "configured" if settings.paypal_client_id else "visible_on_site",
            "provider": "PayPal / Shopify payments",
            "customer_message": "PayPal appears as a familiar trust option for customers.",
            "risk": "Keep refunds aligned with site refund policy.",
            "verification": "Confirm PayPal logo/payment option is visible in checkout.",
        },
        {
            "method": "Card / wallets",
            "status": "visible_on_site",
            "provider": "Shopify checkout",
            "customer_message": "Cards and wallets stay the default low-friction checkout path.",
            "risk": "Do not push crypto at the expense of familiar payment choices.",
            "verification": "Confirm cards/wallets remain visible and clear.",
        },
    ]


def write_sheet(settings: Any, data: list[dict[str, str]]) -> str:
    path = settings.root_dir / "output" / "payments_matrix.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["method", "status", "provider", "customer_message", "risk", "verification"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    return _relative(settings.root_dir, path)


def payload(settings: Any) -> dict[str, Any]:
    data = rows(settings)
    sheet = write_sheet(settings, data)
    return {
        "summary": {
            "active": sum(1 for row in data if row["status"] in {"active", "configured", "visible_on_site"}),
            "planned": sum(1 for row in data if row["status"] == "planned"),
            "bitcoin": "active" if settings.bitcoin_payments_enabled.lower() in {"1", "true", "yes", "on"} else "planned",
            "provider": settings.crypto_payment_provider,
            "sheet": sheet,
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
