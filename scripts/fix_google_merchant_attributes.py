"""Set mm-google-shopping metafields for all 203 BKS products.

Fixes Google Merchant Center warnings:
  - age_group:  adult   (all products — no kids items)
  - gender:     male / female / unisex  (inferred from handle/product_type/tags)
  - condition:  new     (all POD, never used)

Run: python scripts/fix_google_merchant_attributes.py [--dry-run]
"""
from __future__ import annotations
import os, sys, time, requests, urllib3, argparse, re
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
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-01")
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

# Handle/type patterns → gender
FEMALE_PATTERNS = re.compile(
    r"(racerback.dress|one.piece|womens.tee|women|bikini|bralette|swimsuit|dress)",
    re.IGNORECASE,
)
MALE_PATTERNS = re.compile(
    r"(swim.trunk|mens.tee|men[^u]|swim.short)",
    re.IGNORECASE,
)

def detect_gender(handle: str, product_type: str, tags: str) -> str:
    text = f"{handle} {product_type} {tags}".lower()
    # explicit tags take priority
    if "gender:female" in tags.lower() or "female" in tags.lower():
        return "female"
    if "gender:male" in tags.lower():
        return "male"
    if "gender:unisex" in tags.lower():
        return "unisex"
    if FEMALE_PATTERNS.search(text):
        return "female"
    if MALE_PATTERNS.search(text):
        return "male"
    return "unisex"


def get_existing_mf(pid: int) -> dict[str, int]:
    """Return {key: metafield_id} for mm-google-shopping namespace."""
    r = requests.get(
        f"{BASE}/products/{pid}/metafields.json?namespace=mm-google-shopping",
        headers=HDR, timeout=20, verify=False,
    )
    if not r.ok:
        return {}
    return {m["key"]: m["id"] for m in r.json().get("metafields", [])}


def upsert_mf(pid: int, existing: dict[str, int], key: str, value: str, dry: bool) -> str:
    if dry:
        return "DRY"
    if key in existing:
        r = requests.put(
            f"{BASE}/metafields/{existing[key]}.json",
            headers=HDR,
            json={"metafield": {"id": existing[key], "value": value}},
            timeout=20, verify=False,
        )
    else:
        r = requests.post(
            f"{BASE}/products/{pid}/metafields.json",
            headers=HDR,
            json={"metafield": {
                "namespace": "mm-google-shopping",
                "key": key,
                "value": value,
                "type": "single_line_text_field",
            }},
            timeout=20, verify=False,
        )
    return "OK" if r.ok else f"ERR {r.status_code}"


def out(msg: str):
    sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
    sys.stdout.flush()


def get_all_products():
    products, page_info = [], None
    while True:
        params = {"limit": 250, "fields": "id,handle,product_type,tags"}
        if page_info:
            params = {"limit": 250, "page_info": page_info, "fields": "id,handle,product_type,tags"}
        r = requests.get(f"{BASE}/products.json", headers=HDR, params=params, timeout=30, verify=False)
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    dry = args.dry_run

    out(f"=== BKS Google Merchant Attributes ({'DRY RUN' if dry else 'EXECUTE'}) ===\n")

    products = get_all_products()
    out(f"Fetched {len(products)} products\n")

    stats = {"age_group": 0, "gender": 0, "condition": 0, "err": 0,
             "male": 0, "female": 0, "unisex": 0}

    for p in products:
        pid   = p["id"]
        handle = p["handle"]
        ptype  = p.get("product_type", "")
        tags   = p.get("tags", "")
        gender = detect_gender(handle, ptype, tags)
        stats[gender] += 1

        existing = {} if dry else get_existing_mf(pid)

        for key, val in [("age_group", "adult"), ("gender", gender), ("condition", "new")]:
            status = upsert_mf(pid, existing, key, val, dry)
            if status.startswith("ERR"):
                out(f"  {handle[:40]} {key}={val} -> {status}")
                stats["err"] += 1
            else:
                stats[key] += 1
            if not dry:
                time.sleep(0.5)

        if not dry:
            out(f"  {handle[:45]} gender={gender} ✓")
        time.sleep(0.1)

    out(f"\n=== DONE ===")
    out(f"  age_group=adult set: {stats['age_group']}")
    out(f"  gender set:          {stats['gender']}  (male={stats['male']} female={stats['female']} unisex={stats['unisex']})")
    out(f"  condition=new set:   {stats['condition']}")
    out(f"  errors:              {stats['err']}")
    if dry:
        out("\nRun without --dry-run to apply.")


if __name__ == "__main__":
    main()
