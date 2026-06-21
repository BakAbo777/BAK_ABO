"""
Fix image alt text for BKS Origin products:
- Replace 'BKS Folklore' with 'BKS Origin' in all product image alt texts
- Also fixes any 'Folklore' residuals in product image alt

Run dry-run first, then --apply.
"""
import os, sys, re, requests, urllib3, time
from pathlib import Path

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

# Fetch all active products that are in BKS Origin (by title or tag)
# Also catch any product whose image alt text contains 'Folklore'
all_products, page_info = [], None
while True:
    params = "limit=250&fields=id,title,status&status=active"
    if page_info: params += f"&page_info={page_info}"
    r = requests.get(f"{BASE}/products.json?{params}", headers=HDR, verify=False, timeout=30)
    all_products.extend(r.json().get("products", []))
    link = r.headers.get("Link", "")
    if 'rel="next"' not in link: break
    m = re.search(r'page_info=([^&>]+)[^>]*>;\s*rel="next"', link)
    page_info = m.group(1) if m else None

print(f"Total active products: {len(all_products)}")

# Focus on Origin products (by title) plus any with 'Folklore' in title (old name)
origin_prods = [p for p in all_products
    if "origin" in p["title"].lower() or "folklore" in p["title"].lower()]
print(f"Origin/Folklore products: {len(origin_prods)}")

changes = []
for p in origin_prods:
    # Fetch images for this product
    r = requests.get(f"{BASE}/products/{p['id']}/images.json?fields=id,alt,src",
                     headers=HDR, verify=False, timeout=20)
    images = r.json().get("images", [])
    for img in images:
        alt = img.get("alt") or ""
        if "folklore" in alt.lower():
            new_alt = re.sub(r'(?i)BKS Folklore', 'BKS Origin', alt)
            new_alt = re.sub(r'(?i)Folklore', 'Origin', new_alt)
            changes.append({
                "pid": p["id"],
                "iid": img["id"],
                "old_alt": alt,
                "new_alt": new_alt,
                "product": p["title"][:40],
            })
            print(f"  [{p['id']}] img[{img['id']}] {alt!r:60} -> {new_alt!r}")
    time.sleep(0.1)

print(f"\nTotal image alt texts to fix: {len(changes)}")

if not DRY_RUN and changes:
    ok = err = 0
    for c in changes:
        r = requests.put(
            f"{BASE}/products/{c['pid']}/images/{c['iid']}.json",
            headers=HDR,
            json={"image": {"id": c["iid"], "alt": c["new_alt"]}},
            verify=False, timeout=20)
        if r.ok:
            ok += 1
        else:
            err += 1
            print(f"  ERR [{c['iid']}]: {r.status_code} {r.text[:60]}")
        time.sleep(0.25)
    print(f"\nDone: {ok}/{len(changes)} OK, {err} errors")
elif DRY_RUN and changes:
    print(f"\n[DRY RUN] Run with --apply to fix {len(changes)} image alt texts.")
elif not changes:
    print("\nNo 'Folklore' alt texts found. Already clean.")
