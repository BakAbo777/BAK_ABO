"""Push AI assistant position fix + header language pill CSS to live theme."""
import os, sys, requests, urllib3, base64
from pathlib import Path

urllib3.disable_warnings()  # type: ignore
ROOT = Path(__file__).resolve().parent.parent

for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ:
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

DOMAIN   = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN    = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
THEME_ID = "202392961362"
BASE_URL = f"https://{DOMAIN}/admin/api/2025-01/themes/{THEME_ID}/assets.json"
HDR      = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

FILES = [
    ("sections/bks-ai-assistant.liquid",  ROOT / "04_TEMA_SHOPIFY/sections/bks-ai-assistant.liquid"),
    ("snippets/bakabo-header.liquid",     ROOT / "04_TEMA_SHOPIFY/snippets/bakabo-header.liquid"),
]

ok = True
for key, path in FILES:
    content = path.read_text(encoding="utf-8")
    r = requests.put(BASE_URL, headers=HDR, json={"asset": {"key": key, "value": content}}, verify=False, timeout=30)
    if r.status_code == 200:
        print(f"  OK  {key}")
    else:
        print(f"  ERR {key} — {r.status_code}: {r.text[:200]}")
        ok = False

sys.exit(0 if ok else 1)
