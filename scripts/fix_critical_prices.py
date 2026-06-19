"""Corregge i 5 alert prezzo critici (vedi project_bks_business_rules.md).

Scrive su DUE lati per evitare che il prossimo sync Printify->Shopify
sovrascriva la correzione: prezzo aggiornato sia sui variant Shopify
(effetto immediato) sia sui variant Printify corrispondenti (fonte dati
che altrimenti vince al prossimo publish/sync).
"""
from __future__ import annotations
import os, json, time, requests, urllib3
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

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
SHOPIFY_TOKEN = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
SHOPIFY_BASE = f"https://{DOMAIN}/admin/api/{VERSION}"
SHOPIFY_HDR = {"X-Shopify-Access-Token": SHOPIFY_TOKEN, "Content-Type": "application/json"}

PRINTIFY_TOKEN = os.environ.get("PRINTIFY_API_TOKEN") or os.environ.get("PRINTIFY_TOKEN")
PRINTIFY_SHOP_ID = "12030061"
PRINTIFY_BASE = f"https://api.printify.com/v1/shops/{PRINTIFY_SHOP_ID}"
PRINTIFY_HDR = {"Authorization": f"Bearer {PRINTIFY_TOKEN}", "Content-Type": "application/json;charset=utf-8"}

CATEGORIES = {
    "slipper": {"target": 45.00, "ids": [10845207691602, 10845214409042]},
    "flip_flop": {"target": 45.00, "ids": [10845149430098, 10845138125138, 10845096706386]},
    "athletic_long_shorts": {"target": 65.00, "ids": [
        10846183948626, 10846124671314, 10845919641938, 10845928096082,
        10846206427474, 10845875437906, 10845887365458, 10845901128018,
        10853761352018, 10815697781074, 10816621609298,
    ]},
    "puffer": {"target": 129.00, "ids": [
        10033439015250, 8691525452114, 8801270825298, 8801246740818,
        8682100719954, 8672600359250, 10760782905682, 10033427415378,
        10033418305874, 10865275830610, 8672606683474, 8801280754002,
        8672595837266, 8792063508818, 10760931639634, 8670875418962,
        10756765811026, 8927392825682, 10033423515986, 8660298760530,
        10033441538386, 8691523453266, 8801297203538, 10756793991506,
        8694512681298, 8801266368850, 10033444913490, 8694492135762,
        8801286291794,
    ]},
}


def shopify_get_product(pid: int) -> dict:
    r = requests.get(f"{SHOPIFY_BASE}/products/{pid}.json", headers=SHOPIFY_HDR, verify=False, timeout=30)
    r.raise_for_status()
    return r.json()["product"]


def shopify_update_variant_price(variant_id: int, price: str) -> bool:
    for attempt in range(5):
        r = requests.put(
            f"{SHOPIFY_BASE}/variants/{variant_id}.json",
            headers=SHOPIFY_HDR,
            json={"variant": {"id": variant_id, "price": price}},
            verify=False, timeout=30,
        )
        if r.status_code == 429:
            time.sleep(float(r.headers.get("Retry-After", 2 ** attempt + 1)))
            continue
        if r.ok:
            return True
        print(f"    SHOPIFY ERR variant {variant_id}: [{r.status_code}] {r.text[:200]}")
        return False
    print(f"    SHOPIFY ERR variant {variant_id}: rate-limit retries exhausted")
    return False


def printify_load_all() -> list[dict]:
    cache = ROOT / "printify_full.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    products, page = [], 1
    while True:
        r = requests.get(f"{PRINTIFY_BASE}/products.json", headers=PRINTIFY_HDR, params={"limit": 50, "page": page}, verify=False, timeout=30)
        j = r.json()
        data = j.get("data", [])
        products.extend(data)
        last_page = j.get("last_page", page)
        if page >= last_page or not data:
            break
        page += 1
    return products


def printify_update_price(printify_product_id: str, variants: list[dict], target_cents: int) -> bool:
    updated = [
        {**v, "price": target_cents} if v.get("is_enabled") else v
        for v in variants
    ]
    for attempt in range(5):
        r = requests.put(
            f"{PRINTIFY_BASE}/products/{printify_product_id}.json",
            headers=PRINTIFY_HDR,
            json={"variants": updated},
            verify=False, timeout=30,
        )
        if r.status_code == 429:
            time.sleep(float(r.headers.get("Retry-After", 2 ** attempt + 1)))
            continue
        if r.ok:
            return True
        print(f"    PRINTIFY ERR {printify_product_id}: [{r.status_code}] {r.text[:200]}")
        return False
    print(f"    PRINTIFY ERR {printify_product_id}: rate-limit retries exhausted")
    return False


def main():
    printify_products = printify_load_all()
    ext_map = {}
    for p in printify_products:
        ext = p.get("external") or {}
        eid = ext.get("id")
        if eid:
            ext_map[str(eid)] = p

    totals = {"shopify_ok": 0, "shopify_err": 0, "printify_ok": 0, "printify_err": 0, "printify_skip": 0}

    for cat_name, cfg in CATEGORIES.items():
        target = cfg["target"]
        target_str = f"{target:.2f}"
        target_cents = round(target * 100)
        print(f"\n=== {cat_name}: target ${target_str} ===")
        for pid in cfg["ids"]:
            product = shopify_get_product(pid)
            print(f"  [{pid}] {product['title']}")
            for v in product["variants"]:
                if v["price"] == target_str:
                    continue
                ok = shopify_update_variant_price(v["id"], target_str)
                totals["shopify_ok" if ok else "shopify_err"] += 1
                print(f"    shopify variant {v['id']} {v['price']} -> {target_str} {'OK' if ok else 'ERR'}")
                time.sleep(0.55)

            pf = ext_map.get(str(pid))
            if not pf:
                print(f"    PRINTIFY: nessun prodotto collegato trovato per {pid}, skip")
                totals["printify_skip"] += 1
                continue
            already = all(v["price"] == target_cents for v in pf["variants"] if v.get("is_enabled"))
            if already:
                print(f"    printify {pf['id']} gia' a ${target_str}, skip")
                continue
            ok = printify_update_price(pf["id"], pf["variants"], target_cents)
            totals["printify_ok" if ok else "printify_err"] += 1
            print(f"    printify {pf['id']} -> ${target_str} {'OK' if ok else 'ERR'}")
            time.sleep(0.55)

    print("\n=== RIEPILOGO ===")
    print(totals)


if __name__ == "__main__":
    main()
