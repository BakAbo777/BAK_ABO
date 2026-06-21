"""
Rename products NOT covered by V18 schema rename:
- Windbreaker Jacket (product_type)
- Dress / Racerback Dress (product_type)
- Travel Bag (product_type)
- Bags / Backpack (product_type)
- Flip Flop (product_type)
- T-Shirt / Women's Tee (product_type)
- Any product with legacy Printify names still present

Schema: BKS [ProductType] — [Collection] [NN]
Run dry-run first, then --apply.
"""
import os, sys, re, requests, urllib3, time
from pathlib import Path
from collections import defaultdict

urllib3.disable_warnings()  # type: ignore
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
DRY_RUN = "--apply" not in sys.argv

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, _, v = line.partition("="); k=k.strip(); v=v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN","")
BASE   = f"https://{DOMAIN}/admin/api/2025-01"
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
print(f"Shop: {DOMAIN} | DRY_RUN={DRY_RUN}\n")

# Product type → canonical display name
TYPE_MAP = {
    "Windbreaker Jacket":   "Windbreaker",
    "Dress":                "Racerback Dress",
    "Travel Bag":           "Travel Bag",
    "Bags":                 "Backpack",
    "Flip Flop":            "Flip Flop",
    "T-Shirt":              "Tee",
}

# bks.collection metafield → canonical collection name
COLL_MAP = {
    "BKS Hours":   "Hours",
    "BKS Glyph":   "Glyph",
    "BKS Marker":  "Marker",
    "BKS Riviera": "Riviera",
    "BKS Pulse":   "Pulse",
    "BKS Token":   "Token",
    "BKS Flag":    "Flag",
    "BKS Origin":  "Origin",
}

def bks_collection_from_title(title):
    for k, v in COLL_MAP.items():
        if v.lower() in title.lower() or k.lower() in title.lower():
            return v
    return None

def already_schema(title):
    return bool(re.match(r'^BKS .+ — (Hours|Glyph|Marker|Riviera|Pulse|Token|Flag|Origin)', title))

def canonical_type(product_type, title):
    """Override product_type based on title when Shopify type is ambiguous."""
    t = title.lower()
    if "travel bag" in t: return "Travel Bag"
    if "backpack" in t:   return "Bags"  # keep as Bags → Backpack
    return product_type

# Fetch all active products with relevant product_types
TARGET_TYPES = set(TYPE_MAP.keys())
products = []
page_info = None
while True:
    params = "limit=250&fields=id,title,handle,product_type,status,metafields"
    if page_info: params += f"&page_info={page_info}"
    r = requests.get(f"{BASE}/products.json?{params}", headers=HDR, verify=False, timeout=30)
    for p in r.json().get("products",[]):
        if p["status"] == "active" and p.get("product_type","") in TARGET_TYPES:
            products.append(p)
    link = r.headers.get("Link","")
    if 'rel="next"' not in link: break
    m = re.search(r'page_info=([^&>]+)[^>]*>;\s*rel="next"', link)
    page_info = m.group(1) if m else None

print(f"Found {len(products)} products with target product types\n")

# Also find any remaining legacy-named products (old Printify names in all types)
LEGACY_PATTERNS = [
    r'^\(BKS\)',                          # (BKS) prefix
    r'BKS\).',                            # ...BKS)xxx
    r'^[A-Z][a-z]+ [A-Z][a-z]+.*\(BKS\)', # FusionFiber (BKS)...
    r'Piumino',                            # Italian for puffer
    r'Giacca a vento',                     # Italian windbreaker
    r'Zaino',                              # Italian backpack
    r'Costume da bagno',                   # Italian swimwear
    r'Sneakers? Bassa',                    # Italian sneaker
    r'Pantaloni',                          # Italian pants
    r'Maglione',                           # Italian sweater
]
LEGACY_RE = re.compile('|'.join(LEGACY_PATTERNS), re.I)

# Fetch ALL products to find legacy-named ones
all_products = []
page_info = None
while True:
    params = "limit=250&fields=id,title,handle,product_type,status"
    if page_info: params += f"&page_info={page_info}"
    r = requests.get(f"{BASE}/products.json?{params}&status=active", headers=HDR, verify=False, timeout=30)
    all_products.extend(r.json().get("products",[]))
    link = r.headers.get("Link","")
    if 'rel="next"' not in link: break
    m = re.search(r'page_info=([^&>]+)[^>]*>;\s*rel="next"', link)
    page_info = m.group(1) if m else None

legacy_products = [p for p in all_products if LEGACY_RE.search(p["title"]) and not already_schema(p["title"])]
print(f"Legacy-named products (not yet in BKS schema): {len(legacy_products)}")
for p in legacy_products[:20]:
    print(f"  [{p['id']}] {p['title'][:60]} | type={p['product_type']}")
if len(legacy_products) > 20:
    print(f"  ... and {len(legacy_products)-20} more")

print()

# Build rename plan: group by type+collection
to_rename = {}
for p in products:
    if already_schema(p["title"]): continue
    ptype  = canonical_type(p.get("product_type",""), p["title"])
    disp   = TYPE_MAP.get(ptype, ptype)
    coll   = bks_collection_from_title(p["title"]) or "BKS"
    key    = (disp, coll)
    if key not in to_rename: to_rename[key] = []
    to_rename[key].append(p)

print("=== RENAME PLAN (missing schema types) ===")
changes = []
for (disp, coll), prods in sorted(to_rename.items()):
    n = len(prods)
    print(f"\n[{disp} x{n} in {coll}]")
    for i, p in enumerate(prods, 1):
        new_title = f"BKS {disp} — {coll}" if n == 1 else f"BKS {disp} — {coll} {i:02d}"
        print(f"  {p['title'][:50]:50} -> {new_title}")
        changes.append((p["id"], new_title, p["title"]))

print(f"\nTotal to rename: {len(changes)}")
print(f"Legacy products needing manual review: {len(legacy_products)}")

if not DRY_RUN and changes:
    ok = err = 0
    for pid, new_title, old_title in changes:
        r = requests.put(f"{BASE}/products/{pid}.json",
            headers=HDR,
            json={"product": {"id": pid, "title": new_title}},
            verify=False, timeout=20)
        if r.ok:
            ok += 1
            print(f"  OK  [{pid}] {old_title[:40]} -> {new_title}")
        else:
            err += 1
            print(f"  ERR [{pid}] {r.status_code} {r.text[:60]}")
        time.sleep(0.4)
    print(f"\nDone: {ok}/{len(changes)} OK, {err} errors")
elif DRY_RUN and changes:
    print(f"\n[DRY RUN] Run with --apply to rename {len(changes)} products.")
