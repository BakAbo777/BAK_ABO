"""Trova i prodotti pubblicati in Printify ma assenti/non-attivi su Shopify.

Output:
  output/printify_gap_report.json  — lista completa gap
  output/printify_gap_report.csv   — tabella leggibile

Usage:
  python scripts/printify_shopify_gap.py
"""
from __future__ import annotations
import os, sys, json, csv, time, urllib3
from pathlib import Path
from datetime import datetime

urllib3.disable_warnings()
import requests

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

PRINTIFY_TOKEN = os.environ["PRINTIFY_API_TOKEN"]
PRINTIFY_SHOP  = os.environ["PRINTIFY_SHOP_ID"]
SHOPIFY_DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
SHOPIFY_TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]

P_HDR = {"Authorization": f"Bearer {PRINTIFY_TOKEN}"}
S_HDR = {"X-Shopify-Access-Token": SHOPIFY_TOKEN, "Content-Type": "application/json"}
PKW   = {"headers": P_HDR, "timeout": 20, "verify": False}
SKW   = {"headers": S_HDR, "timeout": 20, "verify": False}

BLUEPRINT_NAMES = {
    587: "Flip Flops", 413: "Backpack", 589: "Swim Trunks (AOP)",
    934: "Puffer Jacket (AOP)", 276: "Racerback Dress (AOP)",
    924: "Hawaiian Shirt (AOP)", 888: "Travel Bag", 450: "Pullover Hoodie (AOP)",
    291: "Sneakers", 279: "Women's Tee (AOP)", 360: "One-Piece Swimsuit (AOP)",
    1397: "Windbreaker (AOP)", 1006: "Boho Beach Cloth",
    1084: "Athletic Shorts (AOP)", 372: "Duffel Bag",
}


def fetch_printify_published() -> list[dict]:
    print("Fetching Printify published products…")
    all_prods, page = [], 1
    while True:
        r = requests.get(
            f"https://api.printify.com/v1/shops/{PRINTIFY_SHOP}/products.json"
            f"?limit=50&page={page}", **PKW
        )
        d = r.json()
        chunk = d.get("data", [])
        published = [p for p in chunk if p.get("visible")]
        all_prods.extend(published)
        lp = d.get("last_page", 1)
        print(f"  page {page}/{lp}  +{len(published)} published  running={len(all_prods)}")
        if page >= lp or not chunk:
            break
        page += 1
        time.sleep(0.25)
    print(f"  Total published in Printify: {len(all_prods)}")
    return all_prods


def fetch_shopify_active_ids() -> set[str]:
    print("Fetching Shopify active product IDs…")
    ids: set[str] = set()
    url = f"https://{SHOPIFY_DOMAIN}/admin/api/2025-01/products.json?limit=250&status=active&fields=id"
    while url:
        r = requests.get(url, **SKW)
        data = r.json().get("products", [])
        for p in data:
            ids.add(str(p["id"]))
        link = r.headers.get("Link", "")
        url = None
        if 'rel="next"' in link:
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.strip().split(";")[0].strip("<>")
    print(f"  Active Shopify products: {len(ids)}")
    return ids


def main() -> None:
    printify_pub = fetch_printify_published()
    shopify_ids  = fetch_shopify_active_ids()

    print("\nComputing gap…")
    gap, matched = [], []
    for p in printify_pub:
        ext = p.get("external") or {}
        shopify_id = str(ext.get("id", "")).replace("shopify_", "").strip()
        # extract numeric id if present
        if "_" in shopify_id:
            shopify_id = shopify_id.split("_")[-1]
        in_shopify = shopify_id in shopify_ids if shopify_id else False
        bp = p.get("blueprint_id", 0)
        entry = {
            "printify_id":  p["id"],
            "title":        p["title"],
            "blueprint_id": bp,
            "blueprint":    BLUEPRINT_NAMES.get(bp, f"bp_{bp}"),
            "shopify_id":   shopify_id or "—",
            "in_shopify":   in_shopify,
            "external_handle": ext.get("handle", "—"),
        }
        if in_shopify:
            matched.append(entry)
        else:
            gap.append(entry)

    print(f"  Matched (in Shopify active): {len(matched)}")
    print(f"  Gap    (NOT in Shopify):     {len(gap)}")

    # Sort gap by blueprint name
    gap.sort(key=lambda x: (x["blueprint"], x["title"]))

    # Save JSON
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    report = {
        "generated": datetime.now().isoformat()[:19],
        "printify_published": len(printify_pub),
        "shopify_active":     len(shopify_ids),
        "matched":            len(matched),
        "gap_count":          len(gap),
        "gap":                gap,
    }
    json_path = out / "printify_gap_report.json"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved: {json_path}")

    # Save CSV
    csv_path = out / "printify_gap_report.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["blueprint", "blueprint_id", "title", "shopify_id", "external_handle", "printify_id", "in_shopify"])
        w.writeheader()
        w.writerows(gap)
    print(f"Saved: {csv_path}")

    # Print summary table
    from collections import Counter
    by_bp = Counter(g["blueprint"] for g in gap)
    print(f"\n{'='*60}")
    print(f"GAP SUMMARY — {len(gap)} prodotti Printify published ma non in Shopify")
    print(f"{'='*60}")
    for bp_name, cnt in by_bp.most_common():
        print(f"  {cnt:3d}  {bp_name}")
    print()
    print("Sample titles:")
    for g in gap[:10]:
        title = g["title"].encode("ascii", "replace").decode()[:55]
        print(f"  [{g['blueprint'][:20]:20s}]  {title}")


if __name__ == "__main__":
    main()
