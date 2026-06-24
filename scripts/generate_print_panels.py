"""BKS Print Panel Generator — OpenAI gpt-image-1.

Genera pezze di produzione AOP (seamless pattern tiles) per ogni collezione.
Ogni tile è pronto per upload manuale su Printify come print file.

Output: output/printify_panels/{collection}/{collection}-{product_type}-v{n}.png
Metadata: output/printify_panels/{collection}/metadata.json

VINCOLO: solo product type realizzabili ATTUALMENTE su Printify BKS.
NON generare per tipi non ancora in catalogo.

Workflow:
  1. python scripts/generate_print_panels.py --collection bks-hours
  2. Controlla l'output in output/printify_panels/bks-hours/
  3. Carica su Printify manualmente → Editor prodotto → Upload print file
"""
from __future__ import annotations
import os, sys, json, base64, argparse, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pathlib import Path
from datetime import date

try:
    import requests, urllib3
    urllib3.disable_warnings()
except ImportError:
    print("pip install requests"); sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
if not OPENAI_KEY:
    print("ERROR: OPENAI_API_KEY not set"); sys.exit(1)

# ── Product types realizzabili ora in Printify ────────────────────────────────
PRINTIFY_TYPES = [
    "puffer-jacket",
    "windbreaker",
    "tee",
    "swim-trunks",
    "sneakers",
    "hoodie",
    "hawaiian-shirt",
    "racerback-dress",
    "lounge-pants",
    "backpack",
    "athletic-shorts",
    "travel-bag",
    "flip-flops",
    "beach-towel",
    "one-piece-swimsuit",
]

# ── Collection DNA — mood, colori dominanti, pattern mood ────────────────────
COLLECTIONS: dict[str, dict] = {
    "bks-hours": {
        "label": "BKS Hours",
        "mood": "urban stillness, measured geometry, architectural photography, monochrome",
        "palette": "slate grey, warm black, off-white, subtle blue-grey",
        "pattern_concept": "architectural grid lines, suspended geometric figures, subtle B&W tonal tiles",
        "accent": "#c8c4be",
    },
    "bks-glyph": {
        "label": "BKS Glyph",
        "mood": "constructed graphic signs, dense calligraphic marks, ancient code",
        "palette": "deep maroon, gold-orange, sandy tan, dark ink",
        "pattern_concept": "dense flowing calligraphic glyphs, overlapping ancient script marks, layered gold on dark field",
        "accent": "#d4a030",
    },
    "bks-marker": {
        "label": "BKS Marker",
        "mood": "gestural motion, brushstroke energy, urban mark-making",
        "palette": "rust orange, earthy red-brown, black ink, warm cream",
        "pattern_concept": "bold gestural brushstrokes, marker tag diagonals, layered ink-wash motion",
        "accent": "#c04418",
    },
    "bks-riviera": {
        "label": "BKS Riviera",
        "mood": "Mediterranean coastal geometry, mosaic tile, resort atmosphere",
        "palette": "teal, Mediterranean blue, sandy ochre, warm white",
        "pattern_concept": "mosaic diamond tiles, argyle on teal ground, coastal blue-beige geometric repeat",
        "accent": "#0ca898",
    },
    "bks-pulse": {
        "label": "BKS Pulse",
        "mood": "optical movement, kinetic wave fields, geometric rhythm",
        "palette": "purple, violet, orange-red, lavender",
        "pattern_concept": "fluid wave arcs, optical interference patterns, concentric chord shapes in purple-violet",
        "accent": "#8888cc",
    },
    "bks-token": {
        "label": "BKS Token",
        "mood": "digital objects, pixel arcade, encoded grid",
        "palette": "deep purple, grey-beige pixel mosaic, dark backgrounds",
        "pattern_concept": "pixel mosaic grid, arcade score sprites, digital circuit fragment tiles",
        "accent": "#9828d8",
    },
    "bks-flag": {
        "label": "BKS Flag",
        "mood": "bold graphic fields, pop-collage color blocks, strong geometry",
        "palette": "yellow, black, red, green, blue — bold primary pop palette",
        "pattern_concept": "bold color-block rectangles, flag-stripe diagonals, graphic mosaic in bold primaries",
        "accent": "#c82020",
    },
    "bks-origin": {
        "label": "BKS Origin",
        "mood": "invented narrative folk art, botanical, figurative naif",
        "palette": "earthy blue-green, warm gold, folk red, ivory",
        "pattern_concept": "dense folk botanical motifs, folk arabesque lacework, figurative naif repeat in blue-gold-ivory",
        "accent": "#489808",
    },
}

PROMPT_TEMPLATE = """Seamless repeating all-over-print (AOP) pattern tile for textile production.
Collection: {label}
Visual mood: {mood}
Color palette: {palette}
Pattern concept: {pattern_concept}

Technical requirements:
- The pattern MUST be perfectly seamless (tiles edge-to-edge with no visible seam)
- Square format, fills the entire frame — no borders, no framing, no white margins
- High visual density, suitable for garment printing
- NO human figures, NO text, NO logos, NO brand marks
- Clean repeating motif, suitable for: jackets, swim trunks, sneakers, shirts
- Flat lay graphic aesthetic, print-production ready
- Output is the PATTERN TILE ONLY — not a product mockup"""


def generate_panel(collection_handle: str, variant: int = 1) -> bytes | None:
    if collection_handle not in COLLECTIONS:
        print(f"  Unknown collection: {collection_handle}")
        return None
    col = COLLECTIONS[collection_handle]
    prompt = PROMPT_TEMPLATE.format(**col)

    HDR = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}

    # Try high quality first
    for quality in ("high", "standard"):
        r = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=HDR,
            json={"model": "gpt-image-1", "prompt": prompt,
                  "size": "1024x1024", "quality": quality, "n": 1},
            timeout=120, verify=False,
        )
        if r.ok:
            item = r.json().get("data", [{}])[0]
            if "b64_json" in item:
                return base64.b64decode(item["b64_json"])
            elif "url" in item:
                rr = requests.get(item["url"], timeout=60, verify=False)
                return rr.content if rr.ok else None
        else:
            err = r.json().get("error", {}).get("message", "?")[:100]
            print(f"    quality={quality} failed: {err}")
    return None


def main():
    parser = argparse.ArgumentParser(description="BKS Print Panel Generator")
    parser.add_argument("--collection", default="all",
                        help="Collection handle (bks-hours, bks-glyph, ...) or 'all'")
    parser.add_argument("--variants", type=int, default=1,
                        help="Number of variants to generate (1-3)")
    args = parser.parse_args()

    targets = list(COLLECTIONS.keys()) if args.collection == "all" else [args.collection]
    today = date.today().strftime("%Y-%m-%d")

    print("=" * 62)
    print("BKS Print Panel Generator — gpt-image-1")
    print(f"Target: {', '.join(targets)}")
    print(f"Variants per collection: {args.variants}")
    print("=" * 62)

    total_ok = 0
    for handle in targets:
        col = COLLECTIONS.get(handle)
        if not col:
            print(f"\n[SKIP] {handle} — not in COLLECTIONS dict"); continue

        out_dir = ROOT / "output" / "printify_panels" / handle
        out_dir.mkdir(parents=True, exist_ok=True)

        meta_path = out_dir / "metadata.json"
        meta: list[dict] = json.loads(meta_path.read_text()) if meta_path.exists() else []

        print(f"\n[{handle}] {col['label']}")
        print(f"  Mood: {col['mood'][:60]}")

        for v in range(1, args.variants + 1):
            fname = f"{handle}-panel-{today}-v{v}.png"
            out_path = out_dir / fname
            if out_path.exists():
                print(f"  v{v}: already exists — skip"); continue

            print(f"  v{v}: generating...", end=" ", flush=True)
            img_bytes = generate_panel(handle, v)
            if img_bytes:
                out_path.write_bytes(img_bytes)
                size_kb = len(img_bytes) // 1024
                print(f"OK  {fname}  ({size_kb}KB)")
                meta.append({
                    "file": fname,
                    "collection": handle,
                    "label": col["label"],
                    "date": today,
                    "variant": v,
                    "size_kb": size_kb,
                    "status": "generated",
                    "printify_upload": None,
                    "approved": False,
                    "printify_types": PRINTIFY_TYPES,
                })
                total_ok += 1
                meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
            else:
                print("FAILED")
            time.sleep(3)

    print(f"\n{'=' * 62}")
    print(f"Generated: {total_ok} panels")
    print(f"Output: output/printify_panels/")
    print("\nNext steps:")
    print("  1. Review generated panels in each collection folder")
    print("  2. Mark approved: True in metadata.json")
    print("  3. Upload to Printify → Product editor → Upload print file")
    print("  4. (Future) Automate upload via Make.com webhook")


if __name__ == "__main__":
    main()
