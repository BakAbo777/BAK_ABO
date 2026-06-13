from __future__ import annotations

from typing import Any


def run(context: dict[str, Any]) -> dict[str, Any]:
    settings = context["settings"]
    printify = context["services"]["printify"]
    references = context["references"]
    from bks_assets import active_catalog_csv

    catalog_result = references.seed_from_catalog(active_catalog_csv())
    if not settings.printify_api_token:
        return {
            "status": "needs_config",
            "progress": 45,
            "message": "Catalog references seeded. Add PRINTIFY_API_TOKEN before Printify reconciliation.",
            "metrics": {"printify": "missing_token", "catalog_references": catalog_result},
        }

    snapshot = printify.health_snapshot(settings.printify_shop_title)
    shop_id = snapshot["shop_id"]
    return {
        "status": "complete",
        "progress": 100,
        "message": f"Printify shop resolved: {shop_id}. Product sample loaded.",
        "external_ref": shop_id,
        "metrics": {"printify": snapshot, "catalog_references": catalog_result},
    }
