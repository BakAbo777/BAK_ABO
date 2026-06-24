"""Generate AI hero shots for all BKS products and upload to Shopify as position 1.

Uses drone_shot_generator.generate_drone_shots() with slot=hero_shot only.
Existing Printify mockup images are kept (shifted to positions 2+).

Resume: checks output directory for existing hero files — skips if already generated.

Usage:
  python scripts/generate_product_heroes.py
  python scripts/generate_product_heroes.py --dry-run
  python scripts/generate_product_heroes.py --collection glyph
  python scripts/generate_product_heroes.py --limit 10
"""
from __future__ import annotations
import os, sys, json, time, argparse, base64
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import requests, urllib3
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ecommerce_automation"))
from drone_shot_generator import generate_drone_shots

# ── env ──────────────────────────────────────────────────────────────────────
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]:
        os.environ[k] = v

OPENAI_KEY    = os.environ["OPENAI_API_KEY"]
SHOPIFY_DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
SHOPIFY_TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
SHOPIFY_API    = os.environ.get("SHOPIFY_API_VERSION", "2025-01")

SH   = {"X-Shopify-Access-Token": SHOPIFY_TOKEN, "Content-Type": "application/json"}
BASE = f"https://{SHOPIFY_DOMAIN}/admin/api/{SHOPIFY_API}"

BATCH_LOG = ROOT / "ecommerce_automation" / "design_batch_log.json"
SYNC_LOG  = ROOT / "output" / "mockup_sync_log.json"
OUT_BASE  = ROOT / "BAKABO_IMAGE_FACTORY_v1.1" / "output" / "generated"
HERO_LOG  = ROOT / "output" / "hero_generation_log.json"

# ── product type → label used in prompt ──────────────────────────────────────
TYPE_LABELS: dict[str, str] = {
    "tee": "T-Shirt", "puffer": "Puffer Jacket", "hoodie": "Pullover Hoodie",
    "lounge_pants": "Lounge Pants", "windbreaker": "Windbreaker Jacket",
    "backpack": "Backpack", "sneakers": "Sneakers", "shorts": "Athletic Shorts",
    "one_piece": "One-Piece Swimsuit", "swim_trunks": "Swim Trunks",
    "travel_bag": "Travel Bag", "beach_towel": "Beach Towel",
    "flip_flops": "Flip Flops", "hawaiian": "Hawaiian Shirt",
    "pullover": "Pullover Hoodie", "dress": "Racerback Dress",
    "cozy_slipper": "Cozy Slipper", "lounge": "Lounge Pants",
}

def guess_product_type(title: str) -> str:
    """Extract product type keyword from title like 'BKS Glyph Cross™ Puffer'."""
    tl = title.lower()
    for key, label in TYPE_LABELS.items():
        if key.replace("_", " ") in tl or label.lower() in tl:
            return label
    # fallback: last word(s)
    parts = title.replace("™","").replace("®","").strip().split()
    return parts[-1] if parts else "Product"


def fetch_shopify_products() -> dict[str, dict]:
    """Return {shopify_id_str: {handle, product_type}} for all products."""
    result = {}
    url = f"{BASE}/products.json"
    params = {"limit": 250, "fields": "id,handle,product_type"}
    while url:
        r = requests.get(url, params=params, headers=SH, verify=False, timeout=30)
        for p in r.json().get("products", []):
            result[str(p["id"])] = {
                "handle":       p.get("handle", ""),
                "product_type": p.get("product_type", ""),
            }
        link = r.headers.get("Link", "")
        url = None
        if 'rel="next"' in link:
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.split(";")[0].strip().strip("<>")
                    params = {}
                    break
    return result


def upload_hero_to_shopify(shopify_id: str, jpg_path: Path) -> dict:
    """Add the hero image at position 1 on the Shopify product (does NOT delete existing)."""
    img_b64 = base64.b64encode(jpg_path.read_bytes()).decode()
    payload = {
        "image": {
            "attachment": img_b64,
            "filename":   jpg_path.name,
            "position":   1,
        }
    }
    r = requests.post(f"{BASE}/products/{shopify_id}/images.json",
        headers=SH, json=payload, verify=False, timeout=30)
    if r.ok:
        img = r.json().get("image", {})
        return {"status": "ok", "image_id": img.get("id"), "src": img.get("src", "")[:60]}
    return {"status": "error", "code": r.status_code, "msg": r.text[:200]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run",    action="store_true")
    ap.add_argument("--collection", default="")
    ap.add_argument("--limit",      type=int, default=0)
    ap.add_argument("--force",      action="store_true", help="Regenerate even if hero already exists")
    args = ap.parse_args()

    # Load logs
    batch = json.loads(BATCH_LOG.read_text(encoding="utf-8"))
    sync  = json.loads(SYNC_LOG.read_text(encoding="utf-8")) if SYNC_LOG.exists() else {}
    hero_log: dict = json.loads(HERO_LOG.read_text(encoding="utf-8")) if HERO_LOG.exists() else {}

    # Build targets: products with status=updated + a shopify_id
    targets = []
    for pid, entry in batch.items():
        if entry.get("status") != "updated":
            continue
        col = entry.get("collection", "unknown")
        if args.collection and col.lower() != args.collection.lower():
            continue
        # Get shopify_id from sync log
        sync_entry = sync.get(pid, {})
        shopify_id = str(sync_entry.get("shopify_id") or "")
        if not shopify_id:
            continue
        title = entry.get("title", "") or sync_entry.get("title", "Unknown Product")
        targets.append({
            "printify_id": pid,
            "shopify_id":  shopify_id,
            "collection":  col,
            "title":       title,
        })

    if args.limit:
        targets = targets[:args.limit]

    # Fetch Shopify product data (handle + type)
    print(f"Fetching Shopify product data...")
    shopify_data = fetch_shopify_products()
    print(f"Found {len(shopify_data)} Shopify products\n")

    print(f"Target products: {len(targets)}")
    if args.dry_run:
        print("[DRY RUN — no API calls]\n")

    ok = skipped = err = 0

    for i, t in enumerate(targets, 1):
        pid        = t["printify_id"]
        shopify_id = t["shopify_id"]
        col        = t["collection"]
        title      = t["title"]
        sp         = shopify_data.get(shopify_id, {})
        handle     = sp.get("handle") or title.lower().replace(" ", "-").replace("™","")
        ptype      = sp.get("product_type") or guess_product_type(title)

        # Check if hero already generated
        hero_path = OUT_BASE / col / handle / f"{handle}-drone-hero_shot.jpg"
        already_done = pid in hero_log and hero_log[pid].get("status") == "ok"

        if already_done and not args.force:
            print(f"  SKIP [{i:3d}] {col:8s}  {title[:42]:42s}  (already done)")
            skipped += 1
            continue

        print(f"  GEN  [{i:3d}] {col:8s}  {title[:42]:42s}")

        # Generate hero_shot
        results = generate_drone_shots(
            product_title  = title,
            product_type   = ptype,
            collection     = col,
            handle         = handle,
            openai_api_key = OPENAI_KEY,
            slots          = ["hero_shot"],
            output_base    = OUT_BASE,
            dry_run        = args.dry_run,
        )

        if args.dry_run:
            ok += 1
            hero_log[pid] = {"status": "dry_run", "collection": col, "title": title}
            continue

        result = results[0] if results else {}
        if result.get("status") != "ok":
            print(f"         ERR generate: {result.get('error','')}")
            err += 1
            hero_log[pid] = {"status": "error", "phase": "generate", "msg": str(result.get("error",""))}
            _save_log(hero_log)
            time.sleep(1)
            continue

        # Upload to Shopify
        jpg = Path(result["path"])
        up  = upload_hero_to_shopify(shopify_id, jpg)
        if up["status"] == "ok":
            print(f"         OK  uploaded → {up['src']}")
            ok += 1
            hero_log[pid] = {"status": "ok", "collection": col, "title": title,
                             "hero_path": str(jpg), "shopify_image_id": up.get("image_id")}
        else:
            print(f"         ERR upload: {up['msg'][:80]}")
            err += 1
            hero_log[pid] = {"status": "error", "phase": "upload", "msg": up["msg"][:200]}

        _save_log(hero_log)
        time.sleep(1.5)  # rate limit buffer

    _save_log(hero_log)
    print(f"\nDone: {ok} generated, {skipped} skipped, {err} errors")
    print(f"Log: {HERO_LOG}")


def _save_log(data: dict):
    HERO_LOG.parent.mkdir(exist_ok=True)
    HERO_LOG.write_text(json.dumps(data, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
