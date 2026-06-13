"""BKS Studio — Printify API client."""
import os
import requests
from pathlib import Path
from config.settings import PRINTIFY_API_TOKEN, PRINTIFY_SHOP_ID, SOURCE_DIR

BASE = "https://api.printify.com/v1"
HEADERS = {"Authorization": f"Bearer {PRINTIFY_API_TOKEN}"}
PRINTIFY_SHOP_TITLE = os.getenv("PRINTIFY_SHOP_TITLE", "bakabo.club")


def _get(path: str, params: dict = None) -> dict:
    import ssl, urllib3
    # Retry with SSL verification disabled if SSL handshake fails (proxy/antivirus intercept)
    try:
        r = requests.get(f"{BASE}{path}", headers=HEADERS, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.SSLError:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        r = requests.get(f"{BASE}{path}", headers=HEADERS, params=params,
                         timeout=30, verify=False)
        r.raise_for_status()
        return r.json()


def get_correct_shop_id() -> str:
    """Fetch the numeric Printify shop ID automatically."""
    data = _get("/shops.json")
    if isinstance(data, list):
        raw = data
    elif isinstance(data, dict):
        raw = data.get("data", [])
    else:
        raw = []
    if not raw:
        raise ValueError("No Printify shops found for this token.")
    first = raw[0]
    return str(first["id"] if isinstance(first, dict) else first)


def resolve_shop_id() -> str:
    """Return the numeric Printify shop ID for bakabo.club.

    Priority:
    1. PRINTIFY_SHOP_ID in .env if it's a valid integer
    2. Find the shop whose title or domain contains 'bakabo'
    3. Fall back to the first shop found
    """
    sid = PRINTIFY_SHOP_ID.strip()
    if sid.isdigit():
        return sid

    # Auto-detect correct shop
    data = _get("/shops.json")

    # Normalize: API may return list of dicts, dict with 'data', or list of strings
    if isinstance(data, list):
        raw_shops = data
    elif isinstance(data, dict):
        raw_shops = data.get("data", [])
    else:
        raw_shops = []

    if not raw_shops:
        raise ValueError("No Printify shops found for this token.")

    # Normalize each shop entry — handle both dict and string formats
    shops = []
    for item in raw_shops:
        if isinstance(item, dict):
            shops.append(item)
        elif isinstance(item, (int, str)):
            # API returned bare ID — wrap it
            shops.append({"id": item, "title": "", "sales_channel": ""})

    if not shops:
        raise ValueError("Could not parse Printify shops response.")

    # Debug: log all shops found
    import logging
    log = logging.getLogger("bif.printify")
    for s in shops:
        log.info("Printify shop found: id=%s title=%s channel=%s",
                 s.get("id"), s.get("title"), s.get("sales_channel"))

    # Priority 1: exact title match from env (default: bakabo.club)
    target_title = PRINTIFY_SHOP_TITLE.lower().strip()
    for shop in shops:
        title = str(shop.get("title", "")).lower().strip()
        if title == target_title or target_title in title:
            return str(shop["id"])

    # Priority 2: sales_channel contains bakabo
    for shop in shops:
        channel = str(shop.get("sales_channel", "")).lower()
        if "bakabo" in channel:
            return str(shop["id"])

    # Priority 3: any field contains bakabo
    for shop in shops:
        combined = " ".join(str(v) for v in shop.values()).lower()
        if "bakabo" in combined:
            return str(shop["id"])

    # Priority 4: skip Etsy / expired stores, pick first connected
    for shop in shops:
        title   = str(shop.get("title", "")).lower()
        channel = str(shop.get("sales_channel", "")).lower()
        if "etsy" not in title and "etsy" not in channel:
            return str(shop["id"])

    # Fallback: first shop
    return str(shops[0]["id"])


def load_products(page: int = 1, limit: int = 20) -> list[dict]:
    """Return list of products from the Printify shop (all statuses)."""
    data = _get(f"/shops/{resolve_shop_id()}/products.json", params={"page": page, "limit": limit})
    if isinstance(data, list):
        raw = data
    elif isinstance(data, dict):
        raw = data.get("data", [])
    else:
        raw = []
    # Ensure every item is a dict before returning
    return [p for p in raw if isinstance(p, dict)]


def is_published(product: dict) -> bool:
    """Return True if the product is published on the Shopify sales channel.

    Printify API v1 does not return a simple published flag — we check:
    1. sales_channel_properties list
    2. top-level 'published' boolean
    3. external.id present (product was pushed to Shopify)
    4. visible flag
    """
    # 1. sales_channel_properties (most reliable)
    channels = product.get("sales_channel_properties", [])
    if channels:
        return any(
            ch.get("published", False)
            for ch in channels
            if isinstance(ch, dict)
        )

    # 2. top-level published flag
    if "published" in product:
        return bool(product["published"])

    # 3. external.id — product was pushed to Shopify
    external = product.get("external", {})
    if external and external.get("id"):
        return True

    # 4. visible flag
    if product.get("visible") is False:
        return False

    # 5. If none of the above — assume unpublished (safer default)
    return False


def is_bks_product(product: dict) -> bool:
    """Return True only if the title starts with BKS (brand filter)."""
    title = product.get("title", "")
    return title.strip().upper().startswith("BKS")


def load_all_products(published_only: bool = True,
                      bks_only: bool = True) -> list[dict]:
    """Paginate through all products and return filtered list.

    Args:
        published_only: if True (default), return only products pushed to Shopify.
        bks_only:       if True (default), return only products whose title
                        starts with "BKS" (brand safety filter).
    """
    products = []
    page = 1
    while True:
        batch = load_products(page=page, limit=20)
        if not batch:
            break
        if bks_only:
            batch = [p for p in batch if is_bks_product(p)]
        if published_only:
            batch = [p for p in batch if is_published(p)]
        products.extend(batch)
        page += 1
    return products


def load_variants(product_id: str) -> list[dict]:
    """Return variants for a specific product."""
    data = _get(f"/shops/{resolve_shop_id()}/products/{product_id}.json")
    if not isinstance(data, dict):
        return []
    product = data.get("product", data)  # some versions wrap in {"product": {...}}
    return [v for v in product.get("variants", []) if isinstance(v, dict)]


def download_mockups(product: dict, dest_dir: Path = SOURCE_DIR) -> list[Path]:
    """Download all mockup images for a product. Returns list of saved paths."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    slug = _safe_slug(product.get("title", product["id"]))
    saved = []
    for i, img in enumerate(product.get("images", []), 1):
        if not isinstance(img, dict):
            continue
        url = img.get("src", "")
        if not url:
            continue
        ext = url.split("?")[0].rsplit(".", 1)[-1] or "jpg"
        path = dest_dir / f"{slug}_mockup_{i:02d}.{ext}"
        if not path.exists():
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            path.write_bytes(resp.content)
        saved.append(path)
    return saved


def download_design_files(product: dict, dest_dir: Path = SOURCE_DIR) -> list[Path]:
    """Download design source files if available."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    slug = _safe_slug(product.get("title", product["id"]))
    saved = []
    for i, pf in enumerate(product.get("print_areas", []), 1):
        for j, pfile in enumerate(pf.get("placeholders", []), 1):
            for k, img in enumerate(pfile.get("images", []), 1):
                url = img.get("src", "")
                if not url:
                    continue
                ext = url.split("?")[0].rsplit(".", 1)[-1] or "png"
                path = dest_dir / f"{slug}_design_{i:02d}_{j:02d}_{k:02d}.{ext}"
                if not path.exists():
                    resp = requests.get(url, timeout=60)
                    resp.raise_for_status()
                    path.write_bytes(resp.content)
                saved.append(path)
    return saved


def extract_product_info(product: dict) -> dict:
    """Extract normalized info from a Printify product dict."""
    if not isinstance(product, dict):
        return {}
    return {
        "id":          product.get("id"),
        "title":       product.get("title", ""),
        "description": product.get("description", ""),
        "tags":        product.get("tags", []),
        "variants":    product.get("variants", []),
        "images":      product.get("images", []),
        "slug":        _safe_slug(product.get("title", "")),
    }


def _safe_slug(s: str) -> str:
    import re
    s = re.sub(r"[™®©]", "", s)
    s = re.sub(r"[^a-zA-Z0-9\s\-]", "", s)
    s = re.sub(r"\s+", "-", s.strip()).lower()
    return s[:80]
