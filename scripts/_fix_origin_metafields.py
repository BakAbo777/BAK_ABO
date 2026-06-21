"""Fix: update bks.collection from 'Folklore' -> 'BKS Origin' for all Origin products.
Also creates the metafield where missing.
Run with --apply (default is dry-run).
"""
import os, sys, time, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()  # type: ignore
DRY_RUN = "--apply" not in sys.argv

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "") or os.environ.get("SHOPIFY_API_TOKEN", "")
BASE   = f"https://{DOMAIN}/admin/api/2025-01"
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
print(f"Shop: {DOMAIN} | DRY_RUN={DRY_RUN}")

# (product_id, meta_id_or_None) from scan
TARGETS = [
    (10845887365458, 68759886627154),
    (8644176019794,  68736801145170),
    (8645083726162,  68736800817490),
    (8644176314706,  68736800981330),
    (8644175987026,  68736801505618),
    (8928008536402,  68736776733010),
    (8801495843154,  68736784531794),
    (8801597194578,  68736783384914),
    (10841342443858, 68736764051794),
    (8790393782610,  68736789152082),
    (8691525452114,  68736795181394),
    (8682100719954,  68736795541842),
    (8672600359250,  68736797442386),
    (10760782905682, 68736770933074),
    (10033427415378, 68736772440402),
    (10033418305874, 68736772735314),
    (8691523453266,  68736795378002),
    (10829362299218, 68736767033682),
    (8599704371538,  68736804782418),
    (10829454868818, 68736766804306),
    (8600109089106,  68736804553042),
    (8882766119250,  68736778862930),
    (8620202852690,  68736802128210),
    (10772883145042, 68736769917266),
    (10866561548626, None),            # BKS Tee Origin — no metafield yet
]

ok = 0; errors = []
for pid, mid in TARGETS:
    if DRY_RUN:
        action = "PUT" if mid else "POST"
        print(f"  DRY [{action}] product {pid} -> bks.collection=BKS Origin")
        continue
    if mid:
        r = requests.put(
            f"{BASE}/products/{pid}/metafields/{mid}.json",
            headers=HDR, verify=False, timeout=20,
            json={"metafield": {"id": mid, "value": "BKS Origin", "type": "single_line_text_field"}}
        )
    else:
        r = requests.post(
            f"{BASE}/products/{pid}/metafields.json",
            headers=HDR, verify=False, timeout=20,
            json={"metafield": {"namespace": "bks", "key": "collection", "value": "BKS Origin", "type": "single_line_text_field"}}
        )
    status = "OK" if r.ok else f"ERR {r.status_code}"
    print(f"  [{status}] product {pid}")
    if r.ok: ok += 1
    else: errors.append(f"{pid}: {r.text[:80]}")
    time.sleep(0.3)

if not DRY_RUN:
    print(f"\nDone: {ok}/{len(TARGETS)} OK, {len(errors)} errors")
    for e in errors: print(f"  {e}")
else:
    print(f"\n[DRY RUN] {len(TARGETS)} products would be updated. Run with --apply to write.")
