"""
Rimuove emoji e caratteri non-standard dai titoli prodotto Shopify.
Necessario per Google Merchant Center e AI discoverability.

Problemi corretti:
- Emoji nei titoli (es. "BKS 🤖⚙️Production" → "BKS Production")
- "Copy of..." prefix → rimuove prefisso
- Titoli senza prefisso BKS → aggiunge collezione se rilevabile dai tag

Uso:
    python scripts/fix_emoji_product_titles.py --dry-run
    python scripts/fix_emoji_product_titles.py --collection glyph
    python scripts/fix_emoji_product_titles.py --all
"""
from __future__ import annotations
import re, json, time, argparse, sys
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

DOMAIN  = env["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = env["SHOPIFY_ADMIN_TOKEN"]
VERSION = env.get("SHOPIFY_API_VERSION", "2025-01")
THEME   = "202392961362"
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

EMOJI_RE = re.compile(
    "["
    "\U0001f1e6-\U0001f1ff"
    "\U0001f300-\U0001f5ff"
    "\U0001f600-\U0001f64f"
    "\U0001f680-\U0001f6ff"
    "\U0001f700-\U0001f77f"
    "\U0001f780-\U0001f7ff"
    "\U0001f800-\U0001f8ff"
    "\U0001f900-\U0001f9ff"
    "\U0001fa00-\U0001fa6f"
    "\U0001fa70-\U0001faff"
    "☀-➿"
    "]+", flags=re.UNICODE
)

COPY_RE    = re.compile(r"^[Cc]opy\s+of\s+", re.IGNORECASE)
MULTI_SPACE = re.compile(r"\s{2,}")

COLLECTIONS = ["hours", "glyph", "marker", "riviera", "pulse", "token", "flag", "folklore", "origin"]


def clean_title(title: str) -> str:
    t = EMOJI_RE.sub("", title)
    t = COPY_RE.sub("", t)
    t = t.replace("™", "™").strip()
    t = MULTI_SPACE.sub(" ", t)
    return t


def get_collection_from_tags(tags) -> str | None:
    tag_list = tags if isinstance(tags, list) else [s.strip() for s in (tags or "").split(",")]
    for tag in tag_list:
        tl = str(tag).lower().strip()
        if tl.startswith("collection:"):
            return tl.split(":", 1)[1].strip()
    return None


def fetch_products(collection_filter: str | None = None) -> list[dict]:
    products = []
    url = f"{BASE}/products.json?limit=250"
    while url:
        r = requests.get(url, headers={"X-Shopify-Access-Token": TOKEN},
                         verify=False, timeout=30)
        if not r.ok:
            print(f"  API ERR {r.status_code}: {r.text[:200]}")
            break
        batch = r.json().get("products", [])
        for p in batch:
            col = get_collection_from_tags(p.get("tags", ""))
            if collection_filter and col != collection_filter:
                continue
            products.append({**p, "_collection": col})
        # cursor-based next page
        link = r.headers.get("Link", "")
        nxt = None
        for part in link.split(","):
            if 'rel="next"' in part:
                nxt = part.strip().strip("<>").split(";")[0].strip().strip("<>")
                break
        url = nxt
        time.sleep(0.2)
    return products


def update_product_title(product_id: int, new_title: str) -> bool:
    r = requests.put(
        f"{BASE}/products/{product_id}.json",
        headers=HDR,
        json={"product": {"id": product_id, "title": new_title}},
        verify=False, timeout=20,
    )
    return r.ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",    action="store_true")
    parser.add_argument("--all",        action="store_true")
    parser.add_argument("--collection", default=None)
    args = parser.parse_args()

    col_filter = None if args.all else args.collection
    print(f"\nBKS Emoji Title Fixer — {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print(f"Filter: {col_filter or 'all'}\n")

    products = fetch_products(col_filter)
    print(f"Prodotti caricati: {len(products)}")

    fixed, clean, errors = 0, 0, 0

    for p in products:
        original = p["title"]
        cleaned  = clean_title(original)

        if cleaned == original:
            clean += 1
            continue

        pid = p["id"]
        col = p.get("_collection") or "?"
        print(f"\n  [{col:10s}] {original[:55]}")
        print(f"           -> {cleaned[:55]}")

        if not args.dry_run:
            ok = update_product_title(pid, cleaned)
            if ok:
                fixed += 1
                print("           FIXED")
            else:
                errors += 1
                print("           ERROR")
            time.sleep(0.3)
        else:
            fixed += 1

    print(f"\n{'='*60}")
    print(f"Già puliti : {clean}")
    print(f"{'[DRY-RUN] ' if args.dry_run else ''}Corretti   : {fixed}")
    if errors: print(f"Errori     : {errors}")


if __name__ == "__main__":
    main()
