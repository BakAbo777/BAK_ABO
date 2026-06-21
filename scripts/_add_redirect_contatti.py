"""Add 301 redirect: /pages/contatti → /pages/contact"""
import os, requests, urllib3, sys
urllib3.disable_warnings()  # type: ignore
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
from pathlib import Path

for raw in Path("I:/BAK ABO/.env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ:
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

payload = {"redirect": {"path": "/pages/contatti", "target": "/pages/contact"}}
r = requests.post(f"{BASE}/redirects.json", headers=HDR, json=payload, verify=False, timeout=20)
if r.ok:
    rd = r.json().get("redirect", {})
    print(f"Redirect created: {rd['path']} → {rd['target']} (id={rd['id']})")
else:
    print(f"ERR {r.status_code}: {r.text[:200]}")
