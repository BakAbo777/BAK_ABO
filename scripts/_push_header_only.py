"""Push just bakabo-header.liquid."""
import os, sys, requests, urllib3
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
urllib3.disable_warnings()  # type: ignore
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1); k=k.strip(); v=v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v
DOMAIN=os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]; TOKEN=os.environ["SHOPIFY_ADMIN_TOKEN"]
VER=os.environ.get("SHOPIFY_API_VERSION","2025-01"); THEME="202392961362"
BASE=f"https://{DOMAIN}/admin/api/{VER}"; HDR={"X-Shopify-Access-Token": TOKEN}
key="snippets/bakabo-header.liquid"
body=(ROOT/"04_TEMA_SHOPIFY"/"_merged_tm04"/"snippets"/"bakabo-header.liquid").read_text(encoding="utf-8")
r=requests.put(f"{BASE}/themes/{THEME}/assets.json", json={"asset":{"key":key,"value":body}}, headers=HDR, timeout=30, verify=False)
print(f"HTTP {r.status_code}  {key}")
if r.status_code not in (200,201): print(r.text[:400])
