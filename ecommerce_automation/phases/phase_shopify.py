from __future__ import annotations

from typing import Any

BAKABO_STORE_DOMAIN = "bakabo.club"
BKS_TM04_THEME_ID = "202392961362"


def run(context: dict[str, Any]) -> dict[str, Any]:
    shopify = context["services"]["shopify"]
    if not shopify.configured:
        return {
            "status": "needs_config",
            "progress": 25,
            "message": "Shopify credentials are missing.",
            "store": BAKABO_STORE_DOMAIN,
            "trust_gate": "trust_foundation",
            "metrics": {"shopify": "missing_credentials"},
        }
    info = shopify.health_snapshot(live=True)
    return {
        "status": "complete",
        "progress": 100,
        "message": f"Shopify Admin API connected: {info.get('name') or info.get('domain')}.",
        "store": BAKABO_STORE_DOMAIN,
        "theme_id": BKS_TM04_THEME_ID,
        "trust_gate": "trust_foundation",
        "metrics": info,
    }
