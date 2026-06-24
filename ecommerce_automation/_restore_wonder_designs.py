"""Restore original wonder designs to Printify products updated by the OpenAI pipeline.

Strategy:
  - Products with BAKABO_IMAGE_FACTORY manifests: restore exact original wonder ID (no upload needed)
  - All others: upload a wonder image from I:\BKS database wonder pool, assign deterministically

Usage:
  python _restore_wonder_designs.py [--dry-run] [--limit N] [--collection COL]
"""
import argparse, base64, json, time, sys, requests
from pathlib import Path

ROOT       = Path(__file__).resolve().parent.parent
WONDER_DIR = Path("I:/BKS database/BKS_ORGANIZED_20260615_225737/01_NFT/_Senza_collezione/Generico")
FACTORY    = ROOT / "BAKABO_IMAGE_FACTORY_v1.1/output/printify_library/designs"
LOG_PATH   = ROOT / "ecommerce_automation/design_batch_log.json"
OUT_PATH   = ROOT / "output/wonder_restore_log.json"

env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

TOKEN  = env["PRINTIFY_API_TOKEN"]
SHOP   = "12030061"
HDR    = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
BASE   = "https://api.printify.com/v1"

# PROTECTED logo IDs - never replace these
LOGO_IDS = {
    "6a217ca23d24179e1f1eaf5f",  # bks.png
    "660d81c6209c2958d2f0bb75",  # LG 002.png
}

# --------------------------------------------------
# Build manifest lookup: printify_product_id -> wonder_id
# --------------------------------------------------
MANIFEST_MAP: dict[str, str] = {}  # product_id -> original_wonder_printify_id
for m_path in FACTORY.glob("*/*/manifest.json"):
    try:
        m = json.loads(m_path.read_text(encoding="utf-8"))
        pid = m.get("product_id") or m.get("handle")
        if not pid:
            continue
        for d in m.get("designs", []):
            if "wonder" in d.get("name", "").lower() and d.get("id"):
                MANIFEST_MAP[pid] = d["id"]
                break
    except Exception:
        pass

# --------------------------------------------------
# Load wonder pool from local archive (sorted for determinism)
# --------------------------------------------------
WONDER_POOL = sorted(WONDER_DIR.glob("wonder_*.jpg"), key=lambda p: p.name)
print(f"Wonder pool: {len(WONDER_POOL)} files from {WONDER_DIR}")
print(f"Manifest coverage: {len(MANIFEST_MAP)} products with exact original IDs")

def upload_wonder(jpg_path: Path) -> str | None:
    """Upload a wonder JPEG to Printify, return image ID."""
    img_b64 = base64.b64encode(jpg_path.read_bytes()).decode()
    payload = {"file_name": jpg_path.name, "contents": img_b64}
    r = requests.post(f"{BASE}/uploads/images.json",
        data=json.dumps(payload), headers=HDR, verify=False, timeout=60)
    return r.json().get("id") if r.ok else None

def restore_product(prod_id: str, new_img_id: str, restore_img_id: str, dry: bool) -> dict:
    """Replace new_img_id with restore_img_id in product's print_areas."""
    if dry:
        return {"status": "dry_run", "would_replace": new_img_id, "with": restore_img_id}

    # Fetch current product
    r = requests.get(f"{BASE}/shops/{SHOP}/products/{prod_id}.json",
        headers=HDR, verify=False, timeout=20)
    if not r.ok:
        return {"status": "error", "msg": f"Fetch failed {r.status_code}"}

    prod = r.json()
    print_areas = prod.get("print_areas", [])
    replaced = 0

    for area in print_areas:
        for ph in area.get("placeholders", []):
            for img in ph.get("images", []):
                iid = img.get("id", "")
                if iid == new_img_id and iid not in LOGO_IDS:
                    img["id"] = restore_img_id
                    replaced += 1

    if replaced == 0:
        return {"status": "skipped", "msg": f"new_img_id {new_img_id} not found in print_areas"}

    clean_areas = [
        {**a, "placeholders": [p for p in a.get("placeholders", []) if p.get("images")]}
        for a in print_areas
        if any(p.get("images") for p in a.get("placeholders", []))
    ]

    upd = requests.put(f"{BASE}/shops/{SHOP}/products/{prod_id}.json",
        headers=HDR, json={"print_areas": clean_areas}, verify=False, timeout=30)
    if not upd.ok:
        return {"status": "error", "msg": f"Update failed: {upd.text[:200]}"}

    return {"status": "restored", "replaced": replaced, "restore_img_id": restore_img_id}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Simulate only")
    ap.add_argument("--limit",   type=int, default=0, help="Max products to process")
    ap.add_argument("--collection", default="", help="Filter by collection (e.g. glyph)")
    args = ap.parse_args()

    log = json.loads(LOG_PATH.read_text(encoding="utf-8"))
    targets = [
        (pid, v) for pid, v in log.items()
        if v.get("status") == "updated"
        and (not args.collection or v.get("collection", "").lower() == args.collection.lower())
    ]

    if args.limit:
        targets = targets[:args.limit]

    print(f"\nProducts to restore: {len(targets)}")
    print(f"  - Exact (manifest):  {sum(1 for pid,_ in targets if pid in MANIFEST_MAP)}")
    print(f"  - Fresh wonder pool: {sum(1 for pid,_ in targets if pid not in MANIFEST_MAP)}")
    print()

    if args.dry_run:
        print("[DRY RUN — no changes will be made]\n")

    restore_log: dict[str, dict] = {}
    wonder_idx = 0  # rolling index into wonder pool (deterministic, not random)

    for i, (pid, entry) in enumerate(targets, 1):
        title = entry.get("title", "?")[:50]
        new_img_id = entry.get("result", {}).get("new_image_id", "")
        col = entry.get("collection", "?")

        if not new_img_id:
            print(f"  SKIP  [{i:3d}] {title[:40]}  (no new_image_id)")
            restore_log[pid] = {"status": "skip", "reason": "no new_image_id"}
            continue

        # Determine restore image ID
        if pid in MANIFEST_MAP:
            restore_id = MANIFEST_MAP[pid]
            source     = "manifest"
        else:
            # Upload next wonder from pool
            if wonder_idx >= len(WONDER_POOL):
                print(f"  ERROR  Wonder pool exhausted at idx {wonder_idx}")
                restore_log[pid] = {"status": "error", "reason": "wonder_pool_exhausted"}
                continue
            w_path = WONDER_POOL[wonder_idx]
            wonder_idx += 1
            if not args.dry_run:
                restore_id = upload_wonder(w_path)
                if not restore_id:
                    print(f"  ERROR  [{i:3d}] Upload wonder failed for {pid}")
                    restore_log[pid] = {"status": "error", "reason": "upload_failed"}
                    continue
                time.sleep(0.4)
            else:
                restore_id = f"WOULD_UPLOAD:{w_path.name}"
            source = f"pool:{w_path.name}"

        result = restore_product(pid, new_img_id, restore_id, args.dry_run)
        status = result.get("status","?")
        flag   = "OK " if status in ("restored","dry_run") else ("SKIP" if status == "skipped" else "ERR ")
        print(f"  {flag}  [{i:3d}] {col:8s}  {title[:42]:42s}  [{source[:30]}]")

        restore_log[pid] = {
            "collection": col,
            "title": title,
            "new_img_id": new_img_id,
            "restore_id": restore_id,
            "source": source,
            **result,
        }

        if not args.dry_run:
            time.sleep(0.5)

    # Save restore log
    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text(json.dumps(restore_log, indent=2))

    ok    = sum(1 for v in restore_log.values() if v.get("status") in ("restored","dry_run"))
    errs  = sum(1 for v in restore_log.values() if v.get("status") == "error")
    skips = sum(1 for v in restore_log.values() if v.get("status") in ("skip","skipped"))
    print(f"\nDone: {ok} restored, {errs} errors, {skips} skipped")
    print(f"Log: {OUT_PATH}")


if __name__ == "__main__":
    main()
