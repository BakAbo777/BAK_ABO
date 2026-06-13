from __future__ import annotations

from typing import Any, Callable

from . import phase_ai, phase_amazon, phase_avatar, phase_config, phase_google, phase_images, phase_import, phase_shopify, phase_skills, phase_social


PhaseRunner = Callable[[dict[str, Any]], dict[str, Any]]


PHASE_RUNNERS: dict[str, PhaseRunner] = {
    "01": phase_config.run,
    "02": phase_import.run,
    "03": phase_images.run,
    "04": phase_ai.run,
    "05": phase_shopify.run,
    "06": phase_google.run,
    "07": phase_social.run,
    "08": phase_amazon.run,
    "09": phase_avatar.run,
    "10": phase_skills.run,
}


def get_runner(phase_id: str) -> PhaseRunner:
    try:
        return PHASE_RUNNERS[phase_id]
    except KeyError as exc:
        raise KeyError(f"Unknown phase runner: {phase_id}") from exc
