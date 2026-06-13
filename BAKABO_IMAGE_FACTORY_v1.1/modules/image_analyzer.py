"""BKS Studio — Image analyzer using OpenAI vision."""
import base64
import json
from pathlib import Path
from openai import OpenAI
from config.settings import OPENAI_API_KEY, OPENAI_VISION_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def _encode(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def analyze_product_image(image_path: Path) -> dict:
    """Analyze a product image and return structured metadata.

    Returns:
        {
            "product_type": str,
            "gender": str,        # man | woman | unisex
            "collection": str,    # one of 8 BKS collections
            "palette": list[str], # 3-5 dominant hex colors
            "style": str,
            "recommended_model": str
        }
    """
    prompt = """You are an AI analyst for BKS Studio, an AI-art wearable brand.
Analyze this product image and return ONLY a JSON object with these exact keys:

{
  "product_type": "<one of: lounge-pants, swim-trunks, one-piece-swimsuit, puffer-jacket, windbreaker, pullover-hoodie, racerback-dress, athletic-shorts, sneakers, backpack, travel-bag, flip-flop, cozy-slipper, womens-tee, unknown>",
  "gender": "<man | woman | unisex>",
  "collection": "<one of: hours, glyph, marker, riviera, pulse, token, flag, folklore, unknown>",
  "palette": ["#hex1", "#hex2", "#hex3"],
  "style": "<brief visual style description in English, max 10 words>",
  "recommended_model": "<Autunno Caldo | Autunno Soft | Inverno Brillante | Inverno Freddo | Primavera Calda | Estate Soft | null>"
}

Collection detection rules:
- hours: urban, hyperrealist, windows, shadows, architectural, muted grey
- glyph: abstract marks, symbols, hieroglyphs, coded, black/white graphic
- marker: gestural brush strokes, drip, paint, graffiti, urban mark
- riviera: mediterranean, coastal, terracotta, sea, palm, warm blue
- pulse: optical, geometric grid, kinetic, wave, stripe, checkerboard
- token: pixel, arcade, low-bit, digital, neon, kaleidoscope
- flag: color block, flat, stencil, banner, primary colors, pop
- folklore: animals, plants, garden, naif illustration, fable, organic

Return ONLY valid JSON. No markdown, no explanation."""

    resp = client.chat.completions.create(
        model=OPENAI_VISION_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{_encode(image_path)}"}},
                {"type": "text",      "text": prompt},
            ]
        }],
        max_tokens=400,
        temperature=0,
    )
    raw = resp.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        import re
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        return json.loads(m.group()) if m else {}


def extract_palette(image_path: Path, n_colors: int = 5) -> list[str]:
    """Extract dominant colors using k-means on the image pixels."""
    import numpy as np
    from PIL import Image

    img = Image.open(image_path).convert("RGB").resize((150, 150))
    pixels = np.array(img).reshape(-1, 3).astype(float)

    # Simple k-means
    idx = np.random.choice(len(pixels), n_colors, replace=False)
    centers = pixels[idx]
    for _ in range(20):
        dists   = np.linalg.norm(pixels[:, None] - centers[None, :], axis=2)
        labels  = np.argmin(dists, axis=1)
        new_centers = np.array([pixels[labels == k].mean(axis=0)
                                 if (labels == k).any() else centers[k]
                                 for k in range(n_colors)])
        if np.allclose(centers, new_centers, atol=1):
            break
        centers = new_centers

    return ["#{:02x}{:02x}{:02x}".format(int(c[0]), int(c[1]), int(c[2]))
            for c in centers]
