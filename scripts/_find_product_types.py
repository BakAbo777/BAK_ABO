"""Mostra tutti i prodotti 'All Over Prints' e cerca Hawaiian/shirt nel catalogo."""
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
SH_DOM=os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]; SH_TOK=os.environ["SHOPIFY_ADMIN_TOKEN"]
SH_HDR={"X-Shopify-Access-Token":SH_TOK}

sh_prods=[]
url=f"https://{SH_DOM}/admin/api/2025-01/products.json"
params={"status":"active","limit":250,"fields":"id,handle,title,product_type"}
while url:
    r=requests.get(url,headers=SH_HDR,params=params,verify=False)
    params=None; sh_prods.extend(r.json().get("products",[])); link=r.headers.get("Link",""); url=None
    for part in link.split(","):
        if 'rel="next"' in part: url=part.strip().split(";")[0].strip("<>")

print("-- 'All Over Prints' products (primo 20):")
aop = [p for p in sh_prods if p.get("product_type")=="All Over Prints"]
for p in aop[:20]:
    print(f"  {p['handle'][:55]:55} | {p.get('title','')[:50]}")

print(f"\nTotale AOP: {len(aop)}")
print("\n-- Cerca Hawaiian/shirt/camicia nei titoli:")
for p in sh_prods:
    t = (p.get("title","") + " " + p.get("handle","")).lower()
    if any(w in t for w in ["hawaii","hawaiian","shirt","camicia","aloha"]):
        print(f"  {p['handle'][:55]} | type={p['product_type']}")
