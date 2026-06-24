"""
Carica il vocabolario artistico BakAbo in Cloudflare KV.
Il Worker legge questi dati per arricchire ogni prompt generativo.

KV keys scritte:
  style:bakabo:artist_map          -> dict collection -> [artists + visual_key]
  style:bakabo:textile_prompts     -> list prompt template textile puri
  style:bakabo:product_affinity    -> dict product_type -> [artist, technique, prompt_fragment]
  style:bakabo:version             -> timestamp ultimo training

Uso:
    python scripts/_train_worker_style.py
    python scripts/_train_worker_style.py --dry-run
"""
import json, sys
from datetime import datetime
from pathlib import Path

import requests, urllib3
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

CF_ACCOUNT = "e796d289f744035eee2641e853d8a5af"
CF_TOKEN   = env.get("CLOUDFLARE_API_TOKEN", "")
KV_NS_ID   = "8f6b1e4accae47949b2960735d270a3a"

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()


def kv_put(key: str, value) -> bool:
    if args.dry_run:
        print(f"  [dry-run] KV PUT {key} ({len(json.dumps(value))} bytes)")
        return True
    r = requests.put(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/storage/kv/namespaces/{KV_NS_ID}/values/{key}",
        headers={"Authorization": f"Bearer {CF_TOKEN}"},
        data=json.dumps(value, ensure_ascii=False),
        timeout=20, verify=False,
    )
    ok = r.ok
    print(f"  KV PUT {key}: {'OK' if ok else 'ERR ' + r.text[:100]}")
    return ok


# ── 1. ARTIST → COLLECTION AFFINITY MAP ────────────────────────────────────
artist_map = {
    "hours": {
        "artists": ["Edward Hopper", "Giorgio De Chirico", "Goyard", "Gustav Klimt", "Coco Chanel", "Modigliani"],
        "keywords": "urban solitude, architectural geometry, gold ornament, late-night light, long shadows, empty piazzas, chevron luxury, cool structured elegance",
        "textile_technique": "brocade weaving, gold-black geometric, architectural grid overlay, contemplative scene fragments",
    },
    "glyph": {
        "artists": ["René Magritte", "Salvador Dalì", "Matisse", "Leonardo da Vinci", "Barbara Kruger"],
        "keywords": "impossible logic, surreal symbol systems, greek alphabet fragments, technical precision, text as image, bourgeois surrealism",
        "textile_technique": "micro symbol weaving, thirteen repeating icons, impossible object pattern, flat surreal tile",
    },
    "marker": {
        "artists": ["Jackson Pollock", "Banksy", "SAMO / Basquiat", "Raymond Pettibon", "A1one"],
        "keywords": "drip gesture, automatic painting, stencil street art, raw crown mark, underground comix, Persian calligraphy graffiti",
        "textile_technique": "gestural brushstroke repeat, urban tag overlay, raw mark-making tile, drip pattern seamless",
    },
    "riviera": {
        "artists": ["Henri Matisse", "Botero", "Georges Seurat", "Gauguin", "Masami Teraoka", "Modigliani"],
        "keywords": "Mediterranean joy, flat decorative cutout, volumetric tropical warmth, pointillist ocean dots, Polynesian primitive, ukiyo-e wave",
        "textile_technique": "pointillist beach pattern, flat color Mediterranean tile, ocean wave repeat, tropical flora and fauna",
    },
    "pulse": {
        "artists": ["Piet Mondrian", "Kandinski", "Keith Haring", "Carla Accardi"],
        "keywords": "primary geometry grid, abstract musical color, kinetic figure line, synesthetic bauhaus, sign painting bold symbol",
        "textile_technique": "geometric grid interference, kinetic figure repeat, optical wave pattern, de Stijl overlay",
    },
    "token": {
        "artists": ["Hirohiko Araki", "Takashi Murakami", "Kaneko Ryuichi", "Matt Groening"],
        "keywords": "JoJo manga precision, superflat kawaii darkness, Japanese robot samurai flamingo, Springfield cartoon irreverence, bold outline pop",
        "textile_technique": "pixel art grid, manga panel tile, kawaii icon repeat, cartoon character all-over",
    },
    "flag": {
        "artists": ["Andy Warhol", "Keith Haring", "Obey Giant / Shepard Fairey", "Mr. Brainwash", "Carla Accardi", "Takashi Murakami"],
        "keywords": "pop repetition, screen-print flat, propaganda graphic, mixed media collage, neon motion, celebrity icon",
        "textile_technique": "bold flat color block, screen-print repeat, pop icon tile, stencil overlay pattern",
    },
    "folklore": {
        "artists": ["Jheronimus Bosch", "Joan Mirò", "Masami Teraoka", "Pre-Raphaelites", "Gauguin", "Kaneko Ryuichi"],
        "keywords": "medieval organic chaos, biomorphic symbols, ukiyo-e + pop hybrid, hyper-detail lush natural, primitive narrative, robot-samurai fable",
        "textile_technique": "micro-figure organic weave, biomorphic tile, narrative scene repeat, lush botanical pattern",
    },
}

# ── 2. TEXTILE PROMPTS — i prompt puri estratti dal CSV ─────────────────────
textile_prompts = [
    {"id": "t01", "prompt": "Color Canvas Edward Hopper Style — drawn sequence of Vintage America, urban geometry, late-night contemplation", "collections": ["hours"]},
    {"id": "t02", "prompt": "micro textile by Jheronimus Bosch style — surreal micro-figures, medieval organic chaos, grotesque detail", "collections": ["folklore", "glyph"]},
    {"id": "t03", "prompt": "island textile style Botero and De Chirico — volumetric figures in metaphysical piazzas, Mediterranean warm palette", "collections": ["riviera", "hours"]},
    {"id": "t04", "prompt": "elegant textile black green line design style Goyard and Klimt — chevron luxury meets gold ornament", "collections": ["hours"]},
    {"id": "t05", "prompt": "sands and green vertical micro textile by Magritte — impossible juxtaposition of natural elements, surreal vertical repeat", "collections": ["glyph", "marker"]},
    {"id": "t06", "prompt": "textile made by weaving golden threads and Dalì and Mondrian-style copper cables painted in oil — grid meets dreamscape in metallic", "collections": ["glyph", "pulse"]},
    {"id": "t07", "prompt": "micro textile made by weaving thirteen small greek symbols in the style of Matisse and Dalì — flat color surreal symbol repeat", "collections": ["glyph"]},
    {"id": "t08", "prompt": "fabric with thirteen small fish symbols in the style of Dalì and Pollock — oil painting automatic gesture, surreal fish scatter", "collections": ["riviera", "folklore"]},
    {"id": "t09", "prompt": "overlay of LINES AND GREEKS COLORED WITH COOL COLORS designed by Coco Chanel — structured elegance, chain motif, cool geometry", "collections": ["hours", "glyph"]},
    {"id": "t10", "prompt": "Canvas Underground drawn style — beige and cobalt blue, raw graphic energy, urban archaeology", "collections": ["marker", "hours"]},
    {"id": "t11", "prompt": "fabric made by weaving nine small Carnival symbols in the style of Dalì and Mondrian — festive surreal grid, primary palette", "collections": ["token", "folklore"]},
    {"id": "t12", "prompt": "monochrome rust oil painting — sober weaving of characteristic symbols in the style of Magritte — impossible object repeat", "collections": ["glyph", "marker"]},
    {"id": "t13", "prompt": "losanghe sfalzate per textile — greche e variazioni sottili stilizzati Style Mirò — biomorphic diamond grid, primary black accents", "collections": ["folklore", "pulse"]},
    {"id": "t14", "prompt": "beach towel with elements of oceans in the style of Georges Seurat — pointillist chromatic dots, Mediterranean coastal light", "collections": ["riviera"]},
    {"id": "t15", "prompt": "Space Invaders pattern vintage style Magritte — arcade alien grid meets Belgian surrealism, impossible pixel logic", "collections": ["token", "glyph"]},
    {"id": "t16", "prompt": "PacMan pattern vintage style Matt Groening — classic arcade maze meets Springfield yellow cartoon irreverence", "collections": ["token"]},
    {"id": "t17", "prompt": "yellow textile Carla Accardi style — one large iconic painted sign symbol, bold Italian avant-garde", "collections": ["flag", "pulse"]},
]

# ── 3. PRODUCT TYPE → ARTIST AFFINITY ───────────────────────────────────────
product_affinity = {
    "backpack": {
        "primary_artists": ["Jheronimus Bosch", "René Magritte", "Gustav Klimt", "Goyard"],
        "technique": "micro-figure organic weave meets luxury chevron geometry",
        "prompt_fragment": "micro textile canvas with Bosch organic chaos and Klimt gold ornament overlay",
    },
    "sneakers": {
        "primary_artists": ["Hirohiko Araki", "Giorgio De Chirico", "Leonardo da Vinci"],
        "technique": "manga technical precision on architectural geometry",
        "prompt_fragment": "JoJo bold outline meets De Chirico shadow geometry, hyper-real technical detail",
    },
    "athletic_shorts": {
        "primary_artists": ["Joan Mirò", "Piet Mondrian", "Keith Haring"],
        "technique": "biomorphic grid with kinetic figure energy",
        "prompt_fragment": "Mirò biomorphic losanghe on Mondrian grid, Keith Haring kinetic motion implied",
    },
    "swim_trunks": {
        "primary_artists": ["Georges Seurat", "Henri Matisse", "Gauguin"],
        "technique": "pointillist ocean with flat tropical cutout",
        "prompt_fragment": "Seurat pointillist beach light, Matisse flat Mediterranean color, Gauguin tropical vitality",
    },
    "windbreaker": {
        "primary_artists": ["René Magritte", "Kandinski", "A1one"],
        "technique": "impossible overlay of geometric music and calligraphic flow",
        "prompt_fragment": "Magritte surreal sky fragment overlay, Kandinski synesthetic geometry, A1one Persian flow",
    },
    "hawaiian_shirt": {
        "primary_artists": ["Gauguin", "Masami Teraoka", "Henri Matisse"],
        "technique": "tropical ukiyo-e with flat Mediterranean color",
        "prompt_fragment": "Gauguin Polynesian flatness meets Teraoka ukiyo-e wave pattern, Matisse cutout flora",
    },
    "tee": {
        "primary_artists": ["Andy Warhol", "Banksy", "SAMO / Basquiat"],
        "technique": "pop repetition with street intervention energy",
        "prompt_fragment": "Warhol screen-print flat meets Basquiat raw crown, Banksy stencil irony underlying",
    },
    "hoodie": {
        "primary_artists": ["Takashi Murakami", "Keith Haring", "Matt Groening"],
        "technique": "superflat kawaii meets kinetic cartoon",
        "prompt_fragment": "Murakami superflat flower-skull, Keith Haring figure outline, Groening cartoon irreverence",
    },
    "lounge_pants": {
        "primary_artists": ["Edward Hopper", "René Magritte", "Coco Chanel"],
        "technique": "contemplative geometry with structured elegance",
        "prompt_fragment": "Hopper late-night geometric light, Magritte sober impossible symbol, Chanel cool structured line",
    },
    "travel_bag": {
        "primary_artists": ["Goyard", "Gustav Klimt", "Mr. Brainwash"],
        "technique": "luxury heritage pattern with pop energy injection",
        "prompt_fragment": "Goyard chevron luxury heritage, Klimt gold ornament, Mr. Brainwash collage pop disruption",
    },
    "slippers": {
        "primary_artists": ["Kaneko Ryuichi", "Joan Mirò", "Henri Matisse"],
        "technique": "Japanese pop biomorphic with Mediterranean warmth",
        "prompt_fragment": "Kaneko robot-flamingo precision, Mirò biomorphic symbol, Matisse flat decorative warmth",
    },
    "flip_flops": {
        "primary_artists": ["Georges Seurat", "Botero", "Gauguin"],
        "technique": "pointillist beach with tropical volumetric energy",
        "prompt_fragment": "Seurat coastal dots, Botero generous tropical forms, Gauguin Polynesian vibrancy",
    },
    "dress": {
        "primary_artists": ["Henri Matisse", "Klimt", "Modigliani"],
        "technique": "flat cutout decorative with elongated elegance",
        "prompt_fragment": "Matisse flat color cutout flow, Klimt gold decorative surface, Modigliani elongated grace",
    },
    "puffer_jacket": {
        "primary_artists": ["Kandinski", "Piet Mondrian", "Keith Haring"],
        "technique": "geometric musical abstraction with kinetic line",
        "prompt_fragment": "Kandinski synesthetic Bauhaus geometry, Mondrian primary grid, Haring kinetic figure outline",
    },
}

# ── 4. PUSH TO KV ───────────────────────────────────────────────────────────
print("\nBKS Worker Style Training")
print(f"  Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}\n")

kv_put("style:bakabo:artist_map",       artist_map)
kv_put("style:bakabo:textile_prompts",  textile_prompts)
kv_put("style:bakabo:product_affinity", product_affinity)
kv_put("style:bakabo:version", {
    "trained_at": datetime.now().isoformat(),
    "artists_total": sum(len(v["artists"]) for v in artist_map.values()),
    "textile_prompts": len(textile_prompts),
    "product_types": len(product_affinity),
    "source": "zaino_prompts_raw.csv + bakabo-artistic-vocabulary SKILL.md",
})

print("\nTraining completato.")
print(f"  Artisti mappati : {sum(len(v['artists']) for v in artist_map.values())}")
print(f"  Prompt textile  : {len(textile_prompts)}")
print(f"  Tipi prodotto   : {len(product_affinity)}")
