from __future__ import annotations

from typing import Any


def run(context: dict[str, Any]) -> dict[str, Any]:
    settings = context["settings"]
    make = context["services"]["make"]
    queue = settings.root_dir / "output" / "social_posts_queue.csv"
    make_ready = bool(settings.make_webhook_url)
    return {
        "status": "ready" if make_ready else "needs_config",
        "progress": 80 if make_ready else 40,
        "message": "Social queue can trigger Make." if make_ready else "Configure MAKE_WEBHOOK_URL for social automation.",
        "trust_gate": "campaign_layer",
        "metrics": {"social_queue": str(queue), "queue_exists": queue.exists(), "make": make.health_snapshot()},
    }
