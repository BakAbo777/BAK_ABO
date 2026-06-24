"""
Carica bks_patterns.json nel Worker KV via POST /admin/patterns/sync
Poi pushes pattern ID come metafield Shopify su ogni prodotto.

Usage:
  python scripts/sync_patterns_to_worker.py              # solo Worker KV
  python scripts/sync_patterns_to_worker.py --shopify    # + metafields Shopify
"""
from __future__ import annotations
import os, sys, json, argparse
from pathlib import Path

import requests, urllib3
urllib3.disable_warnings()

ROOT         = Path(__file__).parent.parent
PATTERNS_FILE = ROOT / "output" / "bks_patterns.json"

WORKER_URL   = "https://bks-agent.bakabo.workers.dev"
SHOPIFY_TOKEN = os.environ.get("SHOPIFY_TOKEN") or ""
SHOPIFY_DOMAIN = os.environ.get("SHOPIFY_DOMAIN") or ""
SHOPIFY_API   = os.environ.get("SHOPIFY_API_VERSION", "2024-04")
BKS_TOKEN     = os.environ.get("BKS_ASSISTANT_PUBLIC_TOKEN") or ""

# Carica .env se disponibile
env_path = ROOT / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
    SHOPIFY_TOKEN  = os.environ.get("SHOPIFY_TOKEN", "")
    SHOPIFY_DOMAIN = os.environ.get("SHOPIFY_DOMAIN", "")
    SHOPIFY_API    = os.environ.get("SHOPIFY_API_VERSION", "2024-04")
    BKS_TOKEN      = os.environ.get("BKS_ASSISTANT_PUBLIC_TOKEN", "")

SH = {"X-Shopify-Access-Token": SHOPIFY_TOKEN, "Content-Type": "application/json"}
BASE = f"https://{SHOPIFY_DOMAIN}/admin/api/{SHOPIFY_API}"


def sync_to_worker(registry: dict) -> None:
    print("→ Sync pattern registry al Worker KV...")
    r = requests.post(
        f"{WORKER_URL}/admin/patterns/sync",
        headers={"Authorization": f"Bearer {BKS_TOKEN}", "Content-Type": "application/json"},
        json={"registry": registry},
        timeout=30,
    )
    if r.ok:
        data = r.json()
        print(f"  ✓ {data.get('synced')} pattern caricati nel Worker KV")
    else:
        print(f"  ✗ Errore Worker: {r.status_code} {r.text[:100]}")


def push_shopify_metafields(registry: dict) -> None:
    print("→ Push pattern ID come metafield Shopify...")
    patterns = registry.get("patterns", {})

    # Costruisci indice shopify_id → pattern_id
    shopify_map: dict[str, str] = {}
    for pid, p in patterns.items():
        for prod in p.get("products", []):
            sid = prod.get("shopify_id")
            if sid:
                shopify_map[str(sid)] = pid

    ok = err = 0
    for shopify_id, pattern_id in shopify_map.items():
        payload = {
            "metafield": {
                "namespace": "bks",
                "key":       "pattern_id",
                "value":     pattern_id,
                "type":      "single_line_text_field",
            }
        }
        r = requests.post(
            f"{BASE}/products/{shopify_id}/metafields.json",
            headers=SH, json=payload, verify=False, timeout=15,
        )
        if r.ok:
            ok += 1
            print(f"  ✓ {pattern_id} → Shopify #{shopify_id}")
        else:
            err += 1
            print(f"  ✗ {pattern_id} → #{shopify_id}: {r.status_code} {r.text[:60]}")

    print(f"\n  Metafields: {ok} OK, {err} errori")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shopify", action="store_true", help="Pusha anche metafields su Shopify")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not PATTERNS_FILE.exists():
        print(f"ERRORE: {PATTERNS_FILE} non trovato. Esegui prima generate_pattern_registry.py")
        sys.exit(1)

    registry = json.loads(PATTERNS_FILE.read_text(encoding="utf-8"))
    stats = registry.get("_meta", {}).get("stats", {})
    print(f"Registry caricato: {stats.get('total')} pezze, collezioni: {stats.get('by_collection')}")

    if args.dry_run:
        print("[DRY RUN — nessuna chiamata API]")
        return

    sync_to_worker(registry)

    if args.shopify:
        push_shopify_metafields(registry)

    print("\nDone.")


if __name__ == "__main__":
    main()
