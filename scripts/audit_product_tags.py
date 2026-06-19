"""Read-only audit: tag hygiene su tutti i prodotti live Shopify.
Verifica residui Folklore, case/whitespace duplicati, tag vuoti, copertura
tag usati dalle regole smart collection. Nessuna scrittura.
"""
from __future__ import annotations
import os, sys, json, requests, urllib3
from collections import defaultdict
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
TOKEN = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}


def fetch_all_products() -> list[dict]:
    products, url, params = [], f"{BASE}/products.json", {"limit": 250, "fields": "id,title,handle,status,tags"}
    while url:
        r = requests.get(url, headers=HDR, params=params, timeout=30, verify=False)
        r.raise_for_status()
        products.extend(r.json().get("products", []))
        link = r.headers.get("Link", "")
        next_url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                next_url = part.split(";")[0].strip().strip("<>")
        url, params = next_url, None
    return products


def fetch_smart_collections() -> list[dict]:
    cols, page_info, url = [], None, f"{BASE}/smart_collections.json"
    params = {"limit": 250}
    while True:
        r = requests.get(url, headers=HDR, params=params, timeout=30, verify=False)
        r.raise_for_status()
        cols.extend(r.json().get("smart_collections", []))
        link = r.headers.get("Link", "")
        next_url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                next_url = part.split(";")[0].strip().strip("<>")
        if not next_url:
            break
        url, params = next_url, None
    return cols


def main():
    print("=== Fetch prodotti live ===")
    products = fetch_all_products()
    print(f"  {len(products)} prodotti totali")

    tag_count = defaultdict(int)
    tag_casing = defaultdict(set)
    products_no_tags = []
    whitespace_issues = []
    empty_tag_issues = []
    folklore_residue = []
    case_dupes_per_product = []

    for p in products:
        raw = p.get("tags", "")
        parts = raw.split(",") if raw else []
        tags = [t.strip() for t in parts]
        if not raw.strip():
            products_no_tags.append((p["id"], p["handle"]))
            continue

        seen_lower = {}
        for t in tags:
            if t == "":
                empty_tag_issues.append((p["handle"], raw))
                continue
            stripped = t.strip()
            if stripped != t or t != parts[tags.index(t)].strip():
                pass
            tag_count[stripped.lower()] += 1
            tag_casing[stripped.lower()].add(stripped)
            if "folklore" in stripped.lower():
                folklore_residue.append((p["handle"], stripped))
            low = stripped.lower()
            if low in seen_lower and seen_lower[low] != stripped:
                case_dupes_per_product.append((p["handle"], seen_lower[low], stripped))
            seen_lower[low] = stripped

        for raw_part in parts:
            if raw_part != raw_part.strip():
                whitespace_issues.append((p["handle"], repr(raw_part)))

    print(f"\n=== Prodotti senza tag ({len(products_no_tags)}) ===")
    for pid, handle in products_no_tags[:20]:
        print(f"  [{pid}] {handle}")

    print(f"\n=== Tag con whitespace extra (leading/trailing spazio) ({len(whitespace_issues)}) ===")
    for handle, t in whitespace_issues[:20]:
        print(f"  {handle}: {t}")

    print(f"\n=== Tag vuoti (virgola doppia ',,') ({len(empty_tag_issues)}) ===")
    for handle, raw in empty_tag_issues[:20]:
        print(f"  {handle}: {raw}")

    print(f"\n=== Residuo 'folklore' in tag ({len(folklore_residue)}) ===")
    for handle, t in folklore_residue:
        print(f"  {handle}: {t}")

    print(f"\n=== Tag con casing inconsistente fra prodotti diversi ===")
    inconsistent = {k: v for k, v in tag_casing.items() if len(v) > 1}
    for low, variants in sorted(inconsistent.items()):
        print(f"  '{low}' -> varianti trovate: {sorted(variants)} (usato {tag_count[low]}x)")
    if not inconsistent:
        print("  Nessuna.")

    print(f"\n=== Tag duplicati nello stesso prodotto (case-diff) ===")
    for handle, t1, t2 in case_dupes_per_product:
        print(f"  {handle}: '{t1}' e '{t2}'")
    if not case_dupes_per_product:
        print("  Nessuno.")

    print("\n=== Smart collection: copertura tag rule ===")
    cols = fetch_smart_collections()
    live_tags_lower = set(tag_count.keys())
    for c in cols:
        rules = c.get("rules") or []
        tag_rules = [r for r in rules if r.get("column") == "tag"]
        for r in tag_rules:
            cond = (r.get("condition") or "").strip()
            hit = cond.lower() in live_tags_lower
            flag = "OK" if hit else "ORFANO (nessun prodotto live ha questo tag)"
            print(f"  [{c['handle']}] rule tag='{cond}' -> {flag}")

    print("\n=== Top 25 tag più usati ===")
    for tag, cnt in sorted(tag_count.items(), key=lambda x: -x[1])[:25]:
        canon = sorted(tag_casing[tag])[0]
        print(f"  {cnt:4d}  {canon}")

    print("\n=== RIEPILOGO ===")
    print(json.dumps({
        "prodotti_totali": len(products),
        "prodotti_senza_tag": len(products_no_tags),
        "tag_distinti": len(tag_count),
        "whitespace_issues": len(whitespace_issues),
        "empty_tag_issues": len(empty_tag_issues),
        "folklore_residue": len(folklore_residue),
        "casing_inconsistente": len(inconsistent),
        "dupes_stesso_prodotto": len(case_dupes_per_product),
    }, indent=2))


if __name__ == "__main__":
    main()
