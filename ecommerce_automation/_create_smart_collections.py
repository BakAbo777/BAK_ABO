"""Create Shopify smart collections filtered by product_type, one per BKS product type."""
import json, time, requests
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
HEADERS = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

# handle → (title, exact product_type value)
PRODUCT_TYPES = {
    "bks-type-puffer-jacket":     ("BKS Puffer Jackets",      "Puffer Jacket"),
    "bks-type-swim-trunks":       ("BKS Swim Trunks",         "Swim Trunks"),
    "bks-type-windbreaker":       ("BKS Windbreakers",        "Windbreaker Jacket"),
    "bks-type-backpack":          ("BKS Backpacks",           "Backpack"),
    "bks-type-sneakers":          ("BKS Sneakers",            "Sneakers"),
    "bks-type-travel-bag":        ("BKS Travel Bags",         "Travel Bag"),
    "bks-type-beach-towel":       ("BKS Beach Towels",        "Beach Towel"),
    "bks-type-hoodie":            ("BKS Hoodies",             "Pullover Hoodie"),
    "bks-type-athletic-shorts":   ("BKS Athletic Shorts",     "Athletics Shorts"),
    "bks-type-lounge-pants":      ("BKS Lounge Pants",        "Lounge Pants"),
    "bks-type-flip-flop":         ("BKS Flip Flops",          "Flip Flop"),
    "bks-type-hawaiian":          ("BKS Hawaiian Shirts",     "Hawaiian Shirt"),
    "bks-type-duffel-bag":        ("BKS Duffel Bags",         "Duffel Bag"),
    "bks-type-swimwear":          ("BKS Swimwear",            "Swimwear"),
    "bks-type-one-piece":         ("BKS One-Piece Swimsuits", "One-Piece Swimsuit"),
    "bks-type-dress":             ("BKS Dresses",             "Dress"),
    "bks-type-shoes":             ("BKS Shoes",               "Shoes"),
    "bks-type-tee":               ("BKS T-Shirts",            "T-Shirt"),
}

# Check existing smart collections
existing = {}
r = requests.get(f"https://{SHOP}/admin/api/{API}/smart_collections.json",
    params={"limit": 250, "fields": "id,handle,title"},
    headers=HEADERS, verify=False, timeout=30)
for c in r.json().get("smart_collections", []):
    existing[c["handle"]] = c["id"]

results = {}
for handle, (title, ptype) in PRODUCT_TYPES.items():
    if handle in existing:
        print(f"  EXISTS  {handle} (id={existing[handle]})")
        results[handle] = existing[handle]
        continue
    payload = {"smart_collection": {
        "title": title,
        "handle": handle,
        "rules": [{"column": "type", "relation": "equals", "condition": ptype}],
        "published": True,
        "sort_order": "best-selling",
    }}
    resp = requests.post(f"https://{SHOP}/admin/api/{API}/smart_collections.json",
        headers=HEADERS, json=payload, verify=False, timeout=15)
    sc = resp.json().get("smart_collection", {})
    if sc.get("id"):
        print(f"  CREATED {handle} id={sc['id']} ({sc.get('products_count', '?')} products)")
        results[handle] = sc["id"]
    else:
        print(f"  ERROR   {handle}: {resp.json()}")
    time.sleep(0.5)

print(f"\nSmart collections: {len(results)}")
# Save mapping for next script
(ROOT / "output" / "smart_collections.json").write_text(json.dumps(results, indent=2))
print("Saved → output/smart_collections.json")
