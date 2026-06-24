"""Fix Shopify products that have no tags.

Derives collection + product-type tags from product title.
Base tags always added: ai-art, aop, bakabo-enriched, brand:bks, made-to-order

Usage:
  python scripts/fix_missing_tags.py
  python scripts/fix_missing_tags.py --dry-run
"""
from __future__ import annotations
import os, sys, requests, urllib3, argparse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
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

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
API    = f"https://{DOMAIN}/admin/api/2025-01"

BASE_TAGS = ["ai-art", "aop", "bakabo-enriched", "brand:bks", "made-to-order"]

# Collection keyword → tag
COLLECTION_MAP = {
    "flag":     "collection:flag",
    "glyph":    "collection:glyph",
    "folklore": "collection:origin",
    "origin":   "collection:origin",
    "marker":   "collection:marker",
    "hours":    "collection:hours",
    "pulse":    "collection:pulse",
    "riviera":  "collection:riviera",
    "token":    "collection:token",
}

# Product type keyword → tag
TYPE_MAP = {
    "puffer":         "puffer",
    "tee":            "tee",
    "hoodie":         "hoodie",
    "pullover":       "hoodie",
    "backpack":       "backpack",
    "sneaker":        "sneakers",
    "swim trunks":    "swim-trunks",
    "lounge pants":   "lounge-pants",
    "windbreaker":    "windbreaker",
    "travel bag":     "travel-bag",
    "beach towel":    "beach-towel",
    "flip flop":      "flip-flops",
    "flip-flop":      "flip-flops",
    "hawaiian":       "hawaiian-shirt",
    "dress":          "racerback-dress",
    "one-piece":      "one-piece",
    "slipper":        "cozy-slipper",
    "shorts":         "athletic-shorts",
    "short":          "athletic-shorts",
}


def derive_tags(title: str, product_type: str) -> list[str]:
    tags = list(BASE_TAGS)
    tl = title.lower()

    # Collection
    for keyword, col_tag in COLLECTION_MAP.items():
        if keyword in tl:
            tags.append(col_tag)
            break

    # Product type from title
    for keyword, type_tag in TYPE_MAP.items():
        if keyword in tl:
            if type_tag not in tags:
                tags.append(type_tag)
            break

    # Fallback: product_type field
    if product_type:
        pt = product_type.lower()
        for keyword, type_tag in TYPE_MAP.items():
            if keyword in pt:
                if type_tag not in tags:
                    tags.append(type_tag)
                break

    return sorted(set(tags))


def fetch_all_products() -> list[dict]:
    products = []
    url = f"{API}/products.json"
    params = {"limit": 250, "fields": "id,title,tags,product_type"}
    while url:
        r = requests.get(url, headers=HDR, params=params, verify=False, timeout=30)
        products.extend(r.json().get("products", []))
        link = r.headers.get("Link", "")
        url = None
        if 'rel="next"' in link:
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.split(";")[0].strip().strip("<>")
                    params = {}
                    break
    return products


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    products = fetch_all_products()
    no_tags = [p for p in products if not p.get("tags", "").strip()]

    print(f"Total products: {len(products)}")
    print(f"Products without tags: {len(no_tags)}\n")

    if not no_tags:
        print("Nothing to fix.")
        return

    ok = err = 0
    for p in no_tags:
        new_tags = derive_tags(p["title"], p.get("product_type", ""))
        tags_str = ", ".join(new_tags)
        action = "DRY RUN" if args.dry_run else "FIX"
        print(f"  [{action}] {p['title'][:50]}")
        print(f"          → {tags_str}")

        if args.dry_run:
            ok += 1
            continue

        r = requests.put(
            f"{API}/products/{p['id']}.json",
            headers=HDR,
            json={"product": {"id": p["id"], "tags": tags_str}},
            verify=False,
            timeout=20,
        )
        if r.ok:
            ok += 1
        else:
            print(f"          ERR {r.status_code}: {r.text[:100]}")
            err += 1

    print(f"\nDone: {ok} fixed, {err} errors")


if __name__ == "__main__":
    main()
