"""
BKS — Printify Design Generator
Genera nuova artwork (pezza) per un prodotto Printify.

Pipeline:
  1. Carica il design template esistente (wonder_*.jpg scaricato da Printify)
  2. Invia a OpenAI images.edit con prompt stile BakAbo
  3. Salva la nuova artwork
  4. Opzionale: carica su Printify via /printify-update

Il modello del prodotto (cuciture, sagoma, blueprint) rimane invariato —
OpenAI modifica SOLO il design artwork sulla superficie.
"""
from __future__ import annotations

import base64, json, time
from pathlib import Path
from typing import Any

import requests, urllib3
urllib3.disable_warnings()

# Importa il DNA visivo dal generatore esistente
from ecommerce_automation.drone_shot_generator import (
    COLLECTION_STAGES,
    AI_CAMERA_SYSTEM,
)

# DNA visivo per collezione — armocromia-driven, nessuna base fissa
COLLECTION_DNA = {
    "hours":    "Gordon Willis chiaroscuro depth — Hopper late-night solitude, Klimt gold ornament, De Chirico metaphysical drama. Cool-neutral silver tones.",
    "glyph":    "Magritte impossible precision — Dalì dreamscape on Mondrian grid, Leonardo da Vinci hidden line. Amber-gold dominant, deep blacks.",
    "marker":   "Storaro Rembrandt warmth — Basquiat raw crown, Pollock gesture over old-master amber, Banksy stencil irony. Rust-orange dominant.",
    "riviera":  "Mediterranean golden naturalism — Seurat pointillist light, Matisse flat cutout, Gauguin tropical warmth. Warm teal accent.",
    "pulse":    "Deakins cold electric precision — Mondrian primary geometry, Kandinski synesthetic color, Keith Haring kinetic neon. Lavender and electric blue.",
    "token":    "Araki manga bold — Murakami superflat kawaii-darkness, Kaneko Ryuichi Japanese pop. Deep purple dominant, neon halo.",
    "flag":     "Warhol screen-print flat — Banksy stencil, Shepard Fairey propaganda graphic. Bold red, flat pop blocks.",
    "folklore": "Delli Colli rustic candle warmth — Bosch medieval micro-figure chaos, Mirò biomorphic symbols, Gauguin lush narrative. Forest green accent.",
}

DESIGNS_DIR = Path(__file__).parent.parent / "BAKABO_IMAGE_FACTORY_v1.1" / "output" / "printify_library" / "designs"
GENERATED_DIR = Path(__file__).parent.parent / "BAKABO_IMAGE_FACTORY_v1.1" / "output" / "generated"
BKS_DATABASE = Path("I:/BKS database")
BLUEPRINT_MAP_PATH = Path(__file__).parent / "blueprint_templates.json"

def _load_blueprint_map() -> dict:
    if BLUEPRINT_MAP_PATH.exists():
        return json.loads(BLUEPRINT_MAP_PATH.read_text(encoding="utf-8"))
    return {}

def find_local_template(blueprint_id: int | str | None, position: str = "") -> Path | None:
    """
    Cerca il PNG template locale in I:\\BKS database per blueprint_id.
    Restituisce None se posizione è in skip_positions, non trovato, o solo AI/PSD.
    """
    if not blueprint_id:
        return None
    bp_map = _load_blueprint_map()
    entry = bp_map.get(str(blueprint_id))
    if not entry or not entry.get("has_png"):
        return None
    # Salta posizioni etichetta
    skip = {s.lower().replace(" ", "_") for s in entry.get("skip_positions", [])}
    if position and position.lower().replace(" ", "_") in skip:
        return None
    folder = BKS_DATABASE / entry["folder"]
    if not folder.exists():
        return None
    png_areas = entry.get("png_per_area", {})
    # Cerca corrispondenza posizione (fuzzy match)
    if position:
        norm = position.lower().replace(" ", "_")
        for pos_key, rel_path in png_areas.items():
            if norm in pos_key or pos_key in norm:
                p = folder / rel_path
                if p.exists() and p.stat().st_size > 5000:
                    return p
    # Fallback: primo PNG disponibile
    for rel_path in png_areas.values():
        p = folder / rel_path
        if p.exists() and p.stat().st_size > 5000:
            return p
    return None

# Istruzioni per la generazione artwork
ARTWORK_DIRECTIVES: dict[str, str] = {
    "hours": (
        "Transform this all-over print design with BKS Hours collection aesthetic: "
        "dark urban brocade, gold-black architectural patterns, Edward Hopper contemplation energy. "
        "Maintain seamless tile structure and full surface coverage."
    ),
    "glyph": (
        "Transform this all-over print design with BKS Glyph collection aesthetic: "
        "proprietary BKS graphic alphabet, abstract symbols, geometric code fragments, "
        "high contrast gold-on-black or monochrome. Maintain seamless coverage."
    ),
    "marker": (
        "Transform this all-over print design with BKS Marker collection aesthetic: "
        "gestural brushstroke, urban drip and stroke, raw mark-making energy, "
        "cream-white base with bold gesture. Maintain seamless coverage."
    ),
    "riviera": (
        "Transform this all-over print design with BKS Riviera collection aesthetic: "
        "Mediterranean resort — sea teal, warm sand, coral, terracotta, "
        "fluid organic forms. Maintain seamless tile coverage."
    ),
    "pulse": (
        "Transform this all-over print design with BKS Pulse collection aesthetic: "
        "optical kinetic geometry — hexagonal grids, wave interference patterns, "
        "deep navy with lavender/white accent, movement implied. Maintain seamless coverage."
    ),
    "token": (
        "Transform this all-over print design with BKS Token collection aesthetic: "
        "pixel art and arcade grid — low-bit visual language, cyan-magenta-violet palette, "
        "digital tokens and icons. Maintain seamless coverage."
    ),
    "flag": (
        "Transform this all-over print design with BKS Flag collection aesthetic: "
        "pop-Dada color blocks — bold flat fields, graphic stencil shapes, "
        "pure white base with vivid accent. Maintain seamless coverage."
    ),
    "folklore": (
        "Transform this all-over print design with BKS Folklore collection aesthetic: "
        "invented folklore — naif illustration, organic figures, animal narratives, "
        "warm parchment tones with teal-green accents. Maintain seamless coverage."
    ),
}


def _build_design_prompt(collection: str, design_description: str = "",
                         material_context: str = "") -> str:
    stage    = COLLECTION_STAGES.get(collection, COLLECTION_STAGES["glyph"])
    directive = ARTWORK_DIRECTIVES.get(collection, ARTWORK_DIRECTIVES["glyph"])
    extra = f"Specific design direction: {design_description}. " if design_description else ""
    mat   = (f"Product material: {material_context}. "
             f"The artwork must be designed for this specific fabric — "
             f"honor texture, weight and drape characteristics. ") if material_context else ""

    return (
        f"BKS Studio wearable art — redesign the printed artwork on this all-over print canvas. "
        f"{directive} "
        f"{mat}"
        f"{extra}"
        f"Cinematic lighting reference for color mood: {stage['light_ref']}. "
        f"Collection visual DNA: {COLLECTION_DNA.get(collection, COLLECTION_DNA['glyph'])} "
        f"Collection accent color: {stage['accent']}. "
        f"Rules: maintain seamless tile format, full canvas coverage, "
        f"no text or typography, no BKS logo (handled separately), "
        f"no isolated figures that would look wrong when tiled, "
        f"photorealistic or highly detailed illustration quality."
    )


def generate_design_artwork(
    product_id: str,
    collection: str,
    handle: str,
    openai_api_key: str,
    design_description: str = "",
    template_path: Path | str | None = None,
    blueprint_id: int | str | None = None,
    position: str = "",
    output_dir: Path | str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Genera una nuova artwork per un prodotto Printify.
    Priorità template: 1) template_path esplicito, 2) template locale BKS database
    (per blueprint_id+position), 3) wonder_*/img-* scaricato da CDN, 4) genera da zero.
    """
    # Risolvi template: local BKS database > wonder_* CDN > nessuno
    template_source = "none"
    if template_path:
        template_path = Path(template_path)
        template_source = "explicit"
    if not template_path and blueprint_id:
        local_tpl = find_local_template(blueprint_id, position)
        if local_tpl:
            template_path = local_tpl
            template_source = f"local_bks_db/{local_tpl.name}"
    if not template_path:
        discovered = find_design_template(product_id, collection, handle)
        if discovered:
            template_path = discovered
            template_source = f"cdn_cache/{discovered.name}"

    prompt = _build_design_prompt(collection, design_description, material_context="")

    if output_dir is None:
        output_dir = GENERATED_DIR / collection / handle
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    out_jpg = output_dir / f"{handle}_design_new.jpg"
    out_txt = output_dir / f"{handle}_design_new_prompt.txt"
    out_txt.write_text(prompt, encoding="utf-8")

    if dry_run:
        print(f"  [dry-run] template: {template_source}")
        print(f"  [dry-run] prompt salvato ({len(prompt)} chars)")
        return {"status": "dry_run", "path": str(out_jpg), "prompt": prompt,
                "mode": "edit" if template_path else "generate", "template_source": template_source}

    hdrs = {"Authorization": f"Bearer {openai_api_key}"}

    if template_path:
        # Mode: images.edit — usa il design template come base
        template_path = Path(template_path)
        if not template_path.exists():
            return {"status": "error", "error": f"Template non trovato: {template_path}"}

        print(f"  Generando artwork via images.edit (template: {template_path.name})...")
        try:
            with open(template_path, "rb") as f:
                img_bytes = f.read()

            r = requests.post(
                "https://api.openai.com/v1/images/edits",
                headers={"Authorization": f"Bearer {openai_api_key}"},
                files={"image": (template_path.name, img_bytes, "image/jpeg")},
                data={
                    "model": "gpt-image-1",
                    "prompt": prompt,
                    "n": "1",
                    "size": "1024x1024",
                },
                timeout=120,
                verify=False,
            )
            r.raise_for_status()
            data   = r.json()
            b64img = data["data"][0].get("b64_json")
            if b64img:
                out_jpg.write_bytes(base64.b64decode(b64img))
            else:
                url = data["data"][0].get("url")
                out_jpg.write_bytes(requests.get(url, verify=False, timeout=60).content)

            size_kb = out_jpg.stat().st_size // 1024
            print(f"  OK artwork: {out_jpg.name} ({size_kb}KB) [template: {template_source}]")
            return {"status": "ok", "path": str(out_jpg), "prompt": prompt,
                    "mode": "edit", "size_kb": size_kb, "template_source": template_source}

        except Exception as e:
            print(f"  ERR images.edit: {e}")
            return {"status": "error", "error": str(e), "mode": "edit", "template_source": template_source}
    else:
        # Mode: images.generations — genera da zero con il prompt
        print(f"  Generando artwork via images.generations (nessun template)...")
        try:
            r = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={**hdrs, "Content-Type": "application/json"},
                json={
                    "model":   "gpt-image-1",
                    "prompt":  prompt,
                    "n":       1,
                    "size":    "1024x1024",
                    "quality": "high",
                    "output_format": "jpeg",
                },
                timeout=120,
                verify=False,
            )
            r.raise_for_status()
            data   = r.json()
            b64img = data["data"][0].get("b64_json")
            if b64img:
                out_jpg.write_bytes(base64.b64decode(b64img))
            else:
                url = data["data"][0].get("url")
                out_jpg.write_bytes(requests.get(url, verify=False, timeout=60).content)

            size_kb = out_jpg.stat().st_size // 1024
            print(f"  OK artwork: {out_jpg.name} ({size_kb}KB)")
            return {"status": "ok", "path": str(out_jpg), "prompt": prompt,
                    "mode": "generate", "size_kb": size_kb, "template_source": "none"}

        except Exception as e:
            print(f"  ERR images.generations: {e}")
            return {"status": "error", "error": str(e), "mode": "generate"}


LOGO_PATTERNS = ("logo", "log9", "log0", "sd0", "sd1", "sd11", "sd19",
                  "barra", "logo-base", "logo_hoodie", "logo z0")

def _is_logo_file(path: Path) -> bool:
    n = path.name.lower()
    return any(p in n for p in LOGO_PATTERNS) or path.stat().st_size < 5000

def find_design_template(product_id: str, collection: str, handle: str) -> Path | None:
    """
    Cerca il design template locale per un prodotto.
    Priorità: wonder_* → img-* → altri grandi → skip loghi/piccoli
    """
    for search_key in [handle, product_id]:
        d = DESIGNS_DIR / collection / search_key
        if not d.exists():
            continue
        all_files = [f for f in (list(d.glob("*_design_*.jpg")) + list(d.glob("*_design_*.png")))
                     if f.stat().st_size > 5000 and not _is_logo_file(f)]
        if not all_files:
            continue
        # Priorità 1: wonder_* (design originali Printify)
        wonder = [f for f in all_files if "wonder" in f.name.lower()]
        if wonder:
            return sorted(wonder, key=lambda f: f.stat().st_size, reverse=True)[0]
        # Priorità 2: img-* (AI generated, già di qualità)
        ai_gen = [f for f in all_files if f.name.startswith("img-")]
        if ai_gen:
            return sorted(ai_gen, key=lambda f: f.stat().st_size, reverse=True)[0]
        # Priorità 3: il file più grande (probabilmente il design principale)
        return sorted(all_files, key=lambda f: f.stat().st_size, reverse=True)[0]
    return None
