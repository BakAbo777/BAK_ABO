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
for path in ["/collections/bks-folklore", "/collections/outerwear"]:
    r = requests.get(f"https://{DOMAIN}/admin/api/2025-01/redirects.json?path={path}",
                     headers={"X-Shopify-Access-Token": TOKEN}, verify=False, timeout=10)
    data = r.json().get("redirects", [])
    if data:
        print(f"  {path} -> {data[0]['target']} (id={data[0]['id']})")
    else:
        print(f"  {path}: NO REDIRECT")
