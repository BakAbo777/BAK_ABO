"""BKS Studio — Image Director v1.1
Orchestrates full pipeline + saves manifest per product.
"""
from __future__ import annotations
import logging
import re
from pathlib import Path

log = logging.getLogger("bif.director")

_DEFAULT_SLOTS = [
    "product_front", "product_back", "editorial_square",
    "editorial_4x5", "hero_banner", "texture_detail",
]


def run_product(
    source_image:  Path,
    product_title: str        = "",
    tags:          list[str]  = None,
    slots:         list[str]  = None,
    count:         int        = 1,
    dry_run:       bool       = False,
    progress_cb                = None,
    collection_override: str   = "",
    product_type_override: str = "",
) -> dict:
    from modules.image_analyzer     import analyze_product_image, extract_palette
    from modules.collection_detector import detect
    from modules.prompt_builder      import build_all_slots
    from modules.image_generator     import generate
    from modules.quality_validator   import validate
    from modules.seo_generator       import generate_all as gen_seo
    from modules.manifest            import save as save_manifest
    from config.settings             import GENERATED_DIR

    def _step(msg: str, pct: float):
        log.info("[%.0f%%] %s", pct * 100, msg)
        if progress_cb:
            progress_cb(msg, pct)

    tags  = tags or []
    slots = slots or _DEFAULT_SLOTS

    # ── 1. Analyze ────────────────────────────────────────────────────────
    _step("Analyzing product image...", 0.10)
    if dry_run:
        analysis = {"product_type": "lounge-pants", "gender": "woman",
                    "collection": "unknown", "palette": [], "style": ""}
    else:
        try:
            analysis = analyze_product_image(source_image)
        except Exception as e:
            log.warning("Vision analysis failed: %s", e)
            analysis = {"product_type": "unknown", "collection": "unknown",
                        "palette": [], "error": str(e)}

    # ── 2. Detect collection ──────────────────────────────────────────────
    _step("Detecting collection...", 0.20)
    if product_type_override:
        analysis["product_type"] = product_type_override
    if collection_override:
        detection = {"collection": collection_override, "source": "manual", "confidence": 1.0}
    else:
        detection = detect(image_path=source_image, analysis=analysis,
                           title=product_title, tags=tags)
    collection   = detection["collection"]
    product_type = analysis.get("product_type", "unknown")

    # ── 3. Build prompts ──────────────────────────────────────────────────
    _step("Building prompts...", 0.30)
    all_prompts = build_all_slots(product_type, collection, count=count)
    prompts     = {k: v for k, v in all_prompts.items() if k in slots}

    # ── 4. Generate ───────────────────────────────────────────────────────
    slug = re.sub(r"[^a-z0-9\-]", "", re.sub(r"\s+", "-", product_title.lower()))[:60] or "product"
    out_dir = GENERATED_DIR / collection / slug
    generated: dict[str, list[dict]] = {}
    total = len(prompts) * count
    call_n = 0

    for slot, variant_prompts in prompts.items():
        generated[slot] = []
        for i, prompt in enumerate(variant_prompts, 1):
            call_n += 1
            _step(f"Generating {slot} v{i}...", 0.30 + 0.50 * call_n / total)
            r = generate(
                reference_path=source_image,
                prompt=prompt,
                slug=slug,
                collection=collection,
                slot=slot,
                variant=i,
                output_dir=out_dir,
                dry_run=dry_run,
            )
            generated[slot].append(r)

    # ── 5. QA ─────────────────────────────────────────────────────────────
    _step("QA validation...", 0.85)
    qa: dict[str, list[dict]] = {}
    for slot, results in generated.items():
        qa[slot] = []
        for r in results:
            out_jpg = r.get("output_jpg")
            if out_jpg and Path(str(out_jpg)).exists():
                score = validate(Path(str(out_jpg)), dry_run=dry_run)
            else:
                score = {"score": 0, "approved": False, "issues": ["not generated"]}
            qa[slot].append(score)

    # ── 6. SEO ────────────────────────────────────────────────────────────
    _step("Generating SEO...", 0.95)
    seo = gen_seo(product_title, collection, product_type)

    # ── 7. Manifest ───────────────────────────────────────────────────────
    result = {
        "collection":   collection,
        "product_type": product_type,
        "detection":    detection,
        "analysis":     analysis,
        "prompts":      prompts,
        "generated":    generated,
        "qa":           qa,
        "seo":          seo,
    }
    try:
        mf = save_manifest(result, out_dir, product_title, source_image)
        result["manifest"] = mf
    except Exception as e:
        log.warning("Manifest save failed: %s", e)

    _step("Done.", 1.0)
    return result
