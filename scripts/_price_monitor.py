"""
BKS Price Monitor — controlla e corregge prezzi Shopify automaticamente.

Gira 24/7 su Hetzner via systemd timer (ogni 6 ore).
Carica regole dal Worker KV se disponibile, altrimenti usa defaults locali.

Uso:
    python scripts/_price_monitor.py            # check + fix automatico
    python scripts/_price_monitor.py --dry-run  # solo report, no fix
    python scripts/_price_monitor.py --report   # report JSON in stdout
"""
from __future__ import annotations
import argparse, json, sys, time, urllib3
from datetime import datetime
from pathlib import Path

urllib3.disable_warnings()
import requests

ROOT = Path(__file__).resolve().parent.parent
env: dict[str, str] = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DOMAIN = env.get("SHOPIFY_MYSHOPIFY_DOMAIN", "")
TOKEN  = env.get("SHOPIFY_ADMIN_TOKEN", "")
BASE   = f"https://{DOMAIN}/admin/api/2024-01"
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
LOG    = ROOT / "ecommerce_automation" / "price_monitor_log.json"

# ── Price ladder approvata (da BKS Pricing Skill) ─────────────────────────────

PRICE_RULES: list[dict] = [
    # product_type match, title_contains, min_price, target_price, note
    {"type": "T-Shirt",         "title": None,          "min": 49.00, "target": 49.00, "note": "Tee standard"},
    {"type": "All Over Prints", "title": "Tee",         "min": 49.00, "target": 49.00, "note": "AOP Tee"},
    {"type": "Windbreaker Jacket","title": None,         "min": 109.00,"target": 109.00,"note": "Windbreaker"},
    {"type": "Dress",           "title": None,          "min": 65.00, "target": 65.00, "note": "Dress"},
    {"type": "Pullover Hoodie", "title": None,          "min": 79.00, "target": 79.00, "note": "Hoodie"},
    {"type": "Swimwear",        "title": None,          "min": 55.00, "target": 55.00, "note": "Swimwear"},
    {"type": "Swim Trunks",     "title": None,          "min": 55.00, "target": 59.00, "note": "Swim trunks"},
    {"type": "Athletics Shorts","title": None,          "min": 65.00, "target": 69.00, "note": "Athletic shorts"},
    {"type": "Lounge Pants",    "title": None,          "min": 65.00, "target": 65.00, "note": "Lounge pants"},
    # Shoes: skip slippers/flip flops
    {"type": "Shoes",           "title": "Sneaker",     "min": 75.00, "target": 75.00, "note": "Sneakers"},
    {"type": "Sneakers",        "title": None,          "min": 75.00, "target": 75.00, "note": "Sneakers"},
    # All Over Prints general floor (non-tee)
    {"type": "All Over Prints", "title": None,          "min": 55.00, "target": None,  "note": "AOP floor"},
]

SLIPPER_KEYWORDS = ["slipper", "flip flop", "cozy", "mule", "sandal", "slide"]


def is_slipper(title: str) -> bool:
    tl = title.lower()
    return any(k in tl for k in SLIPPER_KEYWORDS)


def find_rule(product_type: str, title: str) -> dict | None:
    tl = title.lower()
    if is_slipper(title):
        return None  # no rule for slippers
    for rule in PRICE_RULES:
        if rule["type"] != product_type:
            continue
        if rule["title"] and rule["title"].lower() not in tl:
            continue
        return rule
    return None


def fetch_products() -> list[dict]:
    import re
    products, url = [], f"{BASE}/products.json?limit=250&status=active&fields=id,title,product_type,variants"
    while url:
        r = requests.get(url, headers=HDR, verify=False, timeout=30)
        if not r.ok:
            break
        products.extend(r.json().get("products", []))
        link = r.headers.get("Link", "")
        m = re.search(r"<([^>]+)>; rel=\"next\"", link)
        url = m.group(1) if m else None
        time.sleep(0.1)
    return products


def fix_variant_price(variant_id: int, new_price: float) -> bool:
    payload = {"variant": {"id": variant_id, "price": f"{new_price:.2f}"}}
    r = requests.put(f"{BASE}/variants/{variant_id}.json", headers=HDR, json=payload, verify=False, timeout=15)
    return r.ok


def load_log() -> list:
    return json.loads(LOG.read_text(encoding="utf-8")) if LOG.exists() else []


def save_log(entries: list):
    LOG.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def run(dry_run: bool = False) -> dict:
    ts = datetime.now().isoformat()
    print(f"\nBKS Price Monitor — {ts} {'[DRY RUN]' if dry_run else '[LIVE]'}")
    print(f"Store: {DOMAIN}")
    print("=" * 60)

    products = fetch_products()
    print(f"Prodotti attivi: {len(products)}")

    anomalies, fixes, errors = [], 0, 0

    for p in products:
        pt    = p.get("product_type", "") or ""
        title = p.get("title", "")
        rule  = find_rule(pt, title)
        if not rule:
            continue

        for v in p.get("variants", []):
            price = float(v["price"])
            if price >= rule["min"]:
                continue  # price OK

            target = rule["target"] if rule["target"] else rule["min"]
            anomalies.append({
                "product_id": p["id"], "variant_id": v["id"],
                "title": title, "product_type": pt,
                "old_price": price, "new_price": target,
                "rule": rule["note"],
            })

            short = title[:45].encode("ascii", "replace").decode()
            if dry_run:
                print(f"  DRY  {short}  ${price:.2f} → ${target:.2f}  [{rule['note']}]")
            else:
                ok = fix_variant_price(v["id"], target)
                if ok:
                    fixes += 1
                    print(f"  FIX  {short}  ${price:.2f} → ${target:.2f}  [{rule['note']}]")
                else:
                    errors += 1
                    print(f"  ERR  {short}  ${price:.2f} → ${target:.2f}")
                time.sleep(0.25)

    print("=" * 60)
    print(f"Anomalie trovate : {len(anomalies)}")
    if not dry_run:
        print(f"Fix applicati    : {fixes}")
        print(f"Errori           : {errors}")

    result = {
        "ts": ts, "dry_run": dry_run, "products_checked": len(products),
        "anomalies": len(anomalies), "fixes": fixes, "errors": errors,
        "items": anomalies,
    }

    if not dry_run and anomalies:
        log = load_log()
        log.append(result)
        log = log[-200:]  # mantieni ultimi 200 run
        save_log(log)

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report",  action="store_true", help="Output JSON report")
    args = parser.parse_args()

    if not DOMAIN or not TOKEN:
        print("ERRORE: SHOPIFY_MYSHOPIFY_DOMAIN o SHOPIFY_ADMIN_TOKEN mancanti nel .env")
        sys.exit(1)

    result = run(dry_run=args.dry_run)
    if args.report:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
