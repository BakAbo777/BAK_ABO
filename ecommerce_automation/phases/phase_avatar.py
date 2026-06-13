from __future__ import annotations

from typing import Any

from ecommerce_automation.avatar_production import ensure_workspace


def run(context: dict[str, Any]) -> dict[str, Any]:
    settings = context["settings"]
    result = ensure_workspace(settings.root_dir)
    summary = result["summary"]

    if summary["exports_ready"] == summary["collections"] and summary["metadata_ready"] == summary["collections"]:
        status = "complete"
        message = "All avatar videos have exports and delivery metadata."
    elif summary["scripts_ready"] == summary["collections"]:
        status = "active"
        message = (
            f"Avatar workspace ready. Scripts {summary['scripts_ready']}/{summary['collections']}, "
            f"images {summary['images_ready']}/{summary['collections']}, "
            f"exports {summary['exports_ready']}/{summary['collections']}."
        )
    else:
        status = "planned"
        message = (
            f"Avatar workspace created. Scripts {summary['scripts_ready']}/{summary['collections']} "
            "are ready for HeyGen prep."
        )

    return {
        "status": status,
        "progress": summary["progress"],
        "message": message,
        "external_ref": summary["workspace"],
        "metrics": summary,
    }
