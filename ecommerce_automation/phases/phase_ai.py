from __future__ import annotations

import socket
from typing import Any


def _port_open(host: str = "127.0.0.1", port: int = 8503) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1.0):
            return True
    except OSError:
        return False


def run(context: dict[str, Any]) -> dict[str, Any]:
    settings = context["settings"]
    openai_service = context["services"]["openai"]
    image_factory_online = _port_open()
    generated_dir = settings.image_factory_dir / "output" / "generated"
    generated_files = list(generated_dir.rglob("*")) if generated_dir.exists() else []
    generated_count = sum(1 for item in generated_files if item.is_file())

    if openai_service.configured and image_factory_online:
        return {
            "status": "active",
            "progress": 85,
            "message": "Image Factory is online and OpenAI is configured. Shooting Generator can run.",
            "metrics": {
                "openai": openai_service.health(),
                "image_factory_online": True,
                "image_factory_url": settings.image_factory_url,
                "generated_files": generated_count,
            },
        }

    return {
        "status": "ready" if openai_service.configured else "needs_config",
        "progress": 70 if openai_service.configured else 20,
        "message": "OpenAI key configured; generation workflow can run from Image Factory."
        if openai_service.configured
        else "Add OPENAI_API_KEY before AI image/video tasks.",
        "metrics": {
            "openai": openai_service.health(),
            "image_factory_online": image_factory_online,
            "image_factory_url": settings.image_factory_url,
            "generated_files": generated_count,
        },
    }
