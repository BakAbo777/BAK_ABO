"""Archivia prodotti Shopify senza immagine (vecchi / non più disponibili).

Modalità:
  --dry-run   stampa i prodotti senza archiviarli (default)
  --execute   archivia realmente (status → archived)
"""
import os, sys, time, requests, urllib3, argparse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
urllib3.disable_warnings()  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
VER    = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE   = f"https://{DOMAIN}/admin/api/{VER}"
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

parser = argparse.ArgumentParser()
parser.add_argument("--execute", action="store_true", help="Archivia realmente i prodotti")
args = parser.parse_args()
dry_run = not args.execute

print(f"=== {'DRY RUN' if dry_run else 'EXECUTE'} — Prodotti senza immagine ===\n")

# Raccoglie tutti i prodotti con paginazione
products_no_image = []
url = f"{BASE}/products.json?limit=250&fields=id,title,status,images"

while url:
    r = requests.get(url, headers=HDR, timeout=30, verify=False)
    r.raise_for_status()
    data = r.json()
    for p in data.get("products", []):
        if p["status"] != "archived" and len(p.get("images", [])) == 0:
            products_no_image.append(p)
    # Paginazione Link header
    link = r.headers.get("Link", "")
    next_url = None
    for part in link.split(","):
        if 'rel="next"' in part:
            next_url = part.split(";")[0].strip().strip("<>")
    url = next_url
    time.sleep(0.4)

print(f"Trovati {len(products_no_image)} prodotti senza immagine:\n")
for p in products_no_image:
    print(f"  [{p['id']}] {p['title']}")

if not products_no_image:
    print("Nessun prodotto da archiviare.")
    sys.exit(0)

if dry_run:
    print("\nDry run completato. Usa --execute per archiviare.")
    sys.exit(0)

# Archivia
print(f"\nArchiviando {len(products_no_image)} prodotti...")
ok = err = 0
for p in products_no_image:
    r = requests.put(
        f"{BASE}/products/{p['id']}.json",
        json={"product": {"id": p["id"], "status": "archived"}},
        headers=HDR, timeout=20, verify=False
    )
    if r.status_code in (200, 201):
        print(f"  ARCH  {p['title']}")
        ok += 1
    else:
        print(f"  ERR   {p['title']}  HTTP {r.status_code}")
        err += 1
    time.sleep(0.35)

print(f"\nFine: {ok} archiviati, {err} errori")
