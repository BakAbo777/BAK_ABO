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
# BKS Origin collection ID
r = requests.get(
    f"https://{DOMAIN}/admin/api/2025-01/smart_collections/685331054930.json?fields=id,title,handle",
    headers={"X-Shopify-Access-Token": TOKEN}, verify=False, timeout=15)
if r.ok:
    c = r.json().get("smart_collection") or {}
else:
    r2 = requests.get(
        f"https://{DOMAIN}/admin/api/2025-01/custom_collections/685331054930.json?fields=id,title,handle",
        headers={"X-Shopify-Access-Token": TOKEN}, verify=False, timeout=15)
    c = r2.json().get("custom_collection") or {}
print(f"ID: {c.get('id')}  Handle: {c.get('handle')}  Title: {c.get('title')}")
