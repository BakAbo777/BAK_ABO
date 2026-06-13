"""BKS Studio — Quality validator for generated images."""
import base64
import json
from pathlib import Path
from openai import OpenAI
from config.settings import OPENAI_API_KEY, OPENAI_VISION_MODEL, QA_THRESHOLD

client = OpenAI(api_key=OPENAI_API_KEY)


CRITERIA = [
    ("anatomy",    "Human anatomy is correct. No extra fingers, deformed limbs, or distorted faces."),
    ("product",    "The product (garment or accessory) is clearly visible and occupies at least 50% of the frame."),
    ("logo",       "No unwanted text, watermark, or brand logo visible in the image."),
    ("focus",      "The product is in sharp focus. Not blurry."),
    ("colors",     "The product colors appear consistent with typical all-over print wearables."),
    ("proportion", "Product proportions are realistic. No stretched or distorted silhouette."),
]

WEIGHTS = {
    "anatomy":    20,
    "product":    25,
    "logo":       20,
    "focus":      15,
    "colors":     10,
    "proportion": 10,
}


def validate(image_path: Path, dry_run: bool = False) -> dict:
    """Score an image 0-100 against QA criteria.

    Returns:
        {
            "score": int,
            "approved": bool,
            "criteria": {criterion: {"pass": bool, "note": str}},
            "issues": list[str],
        }
    """
    if dry_run:
        return {"score": 100, "approved": True, "criteria": {}, "issues": [],
                "note": "dry-run — no validation performed"}

    prompt = f"""You are a quality control analyst for BKS Studio fashion e-commerce images.
Evaluate this image against the following criteria and return ONLY a JSON object.

Criteria to evaluate:
{json.dumps({k: v for k, v in CRITERIA}, indent=2)}

Return this exact JSON structure:
{{
  "anatomy":    {{"pass": true/false, "note": "brief note"}},
  "product":    {{"pass": true/false, "note": "brief note"}},
  "logo":       {{"pass": true/false, "note": "brief note"}},
  "focus":      {{"pass": true/false, "note": "brief note"}},
  "colors":     {{"pass": true/false, "note": "brief note"}},
  "proportion": {{"pass": true/false, "note": "brief note"}}
}}

Return ONLY valid JSON. No markdown, no explanation."""

    img_b64 = base64.b64encode(image_path.read_bytes()).decode()

    try:
        resp = client.chat.completions.create(
            model=OPENAI_VISION_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                    {"type": "text",      "text": prompt},
                ]
            }],
            max_tokens=400,
            temperature=0,
        )
        raw = resp.choices[0].message.content.strip()
        try:
            criteria = json.loads(raw)
        except json.JSONDecodeError:
            import re
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            criteria = json.loads(m.group()) if m else {}
    except Exception as e:
        return {"score": 0, "approved": False, "criteria": {}, "issues": [str(e)]}

    # Compute score
    score = sum(WEIGHTS[k] for k, v in criteria.items() if v.get("pass") and k in WEIGHTS)
    issues = [f"{k}: {v['note']}" for k, v in criteria.items() if not v.get("pass")]

    return {
        "score":    score,
        "approved": score >= QA_THRESHOLD,
        "criteria": criteria,
        "issues":   issues,
    }


def score_label(score: int) -> str:
    if score >= 90: return "✅ Excellent"
    if score >= 85: return "✅ Approved"
    if score >= 70: return "⚠️ Review needed"
    return "❌ Rejected"
