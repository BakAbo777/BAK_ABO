"""Scarica i file members dal live theme e aggiorna il locale."""
import os, requests, urllib3
from pathlib import Path
urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, _, v = line.partition("=")
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v
SH_DOM = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
SH_TOK = os.environ["SHOPIFY_ADMIN_TOKEN"]
SH_HDR = {"X-Shopify-Access-Token": SH_TOK}
THEME  = "202392961362"
BASE   = f"https://{SH_DOM}/admin/api/2025-01"

PULL = [
    ("snippets/bakabo-header.liquid", "04_TEMA_SHOPIFY/snippets/bakabo-header.liquid"),
    ("assets/bks-member.css",         "04_TEMA_SHOPIFY/assets/bks-member.css"),
    ("assets/bks-member.js",          "04_TEMA_SHOPIFY/assets/bks-member.js"),
]

for (shopify_key, local_path) in PULL:
    r = requests.get(f"{BASE}/themes/{THEME}/assets.json",
        headers=SH_HDR, params={"asset[key]": shopify_key}, verify=False)
    if r.status_code != 200:
        print(f"  ERRORE {shopify_key}: {r.status_code}")
        continue
    content = r.json().get("asset", {}).get("value", "")
    target = ROOT / local_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"  OK  {local_path} ({len(content):,} chars)")
