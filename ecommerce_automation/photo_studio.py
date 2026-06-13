from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


PHOTO_SHEET = Path("output/photo_studio_pipeline.csv")
THEME_PROGRESSIONS = Path("output/theme_progression_matrix.csv")
PHOTO_SKILL = Path("docs/bakabo-photo-studio_SKILL.md")


SHOT_TYPES: tuple[dict[str, str], ...] = (
    {
        "shot": "01 front product",
        "format": "1:1 JPG 2000x2000",
        "purpose": "Primary Shopify PDP image and product card thumbnail.",
        "requirements": "Exact mockup reference, clean background, no props, print fully visible.",
    },
    {
        "shot": "02 back product",
        "format": "1:1 JPG 2000x2000",
        "purpose": "Back view for PDP gallery and product truth.",
        "requirements": "Use only when back mockup exists or is provided; never invent a back print.",
    },
    {
        "shot": "04 editorial front",
        "format": "4:5 JPG 1600x2000",
        "purpose": "Second PDP image, desktop hover and collection mood.",
        "requirements": "Still-life or on-model based on collection, exact product from reference, no text/logo overlay.",
    },
    {
        "shot": "06 detail fabric",
        "format": "1:1 JPG 1500x1500",
        "purpose": "Texture, print detail, finish and quality reassurance.",
        "requirements": "Close-up from real/reference print; no invented pattern or color shift.",
    },
    {
        "shot": "07 hero banner",
        "format": "16:7 JPG 2400x1050",
        "purpose": "Collection page, homepage band and campaign hero.",
        "requirements": "Generous negative space for theme text; product reality remains visible.",
    },
    {
        "shot": "08 lifestyle front",
        "format": "4:5 and 9:16",
        "purpose": "Social proof, social campaign and PDP context.",
        "requirements": "Adult model only when approved; no celebrity resemblance; product still inspectable.",
    },
    {
        "shot": "12 packaging",
        "format": "1:1",
        "purpose": "Support trust, shipping and unboxing expectations.",
        "requirements": "Show packaging only if it represents real delivery experience.",
    },
    {
        "shot": "Review prompt asset",
        "format": "9:16",
        "purpose": "Post-purchase email/social prompt for honest reviews.",
        "requirements": "Transparent: ask for real feedback, never incentivize deceptive reviews.",
    },
)


COLLECTION_DIRECTIONS: tuple[dict[str, str], ...] = (
    {"collection": "Hours", "surface": "dark raw concrete", "light": "hard lateral single source", "mood": "urban, contemplative"},
    {"collection": "Glyph", "surface": "matte black plane", "light": "flat studio ring light", "mood": "graphic, coded"},
    {"collection": "Marker", "surface": "rough paper / iron", "light": "hard lateral with sharp shadow", "mood": "gestural, urban"},
    {"collection": "Riviera", "surface": "travertine / linen", "light": "golden hour from right", "mood": "resort, mediterranean"},
    {"collection": "Pulse", "surface": "dark plane / tiles", "light": "front ring light", "mood": "optical, kinetic"},
    {"collection": "Token", "surface": "reflective surface / plexiglass", "light": "low-key neon accent", "mood": "arcade, digital"},
    {"collection": "Flag", "surface": "white studio", "light": "flat uniform light", "mood": "pop, graphic"},
    {"collection": "Folklore", "surface": "light stone / linen / earth", "light": "soft overcast", "mood": "narrative, naive"},
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


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _read_catalog_sample(settings: Any) -> tuple[int, int]:
    candidates = [
        settings.root_dir / "output" / "products_export_updated.csv",
        settings.root_dir / "input" / "products_export_updated.csv",
    ]
    for path in candidates:
        if path.exists():
            try:
                lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
            except OSError:
                return 0, 0
            product_rows = max(0, len([line for line in lines[1:] if line.split(",", 1)[0].strip()]))
            image_mentions = sum(1 for line in lines[1:] if "http" in line.lower() and any(ext in line.lower() for ext in (".jpg", ".png", ".webp")))
            return product_rows, image_mentions
    return 0, 0


def photo_rows(settings: Any, snapshot: dict[str, Any]) -> list[dict[str, str]]:
    products, image_mentions = _read_catalog_sample(settings)
    theme_status = snapshot.get("theme", {}).get("summary", {}).get("status", "")
    google_status = snapshot.get("google", {}).get("summary", {}).get("status", "")
    result: list[dict[str, str]] = []
    for shot in SHOT_TYPES:
        if shot["shot"] in {"01 front product", "04 editorial front", "06 detail fabric", "07 hero banner"}:
            priority = "P0"
        elif google_status == "suspended" and shot["shot"] == "08 lifestyle front":
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
                "theme_dependency": theme_status or "unknown",
                "agent_next": "Use uploaded mockups only, generate prompts by slot, QA visual truth, then map images to Shopify media.",
            }
        )
    return result


def write_outputs(settings: Any, photos: list[dict[str, str]]) -> tuple[str, str, str]:
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
        "Skill for product photography, collection imagery, theme composition and review enablement after Shopify products are created.",
        "",
        "## Workflow",
        "",
        "1. Detect published/realized Shopify products.",
        "2. Build shot list by product and collection.",
        "3. Produce hero, detail, scale, lifestyle and packaging images.",
        "4. Map images to product media, collection hero, theme bands and social formats.",
        "5. Verify truthfulness: image must show the product reality and not create misleading expectations.",
        "6. Activate review request flow only after delivery/customer experience.",
        "7. Save winning image/theme combinations to Knowledge DB.",
        "",
        "## Theme progression",
        "",
    ]
    lines.extend(f"- {row['stage']}: {row['theme_use']} / images: {row['image_need']}." for row in THEME_STAGES)
    lines.extend(["", "## Collection directions", ""])
    lines.extend(f"- {row['collection']}: {row['surface']}; {row['light']}; {row['mood']}." for row in COLLECTION_DIRECTIONS)
    lines.extend(
        [
            "",
            "## Review guardrails",
            "",
        ]
    )
    lines.extend(f"- {row['guard']}: {row['meaning']}" for row in REVIEW_GUARDS)
    skill_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return _relative(settings.root_dir, photo_path), _relative(settings.root_dir, progression_path), _relative(settings.root_dir, skill_path)


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    photos = photo_rows(settings, snapshot)
    sheet, progression, skill = write_outputs(settings, photos)
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
        },
        "shots": photos,
        "theme_stages": list(THEME_STAGES),
        "collection_directions": list(COLLECTION_DIRECTIONS),
        "review_guards": list(REVIEW_GUARDS),
        "learning_rule": "The agent records which photo/theme/review combinations improve trust, clarity and conversion. It never invents product patterns, colors or logos.",
    }
