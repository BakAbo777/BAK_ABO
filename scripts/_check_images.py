"""Verifica quanti prodotti hanno immagini su Shopify."""
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
HDR    = {"X-Shopify-Access-Token": TOKEN}

all_prods = []
url = f"https://{DOMAIN}/admin/api/{VER}/products.json?limit=250&fields=id,title,images"
while url:
    r = requests.get(url, headers=HDR, verify=False, timeout=30)
    data = r.json()
    all_prods.extend(data.get("products", []))
    link = r.headers.get("Link", "")
    url = None
    if 'rel="next"' in link:
        for part in link.split(","):
            if 'rel="next"' in part:
                url = part.split(";")[0].strip().strip("<>")
                break

no_img  = [p for p in all_prods if len(p.get("images", [])) == 0]
one_img = [p for p in all_prods if len(p.get("images", [])) == 1]
many    = [p for p in all_prods if len(p.get("images", [])) > 1]

print(f"Totale prodotti: {len(all_prods)}")
print(f"  0 immagini:    {len(no_img)}")
print(f"  1 immagine:    {len(one_img)}")
print(f"  2+ immagini:   {len(many)}")

if no_img:
    print("\nProdotti senza immagini:")
    for p in no_img:
        print(f"  [{p['id']}] {p['title']}")
