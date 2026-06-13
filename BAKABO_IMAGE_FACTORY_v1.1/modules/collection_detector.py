"""BKS Studio — Collection detector.
Assigns one of the 8 BKS editorial collections based on image analysis.
"""
import yaml
from pathlib import Path


CONFIG = yaml.safe_load((Path(__file__).parent.parent / "config" / "collections.yaml").read_text())
COLL   = CONFIG["collections"]


def detect_from_analysis(analysis: dict) -> str:
    """Use GPT-vision analysis result to confirm/assign a collection."""
    col = analysis.get("collection", "unknown")
    if col in COLL:
        return col
    return detect_from_palette(analysis.get("palette", []))


def detect_from_palette(palette: list[str]) -> str:
    """Heuristic: map dominant colors to nearest collection.

    Falls back to 'folklore' if nothing matches.
    """
    if not palette:
        return "folklore"

    # Convert hex → RGB
    def h2rgb(h: str) -> tuple[int, int, int]:
        h = h.lstrip("#")
        return int(h[:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    # Compute average warmth (R - B) and brightness
    rgbs = [h2rgb(h) for h in palette if len(h) == 7]
    if not rgbs:
        return "folklore"

    avg_r = sum(c[0] for c in rgbs) / len(rgbs)
    avg_g = sum(c[1] for c in rgbs) / len(rgbs)
    avg_b = sum(c[2] for c in rgbs) / len(rgbs)
    brightness = (avg_r + avg_g + avg_b) / 3
    warmth     = avg_r - avg_b
    saturation = max(avg_r, avg_g, avg_b) - min(avg_r, avg_g, avg_b)

    # Dark + low saturation → hours or glyph
    if brightness < 60 and saturation < 40:
        return "glyph"
    if brightness < 80:
        return "hours"

    # Warm medium tones → folklore or riviera
    if warmth > 30 and brightness > 150:
        return "riviera" if avg_b > 80 else "folklore"

    # Cool dark → token or pulse
    if warmth < -20 and brightness < 120:
        return "token"
    if saturation > 80 and brightness > 80:
        return "pulse"

    # Light + low sat → flag
    if brightness > 200 and saturation < 60:
        return "flag"

    # Warm dark → marker
    if warmth > 10 and brightness < 130:
        return "marker"

    return "folklore"


def detect_from_keywords(text: str) -> str:
    """Scan product title or description for collection keywords."""
    text_lower = text.lower()
    for col_id, col_data in COLL.items():
        for kw in col_data.get("keywords", []):
            if kw.lower() in text_lower:
                return col_id
    return "unknown"


def detect_from_tags(tags: list[str]) -> str:
    """Check Shopify/Printify tags for collection: prefix."""
    for tag in tags:
        t = tag.lower().strip()
        if t.startswith("collection:"):
            col = t.split(":", 1)[1].strip()
            if col in COLL:
                return col
    return "unknown"


def detect(image_path=None, analysis: dict = None, title: str = "",
           tags: list[str] = None) -> dict:
    """Full detection pipeline. Returns best guess with confidence.

    Priority: tags > analysis > keyword > palette
    """
    tags = tags or []

    # 1. Tags (most reliable)
    from_tags = detect_from_tags(tags)
    if from_tags != "unknown":
        return {"collection": from_tags, "source": "tags", "confidence": 1.0}

    # 2. GPT-vision analysis
    if analysis and analysis.get("collection", "unknown") != "unknown":
        col = analysis["collection"]
        return {"collection": col, "source": "vision", "confidence": 0.9}

    # 3. Keywords in title
    if title:
        from_kw = detect_from_keywords(title)
        if from_kw != "unknown":
            return {"collection": from_kw, "source": "keywords", "confidence": 0.7}

    # 4. Palette
    if analysis and analysis.get("palette"):
        col = detect_from_palette(analysis["palette"])
        return {"collection": col, "source": "palette", "confidence": 0.5}

    return {"collection": "folklore", "source": "default", "confidence": 0.1}
