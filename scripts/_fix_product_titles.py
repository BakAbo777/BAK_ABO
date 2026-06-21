"""
Fix product titles:
  1. Replace non-ASCII separator char with ' — ' (em dash)
     e.g. "BKS Athletic Shorts ▶ Flag" → "BKS Athletic Shorts — Flag"
  2. Rename Folklore → Origin
     e.g. "BKS Folklore Field Windbreaker" → "BKS Windbreaker — Origin Field"
  3. Set ALL variant inventory_policy = "continue" (POD: never sold out)

Run with --dry-run first to preview, then without to apply.
"""
import os, re, sys, time, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()  # type: ignore

DRY_RUN = "--dry-run" not in sys.argv and "--apply" not in sys.argv
if "--apply" in sys.argv:
    DRY_RUN = False
else:
    DRY_RUN = True

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ:
        os.environ[k] = v

DOMAIN = os.environ.get("SHOPIFY_MYSHOPIFY_DOMAIN", "")
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "") or os.environ.get("SHOPIFY_API_TOKEN", "")
BASE   = f"https://{DOMAIN}/admin/api/2024-04"
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

print(f"Shop: {DOMAIN} | DRY_RUN={DRY_RUN}")
print("Use --apply to actually write to Shopify.\n")

EMOJI_RE = re.compile(r"[^\x00-\x7F]+")

# Folklore sub-name → keep as suffix in new name
FOLKLORE_PRODUCT_TYPES = {
    "Windbreaker": "BKS Windbreaker",
    "Flip Flop": "BKS Flip Flop",
    "Racerback Dress": "BKS Racerback Dress",
    "Hawaiian Shirt": "BKS Hawaiian Shirt",
    "Travel Bag": "BKS Travel Bag",
}

def clean_emoji_title(title: str) -> str:
    """Replace non-ASCII separator with ' — '."""
    # Pattern: "BKS Something [non-ascii] CollectionInfo"
    cleaned = EMOJI_RE.sub(" — ", title)
    # Collapse multiple spaces
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    # Remove trailing/leading dashes from cleanup artifacts
    cleaned = re.sub(r"\s+—\s+—\s+", " — ", cleaned)
    return cleaned

def clean_folklore_title(title: str) -> str:
    """BKS Folklore [SubName] [Type] → BKS [Type] — Origin [SubName]"""
    # Remove "Folklore" keyword
    # e.g. "BKS Folklore Field Windbreaker" → type="Windbreaker", sub="Field"
    m = re.match(r"BKS Folklore\s+(\w+)\s+(.+)", title, re.IGNORECASE)
    if not m:
        return title
    sub_name  = m.group(1).strip()   # "Field"
    remainder = m.group(2).strip()   # "Windbreaker" or "Racerback Dress"
    return f"BKS {remainder} — Origin {sub_name}"

def get(path, **kw):
    return requests.get(f"{BASE}{path}", headers=HDR, verify=False, timeout=20, **kw)

def put(path, payload, **kw):
    return requests.put(f"{BASE}{path}", headers=HDR, json=payload, verify=False, timeout=20, **kw)

# --- STEP 1: inspect one emoji title to see raw chars ---
r = get("/products.json?limit=1&fields=id,title")
sample_title = r.json()["products"][0]["title"] if r.json().get("products") else ""
print(f"Sample title bytes: {sample_title[:30].encode('utf-8')}")
print(f"Sample after clean: {clean_emoji_title(sample_title)}\n")

# --- STEP 2: paginate all products ---
page_info = None
products  = []
while True:
    if page_info:
        url = f"/products.json?limit=50&fields=id,title,variants&page_info={page_info}"
    else:
        url = "/products.json?limit=50&fields=id,title,variants"
    r = get(url)
    batch = r.json().get("products", [])
    if not batch:
        break
    products.extend(batch)
    link = r.headers.get("Link", "")
    nxt  = re.search(r'<[^>]+page_info=([^&>]+)[^>]*>;\s*rel="next"', link)
    page_info = nxt.group(1) if nxt else None
    if not page_info:
        break
    time.sleep(0.3)

print(f"Loaded {len(products)} products.\n")

# --- STEP 3: build changes list ---
title_changes    = []  # (product_id, old_title, new_title)
policy_changes   = []  # (product_id, variant_id, old_policy)

for p in products:
    title = p.get("title", "")
    pid   = p["id"]

    # Title fix
    new_title = title
    if EMOJI_RE.search(title):
        new_title = clean_emoji_title(new_title)
    if re.search(r"folklore", new_title, re.IGNORECASE):
        new_title = clean_folklore_title(new_title)

    if new_title != title:
        title_changes.append((pid, title, new_title))

    # Inventory policy fix
    for v in p.get("variants", []):
        if v.get("inventory_policy", "deny") != "continue":
            policy_changes.append((pid, v["id"], v.get("inventory_policy")))

print(f"Title changes needed:  {len(title_changes)}")
print(f"Policy changes needed: {len(policy_changes)}")

print("\n--- Title preview (first 20) ---")
for pid, old, new in title_changes[:20]:
    print(f"  [{pid}]")
    print(f"    OLD: {old[:80]}")
    print(f"    NEW: {new[:80]}")

print(f"\n--- Inventory policy (first 10 to 'continue') ---")
for pid, vid, pol in policy_changes[:10]:
    print(f"  product {pid} / variant {vid}: {pol} -> continue")

if DRY_RUN:
    print("\n[DRY RUN] No changes written. Re-run with --apply to apply.")
    sys.exit(0)

# --- STEP 4: apply ---
print("\n[APPLYING changes...]\n")
errors = []

# Title updates (one PUT per product)
for i, (pid, old, new) in enumerate(title_changes, 1):
    r = put(f"/products/{pid}.json", {"product": {"id": pid, "title": new}})
    status = "OK" if r.ok else f"ERR {r.status_code}"
    print(f"  [{i}/{len(title_changes)}] {status} | {new[:60]}")
    if not r.ok:
        errors.append(f"title {pid}: {r.text[:100]}")
    time.sleep(0.5)

# Inventory policy updates (one PUT per variant)
for i, (pid, vid, _) in enumerate(policy_changes, 1):
    r = put(f"/variants/{vid}.json", {"variant": {"id": vid, "inventory_policy": "continue"}})
    status = "OK" if r.ok else f"ERR {r.status_code}"
    if i % 20 == 0 or not r.ok:
        print(f"  policy [{i}/{len(policy_changes)}] {status} | variant {vid}")
    if not r.ok:
        errors.append(f"variant {vid}: {r.text[:100]}")
    time.sleep(0.3)

print(f"\nDone. Errors: {len(errors)}")
for e in errors[:10]:
    print(f"  {e}")
