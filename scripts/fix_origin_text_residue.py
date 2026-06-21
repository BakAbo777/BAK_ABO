"""Fix remaining 'BKS Folklore' text in collection body_html and product title/body_html
(text only - no handle changes, no URL impact). One-off follow-up to rename_folklore_to_origin.py.
"""
import os, requests, urllib3, json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore

urllib3.disable_warnings()  # type: ignore
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]:
        os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

COLLECTION_ID = 685331054930
PRODUCT_ID = 10845887365458


def replace_folklore(text):
    return (text or "").replace("BKS Folklore", "BKS Origin").replace("Folklore", "Origin")


print("=== Fix collection body_html ===")
r = requests.get(f"{BASE}/smart_collections/{COLLECTION_ID}.json", headers=HDR, timeout=30, verify=False)
col = r.json()["smart_collection"]
new_body = replace_folklore(col["body_html"])
print("Before:", col["body_html"][:120])
print("After: ", new_body[:120])
r2 = requests.put(
    f"{BASE}/smart_collections/{COLLECTION_ID}.json",
    json={"smart_collection": {"id": COLLECTION_ID, "body_html": new_body}},
    headers=HDR, timeout=30, verify=False,
)
print(r2.status_code)

print("\n=== Fix product title/body_html ===")
r = requests.get(f"{BASE}/products/{PRODUCT_ID}.json", headers=HDR, timeout=30, verify=False)
prod = r.json()["product"]
new_title = replace_folklore(prod["title"])
new_body = replace_folklore(prod["body_html"])
print("Title before:", prod["title"])
print("Title after: ", new_title)
r2 = requests.put(
    f"{BASE}/products/{PRODUCT_ID}.json",
    json={"product": {"id": PRODUCT_ID, "title": new_title, "body_html": new_body}},
    headers=HDR, timeout=30, verify=False,
)
print(r2.status_code)
print("Handle unchanged:", r2.json().get("product", {}).get("handle"))
