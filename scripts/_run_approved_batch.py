"""
BKS Design Batch — prodotti approvati (pubblicati + draft con TM).
Approvato = "™" nel titolo Printify.

Pipeline per ogni prodotto:
  Worker POST /design-generate -> Printify API -> OpenAI gpt-image-1 -> upload -> update

Uso:
    python scripts/_run_approved_batch.py --test 3          (prova 3 prodotti)
    python scripts/_run_approved_batch.py                    (tutti i 200 approvati)
    python scripts/_run_approved_batch.py --collection pulse
    python scripts/_run_approved_batch.py --dry-run          (solo prompt, no generazione)
    python scripts/_run_approved_batch.py --resume           (salta prodotti gia processati)
"""
from __future__ import annotations
import argparse, json, sys, time
from datetime import datetime
from pathlib import Path

import requests, urllib3
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

WORKER_URL     = "https://bks-agent.bakabo.workers.dev"
BKS_TOKEN      = env.get("BKS_AI_TOKEN") or env.get("BKS_ASSISTANT_PUBLIC_TOKEN", "")
PRINTIFY_TOKEN = env.get("PRINTIFY_API_TOKEN", "")
SHOP_ID        = env.get("PRINTIFY_SHOP_ID", "12030061")

WORKER_HDR   = {"Authorization": f"Bearer {BKS_TOKEN}", "Content-Type": "application/json"}
PRINTIFY_HDR = {"Authorization": f"Bearer {PRINTIFY_TOKEN}"}

LOG_PATH = ROOT / "ecommerce_automation" / "design_batch_log.json"
COLLECTIONS = ["hours", "glyph", "marker", "riviera", "pulse", "token", "flag", "folklore", "origin"]


TITLE_KEYWORDS = {
    "hours": ["hours"], "glyph": ["glyph"], "marker": ["marker"],
    "riviera": ["riviera"], "pulse": ["pulse"], "token": ["token"],
    "flag": ["flag", "burst"], "folklore": ["folklore"],
}

def get_collection(tags, title: str = "") -> str:
    tag_list = tags if isinstance(tags, list) else [t.strip() for t in (tags or "").split(",")]
    for tag in tag_list:
        t = str(tag).strip().lower()
        if t.startswith("collection:"):
            return t.split(":", 1)[1].strip()
    # Fallback: infer from title
    tl = title.lower()
    for col, keywords in TITLE_KEYWORDS.items():
        if any(kw in tl for kw in keywords):
            return col
    return "unknown"


def fetch_approved(collection_filter: str | None = None) -> list[dict]:
    """Carica tutti i prodotti con TM nel titolo."""
    products, page = [], 1
    print("Carico prodotti approvati da Printify...")
    while True:
        r = requests.get(
            f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json?limit=20&page={page}",
            headers=PRINTIFY_HDR, verify=False, timeout=30,
        )
        if not r.ok:
            print(f"  ERR {r.status_code}: {r.text[:150]}")
            break
        batch = r.json().get("data", [])
        if not batch:
            break
        for p in batch:
            if "™" not in p.get("title", ""):
                continue
            col = get_collection(p.get("tags", ""), p.get("title", ""))
            if collection_filter and col != collection_filter:
                continue
            products.append({
                "id":         p["id"],
                "title":      p["title"],
                "visible":    p.get("visible", False),
                "collection": col,
            })
        if len(batch) < 20:
            break
        page += 1
        time.sleep(0.15)
    return products


def call_worker(product_id: str, collection: str, dry_run: bool) -> dict:
    payload = {
        "product_id":  product_id,
        "collection":  collection if collection in COLLECTIONS else "glyph",
        "dry_run":     dry_run,
    }
    try:
        r = requests.post(
            f"{WORKER_URL}/design-generate",
            headers=WORKER_HDR,
            json=payload,
            timeout=180,
            verify=False,
        )
        if r.ok:
            return r.json()
        return {"status": "error", "http": r.status_code, "body": r.text[:300]}
    except Exception as e:
        return {"status": "error", "body": str(e)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",    action="store_true")
    parser.add_argument("--resume",     action="store_true", help="Salta prodotti già nel log")
    parser.add_argument("--test",       type=int, default=0, metavar="N", help="Processa solo N prodotti")
    parser.add_argument("--collection", default=None)
    parser.add_argument("--pause",      type=float, default=4.0)
    args = parser.parse_args()

    products = fetch_approved(args.collection)
    print(f"  Trovati {len(products)} approvati (™)")
    if args.collection:
        print(f"  Filtro collezione: {args.collection}")

    # Resume: salta già processati
    log = json.loads(LOG_PATH.read_text(encoding="utf-8")) if LOG_PATH.exists() else {}
    if args.resume:
        before = len(products)
        products = [p for p in products if p["id"] not in log or log[p["id"]].get("status") == "error"]
        print(f"  Resume: {before - len(products)} già OK, {len(products)} da processare")

    if args.test:
        products = products[:args.test]
        print(f"  TEST MODE: solo {args.test} prodotti")

    if not products:
        print("Nessun prodotto da processare.")
        return

    mode = "[DRY-RUN]" if args.dry_run else "[LIVE]"
    print(f"\nBKS Design Batch {mode} — {len(products)} prodotti")
    print(f"Worker: {WORKER_URL}/design-generate")
    print("=" * 65)

    stats = {"ok": 0, "dry_run": 0, "no_design": 0, "error": 0}
    start = datetime.now()

    for i, prod in enumerate(products, 1):
        pid   = prod["id"]
        col   = prod["collection"]
        pub   = "PUB" if prod["visible"] else "DRF"
        title = prod["title"][:45].encode("ascii", "replace").decode()

        print(f"\n[{i:>3}/{len(products)}] [{pub}] {col:10s} | {title}")

        result = call_worker(pid, col, args.dry_run)
        status = result.get("status", "error")

        if status == "dry_run":
            stats["dry_run"] += 1
            mode_txt = result.get("decision", {}).get("mode", "?")
            tpl  = result.get("decision", {}).get("reason", "?")
            prompt_len = len(result.get("artwork_prompt", ""))
            mat  = result.get("material_context") or "-"
            print(f"  prompt={prompt_len}ch  mode={mode_txt}  tpl={tpl}")
            print(f"  material: {mat[:80]}")
        elif status == "updated":
            stats["ok"] += 1
            new_id   = result.get("new_image_id", "")[:12]
            replaced = result.get("areas_replaced", 0)
            tpl      = result.get("template_used") or "none"
            mode_txt = result.get("mode", "?")
            print(f"  OK  image={new_id}  areas={replaced}  tpl={tpl}  mode={mode_txt}")
        elif status == "no_design":
            stats["no_design"] += 1
            print(f"  SKIP: nessun design area")
        else:
            stats["error"] += 1
            err = (result.get("body") or result.get("error", "?"))[:120]
            print(f"  ERR: {err}")

        log[pid] = {
            "ts":         datetime.now().isoformat(),
            "collection": col,
            "title":      prod["title"],
            "visible":    prod["visible"],
            "status":     status,
            "result":     {k: v for k, v in result.items() if k != "artwork_prompt"},
        }
        LOG_PATH.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
        time.sleep(args.pause)

    elapsed = (datetime.now() - start).seconds
    print(f"\n{'='*65}")
    print(f"Completati   : {stats['ok']}")
    print(f"Dry run      : {stats['dry_run']}")
    print(f"Saltati      : {stats['no_design']}")
    print(f"Errori       : {stats['error']}")
    print(f"Tempo totale : {elapsed//60}m {elapsed%60}s")
    print(f"Log          : {LOG_PATH}")


if __name__ == "__main__":
    main()
