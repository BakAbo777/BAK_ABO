"""
Lancia POST /design-generate sul Worker per tutti i prodotti BakAbo.
Il Worker decide template, stile, genera con OpenAI, carica su Printify.

Uso:
    python scripts/_run_design_batch.py --collection pulse
    python scripts/_run_design_batch.py --collection all
    python scripts/_run_design_batch.py --collection marker --dry-run
    python scripts/_run_design_batch.py --product-id 651f3b7691a9771a560ac91d --collection pulse

Modalita dry-run: chiede al Worker il prompt senza generare/caricare.
"""
import argparse, json, sys, time
from pathlib import Path

import requests, urllib3
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

WORKER_URL    = "https://bks-agent.bakabo.workers.dev"
BKS_TOKEN     = env.get("BKS_AI_TOKEN") or env.get("BKS_ASSISTANT_PUBLIC_TOKEN", "")
PRINTIFY_TOKEN = env.get("PRINTIFY_API_TOKEN", "")
PRINTIFY_SHOP  = env.get("PRINTIFY_SHOP_ID", "12030061")

WORKER_HDR = {"Authorization": f"Bearer {BKS_TOKEN}", "Content-Type": "application/json"}
PRINTIFY_HDR = {"Authorization": f"Bearer {PRINTIFY_TOKEN}"}

COLLECTIONS = ["hours", "glyph", "marker", "riviera", "pulse", "token", "flag", "folklore"]

LOG_PATH = ROOT / "ecommerce_automation" / "design_batch_log.json"


def get_collection_from_tags(tags) -> str:
    tag_list = tags if isinstance(tags, list) else [t.strip() for t in (tags or "").split(",")]
    for tag in tag_list:
        t = str(tag).strip().lower()
        if t.startswith("collection:"):
            return t.split(":", 1)[1].strip()
    return "unknown"


def fetch_all_products(collection_filter: str | None = None) -> list[dict]:
    products = []
    page = 1
    while True:
        r = requests.get(
            f"https://api.printify.com/v1/shops/{PRINTIFY_SHOP}/products.json?limit=20&page={page}",
            headers=PRINTIFY_HDR, verify=False, timeout=30,
        )
        if not r.ok: break
        batch = r.json().get("data", [])
        if not batch: break
        for p in batch:
            col = get_collection_from_tags(p.get("tags", ""))
            if collection_filter and collection_filter != "all" and col != collection_filter:
                continue
            products.append({**p, "_collection": col})
        if len(batch) < 20: break
        page += 1
        time.sleep(0.2)
    return products


def call_worker_generate(product_id: str, collection: str,
                          design_description: str = "", dry_run: bool = False) -> dict:
    payload = {
        "product_id": product_id,
        "collection": collection,
        "design_description": design_description,
        "dry_run": dry_run,
    }
    r = requests.post(
        f"{WORKER_URL}/design-generate",
        headers=WORKER_HDR,
        json=payload,
        timeout=180,  # OpenAI puo impiegare fino a 90s
        verify=False,
    )
    if r.ok:
        return r.json()
    return {"status": "error", "http": r.status_code, "body": r.text[:300]}


def main():
    parser = argparse.ArgumentParser(description="BKS Design Batch Generator")
    parser.add_argument("--collection",  default="all", help=f"Collezione o 'all'. Valori: {', '.join(COLLECTIONS)}")
    parser.add_argument("--product-id",  default=None,  help="Genera solo questo prodotto")
    parser.add_argument("--design",      default="",    help="Descrizione design extra (opzionale)")
    parser.add_argument("--dry-run",     action="store_true", help="Chiede prompt al Worker senza generare")
    parser.add_argument("--limit",       type=int, default=0, help="Max prodotti da processare (0=tutti)")
    parser.add_argument("--pause",       type=float, default=3.0, help="Secondi di pausa tra prodotti (default 3)")
    args = parser.parse_args()

    if args.product_id:
        # Modalita singolo prodotto
        if args.collection == "all":
            print("ERRORE: --product-id richiede anche --collection")
            sys.exit(1)
        products = [{"id": args.product_id, "_collection": args.collection, "title": args.product_id}]
    else:
        col_filter = None if args.collection == "all" else args.collection
        print(f"Carico prodotti da Printify (collezione: {col_filter or 'tutte'})...")
        products = fetch_all_products(col_filter)
        # Filtra collezioni non BKS
        products = [p for p in products if p["_collection"] in COLLECTIONS]
        if args.limit:
            products = products[:args.limit]
        print(f"  {len(products)} prodotti da processare\n")

    # Carica log esistente
    log = json.loads(LOG_PATH.read_text(encoding="utf-8")) if LOG_PATH.exists() else {}

    stats = {"ok": 0, "dry_run": 0, "error": 0, "skipped": 0}
    mode_label = "[DRY-RUN]" if args.dry_run else "[LIVE]"

    print(f"BKS Design Batch Generator {mode_label}")
    print(f"Worker: {WORKER_URL}/design-generate")
    print("=" * 60)

    for i, prod in enumerate(products, 1):
        pid   = prod["id"]
        col   = prod["_collection"]
        title = prod.get("title", pid)[:45].encode("ascii", "replace").decode()

        print(f"\n[{i}/{len(products)}] {col:10s} | {title}")

        result = call_worker_generate(pid, col, args.design, args.dry_run)
        status = result.get("status", "error")

        if status in ("updated", "dry_run"):
            if status == "dry_run":
                stats["dry_run"] += 1
                mode_txt = result.get("decision", {}).get("mode", "?")
                prompt_len = len(result.get("artwork_prompt", ""))
                print(f"  -> prompt={prompt_len}chars  mode={mode_txt}")
            else:
                stats["ok"] += 1
                new_id = result.get("new_image_id", "")
                replaced = result.get("areas_replaced", 0)
                tpl = result.get("template_used", "none")
                mode_txt = result.get("mode", "?")
                print(f"  -> OK  image={new_id[:12]}  areas={replaced}  tpl={tpl}  mode={mode_txt}")

            # Log
            log[pid] = {
                "ts": __import__("datetime").datetime.now().isoformat(),
                "collection": col,
                "status": status,
                "result": result,
            }
        elif status == "no_design":
            stats["skipped"] += 1
            print(f"  -> SKIP: nessun design area trovato")
        else:
            stats["error"] += 1
            body = result.get("body") or result.get("error", "?")
            print(f"  -> ERR: {body[:120]}")
            log[pid] = {"ts": __import__("datetime").datetime.now().isoformat(),
                        "collection": col, "status": "error", "error": str(body)[:200]}

        LOG_PATH.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
        time.sleep(args.pause)

    print(f"\n{'='*60}")
    print(f"Completati   : {stats['ok']}")
    print(f"Dry run      : {stats['dry_run']}")
    print(f"Saltati      : {stats['skipped']}")
    print(f"Errori       : {stats['error']}")
    print(f"Log salvato  : {LOG_PATH}")

if __name__ == "__main__":
    main()
