from __future__ import annotations

from typing import Any


def run(context: dict[str, Any]) -> dict[str, Any]:
    amazon = context["services"]["amazon"]
    return {
        "status": "ready" if amazon.configured else "planned",
        "progress": 60 if amazon.configured else 10,
        "message": "Amazon SP-API client configured." if amazon.configured else "Amazon is planned; credentials not configured yet.",
        "trust_gate": "merchant_appeal",
        "metrics": amazon.health(),
    }

