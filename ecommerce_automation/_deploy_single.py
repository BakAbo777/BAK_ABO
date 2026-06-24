"""Deploy a single theme asset to Shopify. Usage: python _deploy_single.py <asset_key> <local_file>"""
import sys, os, json, requests
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

shop = env["SHOPIFY_MYSHOPIFY_DOMAIN"]
token = env["SHOPIFY_ADMIN_TOKEN"]
theme_id = "202392961362"

asset_key = sys.argv[1]
local_file = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "04_TEMA_SHOPIFY" / asset_key

value = local_file.read_text(encoding="utf-8")
resp = requests.put(
    f"https://{shop}/admin/api/2025-01/themes/{theme_id}/assets.json",
    headers={"X-Shopify-Access-Token": token, "Content-Type": "application/json"},
    json={"asset": {"key": asset_key, "value": value}},
    verify=False,
)
a = resp.json().get("asset", {})
print(f"OK: {a.get('key')} @ {a.get('updated_at')}")
