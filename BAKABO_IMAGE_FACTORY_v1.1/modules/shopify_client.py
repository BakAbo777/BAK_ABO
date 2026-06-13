"""BKS Studio — Shopify Admin API client."""
import requests
import base64
import csv
import io
from pathlib import Path
from config.settings import SHOPIFY_STORE, SHOPIFY_ACCESS_TOKEN

BASE    = f"https://{SHOPIFY_STORE}/admin/api/2024-01"
HEADERS = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    "Content-Type":           "application/json",
}


def _get(path: str, params: dict = None) -> dict:
    r = requests.get(f"{BASE}{path}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def _post(path: str, payload: dict) -> dict:
    r = requests.post(f"{BASE}{path}", headers=HEADERS, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()


def _put(path: str, payload: dict) -> dict:
    r = requests.put(f"{BASE}{path}", headers=HEADERS, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()


# ── Products ──────────────────────────────────────────────────────────────────

def get_product(product_id: str) -> dict:
    return _get(f"/products/{product_id}.json")["product"]


def update_seo(product_id: str, seo_title: str, seo_description: str) -> dict:
    return _put(f"/products/{product_id}.json", {
        "product": {
            "id":               product_id,
            "metafields_global_title_tag":       seo_title[:70],
            "metafields_global_description_tag": seo_description[:160],
        }
    })["product"]


def upload_image(product_id: str, image_path: Path, alt: str = "", position: int = 1) -> dict:
    """Upload a local image file to a Shopify product."""
    data = image_path.read_bytes()
    b64  = base64.b64encode(data).decode()
    return _post(f"/products/{product_id}/images.json", {
        "image": {
            "attachment": b64,
            "filename":   image_path.name,
            "alt":        alt[:512],
            "position":   position,
        }
    })["image"]


def update_tags(product_id: str, tags: list[str]) -> dict:
    tag_str = ",".join(tags)
    return _put(f"/products/{product_id}.json", {
        "product": {"id": product_id, "tags": tag_str}
    })["product"]


def assign_collection(product_id: str, collection_id: str) -> dict:
    return _post("/collects.json", {
        "collect": {"product_id": product_id, "collection_id": collection_id}
    })


# ── Export ────────────────────────────────────────────────────────────────────

def build_shopify_csv(assets: list[dict]) -> str:
    """Generate a Shopify-compatible CSV for image import.

    Each dict in assets should have:
      handle, image_src, image_position, image_alt_text
    """
    fields = ["Handle", "Image Src", "Image Position", "Image Alt Text"]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for a in assets:
        writer.writerow({
            "Handle":           a.get("handle", ""),
            "Image Src":        a.get("image_src", ""),
            "Image Position":   a.get("image_position", 1),
            "Image Alt Text":   a.get("image_alt", ""),
        })
    return output.getvalue()
