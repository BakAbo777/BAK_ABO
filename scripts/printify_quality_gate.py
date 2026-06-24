"""BKS Quality Gate — Printify texture analysis + OpenAI regeneration pipeline.

Per ogni prodotto nel gap (published Printify, assente da Shopify):
  1. Fetch immagine mockup dal prodotto Printify
  2. Analisi GPT-4o Vision → score BKS 0-25
  3. Score >= 21 → flag "approved" (pronto per sync Shopify manuale)
  4. Score <  21 → gpt-image-1 ricrea texture → upload libreria Printify

Esclusi: Boho Beach Cloth (bp=1006), Duffel Bag (bp=372) — originali BAK ABO non da pubblicare.

Usage:
  python scripts/printify_quality_gate.py [--dry-run] [--limit N]
"""
from __future__ import annotations
import os, sys, json, base64, time, argparse, urllib3
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
urllib3.disable_warnings()
import requests

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

PRINTIFY_TOKEN = os.environ["PRINTIFY_API_TOKEN"]
PRINTIFY_SHOP  = os.environ["PRINTIFY_SHOP_ID"]
OPENAI_KEY     = os.environ["OPENAI_API_KEY"]

P_HDR  = {"Authorization": f"Bearer {PRINTIFY_TOKEN}"}
OA_HDR = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
PKW    = {"headers": P_HDR, "timeout": 20, "verify": False}

# Blueprint IDs to SKIP — originali BAK ABO, non da pubblicare su bakabo.club
SKIP_BLUEPRINTS = {1006, 372}

# Collection name → handle mapping
COLLECTION_MAP = {
    "hours":   "bks-hours",
    "glyph":   "bks-glyph",
    "marker":  "bks-marker",
    "riviera": "bks-riviera",
    "pulse":   "bks-pulse",
    "token":   "bks-token",
    "flag":    "bks-flag",
    "origin":  "bks-origin",
    "folklore":"bks-origin",  # old name → origin
}

COLLECTION_DNA = {
    "bks-hours":   {"mood": "urban stillness, measured geometry, architectural monochrome",
                    "palette": "slate grey, warm black, off-white, blue-grey",
                    "pattern": "architectural grid lines, suspended geometric figures, subtle B&W tonal tiles"},
    "bks-glyph":   {"mood": "constructed graphic signs, dense calligraphic marks, ancient code",
                    "palette": "deep maroon, gold-orange, sandy tan, dark ink",
                    "pattern": "dense flowing calligraphic glyphs, overlapping ancient script marks, layered gold on dark"},
    "bks-marker":  {"mood": "gestural motion, brushstroke energy, urban mark-making",
                    "palette": "rust orange, earthy red-brown, black ink, warm cream",
                    "pattern": "bold gestural brushstrokes, marker tag diagonals, layered ink-wash motion"},
    "bks-riviera": {"mood": "Mediterranean coastal geometry, mosaic tile, resort atmosphere",
                    "palette": "teal, Mediterranean blue, sandy ochre, warm white",
                    "pattern": "mosaic diamond tiles, coastal blue-beige geometric repeat"},
    "bks-pulse":   {"mood": "optical movement, kinetic wave fields, geometric rhythm",
                    "palette": "purple, violet, orange-red, lavender",
                    "pattern": "fluid wave arcs, optical interference patterns, concentric chord shapes"},
    "bks-token":   {"mood": "digital objects, pixel arcade, encoded grid",
                    "palette": "deep purple, grey-beige pixel mosaic, dark backgrounds",
                    "pattern": "pixel mosaic grid, arcade score sprites, digital circuit fragment tiles"},
    "bks-flag":    {"mood": "bold graphic fields, pop-collage color blocks, strong geometry",
                    "palette": "yellow, black, red, green, blue — bold primary pop palette",
                    "pattern": "bold color-block rectangles, flag-stripe diagonals, graphic mosaic"},
    "bks-origin":  {"mood": "invented narrative folk art, botanical, naif storytelling motifs",
                    "palette": "earthy blue-green, warm gold, folk red, ivory",
                    "pattern": "dense folk botanical motifs, folk arabesque lacework, storybook character repeat tiles"},
}

SCORE_PROMPT = """Rate this repeating graphic pattern tile on 5 qualities. Use integers 0-5 for each.

- seamless: does it tile seamlessly (no visible seams or edges)?
- style: does it match this aesthetic — {mood} — colors {palette}?
- density: is the graphic coverage dense (full coverage, no large blank areas)?
- clean: is it free of text overlays and watermarks?
- quality: overall graphic originality and visual appeal?

Respond with ONLY this JSON (no other text):
{{"seamless": 4, "style": 3, "density": 5, "clean": 5, "quality": 4}}"""


def detect_collection(title: str) -> str:
    title_lower = title.lower()
    for keyword, handle in COLLECTION_MAP.items():
        if keyword in title_lower:
            return handle
    return "bks-origin"  # fallback


def get_product_image(printify_id: str) -> str | None:
    """Return the print tile URL (actual texture, no model/person) from a Printify product.

    Uses print_areas[0].placeholders[0].images[0].src — the raw S3 print file.
    Falls back to product images[] only if print_areas not available.
    """
    r = requests.get(f"https://api.printify.com/v1/shops/{PRINTIFY_SHOP}/products/{printify_id}.json", **PKW)
    if not r.ok:
        return None
    d = r.json()
    # Primary: actual print tile (no human models, just the pattern)
    try:
        tile_src = d["print_areas"][0]["placeholders"][0]["images"][0].get("src")
        if tile_src:
            return tile_src
    except (KeyError, IndexError):
        pass
    # Fallback: mockup image
    imgs = d.get("images", [])
    return imgs[0]["src"] if imgs else None


_FALLBACK_PROMPT = (
    'Score this graphic pattern on 5 qualities (integers 0-5 each). '
    'Reply ONLY with JSON: {{"seamless":4,"style":4,"density":4,"clean":5,"quality":4}}'
)


def _call_vision(data_url: str, prompt: str) -> str:
    """Single GPT-4o vision call. Returns content string (may be empty on refusal)."""
    payload = {
        "model": "gpt-4o",
        "max_tokens": 150,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": data_url, "detail": "low"}},
        ]}],
    }
    r = requests.post("https://api.openai.com/v1/chat/completions",
                      headers=OA_HDR, json=payload, timeout=40, verify=False)
    if not r.ok:
        return ""
    choices = r.json().get("choices") or []
    return ((choices[0].get("message") or {}).get("content") or "").strip()


def _parse_score_content(content: str) -> dict | None:
    """Parse JSON score from GPT-4o content string. Returns None if unparseable."""
    start = content.find("{")
    end   = content.rfind("}") + 1
    if start == -1:
        return None
    try:
        parsed = json.loads(content[start:end])
        if "style" in parsed:
            parsed["dna"] = parsed.pop("style")
        if "quality" in parsed:
            parsed["artistic"] = parsed.pop("quality")
        axes = ["seamless", "dna", "density", "clean", "artistic"]
        total = sum(int(parsed.get(k, 0)) for k in axes)
        parsed["total"] = total
        parsed["verdict"] = "pass" if total >= 21 else "fail"
        parsed.setdefault("note", "")
        return parsed
    except Exception:
        return None


def score_image(image_url: str, collection: str) -> dict:
    """Score a texture image via GPT-4o Vision. Downloads image first, sends as base64.
    Retries with a shorter fallback prompt if the main prompt gets refused.
    """
    dna = COLLECTION_DNA.get(collection, COLLECTION_DNA["bks-origin"])
    main_prompt = SCORE_PROMPT.format(**dna)

    try:
        img_r = requests.get(image_url, timeout=20, verify=False)
        if not img_r.ok:
            return {"total": -1, "verdict": "error", "note": f"image download failed {img_r.status_code}"}
        img_b64 = base64.b64encode(img_r.content).decode()
        mime = img_r.headers.get("Content-Type", "image/jpeg").split(";")[0]
        data_url = f"data:{mime};base64,{img_b64}"
    except Exception as e:
        return {"total": -1, "verdict": "error", "note": f"download error: {str(e)[:60]}"}

    # Attempt 1: main prompt
    content = _call_vision(data_url, main_prompt)
    result = _parse_score_content(content)
    if result:
        return result

    # Attempt 2: fallback (shorter, neutral prompt)
    time.sleep(1)
    content2 = _call_vision(data_url, _FALLBACK_PROMPT)
    result2 = _parse_score_content(content2)
    if result2:
        result2["note"] = "(fallback prompt) " + result2.get("note", "")
        return result2

    # Both attempts refused — treat as fail (needs regeneration) not error
    note = content2 if content2 else content
    return {"total": 10, "verdict": "fail", "note": f"[GPT refused, auto-regen] {note[:80]}"}


def generate_texture(collection: str) -> bytes | None:
    """Generate new AOP tile via gpt-image-1."""
    dna = COLLECTION_DNA.get(collection, COLLECTION_DNA["bks-origin"])
    prompt = (
        f"Seamless repeating all-over-print (AOP) pattern tile for textile production. "
        f"Collection: {collection}. Mood: {dna['mood']}. Palette: {dna['palette']}. "
        f"Pattern: {dna['pattern']}. "
        "Must be perfectly seamless, square, fills entire frame, no borders, no text, no logos, "
        "no human figures. High density, suitable for garment printing. Flat lay graphic aesthetic."
    )
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers=OA_HDR,
        json={"model": "gpt-image-1", "prompt": prompt,
              "size": "1024x1024", "quality": "high", "n": 1},
        timeout=120, verify=False,
    )
    if not r.ok:
        print(f"    gpt-image-1 error: {r.text[:100]}")
        return None
    item = r.json().get("data", [{}])[0]
    if "b64_json" in item:
        return base64.b64decode(item["b64_json"])
    elif "url" in item:
        rr = requests.get(item["url"], timeout=60, verify=False)
        return rr.content if rr.ok else None
    return None


def upload_to_printify_library(img_bytes: bytes, filename: str) -> dict | None:
    """Upload image to Printify uploads library. Returns upload record."""
    b64 = base64.b64encode(img_bytes).decode()
    r = requests.post(
        "https://api.printify.com/v1/uploads/images.json",
        headers=P_HDR,
        json={"file_name": filename, "contents": b64},
        timeout=60, verify=False,
    )
    if r.ok:
        return r.json()
    print(f"    Upload error: {r.status_code} {r.text[:120]}")
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Score only, no generation/upload")
    parser.add_argument("--limit", type=int, default=0, help="Max products to process (0=all)")
    args = parser.parse_args()

    # Load gap report
    gap_path = ROOT / "output" / "printify_gap_report.json"
    if not gap_path.exists():
        print("ERROR: run printify_shopify_gap.py first"); sys.exit(1)
    gap_data = json.loads(gap_path.read_text(encoding="utf-8"))
    gap = [g for g in gap_data["gap"] if g["blueprint_id"] not in SKIP_BLUEPRINTS]
    if args.limit:
        gap = gap[:args.limit]

    print("=" * 62)
    print("BKS Quality Gate — Printify texture analysis")
    print(f"Products to process: {len(gap)}  dry-run={args.dry_run}")
    print("=" * 62)

    results = []
    approved, regenerated, errors = 0, 0, 0
    today = datetime.now().strftime("%Y-%m-%d")

    for i, prod in enumerate(gap, 1):
        pid   = prod["printify_id"]
        title = prod["title"]
        bp    = prod["blueprint_id"]
        col   = detect_collection(title)
        short = title[:45].encode("ascii", "replace").decode()

        print(f"\n[{i:03d}/{len(gap)}] {short}")
        print(f"  collection={col}  bp={bp}")

        # 1. Get image
        img_url = get_product_image(pid)
        if not img_url:
            print("  ERROR: no image found")
            results.append({**prod, "collection": col, "score": -1, "verdict": "error", "note": "no image", "action": "skip"})
            errors += 1
            continue

        # 2. Score
        print(f"  Scoring via GPT-4o... ", end="", flush=True)
        score = score_image(img_url, col)
        total = score.get("total", -1)
        verdict = score.get("verdict", "error")
        note  = score.get("note", "")
        print(f"score={total}/25  verdict={verdict}")
        print(f"  {note}")

        action = "approved" if total >= 21 else ("regenerated" if total >= 0 else "error")
        upload_id = None

        # 3. Regenerate if below threshold
        if total < 21 and total >= 0 and not args.dry_run:
            print(f"  Score {total}<21 — regenerating via gpt-image-1...")
            img_bytes = generate_texture(col)
            if img_bytes:
                fname = f"bks-{col}-regen-{today}-{i:03d}.png"
                print(f"  Uploading {fname} ({len(img_bytes)//1024}KB) to Printify library...")
                upload = upload_to_printify_library(img_bytes, fname)
                if upload:
                    upload_id = upload.get("id")
                    print(f"  Upload OK — id={upload_id}")
                    action = "regenerated"
                    regenerated += 1
                    # Save locally too
                    local_out = ROOT / "output" / "printify_regen" / col
                    local_out.mkdir(parents=True, exist_ok=True)
                    (local_out / fname).write_bytes(img_bytes)
                else:
                    action = "regen_upload_failed"
                    errors += 1
            else:
                action = "regen_failed"
                errors += 1
            time.sleep(2)
        elif total >= 21:
            approved += 1

        results.append({
            **prod,
            "collection": col,
            "score_total": total,
            "score_detail": {k: v for k, v in score.items() if k not in ("total", "verdict", "note")},
            "verdict": verdict,
            "note": note,
            "action": action,
            "printify_upload_id": upload_id,
        })

        # Save progress after each product
        out_path = ROOT / "output" / "printify_quality_results.json"
        out_path.write_text(json.dumps({
            "generated": datetime.now().isoformat()[:19],
            "dry_run": args.dry_run,
            "processed": i, "total": len(gap),
            "approved": approved, "regenerated": regenerated, "errors": errors,
            "results": results,
        }, indent=2, ensure_ascii=False), encoding="utf-8")

        time.sleep(1.5)

    print(f"\n{'='*62}")
    print(f"RISULTATO:")
    print(f"  Approved (score>=21): {approved}")
    print(f"  Regenerated + uploaded: {regenerated}")
    print(f"  Errors: {errors}")
    print(f"  Report: output/printify_quality_results.json")
    print(f"  Regen tiles: output/printify_regen/")

    # Print approved list
    approved_list = [r for r in results if r["action"] == "approved"]
    if approved_list:
        print(f"\nPronti per sync Shopify ({len(approved_list)}):")
        for r in approved_list:
            t = r["title"][:50].encode("ascii", "replace").decode()
            print(f"  [{r['score_total']:2d}/25]  {t}")


if __name__ == "__main__":
    main()
