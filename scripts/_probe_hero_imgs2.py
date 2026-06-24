"""Proba immagini Printify — tutti i tipi disponibili per 3 prodotti."""
import os, requests, urllib3, sys
from pathlib import Path
urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, _, v = line.partition("=")
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

SH_DOM=os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]; SH_TOK=os.environ["SHOPIFY_ADMIN_TOKEN"]
PY_TOK=os.environ["PRINTIFY_API_TOKEN"]; SHOP_ID=os.environ.get("PRINTIFY_SHOP_ID","12030061")
SH_HDR={"X-Shopify-Access-Token":SH_TOK}; PY_HDR={"Authorization":f"Bearer {PY_TOK}"}

# Prendi i primi 3 prodotti disponibili
d = requests.get(f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json",
                 headers=PY_HDR, params={"page":1,"limit":3}, verify=False).json()
prods = d.get("data", [])

for p in prods:
    ext_id = (p.get("external") or {}).get("id","?")
    print(f"\n== {p['title'][:60]} (ext_id={ext_id})")
    for i, img in enumerate(p.get("images",[])[:10]):
        src = img.get("src","")
        qs = src.split("?",1)[1] if "?" in src else "(no qs)"
        print(f"  [{i}] {qs[:130]}")
        sys.stdout.flush()
