"""Imposta come draft i 2 prodotti orfani senza immagini e senza Printify."""
import os, sys, requests, urllib3
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
VER    = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

ORPHANS = {
    8970368418130:  "BKS Windbreaker — Flag 02",
    10768310698322: "BKS Windbreaker — Token 02",
}

for pid, title in ORPHANS.items():
    r = requests.put(
        f"https://{DOMAIN}/admin/api/{VER}/products/{pid}.json",
        headers=HDR,
        json={"product": {"id": pid, "status": "draft"}},
        verify=False, timeout=20,
    )
    if r.status_code == 200:
        print(f"DRAFT: {title}")
    else:
        print(f"ERR {r.status_code}: {title} → {r.text[:100]}")
