"""Bulk-fix product types for items stuck on 'All Over Prints'."""
import re, time, requests
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

SHOP  = env["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN = env["SHOPIFY_ADMIN_TOKEN"]
API   = "2025-01"

# keyword patterns → correct product type
TYPE_RULES = [
    (re.compile(r"puffer",                  re.I), "Puffer Jacket"),
    (re.compile(r"\btee\b|t-shirt",         re.I), "T-Shirt"),
    (re.compile(r"beach towel",             re.I), "Beach Towel"),
    (re.compile(r"hawaiian",                re.I), "Hawaiian Shirt"),
    (re.compile(r"backpack",                re.I), "Backpack"),
    (re.compile(r"duffel",                  re.I), "Duffel Bag"),
    (re.compile(r"hoodie",                  re.I), "Pullover Hoodie"),
    (re.compile(r"lounge pant",             re.I), "Lounge Pants"),
    (re.compile(r"athletic|long short",     re.I), "Athletics Shorts"),
    (re.compile(r"one.piece",               re.I), "One-Piece Swimsuit"),
    (re.compile(r"pullover",                re.I), "Pullover Hoodie"),
    (re.compile(r"swim trunk",              re.I), "Swim Trunks"),
]

r = requests.get(
    f"https://{SHOP}/admin/api/{API}/products.json",
    params={"product_type": "All Over Prints", "fields": "id,title,product_type", "limit": 250},
    headers={"X-Shopify-Access-Token": TOKEN},
    verify=False, timeout=30,
)
products = r.json().get("products", [])
print(f"Found {len(products)} 'All Over Prints' products\n")

updated = 0
skipped = []
for p in products:
    new_type = None
    for pattern, ptype in TYPE_RULES:
        if pattern.search(p["title"]):
            new_type = ptype
            break
    if new_type:
        for attempt in range(3):
            resp = requests.put(
                f"https://{SHOP}/admin/api/{API}/products/{p['id']}.json",
                headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"},
                json={"product": {"id": p["id"], "product_type": new_type}},
                verify=False, timeout=15,
            )
            if resp.status_code == 429:
                print(f"  RATE LIMIT — waiting 2s...")
                time.sleep(2)
                continue
            if resp.status_code in (200, 201) and resp.text:
                break
            time.sleep(1)
        try:
            ok = resp.json().get("product", {}).get("product_type") == new_type
        except Exception:
            ok = resp.status_code == 200
        print(f"  {'OK' if ok else 'ERR'}  {new_type:20s}  {p['title'][:55]}")
        updated += 1
        time.sleep(0.5)
    else:
        skipped.append(p["title"])

print(f"\nUpdated: {updated}")
print(f"Skipped ({len(skipped)}) — still 'All Over Prints':")
for t in skipped[:20]:
    print(f"  - {t}")
