# BKS Asset Database — central registry of all visual assets available to the master AI.
#
# Sources:
#   1. Product catalog photos   — I:\BAK ABO\output\foto collezioni\00_originals_catalogued
#   2. Image Factory mockups    — E:\BAKSITO\...\BAKABO_IMAGE_FACTORY_v1.1\output\source
#   3. BakAbo AI artworks       — E:\IMMAGINI AI  (2 362 imgs, 49 series)
#   4. NFT / original artworks  — E:\NFT          (12 711 imgs, 135 dirs)
#   5. Social / Facebook videos — E:\NFT\VIDEO FACEBOOK  (16 MP4)
#   6. AI-generated videos      — E:\IMMAGINI AI\video   (18 MP4)
#   7. Portraits                — E:\RITRATTI             (11 imgs, future collection)
#
# Query entry: bks_asset_db.query(asset_type=..., series=..., collection=..., ext=...)

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator


# ── Source roots ────────────────────────────────────────────────────────────

CATALOG_PHOTOS    = Path(r"I:\BAK ABO\output\foto collezioni\00_originals_catalogued")
IMAGE_FACTORY     = Path(r"E:\BAKSITO\BAKABO\BAK ABO\BAKABO_IMAGE_FACTORY_v1.1\output\source")
AI_ARTWORKS       = Path(r"E:\IMMAGINI AI")
NFT_ARTWORKS      = Path(r"E:\NFT")
SOCIAL_VIDEOS     = Path(r"E:\NFT\VIDEO FACEBOOK")
AI_VIDEOS         = Path(r"E:\IMMAGINI AI\video")
PORTRAITS         = Path(r"E:\RITRATTI")
LIVE_CSV          = Path(r"I:\BAK ABO\output\live_shopify_products.csv")

# ── BakAbo visual DNA — Roberto Picchioni's art style ───────────────────────

BAKABO_STYLE_DNA = {
    "description": (
        "BakAbo è il brand visivo di Roberto Picchioni. Lo stile nasce dalla grafica urbana, "
        "pop art, art brut, neo-impressionismo e surrealismo. Le immagini AI e NFT definiscono "
        "il DNA visivo del brand: colori saturi su fondi texture, figure deformate/astratte, "
        "simboli e pattern geometrici, riferimenti a Basquiat, Mirò, Escher, De Chirico."
    ),
    "series": {
        # E:\IMMAGINI AI — AI-generated artworks
        "ARCHITETTURA":        {"type": "ai_art", "mood": "urban, structural, brutalism", "count": 584},
        "COPERTE":             {"type": "ai_art", "mood": "textured surfaces, cover-like", "count": 233},
        "CANI 00":             {"type": "ai_art", "mood": "animals, pop", "count": 211},
        "VIOLET 77":           {"type": "ai_art", "mood": "monochrome violet, abstract", "count": 127},
        "Miro 00":             {"type": "ai_art", "mood": "Miró-inspired, surreal shapes", "count": 108},
        "TEXT 001 A":          {"type": "ai_art", "mood": "typographic, lettering, urban", "count": 104},
        "PUPAZZI":             {"type": "ai_art", "mood": "naive, folk, puppet figures", "count": 98},
        "UNDERGROUND 00 A":    {"type": "ai_art", "mood": "underground, dark, street", "count": 98},
        "ROBOT 25":            {"type": "ai_art", "mood": "mechanical, digital, sci-fi", "count": 91},
        "UAP TOWN":            {"type": "ai_art", "mood": "UFO, urban, surreal", "count": 83},
        "B & N 00":            {"type": "ai_art", "mood": "black&white, high contrast", "count": 60},
        "JAPAN 00 1":          {"type": "ai_art", "mood": "Japanese aesthetics, ukiyo-e influenced", "count": 51},
        "Underwhater 00":      {"type": "ai_art", "mood": "underwater, blue, fluid", "count": 43},
        "GREEN 00 A":          {"type": "ai_art", "mood": "green nature, organic", "count": 38},
        "GOLD 00 A":           {"type": "ai_art", "mood": "gold, luxury, metallic", "count": 23},
        "ESCHER 00 A":         {"type": "ai_art", "mood": "geometric illusion, Escher-style", "count": 31},
        "DE CHIRICO":          {"type": "ai_art", "mood": "metaphysical, De Chirico shadows", "count": 0},
        "Jean-Michel Basquiat 00": {"type": "ai_art", "mood": "neo-expressionism, urban marks, Basquiat", "count": 0},
        "SKULL 00 A":          {"type": "ai_art", "mood": "skull, memento mori, graphic", "count": 0},
        # E:\NFT — original NFT artworks
        "2023 BAK ABO":        {"type": "nft", "mood": "multi-series 2023, core BakAbo catalog", "count": 8385},
        "2024 BakAbo":         {"type": "nft", "mood": "2024 series, evolved style", "count": 153},
        "APRILE 24":           {"type": "nft", "mood": "April 2024 series", "count": 1219},
        "trame 34":            {"type": "nft", "mood": "woven texture patterns", "count": 615},
        "PUBBLICITA":          {"type": "nft", "mood": "advertising archive, brand communication", "count": 499},
        "STEMMI 2024":         {"type": "nft", "mood": "heraldic, crest, identity marks", "count": 174},
        "AAA TEXTURES":        {"type": "nft", "mood": "surface textures for print-on-demand", "count": 0},
        "TRAME 01":            {"type": "nft", "mood": "weave pattern series 01", "count": 59},
        "LOGHI":               {"type": "nft", "mood": "logo studies, brand marks", "count": 99},
        "PEZZE2":              {"type": "nft", "mood": "patch/badge graphic system", "count": 97},
    },
    "collection_affinity": {
        # Which BKS collections map to which art series
        "Hours":   ["B & N 00", "UNDERGROUND 00 A", "ARCHITETTURA"],
        "Glyph":   ["TEXT 001 A", "Jean-Michel Basquiat 00", "SKULL 00 A"],
        "Marker":  ["Jean-Michel Basquiat 00", "UNDERGROUND 00 A", "ROBOT 25"],
        "Riviera": ["Underwhater 00", "GREEN 00 A", "JAPAN 00 1"],
        "Pulse":   ["VIOLET 77", "ROBOT 25", "UAP TOWN"],
        "Token":   ["ROBOT 25", "DE CHIRICO", "UAP TOWN"],
        "Flag":    ["STEMMI 2024", "LOGHI", "PEZZE2"],
        "Origin":  ["ARCHITETTURA", "COPERTE", "PUPAZZI"],
    }
}

# ── Helpers ──────────────────────────────────────────────────────────────────

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTS = {".mp4", ".mov", ".avi"}


def _iter_files(root: Path, exts: set[str]) -> Iterator[Path]:
    if not root.exists():
        return
    for p in root.rglob("*"):
        if p.suffix.lower() in exts:
            yield p


def query(
    asset_type: str = "all",
    series: str | None = None,
    collection: str | None = None,
    ext: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """
    Query available assets.

    asset_type: 'product_photo' | 'mockup' | 'ai_art' | 'nft' | 'video' | 'portrait' | 'all'
    series:     folder name in E:\\IMMAGINI AI or E:\\NFT
    collection: BKS collection name (Hours/Glyph/Marker/Riviera/Pulse/Token/Flag/Origin)
    ext:        file extension filter ('.jpg', '.png', '.mp4', ...)
    """
    exts = {ext} if ext else (IMAGE_EXTS | VIDEO_EXTS)
    results: list[dict] = []

    sources: list[tuple[str, Path]] = []

    if asset_type in ("product_photo", "all"):
        sources.append(("product_photo", CATALOG_PHOTOS))
    if asset_type in ("mockup", "all"):
        sources.append(("mockup", IMAGE_FACTORY))
    if asset_type in ("ai_art", "all"):
        base = AI_ARTWORKS / series if series else AI_ARTWORKS
        sources.append(("ai_art", base))
    if asset_type in ("nft", "all"):
        base = NFT_ARTWORKS / series if series else NFT_ARTWORKS
        sources.append(("nft", base))
    if asset_type in ("video", "all"):
        sources.append(("video_social", SOCIAL_VIDEOS))
        sources.append(("video_ai", AI_VIDEOS))
    if asset_type in ("portrait", "all"):
        sources.append(("portrait", PORTRAITS))

    for src_type, root in sources:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.suffix.lower() not in exts:
                continue
            if collection and src_type == "product_photo":
                if collection.lower() not in p.name.lower():
                    continue
            results.append({
                "type": src_type,
                "path": str(p),
                "name": p.name,
                "series": p.parent.name,
                "ext": p.suffix.lower(),
            })
            if len(results) >= limit:
                return results

    return results


def style_dna(collection: str | None = None) -> dict:
    """Return BakAbo visual style DNA, optionally filtered by collection affinity."""
    if not collection:
        return BAKABO_STYLE_DNA
    affinity = BAKABO_STYLE_DNA["collection_affinity"].get(collection, [])
    series_subset = {k: v for k, v in BAKABO_STYLE_DNA["series"].items() if k in affinity}
    return {**BAKABO_STYLE_DNA, "series": series_subset, "collection": collection}


def summary() -> dict:
    """Return a snapshot of available asset counts by source."""
    return {
        "catalog_photos": {
            "path": str(CATALOG_PHOTOS),
            "exists": CATALOG_PHOTOS.exists(),
            "note": "858 total, ~686 matched to published products",
        },
        "image_factory": {
            "path": str(IMAGE_FACTORY),
            "exists": IMAGE_FACTORY.exists(),
            "note": "359 high-quality mockup JPGs for 46 products",
        },
        "ai_artworks": {
            "path": str(AI_ARTWORKS),
            "exists": AI_ARTWORKS.exists(),
            "note": "2 362 images in 49 series — BakAbo AI visual DNA",
            "top_series": ["ARCHITETTURA (584)", "COPERTE (233)", "CANI 00 (211)", "VIOLET 77 (127)", "Miro 00 (108)"],
        },
        "nft_artworks": {
            "path": str(NFT_ARTWORKS),
            "exists": NFT_ARTWORKS.exists(),
            "note": "12 711 images — Roberto Picchioni original NFT art (2023-2024)",
            "top_series": ["2023 BAK ABO (8 385)", "APRILE 24 (1 219)", "trame 34 (615)", "PUBBLICITA (499)"],
        },
        "social_videos": {
            "path": str(SOCIAL_VIDEOS),
            "exists": SOCIAL_VIDEOS.exists(),
            "note": "16 Facebook/WhatsApp videos",
        },
        "ai_videos": {
            "path": str(AI_VIDEOS),
            "exists": AI_VIDEOS.exists(),
            "note": "18 AI-generated / HeyGen videos",
        },
        "portraits": {
            "path": str(PORTRAITS),
            "exists": PORTRAITS.exists(),
            "note": "11 portrait photos — reserved for future BKS collection",
        },
        "bakabo_style_dna": "See bks_asset_db.style_dna() for full BakAbo visual identity map",
    }
