from __future__ import annotations

from typing import Any


def run(context: dict[str, Any]) -> dict[str, Any]:
    settings = context["settings"]
    make = context["services"]["make"]
    snapshot = make.health_snapshot()
    make_ready = bool(settings.make_webhook_url)
    return {
        "status": "complete" if make_ready else "needs_config",
        "progress": 100 if make_ready else 40,
        "message": "Make webhook configured." if make_ready else "Add MAKE_WEBHOOK_URL to enable outbound Make triggers.",
        "trust_gate": "trust_foundation",
        "metrics": {
            "make": snapshot,
            "env_file": str(settings.env_path),
        },
    }
