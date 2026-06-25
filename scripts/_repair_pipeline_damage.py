"""
_repair_pipeline_damage.py
==========================
Ripara il danno della pipeline OpenAI del 24/06/2026:

  Step 1: Pubblica i 13 prodotti 'updated' (score≥20) rimasti in bozza
  Step 2: Unpubblica i prodotti 'needs_rework' (score≤19) ancora visibili
           con design sbagliato

Uso:
  python scripts/_repair_pipeline_damage.py --dry-run    # mostra solo cosa farebbe
  python scripts/_repair_pipeline_damage.py              # applica le correzioni
"""
import argparse, json, sys, time
from pathlib import Path
import requests
requests.packages.urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = ROOT / "ecommerce_automation" / "design_batch_log.json"

env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

TOKEN   = env.get("PRINTIFY_API_TOKEN", "")
SHOP_ID = "12030061"
HDR     = {"Authorization": f"Bearer {TOKEN}"}
BASE    = "https://api.printify.com/v1"

def load_log():
    return json.loads(LOG_PATH.read_text(encoding="utf-8")) if LOG_PATH.exists() else {}

def get_all_products():
    """Fetch all products from Printify (all pages)."""
    products = []
    for page in range(1, 40):
        r = requests.get(f"{BASE}/shops/{SHOP_ID}/products.json?limit=20&page={page}",
            headers=HDR, verify=False, timeout=30)
        if not r.ok:
            print(f"  Error page {page}: {r.status_code}")
            break
        data = r.json().get("data", [])
        if not data:
            break
        products.extend(data)
    return products

def set_publish_status(product_id: str, publish: bool) -> bool:
    """Set product visible=True (publish) or visible=False (draft) in Printify."""
    endpoint = "publish.json" if publish else "unpublish.json"
    payload = {
        "title": True,
        "description": True,
        "images": True,
        "variants": True,
        "tags": True,
    } if publish else {}

    r = requests.post(
        f"{BASE}/shops/{SHOP_ID}/products/{product_id}/{endpoint}",
        headers={**HDR, "Content-Type": "application/json"},
        json=payload,
        verify=False, timeout=30,
    )
    return r.status_code in (200, 201, 204)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    log = load_log()
    dry = args.dry_run

    if dry:
        print("[DRY RUN] — nessuna modifica applicata\n")

    # Build index by product_id
    updated_ids   = {pid for pid, v in log.items() if v.get("status") == "updated"}
    rework_ids    = {pid for pid, v in log.items() if v.get("status") == "needs_rework"}
    restored_ids  = {pid for pid, v in log.items() if v.get("status") == "restored_phase1"}

    print("Caricamento prodotti Printify...")
    products = get_all_products()
    print(f"  {len(products)} prodotti trovati\n")

    to_publish   = []  # updated + in draft → publish
    to_unpublish = []  # needs_rework + published → unpublish

    for p in products:
        pid = p["id"]
        vis = p.get("visible", False)
        title = p.get("title", "?")
        score = 0
        if pid in log:
            r = log[pid].get("result", {})
            score = r.get("bks_score", 0) if isinstance(r, dict) else 0

        if pid in updated_ids and not vis:
            to_publish.append((pid, title, score))
        elif pid in rework_ids and vis:
            to_unpublish.append((pid, title, score))

    # ── Step 1: Publish good products in draft ─────────────────────────────────
    print(f"STEP 1 — Pubblicazione prodotti 'updated' in bozza: {len(to_publish)}")
    pub_ok = pub_err = 0
    for pid, title, score in sorted(to_publish, key=lambda x: -x[2]):
        print(f"  {'[DRY]' if dry else 'PUB'} score={score} {pid[-6:]} {title[:55]}")
        if not dry:
            ok = set_publish_status(pid, publish=True)
            if ok:
                pub_ok += 1
            else:
                pub_err += 1
                print(f"    ERRORE publish")
            time.sleep(0.4)

    if not dry:
        print(f"  → OK: {pub_ok}  ERR: {pub_err}")

    print()

    # ── Step 2: Unpublish bad designs currently live ───────────────────────────
    print(f"STEP 2 — Unpublish prodotti 'needs_rework' visibili (design score<=19): {len(to_unpublish)}")
    unp_ok = unp_err = 0
    for pid, title, score in sorted(to_unpublish, key=lambda x: x[2]):
        print(f"  {'[DRY]' if dry else 'DRF'} score={score} {pid[-6:]} {title[:55]}")
        if not dry:
            ok = set_publish_status(pid, publish=False)
            if ok:
                unp_ok += 1
            else:
                unp_err += 1
                print(f"    ERRORE unpublish")
            time.sleep(0.4)

    if not dry:
        print(f"  → OK: {unp_ok}  ERR: {unp_err}")

    print()
    print("=" * 60)
    print(f"Pubblicati (step 1): {len(to_publish)}")
    print(f"Nascosti   (step 2): {len(to_unpublish)}")
    print()
    print("NEXT STEP:")
    print(f"  {len(rework_ids)} prodotti 'needs_rework' hanno design score<=19")
    print("  Per rigenerare i design:")
    print("  → python scripts/_production_pipeline.py --retry-rework --workers 2")

if __name__ == "__main__":
    main()
