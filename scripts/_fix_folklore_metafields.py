"""
Fix Folklore → Origin for the 8 products:
  1. Update bks.collection metafield → 'BKS Origin'
  2. Replace tag 'bks-folklore' with 'bks-origin'
  3. Add tag 'bks-origin' if missing
  4. Update product images alt text to include Origin

Run with --dry-run (default) or --apply.
"""
import os, re, sys, time, json, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()  # type: ignore

DRY_RUN = "--apply" not in sys.argv

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

def get(path):
    return requests.get(f"{BASE}{path}", headers=HDR, verify=False, timeout=20)

def put(path, payload):
    return requests.put(f"{BASE}{path}", headers=HDR, json=payload, verify=False, timeout=20)

def post(path, payload):
    return requests.post(f"{BASE}{path}", headers=HDR, json=payload, verify=False, timeout=20)

# Find the 8 Folklore products (already renamed or still with "Folklore" in title)
# Use the IDs we know from the audit
FOLKLORE_IDS = [
    8788373930322,   # BKS Folklore Citadel Racerback Dress
    8789095416146,   # BKS Folklore Crew Racerback Dress
    10845138125138,  # BKS Folklore Crowd Flip Flop
    8970303668562,   # BKS Folklore Field Windbreaker
    9285504729426,   # BKS Folklore Grove Racerback Dress
    10831057715538,  # BKS Folklore Manor Travel Bag
    10759740195154,  # BKS Folklore Pelican Hawaiian Shirt
    8969874899282,   # BKS Folklore Shoal Windbreaker
]

# Desired title suffixes after "BKS [Type] — Origin "
SUB_NAMES = {
    8788373930322:  "Citadel",
    8789095416146:  "Crew",
    10845138125138: "Crowd",
    8970303668562:  "Field",
    9285504729426:  "Grove",
    10831057715538: "Manor",
    10759740195154: "Pelican",
    8969874899282:  "Shoal",
}

errors = []

for pid in FOLKLORE_IDS:
    r = get(f"/products/{pid}.json?fields=id,title,tags,images")
    if not r.ok:
        print(f"  SKIP {pid}: {r.status_code}")
        continue

    p = r.json()["product"]
    title    = p.get("title", "")
    tags_raw = p.get("tags", "")
    tags     = [t.strip() for t in tags_raw.split(",") if t.strip()]
    sub_name = SUB_NAMES.get(pid, "")
    images   = p.get("images", [])

    print(f"\n[{pid}] {title}")

    # --- Tag fix ---
    new_tags = [t for t in tags if t.lower() not in ("bks-folklore", "folklore")]
    if "bks-origin" not in [t.lower() for t in new_tags]:
        new_tags.append("bks-origin")
    if new_tags != tags:
        print(f"  Tags: {tags} -> {new_tags}")
        if not DRY_RUN:
            r2 = put(f"/products/{pid}.json",
                     {"product": {"id": pid, "tags": ", ".join(new_tags)}})
            print(f"  Tags update: {'OK' if r2.ok else r2.status_code}")
            if not r2.ok:
                errors.append(f"tags {pid}: {r2.text[:80]}")
    else:
        print(f"  Tags: already correct")
    time.sleep(0.3)

    # --- Metafield: bks.collection ---
    mr = get(f"/products/{pid}/metafields.json")
    meta = mr.json().get("metafields", []) if mr.ok else []
    bks_col_meta = next((m for m in meta if m.get("namespace") == "bks" and m.get("key") == "collection"), None)
    print(f"  bks.collection metafield: {bks_col_meta.get('value') if bks_col_meta else 'NOT SET'}")

    if not DRY_RUN:
        if bks_col_meta:
            # Update existing
            r3 = put(f"/products/{pid}/metafields/{bks_col_meta['id']}.json",
                     {"metafield": {"id": bks_col_meta["id"], "value": "BKS Origin", "type": "single_line_text_field"}})
            print(f"  Metafield update: {'OK' if r3.ok else r3.status_code}")
        else:
            # Create new
            r3 = post(f"/products/{pid}/metafields.json",
                      {"metafield": {"namespace": "bks", "key": "collection",
                                     "value": "BKS Origin", "type": "single_line_text_field"}})
            print(f"  Metafield create: {'OK' if r3.ok else r3.status_code}")
        if not r3.ok:
            errors.append(f"meta {pid}: {r3.text[:80]}")
        time.sleep(0.3)

    # --- Image alt text ---
    for img in images[:3]:
        img_id  = img["id"]
        old_alt = img.get("alt") or ""
        # If alt is empty or contains "Folklore", update
        if not old_alt or "folklore" in old_alt.lower():
            new_alt = f"BKS Origin {sub_name} — wearable art printed after order"
            print(f"  Alt [{img_id}]: '{old_alt}' -> '{new_alt}'")
            if not DRY_RUN:
                r4 = put(f"/products/{pid}/images/{img_id}.json",
                         {"image": {"id": img_id, "alt": new_alt}})
                print(f"  Alt update: {'OK' if r4.ok else r4.status_code}")
                time.sleep(0.3)
        else:
            print(f"  Alt [{img_id}]: already set ('{old_alt[:40]}')")

print(f"\n=== Done. Errors: {len(errors)} ===")
for e in errors:
    print(f"  {e}")
if DRY_RUN:
    print("\n[DRY RUN] Re-run with --apply to write to Shopify.")
