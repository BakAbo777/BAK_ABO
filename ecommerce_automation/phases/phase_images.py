from __future__ import annotations

from typing import Any


def run(context: dict[str, Any]) -> dict[str, Any]:
    root = context["settings"].root_dir
    image_factory = root / "BAKABO_IMAGE_FACTORY_v1.1"
    return {
        "status": "complete" if image_factory.exists() else "needs_config",
        "progress": 100 if image_factory.exists() else 25,
        "message": "Image Factory is present." if image_factory.exists() else "Image Factory folder is missing.",
        "metrics": {"image_factory": str(image_factory), "exists": image_factory.exists()},
    }

