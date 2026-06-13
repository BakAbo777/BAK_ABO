from __future__ import annotations

from typing import Any


def run(context: dict[str, Any]) -> dict[str, Any]:
    shopify = context["services"]["shopify"]
    if not shopify.configured:
        return {
            "status": "needs_config",
            "progress": 25,
            "message": "Shopify credentials are missing.",
            "metrics": {"shopify": "missing_credentials"},
        }
    info = shopify.health_snapshot(live=True)
    return {
        "status": "complete",
        "progress": 100,
        "message": f"Shopify Admin API connected: {info.get('name') or info.get('domain')}.",
        "metrics": info,
    }
