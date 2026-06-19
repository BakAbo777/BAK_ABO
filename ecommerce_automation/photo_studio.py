from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


PHOTO_SHEET = Path("output/photo_studio_pipeline.csv")
THEME_PROGRESSIONS = Path("output/theme_progression_matrix.csv")
PHOTO_SKILL = Path("BKS_SKILL/skills/bakabo-photo-studio/SKILL.md")
WORLD_MODEL_SHEET = Path("output/world_model_context_matrix.csv")

TM04_THEME_ID = "202392961362"


SHOT_TYPES: tuple[dict[str, str], ...] = (
    {
        "shot": "01 front product",
        "format": "1:1 JPG 2000x2000",
        "purpose": "Primary Shopify PDP image and product card thumbnail.",
        "requirements": "Exact mockup reference, clean background, no props, print fully visible.",
        "agent_next": "Match exact Printify mockup. Apply collection accent as subtle gradient overlay only outside the product area. Upload as media[0].",
    },
    {
        "shot": "02 back product",
        "format": "1:1 JPG 2000x2000",
        "purpose": "Back view for PDP gallery and product truth.",
        "requirements": "Use only when back mockup exists or is provided; never invent a back print.",
        "agent_next": "Generate only if back mockup file is present. Never composite a back from a front. Upload as media[1] after front.",
    },
    {
        "shot": "04 editorial front",
        "format": "4:5 JPG 1600x2000",
        "purpose": "Second PDP image, desktop hover and collection mood.",
        "requirements": "Still-life or on-model based on collection, exact product from reference, no text/logo overlay.",
        "agent_next": "Set surface and light from COLLECTION_DIRECTIONS for the matching collection. Match accent hex for ambient fill. Upload as media[2].",
    },
    {
        "shot": "06 detail fabric",
        "format": "1:1 JPG 1500x1500",
        "purpose": "Texture, print detail, finish and quality reassurance.",
        "requirements": "Close-up from real/reference print; no invented pattern or color shift.",
        "agent_next": "Crop from real or reference print at maximum resolution. No color grading that shifts hue. Upload as media[3].",
    },
    {
        "shot": "07 hero banner",
        "format": "16:7 JPG 2400x1050",
        "purpose": "Collection page, homepage band and campaign hero.",
        "requirements": "Generous negative space (left 40%) for TM04 collection signal text. Product visible on right.",
        "agent_next": "Use TM04 accent gradient as background band. Leave left third clear for bks-collection-signal text overlay. Upload to collection metafield hero_image.",
    },
    {
        "shot": "08 lifestyle front",
        "format": "4:5 and 9:16",
        "purpose": "Social proof, social campaign and PDP context.",
        "requirements": "Adult model only when approved; no celebrity resemblance; product inspectable. Only after first order fulfillments.",
        "agent_next": "Check commercial-strategy drop timing: lifestyle assets unlock at Conversion Support stage. Generate 9:16 for Meta/social and 4:5 for PDP. Apply world model rules for target market.",
    },
    {
        "shot": "12 packaging",
        "format": "1:1",
        "purpose": "Support trust, shipping and unboxing expectations.",
        "requirements": "Show only real Printify/BKS delivery packaging. Activate after first orders confirmed.",
        "agent_next": "Use real unboxing photo if available. Otherwise defer until first delivery is documented. Trust stage: Conversion Support.",
    },
    {
        "shot": "Review prompt asset",
        "format": "9:16",
        "purpose": "Post-purchase email/social prompt for honest reviews.",
        "requirements": "Transparent ask for real experience. Never incentivize deceptive reviews.",
        "agent_next": "Generate after delivery window (order shipped + 7 days). Include 1 product image from order + tier progress CTA. Follow REVIEW_GUARDS exactly.",
    },
)


COLLECTION_DIRECTIONS: tuple[dict[str, str], ...] = (
    {"collection": "Hours", "handle": "bks-hours", "accent": "#c8c4be", "surface": "dark raw concrete", "light": "hard lateral single source", "mood": "urban, contemplative"},
    {"collection": "Glyph", "handle": "bks-glyph", "accent": "#d4a030", "surface": "matte black plane", "light": "flat studio ring light", "mood": "graphic, coded"},
    {"collection": "Marker", "handle": "bks-marker", "accent": "#c04418", "surface": "rough paper / iron", "light": "hard lateral with sharp shadow", "mood": "gestural, urban"},
    {"collection": "Riviera", "handle": "bks-riviera", "accent": "#0ca898", "surface": "travertine / linen", "light": "golden hour from right", "mood": "resort, mediterranean"},
    {"collection": "Pulse", "handle": "bks-pulse", "accent": "#8888cc", "surface": "dark plane / tiles", "light": "front ring light", "mood": "optical, kinetic"},
    {"collection": "Token", "handle": "bks-token", "accent": "#9828d8", "surface": "reflective surface / plexiglass", "light": "low-key neon accent", "mood": "arcade, digital"},
    {"collection": "Flag", "handle": "bks-flag", "accent": "#c82020", "surface": "white studio", "light": "flat uniform light", "mood": "pop, graphic"},
    {"collection": "Origin", "handle": "bks-origin", "accent": "#489808", "surface": "light stone / linen / earth", "light": "soft overcast", "mood": "narrative, naive"},
)


THEME_STAGES: tuple[dict[str, str], ...] = (
    {
        "stage": "Trust foundation",
        "theme_use": "trust strip, policy links, product reality, clear image",
        "image_need": "Hero product + detail + scale",
        "when": "Always first, especially while Google Merchant is suspended.",
    },
    {
        "stage": "Collection identity",
        "theme_use": "collection hero, short story, visual rhythm",
        "image_need": "Collection hero + lifestyle context",
        "when": "After product pages and policies are stable.",
    },
    {
        "stage": "Conversion support",
        "theme_use": "reviews, FAQs, shipping/returns reassurance, related products",
        "image_need": "Detail + packaging + review prompt",
        "when": "After first fulfilled orders and review request flow.",
    },
    {
        "stage": "Campaign layer",
        "theme_use": "timed offer, avatar video, multilingual social proof",
        "image_need": "9:16 social/video assets + collection hero",
        "when": "Only when Google Trust and offer clarity are green.",
    },
)


REVIEW_GUARDS: tuple[dict[str, str], ...] = (
    {
        "guard": "Honest review only",
        "meaning": "Ask for real experience; do not script fake reviews.",
        "agent_rule": "Draft review requests, never fabricate testimonials.",
    },
    {
        "guard": "Timing",
        "meaning": "Ask after delivery window or customer confirmation.",
        "agent_rule": "Use order/delivery signals when available; otherwise wait conservative interval.",
    },
    {
        "guard": "No hidden incentive",
        "meaning": "If incentive exists, disclose it clearly and follow platform rules.",
        "agent_rule": "Do not add discount-for-review unless policy is approved.",
    },
    {
        "guard": "Product improvement loop",
        "meaning": "Negative feedback becomes supplier/product/theme improvement evidence.",
        "agent_rule": "Save review signal to Knowledge DB and supplier matrix.",
    },
)


WORLD_MODEL_CONTEXTS: tuple[dict[str, str], ...] = (
    {
        "market": "United States",
        "language": "English",
        "model_direction": "Diverse adult pair, relaxed city-to-coast life, confident but not celebrity-coded.",
        "weather_logic": "Use lightweight tops, shorts, swimwear or sneakers by local season and region.",
        "copy_tone": "Direct, practical, optimistic, product-first.",
        "guardrail": "Do not imply US-made unless true; keep shipping/returns and price currency consistent.",
    },
    {
        "market": "France",
        "language": "French",
        "model_direction": "Adult pair with understated editorial styling, street/gallery/cafe movement.",
        "weather_logic": "Layer outerwear and sneakers in mild/cool weather, resort pieces only in seasonal context.",
        "copy_tone": "Minimal, cultured, tactile, never loud.",
        "guardrail": "Translate product facts accurately; do not overclaim luxury origin.",
    },
    {
        "market": "Germany",
        "language": "German",
        "model_direction": "Adult pair in clean urban settings, function and material clarity visible.",
        "weather_logic": "Favor practical layering, windbreakers, sneakers and bags by temperature.",
        "copy_tone": "Precise, clear, trustworthy, low-pressure.",
        "guardrail": "Make delivery, returns and material/care details easy to inspect.",
    },
    {
        "market": "Canada",
        "language": "English/French",
        "model_direction": "Adult pair in city/outdoor transition, warm but understated.",
        "weather_logic": "Use climate-aware layering; avoid beachwear outside plausible seasonal scenes.",
        "copy_tone": "Friendly, transparent, everyday premium.",
        "guardrail": "Match language/currency to feed and landing page requirements.",
    },
    {
        "market": "Japan",
        "language": "Japanese",
        "model_direction": "Adult pair with composed styling, detail shots, clean negative space and care for proportion.",
        "weather_logic": "Use seasonally precise looks and smaller gestures; product texture remains inspectable.",
        "copy_tone": "Respectful, concise, craft-oriented.",
        "guardrail": "Use native review for translation before publication.",
    },
    {
        "market": "South Korea",
        "language": "Korean",
        "model_direction": "Adult pair with polished daily styling and street/editorial balance.",
        "weather_logic": "Seasonal layering; strong footwear and bag visibility.",
        "copy_tone": "Modern, clean, design-conscious.",
        "guardrail": "Activate only after Merchant business registration and country policies are complete.",
    },
    {
        "market": "China / Chinese-language creative",
        "language": "Chinese",
        "model_direction": "Adult pair with metropolitan daily-life styling and careful product close-ups.",
        "weather_logic": "Adapt by region and season; avoid political or restricted-market assumptions.",
        "copy_tone": "Elegant, practical, image-led.",
        "guardrail": "Use only if channel, payment, shipping and compliance are approved for the market.",
    },
    {
        "market": "Egypt / Arabic-speaking markets",
        "language": "Arabic/English",
        "model_direction": "Adult pair styled with cultural respect, heat-aware layering and modest options when relevant.",
        "weather_logic": "Prefer breathable tops, bags, sandals and swim only in suitable resort contexts.",
        "copy_tone": "Warm, clear, trust-first.",
        "guardrail": "Use local-language review and do not publish unsupported shipping destinations.",
    },
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _read_catalog_sample(settings: Any) -> tuple[int, int]:
    candidates = [
        settings.root_dir / "output" / "live_shopify_products.csv",
        settings.root_dir / "collezioni_csv" / "collezione 12_06_2026_SHOPIFY_IMPORT_READY_SEO_TAGS_READY.csv",
        settings.root_dir / "collezioni_csv" / "collezione 12_06_2026_SHOPIFY_IMPORT_READY.csv",
        settings.root_dir / "output" / "products_export_updated.csv",
        settings.root_dir / "input" / "products_export_updated.csv",
    ]
    for path in candidates:
        if path.exists():
            try:
                lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
            except OSError:
                continue
            product_rows = max(0, len([line for line in lines[1:] if line.split(",", 1)[0].strip()]))
            image_mentions = sum(1 for line in lines[1:] if "http" in line.lower() and any(ext in line.lower() for ext in (".jpg", ".png", ".webp")))
            return product_rows, image_mentions
    return 0, 0


def photo_rows(settings: Any, snapshot: dict[str, Any]) -> list[dict[str, str]]:
    products, image_mentions = _read_catalog_sample(settings)
    theme_summary = snapshot.get("theme", {}).get("summary", {})
    theme_id = theme_summary.get("theme_id", "")
    theme_status = "tm04_live" if theme_id == TM04_THEME_ID else (theme_summary.get("status", "") or "unknown")
    google_status = snapshot.get("google", {}).get("summary", {}).get("status", "")
    result: list[dict[str, str]] = []
    for shot in SHOT_TYPES:
        name = shot["shot"]
        if name in {"01 front product", "04 editorial front", "06 detail fabric", "07 hero banner"}:
            priority = "P0"
        elif name == "08 lifestyle front":
            priority = "P2" if google_status != "suspended" else "P1"
        elif name in {"12 packaging", "02 back product"}:
            priority = "P1"
        else:
            priority = "P2"
        result.append(
            {
                **shot,
                "priority": priority,
                "status": "ready_to_plan" if products else "waiting_for_shopify_products",
                "catalog_products": str(products),
                "image_mentions": str(image_mentions),
                "theme_dependency": theme_status,
            }
        )
    return result


def write_outputs(settings: Any, photos: list[dict[str, str]]) -> tuple[str, str, str, str]:
    photo_path = settings.root_dir / PHOTO_SHEET
    photo_path.parent.mkdir(parents=True, exist_ok=True)
    photo_fields = ["shot", "priority", "status", "format", "purpose", "requirements", "catalog_products", "image_mentions", "theme_dependency", "agent_next"]
    with photo_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=photo_fields)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in photo_fields} for row in photos])

    progression_path = settings.root_dir / THEME_PROGRESSIONS
    progression_path.parent.mkdir(parents=True, exist_ok=True)
    progression_fields = ["stage", "theme_use", "image_need", "when"]
    with progression_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=progression_fields)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in progression_fields} for row in THEME_STAGES])

    skill_path = settings.root_dir / PHOTO_SKILL
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# bakabo-photo-studio",
        "",
        "Photography and image production skill for BKS Studio / bakabo.club.",
        "Covers product shots, collection heroes, editorial direction, global market adaptation and review enablement.",
        "Activated after Shopify products are published. Images must match product reality — never invented.",
        "",
        "## Workflow",
        "",
        "1. Detect published Shopify products (live_shopify_products.csv or active collezioni_csv).",
        "2. Build shot list per product, keyed to collection identity and TM04 accent color.",
        "3. Produce P0 shots first: front product, editorial front, detail fabric, hero banner.",
        "4. Map images to Shopify product media, collection hero metafield, TM04 theme bands.",
        "5. Visual truth check: every image must show the real product; no invented pattern, color or logo.",
        "6. P1/P2 shots (lifestyle, packaging, review asset) activate by commercial-strategy stage.",
        "7. Save high-performing image+theme combinations to Knowledge DB for future drops.",
        "",
        "## TM04 integration",
        "",
        f"Active theme ID: {TM04_THEME_ID}. Hero banners must leave left 40% clear for bks-collection-signal text.",
        "Use collection accent color for gradient overlays. Background: #0A0A0A (dark) or #FAFAF7 (paper).",
        "",
        "## Theme progression (commercial strategy gate)",
        "",
    ]
    lines.extend(f"- **{row['stage']}**: {row['theme_use']} / images needed: {row['image_need']}. When: {row['when']}" for row in THEME_STAGES)
    lines.extend(["", "## Collection directions", ""])
    lines.extend(
        f"- **{row['collection']}** (`{row['handle']}`, accent `{row['accent']}`): {row['surface']}; {row['light']}; mood: {row['mood']}."
        for row in COLLECTION_DIRECTIONS
    )
    lines.extend(["", "## Global Market System", ""])
    lines.extend(
        f"- **{row['market']}** ({row['language']}): {row['model_direction']} Weather: {row['weather_logic']} Guardrail: {row['guardrail']}"
        for row in WORLD_MODEL_CONTEXTS
    )
    lines.extend(["", "## Review guardrails", ""])
    lines.extend(f"- **{row['guard']}**: {row['meaning']} Agent rule: {row['agent_rule']}" for row in REVIEW_GUARDS)
    skill_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    world_path = settings.root_dir / WORLD_MODEL_SHEET
    world_path.parent.mkdir(parents=True, exist_ok=True)
    world_fields = ["market", "language", "model_direction", "weather_logic", "copy_tone", "guardrail"]
    with world_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=world_fields)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in world_fields} for row in WORLD_MODEL_CONTEXTS])

    return _relative(settings.root_dir, photo_path), _relative(settings.root_dir, progression_path), _relative(settings.root_dir, skill_path), _relative(settings.root_dir, world_path)


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    photos = photo_rows(settings, snapshot)
    sheet, progression, skill, world_sheet = write_outputs(settings, photos)
    return {
        "summary": {
            "shot_types": len(photos),
            "p0": sum(1 for row in photos if row["priority"] == "P0"),
            "ready": sum(1 for row in photos if row["status"] == "ready_to_plan"),
            "review_guards": len(REVIEW_GUARDS),
            "sheet": sheet,
            "progression": progression,
            "skill": skill,
            "directions": len(COLLECTION_DIRECTIONS),
            "world_contexts": len(WORLD_MODEL_CONTEXTS),
            "world_sheet": world_sheet,
        },
        "shots": photos,
        "theme_stages": list(THEME_STAGES),
        "collection_directions": list(COLLECTION_DIRECTIONS),
        "review_guards": list(REVIEW_GUARDS),
        "world_contexts": list(WORLD_MODEL_CONTEXTS),
        "learning_rule": "The agent records which photo/theme/review combinations improve trust, clarity and conversion. It never invents product patterns, colors or logos.",
    }
