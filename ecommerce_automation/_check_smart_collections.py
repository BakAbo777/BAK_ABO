"""Check products_count for all BKS type smart collections."""
import requests
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

SHOP  = env["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN = env["SHOPIFY_ADMIN_TOKEN"]

r = requests.get(
    f"https://{SHOP}/admin/api/2025-01/smart_collections.json",
    params={"limit": 250, "fields": "id,handle,title,products_count"},
    headers={"X-Shopify-Access-Token": TOKEN},
    verify=False, timeout=30,
)
cols = r.json().get("smart_collections", [])
bks_type = [c for c in cols if c["handle"].startswith("bks-type-")]
total = 0
for c in sorted(bks_type, key=lambda x: x["handle"]):
    cnt = c.get("products_count", 0)
    total += cnt
    flag = "  " if cnt > 0 else "EMPTY"
    print(f"{flag}  {c['handle']:35s}  {cnt:3d} products")
print(f"\nTotal smart collections: {len(bks_type)}, total products: {total}")
