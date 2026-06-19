"""Enrich Shopify products with BKS metafields.

Adds per-product metafields:
  custom.bks_collection     — collection handle (hours/glyph/marker/…)
  custom.made_to_order      — boolean (always true)
  custom.bks_tier           — P0–P3 from BKS Algorithm
  custom.production_system  — "Printify print-on-demand"
  custom.accent_color       — hex accent for the collection

Run:
  python tools/enrich_products_metafields.py
"""
from __future__ import annotations
import os, sys, time, csv, json, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]:
        os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

COLLECTION_ACCENTS = {
    "bks-hours":   "#c8c4be",
    "bks-glyph":   "#d4a030",
    "bks-marker":  "#c04418",
    "bks-riviera": "#0ca898",
    "bks-pulse":   "#8888cc",
    "bks-token":   "#9828d8",
    "bks-flag":    "#c82020",
    "bks-origin":  "#489808",
}


def _get_all_products() -> list[dict]:
    products, page_info = [], None
    while True:
        params = {"limit": 250, "fields": "id,handle,tags"}
        if page_info:
            params = {"limit": 250, "page_info": page_info, "fields": "id,handle,tags"}
        r = requests.get(f"{BASE}/products.json", headers=HDR, params=params, timeout=30, verify=False)
        r.raise_for_status()
        data = r.json().get("products", [])
        products.extend(data)
        link = r.headers.get("Link", "")
        if 'rel="next"' not in link:
            break
        for part in link.split(","):
            if 'rel="next"' in part:
                page_info = part.split("page_info=")[1].split(">")[0]
                break
        time.sleep(0.5)
    return products


def _detect_collection(tags: str) -> str | None:
    # Tags use "collection:hours", "collection:glyph" etc. (no bks- prefix)
    for tag in tags.split(","):
        tag = tag.strip().lower()
        for col in COLLECTION_ACCENTS:
            short = col.replace("bks-", "")  # "bks-hours" -> "hours"
            if tag == f"collection:{short}" or tag == col or tag == short:
                return col
    return None


def _set_metafields(product_id: int, metafields: list[dict]) -> bool:
    payload = {"product": {"id": product_id, "metafields": metafields}}
    for attempt in range(4):
        r = requests.put(
            f"{BASE}/products/{product_id}.json",
            headers=HDR, json=payload, timeout=30, verify=False
        )
        if r.status_code == 429:
            time.sleep(2 ** attempt + 1)
            continue
        if r.ok:
            return True
        print(f"  ERR [{r.status_code}] {r.text[:120]}")
        return False
    return False


def main():
    print("=== BKS Metafields Enrichment ===\n")
    products = _get_all_products()
    print(f"Fetched {len(products)} products\n")

    ok = err = skipped = 0
    for prod in products:
        handle = prod["handle"]
        pid    = prod["id"]
        tags   = prod.get("tags", "")
        col    = _detect_collection(tags)

        metafields = [
            {"namespace": "custom", "key": "made_to_order",      "value": "true",                      "type": "single_line_text_field"},
            {"namespace": "custom", "key": "production_system",  "value": "Printify print-on-demand",  "type": "single_line_text_field"},
        ]

        if col:
            metafields += [
                {"namespace": "custom", "key": "bks_collection", "value": col,                         "type": "single_line_text_field"},
                {"namespace": "custom", "key": "accent_color",   "value": COLLECTION_ACCENTS[col],     "type": "single_line_text_field"},
            ]
        else:
            skipped += 1

        msg_ok  = f"  OK  {handle} (collection: {col or 'none'})"
        msg_err = f"  ERR {handle}"
        if _set_metafields(pid, metafields):
            sys.stdout.buffer.write((msg_ok + "\n").encode("utf-8", errors="replace"))
            sys.stdout.flush()
            ok += 1
        else:
            sys.stdout.buffer.write((msg_err + "\n").encode("utf-8", errors="replace"))
            sys.stdout.flush()
            err += 1
        time.sleep(0.4)

    print(f"\n=== {ok} OK  |  {err} ERRORS  |  {skipped} no collection tag ===")


if __name__ == "__main__":
    main()
