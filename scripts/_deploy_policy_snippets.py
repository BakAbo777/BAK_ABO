"""Deploy fixed policy snippets and sections to live theme."""
import os, requests, urllib3
urllib3.disable_warnings()  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN","")
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

TO_DEPLOY = [
    ("snippets/bakabo-policy-access.liquid", Path("I:/BAK ABO/scripts/_bakabo-policy-access_live.liquid")),
    ("sections/bks-policy.liquid",           Path("I:/BAK ABO/scripts/_bks_policy_live.liquid")),
]

for shopify_key, local_path in TO_DEPLOY:
    content = local_path.read_text(encoding="utf-8")
    r = requests.put(
        f"{BASE}/themes/202392961362/assets.json",
        headers=HDR,
        json={"asset": {"key": shopify_key, "value": content}},
        verify=False, timeout=30
    )
    if r.ok:
        asset = r.json().get("asset", {})
        print(f"OK  — {shopify_key} ({len(content)} chars) updated_at={asset.get('updated_at')}")
    else:
        print(f"ERR — {shopify_key}: {r.status_code} {r.text[:100]}")
