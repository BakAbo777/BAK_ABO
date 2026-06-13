"""BKS Studio — SEO metadata generator."""
import re
from config.settings import COLLECTIONS


def safe_slug(s: str) -> str:
    s = re.sub(r"[™®©]", "", s)
    s = re.sub(r"[^a-zA-Z0-9\s\-]", "", s)
    return re.sub(r"\s+", "-", s.strip()).lower()


def seo_title(product_title: str, collection: str) -> str:
    """Generate SEO page title ≤ 60 chars."""
    col = collection.capitalize() if collection in COLLECTIONS else collection
    base = f"BKS {col} — {product_title}"
    if len(base) > 60:
        base = base[:57] + "..."
    return base


def seo_description(product_title: str, collection: str, product_type: str) -> str:
    """Generate meta description ≤ 160 chars."""
    col = collection.capitalize() if collection in COLLECTIONS else collection
    ptype = product_type.replace("-", " ").title()
    desc = (
        f"BKS Studio {col} Collection. AI-generated all-over print {ptype}. "
        f"Edge-to-edge sublimation print, made to order. bakabo.club."
    )
    return desc[:160]


def alt_text(product_title: str, slot: str, collection: str) -> str:
    """Generate image alt text for Shopify."""
    slot_labels = {
        "product_front":    "front view",
        "product_back":     "back view",
        "editorial_square": "editorial square",
        "editorial_4x5":    "editorial vertical",
        "hero_banner":      "hero banner",
        "texture_detail":   "fabric detail",
    }
    label = slot_labels.get(slot, slot)
    col   = collection.capitalize() if collection in COLLECTIONS else collection
    return f"BKS Studio {col} — {product_title} — {label}"


def tags(collection: str, product_type: str, design_name: str = "") -> str:
    """Generate Shopify tags string."""
    tag_list = [
        f"collection:{collection}",
        f"type:{product_type}",
        "drop:catalog-reset-2026",
        "bakabo-enriched",
        "aop",
        "made-to-order",
    ]
    if design_name:
        tag_list.append(f"design:{safe_slug(design_name)}")
    return ",".join(tag_list)


def shopify_handle(product_title: str) -> str:
    """Generate a Shopify-compatible URL handle."""
    s = safe_slug(product_title)
    # Remove BKS prefix if present
    s = re.sub(r"^bks-?", "", s)
    return s[:80]


def generate_all(product_title: str, collection: str, product_type: str,
                 design_name: str = "") -> dict:
    """Generate all SEO fields for a product."""
    return {
        "seo_title":       seo_title(product_title, collection),
        "seo_description": seo_description(product_title, collection, product_type),
        "handle":          shopify_handle(product_title),
        "tags":            tags(collection, product_type, design_name),
        "alt_texts": {
            slot: alt_text(product_title, slot, collection)
            for slot in ["product_front", "product_back", "editorial_square",
                         "editorial_4x5", "hero_banner", "texture_detail"]
        }
    }
