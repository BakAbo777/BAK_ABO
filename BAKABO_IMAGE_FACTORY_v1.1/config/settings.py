"""BKS Studio — BAKABO IMAGE FACTORY v1.1
Configuration and constants.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env", override=False)
_parent_env = BASE_DIR.parent / ".env"
if _parent_env.exists():
    load_dotenv(_parent_env, override=False)

# ── API KEYS ──────────────────────────────────────────────────────────────────
OPENAI_API_KEY        = os.getenv("OPENAI_API_KEY", "")
PRINTIFY_API_TOKEN    = os.getenv("PRINTIFY_API_TOKEN", "")
PRINTIFY_SHOP_ID      = os.getenv("PRINTIFY_SHOP_ID", "")
SHOPIFY_STORE         = os.getenv("SHOPIFY_STORE") or os.getenv("SHOPIFY_MYSHOPIFY_DOMAIN", "")
SHOPIFY_ACCESS_TOKEN  = os.getenv("SHOPIFY_ACCESS_TOKEN") or os.getenv("SHOPIFY_ADMIN_TOKEN", "")
REMOVE_BG_API_KEY     = os.getenv("REMOVE_BG_API_KEY", "")
MODEL_PROVIDER        = os.getenv("MODEL_PROVIDER", "openai")

# ── PATHS ─────────────────────────────────────────────────────────────────────
OUTPUT_DIR   = BASE_DIR / "output"
SOURCE_DIR   = OUTPUT_DIR / "source"
CUTOUT_DIR   = OUTPUT_DIR / "cutout"
GENERATED_DIR= OUTPUT_DIR / "generated"
APPROVED_DIR = OUTPUT_DIR / "approved"
SHOPIFY_DIR  = OUTPUT_DIR / "shopify"
CACHE_DIR    = BASE_DIR / "cache"
DB_PATH      = BASE_DIR / "database" / "bakabo.db"

for d in [SOURCE_DIR, CUTOUT_DIR, GENERATED_DIR, APPROVED_DIR, SHOPIFY_DIR, CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── IMAGE FORMATS ─────────────────────────────────────────────────────────────
IMAGE_FORMATS = {
    "product_front":   {"size": (2000, 2000), "ratio": "1:1",  "label": "Product Front"},
    "product_back":    {"size": (2000, 2000), "ratio": "1:1",  "label": "Product Back"},
    "editorial_square":{"size": (2000, 2000), "ratio": "1:1",  "label": "Editorial Square"},
    "editorial_4x5":   {"size": (1600, 2000), "ratio": "4:5",  "label": "Editorial 4:5"},
    "hero_banner":     {"size": (2400, 1050), "ratio": "16:7", "label": "Hero Banner"},
    "texture_detail":  {"size": (1500, 1500), "ratio": "1:1",  "label": "Texture Detail"},
}

# ── COLLECTIONS ───────────────────────────────────────────────────────────────
COLLECTIONS = [
    "hours", "glyph", "marker", "riviera",
    "pulse", "token", "flag", "folklore"
]

COLLECTION_PALETTE = {
    "hours":    {"bg": "#1A1A1A", "text": "#FAFAF7", "accent": "#C9B79C"},
    "glyph":    {"bg": "#0A0A0A", "text": "#FAFAF7", "accent": "#C9B79C"},
    "marker":   {"bg": "#F5F0E8", "text": "#0A0A0A", "accent": "#0A0A0A"},
    "riviera":  {"bg": "#E8DCC8", "text": "#2A2018", "accent": "#2A8B85"},
    "pulse":    {"bg": "#0E1420", "text": "#FAFAF7", "accent": "#C9B79C"},
    "token":    {"bg": "#080810", "text": "#FAFAF7", "accent": "#C9B79C"},
    "flag":     {"bg": "#FAFAF7", "text": "#0A0A0A", "accent": "#0A0A0A"},
    "folklore": {"bg": "#EDE5D0", "text": "#2A2018", "accent": "#2A8B85"},
}

# ── QUALITY THRESHOLD ─────────────────────────────────────────────────────────
QA_THRESHOLD = 85  # minimum score to approve an image

# ── OPENAI ────────────────────────────────────────────────────────────────────
OPENAI_IMAGE_MODEL   = "gpt-image-1"
OPENAI_VISION_MODEL  = "gpt-4o"
OPENAI_IMAGE_QUALITY = "high"
OPENAI_IMAGE_SIZE    = "1024x1024"
