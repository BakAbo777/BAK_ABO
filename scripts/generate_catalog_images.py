"""BKS Studio — Generate catalog images via AI from Printify mockups.

AI is FREE to change:
  - Background and environment (collection-appropriate)
  - Lighting, shadows, atmosphere
  - Framing, composition, camera angle
  - Scene/context (flat lay, studio, location)

AI must PRESERVE exactly:
  - Product type and garment category (hoodie stays hoodie, tee stays tee)
  - Texture and artwork/print on the product (every detail of the design)
  - Product colors and materials

HARD RULE: Zero text, labels, logos, or typography anywhere in the output image.

Uses gpt-image-1 images.edit with the Printify mockup as reference image.
Requires: sync_printify_library.py run first to download mockups.

Usage:
  python scripts/generate_catalog_images.py
  python scripts/generate_catalog_images.py --collection bks-hours
  python scripts/generate_catalog_images.py --collection bks-riviera --shots 3
  python scripts/generate_catalog_images.py --handle "bks-hours-arch-hoodie" --shots 2
  python scripts/generate_catalog_images.py --dry-run
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

import httpx
import requests
import urllib3

urllib3.disable_warnings()  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_env = ROOT / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        if _k.strip() not in os.environ:
            os.environ[_k.strip()] = _v.strip().strip('"').strip("'")

import openai
from ecommerce_automation import catalog_db
from bks_assets import active_catalog_db

CATALOG_AI_DIR = ROOT / "output" / "catalog_images"

# ─── Collection environments ─────────────────────────────────────────────────
# Based on bakabo-photo-studio skill collection directions.
COLLECTION_ENV: dict[str, dict] = {
    "bks-hours": {
        "background": "dark raw concrete wall, industrial surface, deep shadow",
        "lighting": "single hard lateral light source from the left, strong directional shadows",
        "mood": "urban, contemplative, minimal",
        "accent": "#c8c4be",
    },
    "bks-glyph": {
        "background": "matte black flat surface, perfectly neutral studio void",
        "lighting": "soft flat ring light, even front illumination, subtle gradient",
        "mood": "graphic, coded, precise",
        "accent": "#d4a030",
    },
    "bks-marker": {
        "background": "rough torn paper texture, aged iron surface, raw urban material",
        "lighting": "hard lateral key light with sharp cast shadow",
        "mood": "gestural, raw, urban energy",
        "accent": "#c04418",
    },
    "bks-riviera": {
        "background": "travertine stone surface, natural linen fabric, warm mediterranean light",
        "lighting": "golden hour from the right, warm soft diffused sunlight",
        "mood": "resort, mediterranean, relaxed luxury",
        "accent": "#0ca898",
    },
    "bks-pulse": {
        "background": "dark geometric tiles, optical pattern floor, deep neutral plane",
        "lighting": "front ring light, even studio illumination with subtle optical glow",
        "mood": "optical, kinetic, rhythmic",
        "accent": "#8888cc",
    },
    "bks-token": {
        "background": "reflective plexiglass surface, neon light reflections, digital arcade atmosphere",
        "lighting": "low-key neon accent light, purple and magenta edge lighting",
        "mood": "arcade, digital, collectible",
        "accent": "#9828d8",
    },
    "bks-flag": {
        "background": "clean white studio background, pure flat white, crisp pop aesthetic",
        "lighting": "flat uniform studio light, no shadows, high key",
        "mood": "pop, graphic, bold",
        "accent": "#c82020",
    },
    "bks-origin": {
        "background": "light stone surface, natural linen cloth, warm earth tones",
        "lighting": "soft overcast natural light, diffused, no hard shadows",
        "mood": "narrative, naive, artisanal warmth",
        "accent": "#489808",
    },
}

# Shot framing variants
SHOT_VARIANTS: list[dict] = [
    {
        "name": "front_editorial",
        "framing": "centered front view, full product visible, editorial proportions, slightly above eye level",
    },
    {
        "name": "three_quarter",
        "framing": "three-quarter angle view showing front and side, dynamic composition, slight tilt",
    },
    {
        "name": "detail_texture",
        "framing": "extreme close-up detail shot focusing on the print and fabric texture, macro-style",
    },
    {
        "name": "flat_lay",
        "framing": "overhead flat lay composition, product laid flat, clean geometric arrangement",
    },
]


def _out(msg: str) -> None:
    sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
    sys.stdout.flush()


def _build_prompt(product_title: str, blueprint_brand: str, blueprint_model: str,
                  collection: str, shot_variant: dict) -> str:
    """Build the GPT-image-1 prompt for a single catalog shot."""
    env = COLLECTION_ENV.get(collection, COLLECTION_ENV["bks-hours"])
    product_desc = f"{blueprint_brand} {blueprint_model}".strip() if blueprint_brand or blueprint_model else "garment"

    return (
        f"Reframe and restage this product as a high-quality catalog photograph. "
        f"The product is a {product_desc}.\n\n"
        f"PRESERVE EXACTLY — do not change:\n"
        f"- The product type and category: this must remain a {product_desc}\n"
        f"- Every detail of the print, artwork, and texture on the product exactly as shown\n"
        f"- The product colors and material appearance\n\n"
        f"CREATIVE FREEDOM — you may change:\n"
        f"- Background: {env['background']}\n"
        f"- Lighting: {env['lighting']}\n"
        f"- Framing and composition: {shot_variant['framing']}\n"
        f"- Atmosphere and mood: {env['mood']}\n\n"
        f"CRITICAL CONSTRAINT: "
        f"Absolutely no text, labels, logos, typography, captions, or overlays anywhere in the image. "
        f"The image must be completely free of any written characters."
    )


def _load_mockup_png(path: Path) -> bytes:
    """Load image and ensure it's PNG format (required by images.edit)."""
    try:
        from PIL import Image
        import io
        with Image.open(path) as img:
            img = img.convert("RGBA")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
    except ImportError:
        # Pillow not available — read raw (works if source is already PNG)
        return path.read_bytes()


def generate_shot(
    client: openai.OpenAI,
    mockup_path: Path,
    product_title: str,
    blueprint_brand: str,
    blueprint_model: str,
    collection: str,
    shot_variant: dict,
    dry_run: bool,
) -> bytes | None:
    """Generate a single catalog shot. Returns PNG bytes or None."""
    prompt = _build_prompt(product_title, blueprint_brand, blueprint_model, collection, shot_variant)

    if dry_run:
        _out(f"    [DRY] shot={shot_variant['name']}  collection={collection}")
        _out(f"    prompt preview: {prompt[:120]}…")
        return None

    try:
        image_bytes = _load_mockup_png(mockup_path)
        import io
        response = client.images.edit(
            model="gpt-image-1",
            image=io.BytesIO(image_bytes),
            prompt=prompt,
            size="1024x1024",
            n=1,
        )
        b64 = response.data[0].b64_json
        if b64:
            return base64.b64decode(b64)
        # fallback: url-based response
        url = response.data[0].url or ""
        if url:
            r = requests.get(url, timeout=60, verify=False)
            r.raise_for_status()
            return r.content
    except Exception as exc:
        _out(f"    ✗ generation error: {exc}")
    return None


def process_product(
    db_path: Path,
    product: dict,
    client: openai.OpenAI,
    shots: int,
    dry_run: bool,
    force: bool,
) -> dict:
    pid = product["printify_product_id"]
    title = product["title"]
    collection = product["collection"] or "bks-hours"
    blueprint_id = product.get("blueprint_id")

    local_paths = json.loads(product.get("local_mockup_paths_json") or "[]")
    if not local_paths:
        return {"status": "no_mockup", "generated": 0}

    # Get blueprint info for prompt
    blueprint_brand = ""
    blueprint_model = ""
    if blueprint_id:
        bp_rows = []
        import sqlite3
        from contextlib import closing
        with closing(sqlite3.connect(db_path)) as conn:
            conn.row_factory = sqlite3.Row
            r = conn.execute(
                "SELECT brand, model FROM printify_blueprints WHERE blueprint_id = ?",
                (blueprint_id,)
            ).fetchone()
            if r:
                blueprint_brand = r["brand"]
                blueprint_model = r["model"]

    handle = title.lower().replace(" ", "-").replace("/", "-")
    handle = "".join(c for c in handle if c.isalnum() or c == "-")[:40]
    out_dir = CATALOG_AI_DIR / collection / handle
    out_dir.mkdir(parents=True, exist_ok=True)

    # Use first mockup as source
    mockup_path = ROOT / local_paths[0]
    if not mockup_path.exists():
        return {"status": "mockup_missing", "generated": 0}

    generated = 0
    for i, variant in enumerate(SHOT_VARIANTS[:shots]):
        dest = out_dir / f"{handle}_ai_{variant['name']}.jpg"

        if dest.exists() and not force and not dry_run:
            _out(f"  ✓ exists: {dest.name}")
            generated += 1
            continue

        _out(f"  → [{i+1}/{shots}] {variant['name']}…")
        png_bytes = generate_shot(
            client, mockup_path, title, blueprint_brand, blueprint_model,
            collection, variant, dry_run
        )

        if dry_run:
            generated += 1
            continue

        if png_bytes:
            try:
                from PIL import Image
                import io
                with Image.open(io.BytesIO(png_bytes)) as img:
                    img = img.convert("RGB")
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    img.save(dest, "JPEG", quality=92, optimize=True)
            except ImportError:
                dest.write_bytes(png_bytes)

            catalog_db.upsert_asset(
                db_path,
                product_handle=handle,
                asset_type="catalog_ai",
                file_path=str(dest.relative_to(ROOT)),
                collection=collection,
                variant=variant["name"],
                meta={
                    "printify_product_id": pid,
                    "source_mockup": local_paths[0],
                    "ai_tool": "gpt-image-1",
                    "shot_variant": variant["name"],
                    "no_text": True,
                    "product_type_preserved": True,
                    "texture_preserved": True,
                    "collection_env": collection,
                },
            )
            _out(f"    ✓ saved: {dest.name}")
            generated += 1
            time.sleep(1)
        else:
            _out(f"    ✗ generation failed for {variant['name']}")

    return {"status": "ok", "generated": generated}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate BKS catalog images via AI")
    parser.add_argument("--collection", default="",
                        help="Filter by collection handle (e.g. bks-hours)")
    parser.add_argument("--handle", default="",
                        help="Process a single product handle")
    parser.add_argument("--shots", type=int, default=2,
                        help="Number of shot variants per product (1-4, default 2)")
    parser.add_argument("--force", action="store_true",
                        help="Regenerate even if output already exists")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be generated without calling API")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        _out("✗ OPENAI_API_KEY not set")
        sys.exit(1)

    db_path = active_catalog_db()
    lib_summary = catalog_db.printify_library_summary(db_path)
    if not lib_summary.get("ok") or lib_summary.get("products_with_mockups", 0) == 0:
        _out("✗ No products with downloaded mockups. Run sync_printify_library.py first.")
        sys.exit(1)

    client = openai.OpenAI(
        api_key=api_key,
        http_client=httpx.Client(verify=False),
    )

    shots = max(1, min(4, args.shots))
    _out(f"=== BKS Catalog Image Generation ({'DRY RUN' if args.dry_run else 'LIVE'}) ===")
    _out(f"  Shots per product: {shots}  |  Variants: {[v['name'] for v in SHOT_VARIANTS[:shots]]}")
    _out(f"  Output: output/catalog_images/")

    products = catalog_db.list_printify_products(db_path, collection=args.collection)
    if args.handle:
        products = [p for p in products if args.handle in p["title"].lower().replace(" ", "-")]

    _out(f"  Products to process: {len(products)}\n")

    total_generated = 0
    total_skipped = 0
    total_errors = 0

    for prod in products:
        col = prod["collection"] or "unknown"
        _out(f"── {prod['title'][:45]}  [{col}] ──────────────────")
        result = process_product(db_path, prod, client, shots, args.dry_run, args.force)
        status = result.get("status")
        gen = result.get("generated", 0)
        if status in ("no_mockup", "mockup_missing"):
            _out(f"  ⚪ {status} — sync library first")
            total_skipped += 1
        else:
            total_generated += gen

    _out(f"\n=== DONE === generated={total_generated} skipped={total_skipped} errors={total_errors}")
    _out(f"  AI catalog images: {CATALOG_AI_DIR}")


if __name__ == "__main__":
    main()
