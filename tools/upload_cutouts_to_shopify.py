"""Upload processed cutout images from Image Factory to Shopify products.

Only uploads if:
 - Shopify product handle exists in live CSV
 - cutout PNG exists in BAKABO_IMAGE_FACTORY_v1.1/output/cutout/{slug}/
 - product doesn't already have an uploaded cutout (checks image alt text)

Run: python tools/upload_cutouts_to_shopify.py [--dry-run] [--limit N]
"""
from __future__ import annotations
import os, sys, time, csv, base64, argparse, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent.parent

for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ:
        os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VER     = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE    = f"https://{DOMAIN}/admin/api/{VER}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

FACTORY_DIR = ROOT / "BAKABO_IMAGE_FACTORY_v1.1" / "output" / "cutout"
SHOPIFY_CSV = ROOT / "output" / "live_shopify_products.csv"

CUTOUT_KEYS = ["cutout_safe", "white_bg", "commercial_bg"]  # priority order


def _shopify_products() -> dict[str, str]:
    """Returns handle -> id from live CSV."""
    if not SHOPIFY_CSV.exists():
        print("Run _fetch_shopify.py first to populate the live CSV.")
        sys.exit(1)
    result = {}
    with open(SHOPIFY_CSV, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            result[row["handle"]] = row.get("id", "")
    return result


def _get_product_images(product_id: str) -> list[dict]:
    r = requests.get(
        f"{BASE}/products/{product_id}/images.json",
        headers=HDR, params={"fields": "id,alt,src"}, timeout=15, verify=False
    )
    if r.ok:
        return r.json().get("images", [])
    return []


def _has_cutout_already(images: list[dict]) -> bool:
    return any("cutout" in (img.get("alt") or "").lower() for img in images)


def _find_cutout_png(slug: str) -> Path | None:
    cutout_dir = FACTORY_DIR / slug
    if not cutout_dir.exists():
        return None
    for key in CUTOUT_KEYS:
        for ext in (".png", ".jpg", ".webp"):
            candidate = cutout_dir / f"{slug}_{key}{ext}"
            if candidate.exists():
                return candidate
    for f in sorted(cutout_dir.glob("*.png")):
        if "edge_review" not in f.name and "alpha_mask" not in f.name:
            return f
    return None


def _upload_image(product_id: str, img_path: Path, alt: str) -> dict | None:
    data = img_path.read_bytes()
    b64  = base64.b64encode(data).decode()
    payload = {
        "image": {
            "attachment": b64,
            "filename":   img_path.name,
            "alt":        alt[:512],
            "position":   2,
        }
    }
    for attempt in range(3):
        r = requests.post(
            f"{BASE}/products/{product_id}/images.json",
            headers=HDR, json=payload, timeout=120, verify=False
        )
        if r.status_code == 429:
            time.sleep(2 ** attempt + 1)
            continue
        if r.ok:
            return r.json().get("image", {})
        print(f"    ERR [{r.status_code}]: {r.text[:120]}")
        return None
    return None


def _normalize_slug(slug: str, products: dict[str, str]) -> str | None:
    """Try to match a factory slug to a Shopify handle."""
    if slug in products:
        return slug
    # Try stripping bks- prefix (factory adds it, Shopify handle may not have it)
    no_prefix = slug.removeprefix("bks-")
    if no_prefix in products:
        return no_prefix
    # Folklore -> origin mapping (keep bks- prefix if present)
    if "folklore" in slug:
        for candidate in [
            slug.replace("bks-folklore-", "bks-origin-"),
            slug.replace("bks-folklore-", "folklore-"),  # strip bks- + keep folklore
            slug.replace("folklore-", "origin-"),
            no_prefix.replace("folklore-", ""),
        ]:
            if candidate in products:
                return candidate
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="Max uploads (0 = unlimited)")
    args = parser.parse_args()

    # Load Shopify products
    products = _shopify_products()
    print(f"Shopify products in CSV: {len(products)}")

    # Find all available cutout slugs
    if not FACTORY_DIR.exists():
        print(f"Factory output not found: {FACTORY_DIR}")
        sys.exit(1)
    # Skip mockup subdirs (contain _mockup_)
    cutout_slugs = [
        d.name for d in FACTORY_DIR.iterdir()
        if d.is_dir() and "_mockup_" not in d.name
    ]
    print(f"Cutout directories available: {len(cutout_slugs)}")

    uploaded = skipped = missing_id = missing_png = already_done = 0
    count = 0

    for slug in sorted(cutout_slugs):
        if args.limit and count >= args.limit:
            break

        # Match slug -> Shopify handle (with folklore->origin normalization)
        matched_handle = _normalize_slug(slug, products)
        if not matched_handle:
            missing_id += 1
            continue
        product_id = products[matched_handle]
        if not product_id:
            missing_id += 1
            continue

        # Find the best cutout PNG
        png = _find_cutout_png(slug)
        if not png:
            missing_png += 1
            continue

        # Skip if already has a cutout image
        images = _get_product_images(product_id)
        if _has_cutout_already(images):
            already_done += 1
            continue

        alt = f"{slug.replace('-', ' ').title()} — BKS Studio cutout"
        if args.dry_run:
            print(f"  DRY  {slug} -> {png.name}")
            count += 1
            continue

        print(f"  UP   {slug} -> {png.name} ... ", end="", flush=True)
        result = _upload_image(product_id, png, alt)
        if result:
            print(f"OK (id={result.get('id')})")
            uploaded += 1
        else:
            print("FAILED")
        count += 1
        time.sleep(0.5)

    print(f"\n=== Done: {uploaded} uploaded  |  {already_done} already OK  |  {missing_id} no Shopify ID  |  {missing_png} no PNG ===")


if __name__ == "__main__":
    main()
