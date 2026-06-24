"""Genera BKS Collection Setstyle heroes via OpenAI gpt-image-1.

Per ogni collezione invia i 3 prodotti rappresentativi come immagini di riferimento
a gpt-image-1 con un prompt setstyle BKS. Salva in output/catalog_images/setstyle_ai/

Richiede: OPENAI_API_KEY in .env
Modello: gpt-image-1 (image input + output)
Output: 8 JPEG 1792x1024, pronte per upload Shopify
"""
from __future__ import annotations
import os, sys, base64, json, time
from pathlib import Path

try:
    import requests, urllib3
    urllib3.disable_warnings()
except ImportError:
    print("pip install requests")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent

for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ:
        os.environ[k] = v

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
if not OPENAI_KEY:
    print("ERROR: OPENAI_API_KEY not set in .env")
    sys.exit(1)

BKSHERO = ROOT / "output" / "catalog_images" / "bks_hero"
OUT_DIR = ROOT / "output" / "catalog_images" / "setstyle_ai"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# SETSTYLE PROMPT BASE
PROMPT_BASE = """Editorial flat-lay product photography for BKS Studio fashion brand.
Background: solid cream (#fafaf7), perfectly clean and uniform.
Products: {products_desc}
Style: high-end fashion magazine still-life, balanced composition with main piece central (60% frame),
two secondary items symmetrically placed at sides at smaller scale.
Lighting: soft diffused studio light, very subtle drop shadows, no dramatic shadows.
Absolutely NO human beings, NO text overlays, NO logos except BKS product labels on the items themselves.
The products must show their patterns and prints clearly.
Clean negative space. Ratio 16:9. Editorial quality."""

# Per ogni collezione: prodotti + descrizione per il prompt
COLLECTIONS: dict[str, dict] = {
    "bks-hours": {
        "products": [
            ("bks-hours-walker-swim-trunks",   "bks-hours-walker-swim-trunks_hero.png"),
            ("bks-hours-pane™-lounge-pants",   "bks-hours-pane™-lounge-pants_hero.png"),
        ],
        "desc": "1) BKS Hours swim trunks with a Bauhaus-style architectural figure walking a tightrope, in blue-grey watercolor tones (main center piece). 2) BKS Hours lounge pants with a geometric grid/plaid pattern in muted blue-grey-peach tones (secondary left).",
        "mood": "minimalist, architectural, time, monochrome blues and greys",
    },
    "bks-glyph": {
        "products": [
            ("bks-glyph-cross-puffer",       "bks-glyph-cross-puffer_hero.png"),
            ("bks-glyph-lattice-sneakers",   "bks-glyph-lattice-sneakers_hero.png"),
            ("bks-glyph-script-swim-trunks", "bks-glyph-script-swim-trunks_hero.png"),
        ],
        "desc": "1) BKS Glyph puffer jacket with dense flowing calligraphic glyph pattern in orange-gold on deep maroon (main center). 2) BKS Glyph low-top sneakers with bold black-and-white geometric lattice grid pattern (secondary left). 3) BKS Glyph swim trunks with ancient hieroglyphic-style symbols in sandy beige-tan tones (secondary right).",
        "mood": "glyph, ancient symbols, gold-maroon-sand, graphic density",
    },
    "bks-marker": {
        "products": [
            ("bks-marker-hybrid-sneakers", "bks-marker-hybrid-sneakers_hero.png"),
            ("bks-marker-flux-swim-trunks","bks-marker-flux-swim-trunks_hero.png"),
            ("bks-marker-tag-swim-trunks", "bks-marker-tag-swim-trunks_hero.png"),
        ],
        "desc": "1) BKS Marker low-top sneakers with gold-black leopard/dot marker print (main center). 2) BKS Marker swim trunks with gestural brushstroke marks in orange-rust tones (secondary left). 3) BKS Marker swim trunks with tag-style diagonal marker lines in earthy red-brown tones (secondary right).",
        "mood": "gestural, brushstroke, marker lines, rust-orange-gold",
    },
    "bks-riviera": {
        "products": [
            ("bks-riviera-argyle-sneakers",  "bks-riviera-argyle-sneakers_hero.png"),
            ("bks-riviera-tile-swim-trunks", "bks-riviera-tile-swim-trunks_hero.png"),
            ("bks-riviera-blocks™-athletic-long-shorts", "bks-riviera-blocks™-athletic-long-shorts_hero.png"),
        ],
        "desc": "1) BKS Riviera low-top sneakers with black-and-white argyle/diamond checkered pattern on teal background (main center). 2) BKS Riviera swim trunks with mosaic tile pattern in blue-beige-navy geometric diamonds (secondary left). 3) BKS Riviera athletic shorts with bold geometric color blocks in Mediterranean blue-ochre-sand tones (secondary right).",
        "mood": "Mediterranean, coastal, teal-blue-sand, mosaic tile",
    },
    "bks-pulse": {
        "products": [
            ("bks-pulse-wave-sneakers",   "bks-pulse-wave-sneakers_hero.png"),
            ("bks-pulse-chord-swim-trunks","bks-pulse-chord-swim-trunks_hero.png"),
            ("bks-pulse-block-hawaiian",  "bks-pulse-block-hawaiian_hero.png"),
        ],
        "desc": "1) BKS Pulse low-top sneakers with fluid wave pattern in orange-red-blue on lavender background (main center). 2) BKS Pulse swim trunks with geometric chord/arc shapes in purple-black tones (secondary left). 3) BKS Pulse Hawaiian shirt with bold color-block rectangles in purple-lavender-violet (secondary right).",
        "mood": "optical, kinetic wave, purple-violet-orange movement",
    },
    "bks-token": {
        "products": [
            ("bks-token-vault-windbreaker", "bks-token-vault-windbreaker_hero.png"),
            ("bks-token-score-sneakers",    "bks-token-score-sneakers_hero.png"),
        ],
        "desc": "1) BKS Token windbreaker jacket with dense mosaic/pixel grid pattern in grey-beige-blue tones (main center, large). 2) BKS Token low-top sneakers with digital score/arcade pattern in dark tones on purple background (secondary right).",
        "mood": "digital grid, pixel art, mosaic, grey-purple arcade",
    },
    "bks-flag": {
        "products": [
            ("bks-flag-arc-sneakers",    "bks-flag-arc-sneakers_hero.png"),
            ("bks-flag-bloc-swim-trunks","bks-flag-bloc-swim-trunks_hero.png"),
            ("bks-flag-column-sneakers", "bks-flag-column-sneakers_hero.png"),
        ],
        "desc": "1) BKS Flag low-top sneakers with bold yellow-black geometric flag stripe pattern (main center). 2) BKS Flag swim trunks with colorful geometric color-block pattern in green-red-yellow-blue mosaic (secondary left). 3) BKS Flag low-top sneakers with vertical column stripes in blue-grey tones (secondary right).",
        "mood": "bold flag colors, graphic pop, geometric color-blocks",
    },
    "bks-origin": {
        "products": [
            ("folklore-field-windbreaker",  "folklore-field-windbreaker_hero.png"),
            ("folklore-arabesque-puffer",   "folklore-arabesque-puffer_hero.png"),
            ("folklore-bloom-sneakers",     "folklore-bloom-sneakers_hero.png"),
        ],
        "desc": "1) BKS Origin windbreaker jacket with vibrant folk floral pattern combining blue botanical flowers with orange-yellow geometric tiles (main center). 2) BKS Origin puffer jacket with dense ivory-grey arabesque/lacework pattern with folk border details (secondary left). 3) BKS Origin low-top sneakers with gold-blue botanical folk print (secondary right).",
        "mood": "folk art, botanical, floral-folk, earthy-blue-gold-green",
    },
}


def encode_image(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def generate_setstyle(handle: str, data: dict) -> bytes | None:
    """Call OpenAI gpt-image-1 with product reference images + setstyle prompt."""
    prompt = PROMPT_BASE.format(products_desc=data["desc"])
    prompt += f"\nCollection mood: {data['mood']}."

    # Build content array with reference images
    content = [{"type": "text", "text": prompt}]

    for folder, fname in data["products"]:
        img_path = BKSHERO / folder / fname
        if img_path.exists():
            b64 = encode_image(img_path)
            mime = "image/png" if fname.endswith(".png") else "image/jpeg"
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "high"},
            })

    # Use gpt-image-1 via responses API (image output)
    payload = {
        "model": "gpt-image-1",
        "input": content,
        "size": "1792x1024",
        "quality": "high",
        "n": 1,
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json",
    }

    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers=headers,
        json={"model": "gpt-image-1", "prompt": prompt, "size": "1536x1024", "quality": "high", "n": 1},
        timeout=120,
        verify=False,
    )

    if not r.ok:
        err = r.json().get("error", {})
        print(f"    gpt-image-1 attempt 1 failed ({r.status_code}): {err.get('message','?')[:120]}")
        print(f"    Retrying with quality=standard...")
        r2 = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json={"model": "gpt-image-1", "prompt": prompt, "size": "1536x1024", "quality": "standard", "n": 1},
            timeout=120,
            verify=False,
        )
        if not r2.ok:
            print(f"    FAILED: {r2.status_code} {r2.text[:200]}")
            return None
        result = r2.json()
    else:
        result = r.json()

    data_items = result.get("data", [])
    if not data_items:
        print("    No data in response")
        return None

    item = data_items[0]

    # Handle base64 or URL response
    if "b64_json" in item:
        return base64.b64decode(item["b64_json"])
    elif "url" in item:
        img_r = requests.get(item["url"], timeout=60, verify=False)
        return img_r.content if img_r.ok else None

    return None


# ─────────────────────────────────────────────────────────────────────────────
print("=" * 62)
print("BKS Setstyle Hero Generator — OpenAI gpt-image-1")
print("=" * 62)

generated = []
failed = []

for handle, data in COLLECTIONS.items():
    out_path = OUT_DIR / f"{handle}-hero.jpg"
    print(f"\n[{handle}]")
    print(f"  Products: {len(data['products'])} | Mood: {data['mood'][:50]}")
    print(f"  Generating...", end=" ", flush=True)

    try:
        img_bytes = generate_setstyle(handle, data)
        if img_bytes:
            out_path.write_bytes(img_bytes)
            size_kb = len(img_bytes) // 1024
            print(f"OK -> {out_path.name} ({size_kb}KB)")
            generated.append(handle)
        else:
            print("FAILED (no image data)")
            failed.append(handle)
    except Exception as e:
        print(f"ERROR: {e}")
        failed.append(handle)

    time.sleep(2)  # rate limit courtesy pause

print(f"\n{'=' * 62}")
print(f"Generated: {len(generated)}/8 | Failed: {len(failed)}")
if generated:
    print(f"Output: {OUT_DIR}")
    print("\nNext: python scripts/upload_setstyle_heroes.py --source setstyle_ai")
if failed:
    print(f"Failed: {', '.join(failed)}")
    print("Check OPENAI_API_KEY and gpt-image-1 access in your org.")
