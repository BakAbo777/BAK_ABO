"""Trova i prodotti Printify corrispondenti ai 2 Shopify ID senza immagini."""
import os, sys, requests, urllib3
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

P_TOKEN   = os.environ["PRINTIFY_API_TOKEN"]
S_TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
DOMAIN    = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
SHOP_ID   = "12030061"
VER       = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
P_HDR     = {"Authorization": f"Bearer {P_TOKEN}"}
S_HDR     = {"X-Shopify-Access-Token": S_TOKEN}

TARGETS = {8970368418130, 10768310698322}
TARGET_NAMES = {
    8970368418130: "BKS Windbreaker — Flag 02",
    10768310698322: "BKS Windbreaker — Token 02",
}

# Paginate through all Printify products
page = 1
found = {}
while True:
    url = f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json?limit=100&page={page}"
    r = requests.get(url, headers=P_HDR, verify=False, timeout=30)
    data = r.json()
    prods = data.get("data", [])
    if not prods:
        break
    for p in prods:
        ext = p.get("external", {})
        ext_id = ext.get("id")
        try:
            ext_id_int = int(ext_id) if ext_id else 0
        except Exception:
            ext_id_int = 0
        if ext_id_int in TARGETS:
            found[ext_id_int] = p
            print(f"FOUND: printify={p['id']} shopify={ext_id_int} title={p['title']}")
    last = data.get("last_page", page)
    if page >= last:
        break
    page += 1

print(f"\nFound {len(found)} / {len(TARGETS)} products")

# For each found product, get its images and upload to Shopify
for shopify_id, p in found.items():
    print(f"\n--- Restoring images for Shopify {shopify_id}: {p['title']}")
    images = p.get("images", [])
    print(f"  Printify has {len(images)} images")
    for i, img in enumerate(images[:4]):
        src = img.get("src", "")
        if not src:
            continue
        r2 = requests.post(
            f"https://{DOMAIN}/admin/api/{VER}/products/{shopify_id}/images.json",
            headers={**S_HDR, "Content-Type": "application/json"},
            json={"image": {"src": src, "position": i + 1}},
            verify=False, timeout=30,
        )
        if r2.status_code in (200, 201):
            img_id = r2.json().get("image", {}).get("id", "?")
            print(f"  OK  position {i+1}  id={img_id}")
        else:
            print(f"  ERR {r2.status_code}: {r2.text[:120]}")

# For products NOT found in Printify, report
for tid in TARGETS:
    if tid not in found:
        print(f"\nNOT FOUND in Printify: {tid} — {TARGET_NAMES.get(tid)}")
        print("  → These products may have been deleted from Printify. Check admin.")
