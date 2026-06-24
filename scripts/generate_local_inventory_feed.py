"""Generate Google Merchant Center — Local Inventory Feed (TSV).

BKS Studio è 100% online / print-on-demand.
Il feed marca tutti i prodotti con availability=in_stock, quantity=999
per la sede fisica registrata in Google Business Profile (BKS_TERNI).

Questo risolve il conflitto "Numero limitato" nel GMC allineando
il feed locale con il feed principale (entrambi in_stock).

Uso:
  python scripts/generate_local_inventory_feed.py
  python scripts/generate_local_inventory_feed.py --store-code BKS_TERNI
  python scripts/generate_local_inventory_feed.py --dry-run

Output: output/google_local_inventory_feed.tsv
Upload: Google Merchant Center → Feeds → Local products inventory feed
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import time
import requests
import urllib3
from datetime import datetime, timezone
from pathlib import Path

urllib3.disable_warnings()  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# ── .env ──────────────────────────────────────────────────────────────────────
_env = ROOT / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        _k = _k.strip(); _v = _v.strip().strip('"').strip("'")
        if _k not in os.environ:
            os.environ[_k] = _v

DOMAIN  = os.environ.get("SHOPIFY_MYSHOPIFY_DOMAIN", "")
TOKEN   = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-01")

STORE_CODE_DEFAULT = "BKS_TERNI"
OUTPUT_PATH = ROOT / "output" / "google_local_inventory_feed.tsv"
SUMMARY_PATH = ROOT / "output" / "google_local_inventory_summary.json"

# Google TSV columns for local inventory feed
FEED_COLUMNS = [
    "id",
    "store_code",
    "availability",
    "quantity",
    "price",
    "sale_price",
]

CURRENCY = "EUR"


def _out(msg: str) -> None:
    sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
    sys.stdout.flush()


def _shopify_id(product_id: int, variant_id: int, country: str = "IT") -> str:
    """Product ID must match g:id in the primary Google Shopping feed.
    Our custom feed template (page.bks-google-feed.liquid) uses {{ variant.id }}
    so the ID is just the numeric variant ID."""
    return str(variant_id)


def _eur(price_str: str) -> str:
    """Format price as '69.00 EUR' for the feed."""
    try:
        return f"{float(price_str):.2f} {CURRENCY}"
    except (ValueError, TypeError):
        return ""


def fetch_products_with_variants() -> list[dict]:
    """Fetch all Shopify products with their variant IDs and prices."""
    if not DOMAIN or not TOKEN:
        _out("⚠ SHOPIFY_MYSHOPIFY_DOMAIN or SHOPIFY_ADMIN_TOKEN not set — cannot fetch live product IDs.")
        return []

    base = f"https://{DOMAIN}/admin/api/{VERSION}"
    hdr = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
    products: list[dict] = []
    page_info = None

    while True:
        params: dict = {"limit": 250, "fields": "id,handle,variants"}
        if page_info:
            params = {"limit": 250, "page_info": page_info, "fields": "id,handle,variants"}

        r = requests.get(f"{base}/products.json", headers=hdr, params=params,
                         timeout=30, verify=False)
        r.raise_for_status()
        products.extend(r.json().get("products", []))

        link = r.headers.get("Link", "")
        if 'rel="next"' not in link:
            break
        for part in link.split(","):
            if 'rel="next"' in part:
                page_info = part.split("page_info=")[1].split(">")[0]
                break
        time.sleep(0.3)

    return products


def build_feed_rows(products: list[dict], store_code: str) -> list[dict]:
    """Build one TSV row per variant."""
    rows: list[dict] = []
    for p in products:
        pid = p["id"]
        for v in p.get("variants", []):
            vid = v["id"]
            price_raw = v.get("price", "")
            compare_raw = v.get("compare_at_price") or ""

            row = {
                "id": _shopify_id(pid, vid, "IT"),
                "store_code": store_code,
                "availability": "in_stock",
                "quantity": "999",
                "price": _eur(price_raw),
                "sale_price": _eur(compare_raw) if compare_raw else "",
            }
            rows.append(row)
    return rows


def write_tsv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FEED_COLUMNS, delimiter="\t",
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict], path: Path, store_code: str) -> None:
    import json
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "store_code": store_code,
        "total_rows": len(rows),
        "availability": "in_stock",
        "quantity": 999,
        "output_file": str(OUTPUT_PATH.relative_to(ROOT)),
        "upload_to": "Google Merchant Center → Feeds → Local products inventory feed",
        "note": "BKS Studio è online-only / POD. availability=in_stock / quantity=999 allineati al feed principale per eliminare il conflitto 'Numero limitato' su 35K prodotti.",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate BKS Google Local Inventory Feed")
    parser.add_argument("--store-code", default=STORE_CODE_DEFAULT,
                        help=f"Google Business Profile store code (default: {STORE_CODE_DEFAULT})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch products and show count without writing output")
    args = parser.parse_args()

    _out(f"=== BKS Google Local Inventory Feed ({'DRY RUN' if args.dry_run else 'GENERATE'}) ===")
    _out(f"Store code: {args.store_code}")

    _out("→ Fetching Shopify products...")
    products = fetch_products_with_variants()

    if not products:
        _out("✗ No products fetched. Check .env credentials.")
        sys.exit(1)

    _out(f"→ {len(products)} products fetched.")

    rows = build_feed_rows(products, args.store_code)
    _out(f"→ {len(rows)} variant rows built (in_stock, quantity=999 — POD unlimited).")

    if args.dry_run:
        _out("\nFirst 3 rows:")
        for row in rows[:3]:
            _out("  " + "\t".join(f"{k}={v}" for k, v in row.items() if v))
        _out(f"\nDRY RUN complete. Would write {len(rows)} rows to {OUTPUT_PATH.relative_to(ROOT)}")
        return

    write_tsv(rows, OUTPUT_PATH)
    write_summary(rows, SUMMARY_PATH, args.store_code)

    _out(f"\n✓ Feed scritto: {OUTPUT_PATH.relative_to(ROOT)}")
    _out(f"✓ Summary: {SUMMARY_PATH.relative_to(ROOT)}")
    _out("\nProssimo passo:")
    _out("  1. Google Merchant Center → Contenuto → Feed → [+] Nuovo feed")
    _out("  2. Tipo: 'Inventario locale dei prodotti'")
    _out(f"  3. Carica: output/google_local_inventory_feed.tsv")
    _out("  4. Oppure (più rapido): cambia Business Profile da Sede → Area di servizio")


if __name__ == "__main__":
    main()
