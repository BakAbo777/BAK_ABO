"""
_restore_overwritten.py
=======================
Ripristina i design originali dei prodotti sovrascritti dal pipeline il 23/06/2026.

Fase 1 — 8 prodotti con backup locale (Image Factory):
  Carica il file originale su Printify e lo riassegna al prodotto.

Fase 2 — 126 prodotti senza backup locale:
  Recupera tutti gli upload Printify con data PRIMA del 23/06/2026 18:00
  e tenta il match con i prodotti tramite testo/collezione.
  Genera un report CSV per revisione manuale.

Uso:
  python scripts/_restore_overwritten.py --phase 1       # Ripristina 8 backup locali
  python scripts/_restore_overwritten.py --phase 2       # Report matching upload originali
  python scripts/_restore_overwritten.py --phase 2 --apply  # Applica best-match (pericoloso)
"""

import argparse, json, os, sys, csv, time
from pathlib import Path
import requests

requests.packages.urllib3.disable_warnings()

ROOT = Path(__file__).parent.parent
LOG_PATH   = ROOT / "ecommerce_automation" / "design_batch_log.json"
FACTORY    = ROOT / "BAKABO_IMAGE_FACTORY_v1.1" / "output" / "printify_library" / "designs"
RESTORE_LOG = ROOT / "output" / "restore_log.json"

env = {}
with open(ROOT / ".env", "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if "=" in line and not line.startswith("#"):
            k, _, v = line.strip().partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")

PRINTIFY_TOKEN = env.get("PRINTIFY_API_TOKEN", "")
SHOP_ID = "12030061"
PH = {"Authorization": f"Bearer {PRINTIFY_TOKEN}"}
BASE = "https://api.printify.com/v1"

DAMAGE_CUTOFF = "2026-06-23T18:00:00"  # Pipeline started around this time


def load_log():
    return json.loads(LOG_PATH.read_text(encoding="utf-8")) if LOG_PATH.exists() else {}


def save_restore_log(data: dict):
    RESTORE_LOG.parent.mkdir(exist_ok=True)
    RESTORE_LOG.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def upload_image(filepath: Path) -> str | None:
    """Upload image to Printify, return upload ID."""
    with open(filepath, "rb") as f:
        content = f.read()
    import base64
    b64 = base64.b64encode(content).decode()
    ext = filepath.suffix.lstrip(".")
    mime = "image/png" if ext == "png" else "image/jpeg"
    r = requests.post(f"{BASE}/uploads/images.json",
        headers={**PH, "Content-Type": "application/json"},
        json={"file_name": filepath.name, "contents": b64},
        verify=False, timeout=60)
    if r.ok:
        return r.json().get("id")
    print(f"  ERR upload: {r.status_code} {r.text[:100]}")
    return None


def get_product_print_areas(product_id: str) -> list:
    """Fetch current print_areas for a product."""
    r = requests.get(f"{BASE}/shops/{SHOP_ID}/products/{product_id}.json",
        headers=PH, verify=False, timeout=20)
    if r.ok:
        return r.json().get("print_areas", [])
    return []


def apply_image_to_product(product_id: str, img_id: str) -> bool:
    """Replace ALL design areas with img_id."""
    areas = get_product_print_areas(product_id)
    if not areas:
        print(f"  ERR: no print_areas for {product_id}")
        return False
    replaced = 0
    for area in areas:
        for ph in area.get("placeholders", []):
            for img in ph.get("images", []):
                img["id"] = img_id
                replaced += 1
    clean_areas = [
        {**a, "placeholders": [p for p in a.get("placeholders", []) if p.get("images")]}
        for a in areas if any(p.get("images") for p in a.get("placeholders", []))
    ]
    r = requests.put(f"{BASE}/shops/{SHOP_ID}/products/{product_id}.json",
        headers=PH, json={"print_areas": clean_areas}, verify=False, timeout=30)
    if r.ok:
        print(f"  OK restored {replaced} areas")
        return True
    print(f"  ERR apply: {r.status_code} {r.text[:100]}")
    return False


def phase1():
    """Restore 8 products with local Image Factory backups."""
    log = load_log()
    restore_log = {}

    updated_ids = [k for k, v in log.items() if isinstance(v, dict) and v.get("status") == "updated"]

    print(f"\nPhase 1 — Restore backup locali (Image Factory)")
    print("=" * 60)

    count = 0
    for pid in updated_ids:
        for collection in os.listdir(FACTORY):
            coll_path = FACTORY / collection / pid
            if coll_path.is_dir():
                design_files = sorted([
                    f for f in coll_path.iterdir()
                    if f.suffix in (".jpg", ".png") and "manifest" not in f.name
                ])
                if not design_files:
                    continue
                title = log[pid].get("title", pid)
                print(f"\n[{count+1}] {title}")
                print(f"  ID: {pid}")
                print(f"  File: {design_files[0].name}")

                # Upload original design
                img_id = upload_image(design_files[0])
                if not img_id:
                    restore_log[pid] = {"status": "error", "reason": "upload failed"}
                    continue

                print(f"  Uploaded: {img_id}")

                # Apply to product
                ok = apply_image_to_product(pid, img_id)
                if ok:
                    restore_log[pid] = {
                        "status": "restored",
                        "original_file": design_files[0].name,
                        "restored_image_id": img_id,
                        "title": title,
                    }
                    # Update main log status
                    log[pid]["status"] = "restored_phase1"
                    log[pid]["restored_image_id"] = img_id
                    count += 1
                else:
                    restore_log[pid] = {"status": "error", "reason": "apply failed"}

                time.sleep(1)
                break

    # Save updated log
    LOG_PATH.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    save_restore_log(restore_log)

    print(f"\n{'='*60}")
    print(f"Restored: {count}/8")
    print(f"Log: {RESTORE_LOG}")


def phase2(apply: bool = False):
    """Fetch Printify uploads before damage cutoff, match to products."""
    log = load_log()
    updated = {k: v for k, v in log.items() if isinstance(v, dict) and v.get("status") == "updated"}

    print(f"\nPhase 2 — Analisi upload library Printify ({len(updated)} prodotti da ripristinare)")
    print("=" * 60)
    print(f"Fetching uploads created BEFORE {DAMAGE_CUTOFF}...")

    # Fetch uploads from Printify (paginated)
    old_uploads = []
    page = 1
    while True:
        r = requests.get(f"{BASE}/uploads.json?limit=100&page={page}",
            headers=PH, verify=False, timeout=30)
        if not r.ok:
            print(f"  ERR uploads: {r.status_code}")
            break
        batch = r.json().get("data", [])
        if not batch:
            break
        for upload in batch:
            created = upload.get("created_at", "")
            if created < DAMAGE_CUTOFF:
                old_uploads.append(upload)
        # Stop if all remaining uploads are after cutoff (sorted desc)
        if batch and batch[-1].get("created_at", "") < "2026-01-01":
            break
        if len(batch) < 100:
            break
        page += 1
        time.sleep(0.2)

    print(f"Upload originali trovati: {len(old_uploads)}")

    # Generate CSV report
    report_path = ROOT / "output" / "restore_phase2_report.csv"
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["product_id", "product_title", "collection", "new_image_id",
                    "best_match_upload_id", "best_match_filename", "best_match_date",
                    "confidence", "action"])

        for pid, v in updated.items():
            title = v.get("title", "?")
            collection = v.get("collection", "?")
            new_img = v.get("result", {}).get("new_image_id", "")

            # Find best matching upload
            # Match by: 1) collection name in filename, 2) wonder pattern, 3) before cutoff
            matches = []
            for up in old_uploads:
                fname = up.get("file_name", "").lower()
                score = 0
                if collection.lower() in fname:
                    score += 3
                if "wonder" in fname:
                    score += 2
                if up.get("id", "") != new_img:
                    score += 1
                if score > 0:
                    matches.append((score, up))

            matches.sort(key=lambda x: -x[0])
            if matches:
                best_score, best_up = matches[0]
                confidence = "HIGH" if best_score >= 5 else ("MED" if best_score >= 3 else "LOW")
                w.writerow([pid, title, collection, new_img,
                            best_up.get("id"), best_up.get("file_name"),
                            best_up.get("created_at", "")[:10],
                            confidence,
                            "REVIEW"])
                if apply and confidence == "HIGH":
                    print(f"\n  Applying to {title[:40]}...")
                    ok = apply_image_to_product(pid, best_up["id"])
                    if ok:
                        w.writerow([])  # note applied
                        log[pid]["status"] = "restored_phase2"
                        log[pid]["restored_image_id"] = best_up["id"]
            else:
                w.writerow([pid, title, collection, new_img, "", "", "", "NONE", "MANUAL"])

    if apply:
        LOG_PATH.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nReport generato: {report_path}")
    print(f"Revisiona il CSV e usa --apply per applicare i match HIGH-confidence")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=int, default=1, choices=[1, 2])
    parser.add_argument("--apply", action="store_true", help="Applica il ripristino (solo phase 2 HIGH-confidence)")
    args = parser.parse_args()

    if args.phase == 1:
        phase1()
    else:
        phase2(apply=args.apply)
