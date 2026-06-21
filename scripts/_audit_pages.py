"""Audit all Shopify pages: empty, Italian, or OK."""
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
HDR    = {"X-Shopify-Access-Token": TOKEN}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

r = requests.get(f"{BASE}/pages.json?limit=250&fields=id,title,handle,body_html,template_suffix",
                 headers=HDR, verify=False, timeout=30)
pages = r.json().get("pages", [])

ITALIAN_WORDS = ["della", "dello", "degli", "delle", "sono", "con", "per", "dal",
                 "che", "una", "uno", "gli", "nei", "sui", "tra", "fra", "dal",
                 "prodott", "spediz", "reso", "resi", "contatt", "pagina"]

empty, italian, ok_pages = [], [], []
for p in pages:
    body = (p.get("body_html") or "").strip()
    body_lower = body.lower()
    if not body:
        empty.append(p)
    elif any(w in body_lower for w in ITALIAN_WORDS):
        italian.append(p)
    else:
        ok_pages.append(p)

print(f"\n=== EMPTY ({len(empty)}) ===")
for p in empty:
    tmpl = p.get("template_suffix") or "default"
    print(f"  [{p['id']}] '{p['title']}' handle={p['handle']} template={tmpl}")

print(f"\n=== POSSIBLE ITALIAN CONTENT ({len(italian)}) ===")
for p in italian:
    preview = body[:80].replace("\n"," ") if (body := (p.get("body_html") or "").strip()) else ""
    print(f"  [{p['id']}] '{p['title']}' handle={p['handle']}")
    print(f"    {preview}")

print(f"\n=== OK ENGLISH ({len(ok_pages)}) ===")
for p in ok_pages:
    print(f"  [{p['id']}] '{p['title']}' handle={p['handle']}")
