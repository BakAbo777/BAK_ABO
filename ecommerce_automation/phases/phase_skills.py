from __future__ import annotations

from typing import Any

from ecommerce_automation.skill_registry import write_registry


def run(context: dict[str, Any]) -> dict[str, Any]:
    settings = context["settings"]
    result = write_registry(settings.root_dir)
    summary = result["summary"]
    total = summary["active"] + summary["missing"]
    progress = 100 if total and summary["missing"] == 0 else 70
    return {
        "status": "active" if summary["active"] else "planned",
        "progress": progress,
        "message": f"Skill registry updated. Active {summary['active']}, missing referenced {summary['missing']}.",
        "external_ref": summary["registry"],
        "trust_gate": "trust_foundation",
        "metrics": summary,
    }
