"""BKS Studio — Site Image Generator (gpt-image-1)

Genera le immagini sito con i nomi ESATTI attesi dai template Shopify:
  bks-hours-editorial.png      → hero + magazine spread Hours
  bks-glyph-editorial.png      → hero + magazine spread Glyph
  bks-marker-editorial.png     → hero + magazine spread Marker
  bks-riviera-editorial.png    → hero + magazine spread Riviera
  bks-pulse-editorial.png      → hero + magazine spread Pulse
  bks-token-puffer.png         → hero + magazine spread Token
  bks-flag-editorial.png       → hero + magazine spread Flag
  bks-origin-editorial.png     → hero + magazine spread Origin
  bks-magazine-cover.png       → Home Magazine cover (full page)
  bks-hours-piano.png          → Piano Hero tasto Hours  (opzionale)
  ...

Format: 1536×1024 (3:2) per tutte le immagini editoriali
        Testo overlay nella sezione sinistra (40% libero per bks-collection-signal)

Output locale: output/site_images/{filename}
Upload Shopify: python scripts/upload_site_images.py
Dopo upload: shopify://shop_images/{filename} già cablato nei template JSON.

Uso:
  python scripts/generate_site_images.py           # tutte le immagini
  python scripts/generate_site_images.py --type editorial  # 8 editorial + cover
  python scripts/generate_site_images.py --type piano      # 8 piano squares
  python scripts/generate_site_images.py --collection bks-riviera
  python scripts/generate_site_images.py --dry-run
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_env = ROOT / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        _k = _k.strip(); _v = _v.strip().strip('"').strip("'")
        if _k not in os.environ:
            os.environ[_k] = _v

OUTPUT_DIR = ROOT / "output" / "site_images"
MANIFEST   = ROOT / "output" / "site_images" / "manifest.json"

# ── Catalog: collection → image definition ─────────────────────────────────────
# shopify_filename: exact filename used in theme JSON templates
# size: "1536x1024" for editorial/hero, "1024x1024" for piano squares
# type: "editorial" | "piano"

IMAGES: list[dict] = [
    # ── Magazine cover ──────────────────────────────────────────────────────────
    {
        "id": "magazine_cover",
        "shopify_filename": "bks-magazine-cover.png",
        "type": "editorial",
        "size": "1536x1024",
        "collection": "home",
        "accent": "#b8a165",
        "prompt": """\
Wide editorial fashion magazine cover, horizontal 3:2 format.
BKS Studio — Italian AI art-on-fabric atelier.
Clean, minimal composition: a curated selection of 3–4 print apparel pieces \
(folded puffer jacket, lounge pants, swim trunks) arranged as a magazine cover \
still-life, warm cream/paper background #fafaf7.
Soft diffused overhead studio light, no hard shadows.
Left 40% of frame: open cream background for text overlay.
Right 60%: product arrangement with refined editorial spacing.
Color palette: warm cream #fafaf7, gold sand #b8a165, near-black #0a0a0a.
Multiple bold all-over print textiles visible — graphic, colorful, diverse patterns.
No model. No added text. No logo. Photorealistic editorial fashion photography.""",
    },

    # ── Collection editorials ──────────────────────────────────────────────────
    {
        "id": "hours_editorial",
        "shopify_filename": "bks-hours-editorial.png",
        "type": "editorial",
        "size": "1536x1024",
        "collection": "bks-hours",
        "accent": "#c8c4be",
        "prompt": """\
Wide editorial fashion hero banner, horizontal 3:2 format.
Dark raw concrete architectural interior — brutalist columns, rough cement walls.
Still-life arrangement: folded neutral grey apparel (lounge pants, puffer jacket) \
on a concrete ledge or low shelf.
Hard single lateral light source from the left, sharp geometric shadow.
LEFT 40% of frame: deep shadow / near-black concrete negative space for text overlay.
RIGHT 60%: styled product scene.
Color palette: warm grey #c8c4be, near-black #0a0a0a, natural off-white cotton.
No model. No added text. No logo. Photorealistic editorial photography.""",
    },
    {
        "id": "glyph_editorial",
        "shopify_filename": "bks-glyph-editorial.png",
        "type": "editorial",
        "size": "1536x1024",
        "collection": "bks-glyph",
        "accent": "#9b7cba",
        "prompt": """\
Wide editorial fashion hero banner, horizontal 3:2 format.
Matte black infinite studio background.
Still-life: graphic-print hoodie and shorts — all-over coded symbol/glyph patterns, \
angular marks, grid fragments — arranged on a flat matte surface.
Flat studio ring light, perfectly even illumination, minimal shadows.
LEFT 40%: pure near-black negative space for text overlay.
RIGHT 60%: product arrangement, print legible.
Color palette: purple-grey #9b7cba accent visible in pattern, near-black #0a0a0a.
No model. No text. No logo. Photorealistic editorial photography.""",
    },
    {
        "id": "marker_editorial",
        "shopify_filename": "bks-marker-editorial.png",
        "type": "editorial",
        "size": "1536x1024",
        "collection": "bks-marker",
        "accent": "#e03c2d",
        "prompt": """\
Wide editorial fashion hero banner, horizontal 3:2 format.
Large-format textured paper pinned to a raw iron/steel industrial panel.
Still-life: red-and-black gestural all-over print windbreaker and shorts \
arranged dynamically against the paper surface.
Hard lateral light from the left, sharp dramatic shadow.
LEFT 40%: empty textured paper surface for text overlay.
RIGHT 60%: styled apparel scene.
Color palette: #e03c2d marker-red, near-black, raw paper cream.
No model. No text. No logo. Photorealistic editorial photography.""",
    },
    {
        "id": "riviera_editorial",
        "shopify_filename": "bks-riviera-editorial.png",
        "type": "editorial",
        "size": "1536x1024",
        "collection": "bks-riviera",
        "accent": "#3daed6",
        "prompt": """\
Wide editorial fashion hero banner, horizontal 3:2 format.
Travertine pool terrace — warm light stone, Mediterranean afternoon.
Still-life: resort apparel (swim trunks, lounge pants) arranged on travertine ledge \
or draped on a minimal chair. Mediterranean blue water background edge visible.
Golden hour warm light from the right, long horizontal shadow.
LEFT 40%: open sky or plain travertine stone surface for text overlay.
RIGHT 60%: product arrangement, print clearly legible.
Color palette: Mediterranean teal #3daed6, warm travertine cream, natural linen.
No model. No text. No logo. Photorealistic editorial fashion photography.""",
    },
    {
        "id": "pulse_editorial",
        "shopify_filename": "bks-pulse-editorial.png",
        "type": "editorial",
        "size": "1536x1024",
        "collection": "bks-pulse",
        "accent": "#8888cc",
        "prompt": """\
Wide editorial fashion hero banner, horizontal 3:2 format.
Dark glossy metro-style tile surface — near-black square tiles, subtle gloss.
Still-life: optical geometric all-over print shorts, hoodie and accessories — \
repeating rhythmic pattern — arranged on the tile surface.
Front studio ring light, clean even illumination, soft reflections on tiles.
LEFT 40%: dark tile surface negative space for text overlay.
RIGHT 60%: product arrangement, optical pattern prominent.
Color palette: lavender-blue #8888cc, near-black #0a0a0a, optical white.
No model. No text. No logo. Photorealistic editorial photography.""",
    },
    {
        "id": "token_puffer",
        "shopify_filename": "bks-token-puffer.png",
        "type": "editorial",
        "size": "1536x1024",
        "collection": "bks-token",
        "accent": "#4cae8c",
        "prompt": """\
Wide editorial fashion hero banner, horizontal 3:2 format.
Reflective mirror-like plexiglass floor — arcade/digital aesthetic, dark environment.
Hero product: digital pixel-art print puffer jacket — inflated, displayed on minimal \
mannequin stand or folded dramatically — neon teal #4cae8c accent light from below-right.
Product reflection visible on the mirror floor.
LEFT 40%: deep reflective shadow, near-black, for text overlay.
RIGHT 60%: puffer jacket prominently lit with neon teal reflections.
Color palette: teal #4cae8c, near-black #0a0a0a, pixel white.
No model. No text. No logo. Photorealistic editorial photography.""",
    },
    {
        "id": "flag_editorial",
        "shopify_filename": "bks-flag-editorial.png",
        "type": "editorial",
        "size": "1536x1024",
        "collection": "bks-flag",
        "accent": "#d4a017",
        "prompt": """\
Wide editorial fashion hero banner, horizontal 3:2 format.
Clean white photography studio — pure white seamless background #ffffff.
Still-life: bold graphic all-over print t-shirt, shorts and sneakers — \
strong pop-art flag-inspired pattern, high contrast — arranged cleanly.
Flat perfectly uniform overhead studio light, high-key, no shadows.
LEFT 40%: pure white background for text overlay.
RIGHT 60%: product arrangement, bold graphic pattern highly legible.
Color palette: gold #d4a017 accent in pattern, pure white, graphic black.
No model. No text. No logo. Photorealistic editorial photography, pop art energy.""",
    },
    {
        "id": "origin_editorial",
        "shopify_filename": "bks-origin-editorial.png",
        "type": "editorial",
        "size": "1536x1024",
        "collection": "bks-origin",
        "accent": "#6aab48",
        "prompt": """\
Wide editorial fashion hero banner, horizontal 3:2 format.
Natural setting — warm light stone surface, linen cloth, raw earth elements.
Still-life: botanical / naive-art all-over print apparel (lounge pants, tee, travel bag) \
arranged naturally on stone surface with minimal organic props (dry leaves, stone, linen).
Soft overcast natural light, even and diffused, no hard shadows.
LEFT 40%: textured natural stone / linen negative space for text overlay.
RIGHT 60%: product scene, botanical print legible.
Color palette: leaf-green #6aab48, warm stone cream, natural linen, earth brown.
No model. No text. No logo. Photorealistic editorial fashion photography.""",
    },

    # ── Piano squares (optional) ───────────────────────────────────────────────
    {
        "id": "hours_piano",
        "shopify_filename": "bks-hours-piano.png",
        "type": "piano",
        "size": "1024x1024",
        "collection": "bks-hours",
        "accent": "#c8c4be",
        "prompt": """\
Square editorial product photography, 1:1. Dark raw concrete surface.
Single folded neutral-grey puffer jacket, overhead 45° angle.
Hard lateral studio light, sharp geometric shadow.
Near-black background, warm grey textile.
No model. No text. No logo. Photorealistic.""",
    },
    {
        "id": "glyph_piano",
        "shopify_filename": "bks-glyph-piano.png",
        "type": "piano",
        "size": "1024x1024",
        "collection": "bks-glyph",
        "accent": "#9b7cba",
        "prompt": """\
Square editorial product photography, 1:1. Matte black surface.
Single graphic-print hoodie with coded glyph all-over pattern, folded flat.
Overhead flat ring light, no shadow. Purple-grey accent in pattern.
No model. No text. No logo. Photorealistic.""",
    },
    {
        "id": "marker_piano",
        "shopify_filename": "bks-marker-piano.png",
        "type": "piano",
        "size": "1024x1024",
        "collection": "bks-marker",
        "accent": "#e03c2d",
        "prompt": """\
Square editorial product photography, 1:1. Rough paper surface.
Single red-and-black gestural print windbreaker, pinned against paper.
Hard lateral light from left, sharp shadow. Red #e03c2d dominant.
No model. No text. No logo. Photorealistic.""",
    },
    {
        "id": "riviera_piano",
        "shopify_filename": "bks-riviera-piano.png",
        "type": "piano",
        "size": "1024x1024",
        "collection": "bks-riviera",
        "accent": "#3daed6",
        "prompt": """\
Square editorial product photography, 1:1. Travertine surface.
Single Mediterranean blue all-over print swim trunks, folded.
Golden hour warm light from the right. Teal #3daed6 print dominant.
No model. No text. No logo. Photorealistic.""",
    },
    {
        "id": "pulse_piano",
        "shopify_filename": "bks-pulse-piano.png",
        "type": "piano",
        "size": "1024x1024",
        "collection": "bks-pulse",
        "accent": "#8888cc",
        "prompt": """\
Square editorial product photography, 1:1. Dark glossy tile surface.
Single optical geometric pattern shorts, flat-lay overhead.
Front ring light, even illumination. Lavender-blue #8888cc pattern.
No model. No text. No logo. Photorealistic.""",
    },
    {
        "id": "token_piano",
        "shopify_filename": "bks-token-piano.png",
        "type": "piano",
        "size": "1024x1024",
        "collection": "bks-token",
        "accent": "#4cae8c",
        "prompt": """\
Square editorial product photography, 1:1. Mirror plexiglass surface.
Single digital pixel-print puffer jacket on reflective surface.
Low-key neon teal #4cae8c accent light. Reflection below product.
No model. No text. No logo. Photorealistic.""",
    },
    {
        "id": "flag_piano",
        "shopify_filename": "bks-flag-piano.png",
        "type": "piano",
        "size": "1024x1024",
        "collection": "bks-flag",
        "accent": "#d4a017",
        "prompt": """\
Square editorial product photography, 1:1. Pure white surface.
Single bold graphic flag-pattern t-shirt, flat-lay on white.
Flat overhead studio light. Gold #d4a017 and graphic black pattern.
No model. No text. No logo. Photorealistic.""",
    },
    {
        "id": "origin_piano",
        "shopify_filename": "bks-origin-piano.png",
        "type": "piano",
        "size": "1024x1024",
        "collection": "bks-origin",
        "accent": "#6aab48",
        "prompt": """\
Square editorial product photography, 1:1. Natural stone surface.
Single botanical all-over print lounge pants, folded on stone.
Soft overcast light. Leaf-green #6aab48 botanical pattern.
No model. No text. No logo. Photorealistic.""",
    },
]


def _out(msg: str) -> None:
    sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
    sys.stdout.flush()


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {}


def save_manifest(m: dict) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="BKS Site Image Generator")
    parser.add_argument("--type", choices=["editorial", "piano", "all"], default="editorial",
                        help="Image type (default: editorial — 8 collection heroes + cover)")
    parser.add_argument("--collection", default="",
                        help="Generate only this collection handle (e.g. bks-riviera)")
    parser.add_argument("--id", default="",
                        help="Generate single image by id (e.g. riviera_editorial)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true",
                        help="Regenerate even if file already exists")
    args = parser.parse_args()

    client = None
    if not args.dry_run:
        try:
            import openai
            api_key = os.environ.get("OPENAI_API_KEY", "")
            if not api_key:
                _out("✗ OPENAI_API_KEY not set in .env")
                sys.exit(1)
            client = openai.OpenAI(api_key=api_key)
        except ImportError:
            _out("✗ openai package not installed. Run: pip install openai")
            sys.exit(1)

    # Filter images
    targets = IMAGES
    if args.type != "all":
        targets = [i for i in targets if i["type"] == args.type]
    if args.collection:
        targets = [i for i in targets if i["collection"] == args.collection]
    if args.id:
        targets = [i for i in targets if i["id"] == args.id]

    manifest = load_manifest()
    generated = skipped = errors = 0

    _out(f"=== BKS Site Image Generator ({'DRY RUN' if args.dry_run else 'LIVE'}) ===")
    _out(f"Generating {len(targets)} image(s) — type={args.type}\n")

    for img in targets:
        out_path = OUTPUT_DIR / img["shopify_filename"]
        m_key = img["shopify_filename"]

        if out_path.exists() and not args.force and not args.dry_run:
            _out(f"  ✓ {img['shopify_filename']} exists — skip (--force to regenerate)")
            skipped += 1
            continue

        _out(f"  → [{img['type']}] {img['shopify_filename']} ({img['size']})...")
        if args.dry_run:
            _out(f"     {img['prompt'][:120]}...")
            skipped += 1
            continue

        try:
            result = client.images.generate(
                model="gpt-image-1",
                prompt=img["prompt"],
                size=img["size"],
                quality="high",
                n=1,
            )
            b64 = result.data[0].b64_json
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(base64.b64decode(b64))

            manifest[m_key] = {
                "id": img["id"],
                "collection": img["collection"],
                "type": img["type"],
                "size": img["size"],
                "local_path": str(out_path.relative_to(ROOT)),
                "shopify_filename": img["shopify_filename"],
                "shopify_url": manifest.get(m_key, {}).get("shopify_url", ""),
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            save_manifest(manifest)
            _out(f"  ✓ Saved: {out_path.relative_to(ROOT)}")
            generated += 1
            time.sleep(1)

        except Exception as exc:
            _out(f"  ✗ {img['shopify_filename']}: {exc}")
            errors += 1

    _out(f"\n=== DONE === generated={generated} skipped={skipped} errors={errors}")
    if generated > 0:
        _out(f"\nManifest: {MANIFEST.relative_to(ROOT)}")
        _out("Prossimo passo: python scripts/upload_site_images.py")
        _out("  (carica su Shopify CDN — theme templates già cablati sui nomi corretti)")


if __name__ == "__main__":
    main()
