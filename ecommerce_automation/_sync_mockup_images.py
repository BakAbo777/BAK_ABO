"""Sync Printify mockup images → Shopify product images for all updated products.

For each product with status='updated' in the pipeline log:
1. Fetch current mockup URLs from Printify (always reflect current design)
2. Replace Shopify product images with these mockups (max 6)

Safe: keeps product data, variants, prices intact. Only replaces images.
"""
import json, time, requests, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

PRINTIFY_TOKEN   = env["PRINTIFY_API_TOKEN"]
SHOPIFY_DOMAIN   = env["SHOPIFY_MYSHOPIFY_DOMAIN"]
SHOPIFY_TOKEN    = env["SHOPIFY_ADMIN_TOKEN"]
PRINTIFY_SHOP_ID = "12030061"
SHOPIFY_API      = "2025-01"

PH = {"Authorization": f"Bearer {PRINTIFY_TOKEN}"}
SH = {"X-Shopify-Access-Token": SHOPIFY_TOKEN, "Content-Type": "application/json"}

LOG_PATH = ROOT / "ecommerce_automation/design_batch_log.json"
OUT_PATH = ROOT / "output/mockup_sync_log.json"

# Camera priority: show front first, then person shot, then back, then details
CAMERA_PRIORITY = ["front", "front-person", "back", "back-person", "detail", "side"]

def camera_rank(img: dict) -> int:
    label = img.get("src", "")
    for i, kw in enumerate(CAMERA_PRIORITY):
        if kw in label:
            return i
    return 99

def fetch_printify_product(printify_id: str) -> dict | None:
    """Fetch Printify product with retry on timeout."""
    for attempt in range(3):
        try:
            r = requests.get(
                f"https://api.printify.com/v1/shops/{PRINTIFY_SHOP_ID}/products/{printify_id}.json",
                headers=PH, verify=False, timeout=45,
            )
            if r.ok:
                return r.json()
            if r.status_code == 429:
                time.sleep(5)
                continue
        except requests.exceptions.Timeout:
            time.sleep(3 * (attempt + 1))
    return None

def get_mockups_from_product(prod_data: dict) -> list[str]:
    """Extract sorted mockup URLs from a Printify product dict."""
    images = prod_data.get("images", [])
    images.sort(key=lambda img: (0 if img.get("is_default") else 1, camera_rank(img)))
    return [img["src"] for img in images[:6]]

def replace_shopify_images(shopify_id: str, new_srcs: list[str]) -> dict:
    """Replace all Shopify product images with new_srcs."""
    base = f"https://{SHOPIFY_DOMAIN}/admin/api/{SHOPIFY_API}/products/{shopify_id}"

    # 1. Get existing image IDs
    r = requests.get(f"{base}/images.json", params={"limit": 50}, headers=SH, verify=False, timeout=15)
    if not r.ok:
        return {"status": "error", "msg": f"Get images failed {r.status_code}"}
    old_images = r.json().get("images", [])

    # 2. Delete all existing images
    for img in old_images:
        requests.delete(f"{base}/images/{img['id']}.json", headers=SH, verify=False, timeout=15)
        time.sleep(0.15)

    # 3. Upload new images from Printify URLs (Shopify downloads and hosts on CDN)
    uploaded = []
    for pos, src in enumerate(new_srcs, 1):
        payload = {"image": {"src": src, "position": pos}}
        r = requests.post(f"{base}/images.json", headers=SH, json=payload, verify=False, timeout=30)
        if r.ok:
            uploaded.append(r.json().get("image", {}).get("src", "")[:60])
        else:
            uploaded.append(f"ERR:{r.status_code}")
        time.sleep(0.3)

    return {"status": "ok", "uploaded": len(uploaded), "srcs": uploaded}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run",    action="store_true", help="Show what would happen, no changes")
    ap.add_argument("--limit",      type=int, default=0, help="Max products to process")
    ap.add_argument("--collection", default="",          help="Filter by collection (e.g. glyph)")
    args = ap.parse_args()

    log = json.loads(LOG_PATH.read_text(encoding="utf-8"))
    targets = [
        (pid, v) for pid, v in log.items()
        if v.get("status") == "updated"
        and (not args.collection or v.get("collection", "").lower() == args.collection.lower())
    ]
    if args.limit:
        targets = targets[:args.limit]

    print(f"Products to sync: {len(targets)}")
    if args.dry_run:
        print("[DRY RUN]\n")

    sync_log = {}
    ok = err = skip = 0

    # Load existing sync log for resume support
    if OUT_PATH.exists():
        try:
            existing = json.loads(OUT_PATH.read_text(encoding="utf-8"))
            already_done = {k for k, v in existing.items() if v.get("status") in ("ok", "dry_run")}
            sync_log.update(existing)
        except Exception:
            already_done = set()
    else:
        already_done = set()

    if already_done:
        print(f"Resume: skipping {len(already_done)} already processed")

    for i, (pid, entry) in enumerate(targets, 1):
        title = entry.get("title", "?")[:50]
        col   = entry.get("collection", "?")

        # Skip already processed
        if pid in already_done:
            print(f"  SKIP [{i:3d}] {col:8s}  {title[:40]:40s}  (already done)")
            continue

        # Single fetch: get both shopify_id and mockup images in one call
        prod_data = fetch_printify_product(pid)
        if not prod_data:
            print(f"  ERR  [{i:3d}] {title[:42]}  (Printify fetch failed)")
            err += 1
            sync_log[pid] = {"status": "error", "msg": "printify_fetch_failed"}
            continue

        shopify_id  = prod_data.get("external", {}).get("id")
        mockup_urls = get_mockups_from_product(prod_data)

        if not shopify_id:
            print(f"  SKIP [{i:3d}] {title[:42]}  (no Shopify external ID)")
            skip += 1
            sync_log[pid] = {"status": "skip", "msg": "no_shopify_id"}
            time.sleep(0.3)
            continue

        if not mockup_urls:
            print(f"  SKIP [{i:3d}] {title[:42]}  (no mockup images)")
            skip += 1
            sync_log[pid] = {"status": "skip", "msg": "no_mockups"}
            time.sleep(0.3)
            continue

        if args.dry_run:
            print(f"  DRY  [{i:3d}] {col:8s}  {title[:40]:40s}  {len(mockup_urls)} mockups")
            sync_log[pid] = {"status": "dry_run", "mockup_count": len(mockup_urls)}
            continue

        result = replace_shopify_images(str(shopify_id), mockup_urls)
        if result["status"] == "ok":
            print(f"  OK   [{i:3d}] {col:8s}  {title[:40]:40s}  {result['uploaded']}/{len(mockup_urls)} images synced")
            ok += 1
        else:
            print(f"  ERR  [{i:3d}] {col:8s}  {title[:40]:40s}  {result['msg']}")
            err += 1

        sync_log[pid] = {"collection": col, "title": title, "shopify_id": shopify_id, **result}
        # Write after each product — safe resume if crash
        OUT_PATH.parent.mkdir(exist_ok=True)
        OUT_PATH.write_text(json.dumps(sync_log, indent=2))
        time.sleep(0.6)

    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text(json.dumps(sync_log, indent=2))

    print(f"\nDone: {ok} synced, {err} errors, {skip} skipped")
    print(f"Log: {OUT_PATH}")


if __name__ == "__main__":
    main()
