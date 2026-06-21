"""Delete ghost product type pages that have no catalog products."""
import os, requests, urllib3
urllib3.disable_warnings()  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

PAGES_TO_DELETE = [
    (123676164434, "/pages/bks-hawaiian-shirt", "BKS Hawaiian Shirts"),
    (123789050194, "/pages/bks-duffel-bag",     "BKS Duffel Bags"),
    (123454194002, "/pages/bks-beach-towel",    "BKS Beach Towels"),
]

for pid, url, title in PAGES_TO_DELETE:
    r = requests.delete(f"{BASE}/pages/{pid}.json", headers=HDR, verify=False, timeout=20)
    if r.status_code in (200, 204):
        print(f"DELETED [{pid}] {url} - {title!r}")
    else:
        print(f"ERR [{pid}] {r.status_code}: {r.text[:60]}")
