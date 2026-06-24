"""Mostra le prime 8 URL immagini per 2 prodotti puffer jacket."""
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
PY_TOK=os.environ["PRINTIFY_API_TOKEN"]; SHOP_ID=os.environ.get("PRINTIFY_SHOP_ID","12030061")
SH_HDR={"X-Shopify-Access-Token":SH_TOK}; PY_HDR={"Authorization":f"Bearer {PY_TOK}"}

r = requests.get(f"https://{SH_DOM}/admin/api/2025-01/products.json", headers=SH_HDR,
    params={"status":"active","limit":50,"fields":"id,handle,tags,product_type",
            "product_type":"Puffer Jacket"}, verify=False)
puffers = r.json().get("products", [])[:3]

all_py = []
for pg in range(1, 5):
    d = requests.get(f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json",
                     headers=PY_HDR, params={"page":pg,"limit":50}, verify=False).json()
    batch = d.get("data", [])
    if not batch: break
    all_py.extend(batch)
    if pg >= int(d.get("last_page", pg)): break
py_map = {str((p.get("external") or {}).get("id","")): p for p in all_py}

for sh in puffers:
    py_p = py_map.get(str(sh["id"]))
    if not py_p: continue
    print(f"\n{sh['handle']}  tags={sh['tags'][:60]}")
    for img in py_p.get("images", [])[:8]:
        src = img.get("src","")
        qs = "?" + src.split("?")[1] if "?" in src else ""
        print(f"  {qs[:120]}")
