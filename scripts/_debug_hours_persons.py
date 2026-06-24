"""Trova tutte le immagini person-front per prodotti hours."""
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
PY_TOK  = os.environ["PRINTIFY_API_TOKEN"]
SHOP_ID = os.environ.get("PRINTIFY_SHOP_ID", "12030061")
PY_HDR  = {"Authorization": f"Bearer {PY_TOK}"}

all_py = []
for pg in range(1, 30):
    d = requests.get(f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json",
                     headers=PY_HDR, params={"page":pg,"limit":50}, verify=False).json()
    batch = d.get("data", [])
    if not batch: break
    all_py.extend(batch)
    if pg >= int(d.get("last_page", pg)): break

print(f"Totale Printify: {len(all_py)}\n")
print("-- PRODOTTI 'hours' CON person-front:")
for p in all_py:
    ext_id = (p.get("external") or {}).get("id","")
    title = p.get("title","")
    if "hours" not in title.lower(): continue
    for img in p.get("images",[]):
        src = img.get("src","")
        if "camera_label=person-front" in src:
            print(f"  {title[:60]:60} | ext={ext_id}")
            break
