"""
BKS — AI Shot Generator (ex Drone Shot Generator)
Dopo approvazione design: genera foto prodotto via OpenAI.
Camera libera — dal pavimento a quota infinita. Set virtuale senza limiti fisici.
3 slot per prodotto:
  - hero_shot         : AI sceglie angolo/quota per impatto massimo design
  - editorial_scene   : scena cinematografica AI-directed, set virtuale
  - detail_atmosphere : close-up o flottante, texture design in primo piano

Output: BAKABO_IMAGE_FACTORY_v1.1/output/generated/{collection}/{handle}/
"""
from __future__ import annotations

import base64, json, time
from pathlib import Path
from typing import Any

# Set virtuali illimitati per collezione — fisica reale non richiesta
COLLECTION_STAGES: dict[str, dict[str, str]] = {
    "hours": {
        "environment": "Floating obsidian planes suspended in void, industrial warehouse at dusk with fog machines, "
                       "or abandoned brutalist cathedral — the AI chooses what creates maximum tension",
        "light_ref":   "Gordon Willis 'Prince of Darkness' style: dramatically underlit, near-black shadows, "
                       "single hard source from 30° above, no fill light — The Godfather darkness",
        "accent": "#C9B79C",
    },
    "glyph": {
        "environment": "Infinite digital black void with floating geometric solids, "
                       "or dark glass labyrinth with reflective floors — impossible architecture welcome",
        "light_ref":   "Dariusz Wolski high-contrast geometry: hard beams from above slicing through fog, "
                       "deep blacks, no ambient — Prometheus / Alien Covenant precision",
        "accent": "#C9B79C",
    },
    "marker": {
        "environment": "Palazzo with chalk-dust covered floors, artist studio with physically impossible geometry, "
                       "or infinite white canvas that dissolves at the edges",
        "light_ref":   "Vittorio Storaro Rembrandt warmth: rich amber from one side, warm fill opposite, "
                       "painterly golden-brown shadows — Apocalypse Now / The Last Emperor",
        "accent": "#0A0A0A",
    },
    "riviera": {
        "environment": "Mediterranean terrace floating above the sea, crystal-clear water surface shot from below, "
                       "or ancient travertine ruins at golden hour with impossible scale",
        "light_ref":   "Carlo Di Palma bleached Mediterranean: overexposed golden sky, rich warm shadows, "
                       "sea light bounce — Blow-Up / Red Desert naturalism",
        "accent": "#2A8B85",
    },
    "pulse": {
        "environment": "Cyberpunk Tokyo arcade at 3am, neon-lit virtual grid dissolving into void, "
                       "or underground rave space with stroboscopic geometry",
        "light_ref":   "Roger Deakins cold neon: blue-green practical sources, deep amber shadows, "
                       "high contrast electric — Blade Runner 2049 / Sicario",
        "accent": "#C9B79C",
    },
    "token": {
        "environment": "80s arcade retrowave dimension, pixel art universe made physical, "
                       "or retro-futurist monorail station with neon grid floor",
        "light_ref":   "Dean Cundey retro neon: warm amber back-light, cool blue fill, "
                       "strong rim on product edges — Back to the Future / Tron legacy",
        "accent": "#C9B79C",
    },
    "flag": {
        "environment": "Infinity white room dissolving at edges, color-gradient sky with no horizon, "
                       "or white cube gallery with gravity-defying product arrangement",
        "light_ref":   "Emmanuel Lubezki diffused naturalism: flat overcast dome light, no hard shadows, "
                       "pure whites never blown — The Revenant / Children of Men",
        "accent": "#0A0A0A",
    },
    "folklore": {
        "environment": "Enchanted forest clearing at dusk, watercolor-painted impossible landscape, "
                       "or ancient stone courtyard with climbing vines and dust particles",
        "light_ref":   "Tonino Delli Colli rustic chiaroscuro: warm candle-orange fill, deep natural shadows, "
                       "dusty haze in air — Pasolini / Il nome della rosa atmosphere",
        "accent": "#2A8B85",
    },
}

# Sistema camera BKS — Sony FX3 su rig virtuale, libertà totale
AI_CAMERA_SYSTEM = (
    "Sony FX3 on virtual motorized rig — altitude 0m to unlimited, angle -90° to +90°, "
    "any focal length 14mm to 200mm chosen by AI. Virtual set: no physical constraints. "
    "The AI photographer decides camera position, lens, depth of field, and motion feel."
)

# BakAbo base visual DNA — German Expressionism layer presente in ogni scatto
BAKABO_BASE_LAYER = (
    "Underlying visual DNA: German Expressionist cinema (1920s) — "
    "strong graphic shadow geometry that doesn't obey physics, angular light as psychological force, "
    "shadows as design elements, Metropolis-era visual drama, "
    "the menace and the beautiful co-existing in one frame."
)

SLOT_SPECS: dict[str, dict[str, str]] = {
    "hero_shot": {
        "directive": (
            "AI selects the single most powerful angle for this product. "
            "Ground level to any altitude — if the product looks best at 5cm flat on concrete, do that. "
            "If it needs a dramatic overhead, do that. The product is the hero of a luxury campaign. "
            "One product. One perfect image. No compromise."
        ),
        "style":    "Magazine cover quality. Product as wearable art object. Design fully readable. "
                    "Think Visionaire, System Magazine, 032c. Light from the collection cinema reference.",
        "size":     "1024x1024",
    },
    "editorial_scene": {
        "directive": (
            "AI-directed cinematic scene on virtual set. Camera free in 3D space. "
            "Set can be physically impossible — floating surfaces, impossible scale, virtual environments. "
            "1 to 3 products, AI decides composition like a film director. "
            "Movement and tension implied in the still. Collection mood in every pixel."
        ),
        "style":    "Film still quality — could be a frame from a luxury fashion film. "
                    "Dazed & Confused / i-D editorial level. "
                    "Negative space for typographic overlay on right third of frame.",
        "size":     "1536x1024",
    },
    "detail_atmosphere": {
        "directive": (
            "Extreme close or floating perspective chosen by AI — could be 2cm from the fabric, "
            "or a dramatic foreshortening from below. Focus on design texture, material quality, "
            "pattern detail. Camera altitude from floor level upward — AI decides. "
            "Atmosphere, mood, collection world in the background (blurred or abstract)."
        ),
        "style":    "Tactile luxury — you can almost feel the material. "
                    "Shallow depth of field revealing pattern and texture. "
                    "Background: collection environment abstract and atmospheric.",
        "size":     "1536x1024",
    },
}


def _build_prompt(
    product_title: str,
    product_type: str,
    collection: str,
    slot: str,
    design_description: str = "",
) -> str:
    stage = COLLECTION_STAGES.get(collection, COLLECTION_STAGES["glyph"])
    spec  = SLOT_SPECS[slot]
    col_mood = {
        "hours":    "dark urban luxury, brocade gold-black pattern",
        "glyph":    "pure black void, geometric coded symbols",
        "marker":   "cream white expressionist, gestural brush strokes",
        "riviera":  "warm sand Mediterranean, teal sea accents",
        "pulse":    "deep navy kinetic, optical hexagon pattern",
        "token":    "near-black arcade, pixel neon",
        "flag":     "pure white pop, color block stencil",
        "folklore": "warm parchment organic, naif illustration",
    }.get(collection, collection)

    design_line = f"Design artwork on product: {design_description}. " if design_description else ""

    return (
        f"AI-directed luxury fashion photography for BKS Studio wearable art brand. "
        f"Product: {product_title} ({product_type}), BKS {collection.title()} collection — {col_mood}. "
        f"{design_line}"
        f"Camera system: {AI_CAMERA_SYSTEM} "
        f"Camera directive for this shot: {spec['directive']} "
        f"Virtual set environment: {stage['environment']}. "
        f"Cinematic lighting: {stage['light_ref']}. "
        f"Brand visual DNA: {BAKABO_BASE_LAYER} "
        f"Visual style target: {spec['style']} "
        f"Absolute rules: product shape and proportions 100% faithful, design pattern not distorted, "
        f"no invented text or logos on product, no extra limbs or people, "
        f"photorealistic luxury campaign quality, accent color {stage['accent']}."
    )


def generate_drone_shots(
    product_title:  str,
    product_type:   str,
    collection:     str,
    handle:         str,
    openai_api_key: str,
    design_description: str = "",
    slots: list[str] | None = None,
    output_base: Path | None = None,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """
    Genera gli shot drone per un prodotto approvato.
    Ritorna lista di {slot, path, prompt, status}.
    """
    import requests, urllib3
    urllib3.disable_warnings()

    if slots is None:
        slots = list(SLOT_SPECS.keys())

    if output_base is None:
        output_base = Path(__file__).parent.parent / "BAKABO_IMAGE_FACTORY_v1.1" / "output" / "generated"

    out_dir = output_base / collection / handle
    out_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    hdrs = {"Authorization": f"Bearer {openai_api_key}", "Content-Type": "application/json"}

    for slot in slots:
        prompt  = _build_prompt(product_title, product_type, collection, slot, design_description)
        spec    = SLOT_SPECS[slot]
        w, h    = spec["size"].split("x")
        out_jpg = out_dir / f"{handle}-drone-{slot}.jpg"
        out_txt = out_dir / f"{handle}-drone-{slot}_prompt.txt"

        # Salva prompt sempre
        out_txt.write_text(prompt, encoding="utf-8")

        if dry_run:
            results.append({"slot": slot, "path": str(out_jpg), "prompt": prompt, "status": "dry_run"})
            print(f"  [dry-run] {slot}: prompt salvato ({len(prompt)} chars)")
            continue

        print(f"  Generando {slot} ({spec['size']})...")
        try:
            r = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=hdrs,
                json={
                    "model":   "gpt-image-1",
                    "prompt":  prompt,
                    "n":       1,
                    "size":    spec["size"],
                    "quality": "high",
                    "output_format": "jpeg",
                },
                timeout=120,
                verify=False,
            )
            r.raise_for_status()
            data    = r.json()
            b64_img = data["data"][0].get("b64_json") or data["data"][0].get("url")

            if data["data"][0].get("b64_json"):
                out_jpg.write_bytes(base64.b64decode(b64_img))
            else:
                # URL-based response (dall-e-3)
                img_r = requests.get(b64_img, timeout=60, verify=False)
                out_jpg.write_bytes(img_r.content)

            size_kb = out_jpg.stat().st_size // 1024
            results.append({"slot": slot, "path": str(out_jpg), "prompt": prompt, "status": "ok", "size_kb": size_kb})
            print(f"  OK {slot}: {out_jpg.name} ({size_kb}KB)")

        except Exception as e:
            results.append({"slot": slot, "path": str(out_jpg), "prompt": prompt, "status": "error", "error": str(e)})
            print(f"  ERR {slot}: {e}")

        time.sleep(1)  # rate limit

    # Manifest
    manifest_path = out_dir / "manifest_drone.json"
    manifest_path.write_text(
        json.dumps({"product": product_title, "handle": handle, "collection": collection,
                    "shots": results, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                   indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return results
