"""Lista tutte le pagine Shopify con handle e template."""
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

r = requests.get(f"https://{SH_DOM}/admin/api/2025-01/pages.json",
    headers=SH_HDR, params={"limit":250,"fields":"id,handle,title,template_suffix,published_at"},
    verify=False)
pages = sorted(r.json().get("pages",[]), key=lambda p: p["handle"])
print(f"Totale pagine: {len(pages)}\n")
for p in pages:
    pub = "pub" if p.get("published_at") else "DRAFT"
    tmpl = p.get("template_suffix") or "default"
    print(f"  /{p['handle']:<45} [{tmpl:<30}] {pub} | {p['title'][:40]}")
