"""Cerca tutti i prodotti per tipo: beach towel, slipper, cut&sew, tee."""
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

keywords = {
    "beach towel": ["towel","asciugamano","beach"],
    "slipper": ["slipper","ciabatta","mule","house shoe"],
    "cut & sew": ["cut","sew","cut-sew","cut_sew"],
    "tee / t-shirt": ["tee","t-shirt","shirt"],
}

for label, kws in keywords.items():
    hits = [p for p in sh_prods
            if any(k in (p.get("handle","") + " " + p.get("title","")).lower() for k in kws)]
    print(f"\n--- {label.upper()} ({len(hits)})")
    for p in hits[:10]:
        print(f"  {p['handle'][:55]:55} | type={p['product_type']} | {p.get('title','')[:40]}")

# Mostra anche tutti i product_type distinti
from collections import Counter
types = Counter(p.get("product_type","?") for p in sh_prods)
print(f"\n--- TUTTI I PRODUCT TYPE:")
for t, c in sorted(types.items(), key=lambda x: -x[1]):
    print(f"  {t:35} {c:3}")
