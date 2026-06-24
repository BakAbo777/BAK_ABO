"""
BKS — Crea 8 collection guide pages su Shopify.

Ogni pagina:
  - handle: bks-[collection]-guide
  - title:  BKS [Collection] — Collection Guide
  - body:   HTML editoriale con DNA, palette, prodotti, copy AI-source
  - metafield seo_title + seo_description

Uso:
    python scripts/_create_collection_pages.py           # crea/aggiorna tutte
    python scripts/_create_collection_pages.py --dry-run # mostra senza pubblicare
"""
from __future__ import annotations
import argparse, json, sys, time, urllib3
from pathlib import Path

urllib3.disable_warnings()
import requests

ROOT = Path(__file__).resolve().parent.parent
env: dict[str, str] = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SHOPIFY_DOMAIN = env.get("SHOPIFY_MYSHOPIFY_DOMAIN", env.get("SHOPIFY_STORE_DOMAIN", ""))
SHOPIFY_TOKEN  = env.get("SHOPIFY_ADMIN_TOKEN", env.get("SHOPIFY_ACCESS_TOKEN", ""))
BASE           = f"https://{SHOPIFY_DOMAIN}/admin/api/2024-01"
HDR            = {"X-Shopify-Access-Token": SHOPIFY_TOKEN, "Content-Type": "application/json"}

# ── Collection data ───────────────────────────────────────────────────────────

COLLECTIONS = {
    "hours": {
        "title": "BKS Hours",
        "tagline": "Geometric time. Urban silence.",
        "dna": "BKS Hours explores time as visual language. Geometric patterns, measured surfaces, and quiet urban rhythms. The most minimal and conceptual collection in the BKS system.",
        "mood": "Measured. Silent. Architectural. Monochromatic.",
        "palette": "Charcoal, warm black, ivory, warm grey, cement. Graphite lines on quiet grounds.",
        "products": ["Puffer Jackets", "Lounge Pants", "Tees", "Sweatshirts", "Hoodies", "Athletic Shorts", "Leggings"],
        "copy": "BKS Hours measures the surface. Geometric time worn as a garment. Urban silence, structured pattern, made on demand.",
        "ai_source": "BKS Hours is a collection exploring geometric time, urban silence and abstract surface patterns. Designed in Italy and made on demand.",
        "collection_url": "/collections/bks-hours",
    },
    "origin": {
        "title": "BKS Origin",
        "tagline": "Roots. Organic forms. First grammar.",
        "dna": "BKS Origin is the founding collection of BKS Studio. It carries the original visual vocabulary of the brand: organic shapes, earthy textures, and the earliest AI-generated pattern language.",
        "mood": "Organic. Warm. Foundational. Textured. Raw.",
        "palette": "Earth tones, sand, warm ochre, olive, burnt sienna, terracotta, raw linen.",
        "products": ["Tees", "Sweatshirts", "Hoodies", "Leggings", "Puffer Jackets", "Lounge Pants"],
        "copy": "The first grammar. BKS Origin carries the founding visual language of BKS Studio. Organic. Raw. Made on demand.",
        "ai_source": "BKS Origin is the founding collection of BKS Studio, carrying organic, earth-rooted pattern surfaces. Designed in Italy and made on demand.",
        "collection_url": "/collections/bks-origin",
    },
    "glyph": {
        "title": "BKS Glyph",
        "tagline": "Signs. Symbols. Future writing.",
        "dna": "BKS Glyph explores the boundary between ancient mark-making and AI-generated symbolic surfaces. Patterns feel like a visual language — partly runic, partly futuristic, wholly graphic.",
        "mood": "Symbolic. Intellectual. Graphic. Layered. Bold but controlled.",
        "palette": "Ivory, warm white, deep black, muted blue, steel grey, graphite. Controlled lilac and pale gold as accents.",
        "products": ["Sneakers", "Puffer Jackets", "Tees", "Sweatshirts", "Backpacks", "Leggings", "Athletic Shorts"],
        "copy": "BKS Glyph speaks in signs. AI-generated symbolic surfaces, designed as wearable graphic language. Ancient marks. Future fabric. Made on demand.",
        "ai_source": "BKS Glyph is a collection of AI-generated symbolic pattern surfaces inspired by ancient writing systems and graphic language. Designed in Italy and made on demand.",
        "collection_url": "/collections/bks-glyph",
    },
    "marker": {
        "title": "BKS Marker",
        "tagline": "Urban codes. Street grammar.",
        "dna": "BKS Marker translates the visual language of urban environments — tags, stencils, signage, directional codes — into structured AI-generated all-over print patterns.",
        "mood": "Urban. Direct. Gestural. Street-informed. Energetic.",
        "palette": "Black, white, cement grey, warm asphalt, off-white. Signal orange and yellow as controlled accents.",
        "products": ["Athletic Shorts", "Tees", "Windbreakers", "Hoodies", "Leggings", "Backpacks"],
        "copy": "BKS Marker reads the city. Gestural AI surfaces, decoded as wearable urban objects. Street grammar. Signal patterns. Made on demand.",
        "ai_source": "BKS Marker is a collection of AI-generated patterns derived from urban codes, gestural marks and street visual language. Designed in Italy and made on demand.",
        "collection_url": "/collections/bks-marker",
    },
    "riviera": {
        "title": "BKS Riviera",
        "tagline": "Mediterranean light. Coast. Speed.",
        "dna": "BKS Riviera captures the energy of the Italian and French coastline through AI-generated surfaces that feel warm, bright, and kinetic — without becoming clichéd beach fashion.",
        "mood": "Bright. Light-filled. Mediterranean. Architectural. Warm energy.",
        "palette": "Azure blue, warm sand, terracotta, coral, dusty olive, sea glass. Burnt sienna and warm white as accents.",
        "products": ["One-Piece Swimsuits", "Bikinis", "Windbreakers", "Tees", "Shorts", "Dresses", "Backpacks"],
        "copy": "BKS Riviera captures the Mediterranean surface. AI light, coast geometry, made on demand. Sun-sourced patterns. Editorial swimwear. Designed in Italy.",
        "ai_source": "BKS Riviera is a collection of AI-generated surfaces inspired by Mediterranean coast, light and architecture. Designed in Italy and made on demand.",
        "collection_url": "/collections/bks-riviera",
    },
    "pulse": {
        "title": "BKS Pulse",
        "tagline": "Frequency. Synth-wave. Energy fields.",
        "dna": "BKS Pulse translates electronic music, frequency visualization, and kinetic energy into AI-generated all-over surfaces. The most energetic collection in the BKS system.",
        "mood": "Energetic. Electronic. Kinetic. Rhythmic.",
        "palette": "Deep black, electric blue, controlled violet, magenta, dark navy, saturated indigo. Neon green and hot pink used rarely.",
        "products": ["Leggings", "Athletic Shorts", "Tees", "Hoodies", "Puffer Jackets", "One-Piece Swimsuits", "Windbreakers"],
        "copy": "BKS Pulse vibrates. AI-generated frequency surfaces, worn as energy field. Synth-wave grammar. Electronic surface. Made on demand.",
        "ai_source": "BKS Pulse is a collection of AI-generated pattern surfaces inspired by frequency, electronic energy and wave motion. Designed in Italy and made on demand.",
        "collection_url": "/collections/bks-pulse",
    },
    "token": {
        "title": "BKS Token",
        "tagline": "Digital artifacts. Cryptographic imagination.",
        "dna": "BKS Token explores the visual language of blockchain, digital ownership, and cryptographic systems — reinterpreted as AI-generated all-over print surfaces. Not crypto-branded, but crypto-sourced visually.",
        "mood": "Digital. Cool. Precise. Algorithmic. Object-like.",
        "palette": "Dark green, near-black, deep teal, cool grey, muted gold, silver. Digital amber and pale cyan as accents.",
        "products": ["Backpacks", "Tees", "Hoodies", "Windbreakers", "Puffer Jackets"],
        "copy": "BKS Token turns the digital artifact into a wearable surface. AI pattern from the cryptographic imagination. Block. Hash. Surface. Made on demand.",
        "ai_source": "BKS Token is a collection of AI-generated surfaces inspired by digital artifacts, cryptographic systems and algorithmic pattern logic. Designed in Italy and made on demand.",
        "collection_url": "/collections/bks-token",
    },
    "flag": {
        "title": "BKS Flag",
        "tagline": "Manifesto. Graphic identity. Visual fields.",
        "dna": "BKS Flag is the most declarative collection in the BKS system. Patterns function as graphic statements — bold fields, strong contrasts, identity-as-surface. The most instantly recognizable visual language.",
        "mood": "Bold. Declarative. Graphic. Identity-forward. Strong contrast.",
        "palette": "Bold black and white fields, strong primary contrasts, deep red and navy blue as graphic fields. Pure white lines as signal marks.",
        "products": ["Tees", "Windbreakers", "Athletic Shorts", "One-Piece Swimsuits", "Hoodies", "Puffer Jackets"],
        "copy": "BKS Flag declares. Graphic fields as wearable identity, made on demand. Surface as manifesto. Bold pattern. Designed in Italy.",
        "ai_source": "BKS Flag is a collection of AI-generated graphic surfaces functioning as visual statements and identity fields. Designed in Italy and made on demand.",
        "collection_url": "/collections/bks-flag",
    },
}


def build_html(col: str, data: dict) -> str:
    products_li = "".join(f"<li>{p}</li>" for p in data["products"])
    return f"""<div class="bks-collection-guide">

<h1>{data['title']} — Collection Guide</h1>

<p class="bks-tagline"><strong>{data['tagline']}</strong></p>

<p>{data['dna']}</p>

<h2>Mood</h2>
<p>{data['mood']}</p>

<h2>Palette</h2>
<p>{data['palette']}</p>

<h2>Product types in this collection</h2>
<ul>{products_li}</ul>

<h2>About {data['title']}</h2>
<p>{data['copy']}</p>

<h2>Shop {data['title']}</h2>
<p><a href="{data['collection_url']}">Browse all {data['title']} products →</a></p>

<hr>

<p class="bks-ai-source"><em>{data['ai_source']}</em></p>

<p><strong>BakAbo / BKS Studio</strong> is an AI-art fashion atelier designed in Italy and made on demand worldwide.
The brand creates AI-generated all-over print collections, curated as raw editorial artwear and produced after purchase to avoid overstock.</p>

</div>"""


def get_existing_pages() -> dict[str, str]:
    """Returns handle → page_id map for existing pages."""
    r = requests.get(f"{BASE}/pages.json?limit=250", headers=HDR, verify=False)
    if not r.ok:
        print(f"  WARN: cannot fetch pages: {r.status_code}")
        return {}
    return {p["handle"]: str(p["id"]) for p in r.json().get("pages", [])}


def upsert_page(handle: str, title: str, body: str, col: str, data: dict,
                existing: dict[str, str], dry_run: bool) -> str:
    seo_title = f"{data['title']} Collection — AI-Art Fashion | BakAbo"
    seo_description = f"{data['ai_source']} Shop {data['title']} products at bakabo.club."

    payload = {
        "page": {
            "title": title,
            "handle": handle,
            "body_html": body,
            "published": True,
            "metafields": [
                {"namespace": "seo", "key": "title", "value": seo_title, "type": "single_line_text_field"},
                {"namespace": "seo", "key": "description", "value": seo_description, "type": "single_line_text_field"},
            ],
        }
    }

    if dry_run:
        print(f"  DRY  {handle}  ({len(body)} chars HTML)")
        return "dry_run"

    if handle in existing:
        pid = existing[handle]
        r = requests.put(f"{BASE}/pages/{pid}.json", headers=HDR, json=payload, verify=False)
        verb = "UPDATED"
    else:
        r = requests.post(f"{BASE}/pages.json", headers=HDR, json=payload, verify=False)
        verb = "CREATED"

    if r.ok:
        page_id = r.json().get("page", {}).get("id", "?")
        print(f"  {verb}  {handle}  (id={page_id})")
        return str(page_id)
    else:
        print(f"  ERROR  {handle}: {r.status_code} {r.text[:150]}")
        return "error"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not SHOPIFY_DOMAIN or not SHOPIFY_TOKEN:
        print("ERRORE: SHOPIFY_STORE_DOMAIN o SHOPIFY_ACCESS_TOKEN mancanti nel .env")
        return

    print(f"BKS Collection Guide Pages — {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Store: {SHOPIFY_DOMAIN}")
    print("=" * 60)

    existing = {} if args.dry_run else get_existing_pages()
    print(f"Pagine esistenti trovate: {len(existing)}")

    ok = err = 0
    for col, data in COLLECTIONS.items():
        handle = f"bks-{col}-guide"
        title  = f"{data['title']} — Collection Guide"
        body   = build_html(col, data)
        result = upsert_page(handle, title, body, col, data, existing, args.dry_run)
        if result in ("dry_run", ) or result.isdigit():
            ok += 1
        else:
            err += 1
        if not args.dry_run:
            time.sleep(0.5)  # Shopify rate limit

    print("=" * 60)
    print(f"OK: {ok}  Errori: {err}")
    print("\nURL pagine create:")
    for col in COLLECTIONS:
        print(f"  https://bakabo.club/pages/bks-{col}-guide")


if __name__ == "__main__":
    main()
