"""BKS Studio — Prompt builder for editorial image generation."""
import yaml
from pathlib import Path

_PROMPTS_PATH = Path(__file__).parent.parent / "config" / "prompts.yaml"
_COLL_PATH    = Path(__file__).parent.parent / "config" / "collections.yaml"
PROMPTS = yaml.safe_load(_PROMPTS_PATH.read_text())
COLL    = yaml.safe_load(_COLL_PATH.read_text())["collections"]
BASE    = PROMPTS["base_rules"].strip()


def build(product_type: str, collection: str, slot: str,
          extra: str = "", count: int = 1) -> list[str]:
    """Build `count` prompts for the given slot.

    Args:
        product_type: e.g. "lounge-pants"
        collection:   e.g. "folklore"
        slot:         one of keys in prompts.yaml slots
        extra:        any extra instruction appended to the prompt
        count:        how many variant prompts to generate (1-4)

    Returns:
        List of prompt strings.
    """
    col = COLL.get(collection, COLL["folklore"])
    slot_cfg = PROMPTS["slots"].get(slot)
    if not slot_cfg:
        raise ValueError(f"Unknown slot: {slot}")

    mode = col.get("shooting_mode", "still-life")
    pose = PROMPTS["poses"].get(product_type, "displayed on surface")

    if mode == "still-life":
        shooting = PROMPTS["shooting_instructions"]["still_life"].format(
            product_type=product_type.replace("-", " "),
            surface=col.get("surface", "matte surface"),
        )
    elif col.get("gender") == "man" or product_type in ("swim-trunks",):
        shooting = PROMPTS["shooting_instructions"]["on_model_man"].format(
            product_type=product_type.replace("-", " "),
            pose=pose,
        )
    else:
        shooting = PROMPTS["shooting_instructions"]["on_model_woman"].format(
            product_type=product_type.replace("-", " "),
            model_season=col.get("model_season", "neutral"),
            pose=pose,
        )

    template = slot_cfg["template"].strip()
    base_prompt = template.format(
        product_type=product_type.replace("-", " "),
        collection=collection,
        shooting_instruction=shooting.strip(),
        surface=col.get("surface", "matte surface"),
        light=col.get("light", "natural light"),
        mood=col.get("mood", "editorial"),
        model_season=col.get("model_season", "neutral coloring"),
        bg_color=col.get("bg_color", "#FAFAF7"),
    )

    if extra:
        base_prompt += f" {extra.strip()}"

    # Add base rules
    full = f"{base_prompt}\n\n{BASE}"

    # For count > 1, add slight variation seeds
    variants = []
    seeds = ["", "Slight variation in pose.", "Different angle.", "Different lighting mood."]
    for i in range(min(count, 4)):
        seed = seeds[i] if i < len(seeds) else ""
        variants.append(f"{full} {seed}".strip())

    return variants


def build_all_slots(product_type: str, collection: str, count: int = 1) -> dict:
    """Build prompts for all 6 standard slots."""
    slots = ["product_front", "product_back", "editorial_square",
             "editorial_4x5", "hero_banner", "texture_detail"]
    return {slot: build(product_type, collection, slot, count=count)
            for slot in slots}
