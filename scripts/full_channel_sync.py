"""BKS Full Channel Sync — Printify / Shopify / Google Merchant Center.

Azioni:
  1. Fetch prodotti Printify live → output/live_printify_products.csv
  2. Fetch prodotti Shopify live → output/live_shopify_products.csv
  3. Diff Printify ↔ Shopify (prodotti mancanti, non-sincronizzati)
  4. Verifica metafields GMC (age_group, gender, condition) su campione
  5. Forza mini-touch su Shopify (updated_at bump) → fa scattare re-crawl GMC feed
  6. Scrive output/channel_sync_report.json
"""
from __future__ import annotations
import os, sys, json, csv, time, requests, urllib3
from datetime import datetime, timezone
from pathlib import Path

urllib3.disable_warnings()  # type: ignore
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]:
        os.environ[k] = v

SH_DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
SH_TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
PFY_TOKEN  = os.environ["PRINTIFY_API_TOKEN"]
PFY_SHOP   = "12030061"
SH_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-01")
SH_BASE    = f"https://{SH_DOMAIN}/admin/api/{SH_VERSION}"
SH_HDR     = {"X-Shopify-Access-Token": SH_TOKEN, "Content-Type": "application/json"}
PFY_BASE   = "https://api.printify.com/v1"
PFY_HDR    = {"Authorization": f"Bearer {PFY_TOKEN}"}


def out(msg: str):
    sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
    sys.stdout.flush()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ── 1. Fetch Shopify products ─────────────────────────────────────────────────
def fetch_shopify() -> list[dict]:
    products, page_info = [], None
    while True:
        params = {"limit": 250, "fields": "id,handle,title,status,published_at,updated_at,tags,variants,images"}
        if page_info:
            params = {"limit": 250, "page_info": page_info, "fields": params["fields"]}
        r = requests.get(f"{SH_BASE}/products.json", headers=SH_HDR, params=params, timeout=30, verify=False)
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


# ── 2. Fetch Printify products ────────────────────────────────────────────────
def fetch_printify() -> list[dict]:
    products, page = [], 1
    while True:
        r = requests.get(
            f"{PFY_BASE}/shops/{PFY_SHOP}/products.json",
            headers=PFY_HDR,
            params={"limit": 50, "page": page},
            timeout=30, verify=False,
        )
        if not r.ok:
            out(f"  Printify API error: {r.status_code} {r.text[:80]}")
            break
        d = r.json()
        batch = d.get("data", [])
        products.extend(batch)
        last_page = d.get("last_page", 1)
        if page >= last_page:
            break
        page += 1
        time.sleep(0.4)
    return products


# ── 3. GMC metafields spot-check ──────────────────────────────────────────────
def check_gmc_sample(shopify_products: list[dict]) -> dict:
    sample = shopify_products[:5]
    results = {"checked": 0, "age_group_ok": 0, "gender_ok": 0, "condition_ok": 0}
    for p in sample:
        r = requests.get(
            f"{SH_BASE}/products/{p['id']}/metafields.json?namespace=mm-google-shopping",
            headers=SH_HDR, timeout=15, verify=False,
        )
        if not r.ok:
            continue
        mf = {m["key"]: m["value"] for m in r.json().get("metafields", [])}
        results["checked"] += 1
        if mf.get("age_group"):
            results["age_group_ok"] += 1
        if mf.get("gender"):
            results["gender_ok"] += 1
        if mf.get("condition"):
            results["condition_ok"] += 1
        time.sleep(0.3)
    return results


# ── 4. Mini-touch: bump updated_at on first active product ───────────────────
def bump_feed_trigger(shopify_products: list[dict]) -> str:
    active = [p for p in shopify_products if p.get("status") == "active"]
    if not active:
        return "no_active_products"
    p = active[0]
    # Re-set the same tags to bump updated_at without changing anything
    r = requests.put(
        f"{SH_BASE}/products/{p['id']}.json",
        headers=SH_HDR,
        json={"product": {"id": p["id"], "tags": p.get("tags", "")}},
        timeout=20, verify=False,
    )
    return "OK" if r.ok else f"ERR {r.status_code}"


def main():
    out("=== BKS Full Channel Sync ===")
    out(f"Started: {now_iso()}\n")

    # Step 1: Shopify
    out("1/5 Fetching Shopify products...")
    sh_products = fetch_shopify()
    out(f"   → {len(sh_products)} products")
    active = sum(1 for p in sh_products if p.get("status") == "active")
    draft  = sum(1 for p in sh_products if p.get("status") == "draft")
    out(f"   → active:{active}  draft:{draft}")

    # Save CSV
    sh_csv = ROOT / "output" / "live_shopify_products.csv"
    sh_fields = ["id","handle","title","status","published_at","updated_at","tags","variant_count","image_count"]
    with sh_csv.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=sh_fields)
        w.writeheader()
        for p in sh_products:
            w.writerow({
                "id": p["id"], "handle": p["handle"], "title": p.get("title",""),
                "status": p.get("status",""), "published_at": p.get("published_at",""),
                "updated_at": p.get("updated_at",""),
                "tags": p.get("tags",""),
                "variant_count": len(p.get("variants",[])),
                "image_count": len(p.get("images",[])),
            })
    out(f"   → saved: output/live_shopify_products.csv")

    # Step 2: Printify
    out("\n2/5 Fetching Printify products...")
    pfy_products = fetch_printify()
    out(f"   → {len(pfy_products)} products")
    pfy_published = sum(1 for p in pfy_products if p.get("visible") or (p.get("external") or {}).get("id"))
    out(f"   → published/linked:{pfy_published}")

    # Step 3: Diff
    out("\n3/5 Computing Printify ↔ Shopify diff...")
    sh_handles = {p["handle"] for p in sh_products}
    pfy_handles = set()
    pfy_missing_shopify = []
    for p in pfy_products:
        ext = p.get("external") or {}
        h = ext.get("handle") or p.get("slug","")
        if h:
            pfy_handles.add(h)
        if not ext.get("id"):
            pfy_missing_shopify.append(p.get("title","?")[:40])

    only_shopify = sh_handles - pfy_handles
    out(f"   → In Shopify not Printify: {len(only_shopify)}")
    out(f"   → Printify not published to Shopify: {len(pfy_missing_shopify)}")
    for t in pfy_missing_shopify[:5]:
        out(f"     • {t}")

    # Step 4: GMC spot-check
    out("\n4/5 GMC metafields spot-check (5 products)...")
    gmc_check = check_gmc_sample(sh_products)
    out(f"   → Checked:{gmc_check['checked']} age_group:{gmc_check['age_group_ok']}/5 gender:{gmc_check['gender_ok']}/5 condition:{gmc_check['condition_ok']}/5")

    # Step 5: Trigger GMC feed re-crawl
    out("\n5/5 Triggering GMC feed bump (updated_at touch)...")
    bump_result = bump_feed_trigger(sh_products)
    out(f"   → {bump_result}")

    # Report
    report = {
        "sync_at": now_iso(),
        "shopify": {"total": len(sh_products), "active": active, "draft": draft},
        "printify": {"total": len(pfy_products), "published_linked": pfy_published,
                     "not_on_shopify": len(pfy_missing_shopify)},
        "diff": {"only_in_shopify": len(only_shopify)},
        "gmc": gmc_check,
        "feed_bump": bump_result,
    }
    report_path = ROOT / "output" / "channel_sync_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    out(f"\nReport: output/channel_sync_report.json")
    out("=== SYNC COMPLETE ===")


if __name__ == "__main__":
    main()
