"""Resync immagini Printify per i 2 prodotti rimasti senza immagini su Shopify."""
import os, sys, requests, urllib3, json
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

DOMAIN    = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
S_TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
P_TOKEN   = os.environ["PRINTIFY_API_TOKEN"]
SHOP_ID   = "12030061"
VER       = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
S_HDR     = {"X-Shopify-Access-Token": S_TOKEN}
P_HDR     = {"Authorization": f"Bearer {P_TOKEN}"}

# Products with 0 images
TARGETS = {
    8970368418130: "BKS Windbreaker — Flag 02",
    10768310698322: "BKS Windbreaker — Token 02",
}

# Find Printify product_id from hero log (keys are Printify IDs)
LOG_PATH = ROOT / "output" / "hero_generation_log.json"
log = json.loads(LOG_PATH.read_text(encoding="utf-8"))

# Build reverse map: shopify product id → printify id (from log)
# (log has entries where some didn't upload to shopify, but we can try Printify search)

for shopify_id, title in TARGETS.items():
    print(f"\n=== {title} (Shopify {shopify_id}) ===")

    # Try to find via Printify search by title
    r = requests.get(
        f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json?limit=100",
        headers=P_HDR, verify=False, timeout=30
    )
    products = r.json().get("data", [])

    match = None
    for p in products:
        if shopify_id == p.get("external", {}).get("id"):
            match = p
            break
        # Also try by title similarity
        if "Flag 02" in title and "Flag" in p.get("title", "") and "02" in p.get("title", ""):
            match = p
        elif "Token 02" in title and "Token" in p.get("title", "") and "02" in p.get("title", ""):
            match = p

    if not match:
        print(f"  Printify product NOT found — skipping")
        continue

    print(f"  Printify: {match['id']} — {match['title']}")

    # Get mockup images from Printify
    r2 = requests.get(
        f"https://api.printify.com/v1/shops/{SHOP_ID}/products/{match['id']}.json",
        headers=P_HDR, verify=False, timeout=30
    )
    detail = r2.json()
    images = detail.get("images", [])
    print(f"  Printify images: {len(images)}")

    # Upload first 3 images to Shopify product
    for i, img in enumerate(images[:3]):
        src = img.get("src", "")
        if not src: continue
        r3 = requests.post(
            f"https://{DOMAIN}/admin/api/{VER}/products/{shopify_id}/images.json",
            headers={**S_HDR, "Content-Type": "application/json"},
            json={"image": {"src": src, "position": i+1}},
            verify=False, timeout=30
        )
        if r3.status_code in (200, 201):
            print(f"  OK  image {i+1} uploaded")
        else:
            print(f"  ERR image {i+1}: {r3.status_code} {r3.text[:100]}")

print("\nDone.")
