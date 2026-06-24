"""
Scarica le immagini source mancanti da Printify per i 130 prodotti senza immagine locale.
Salva in BAKABO_IMAGE_FACTORY_v1.1/output/source/ come {handle}_source.jpg
"""
from __future__ import annotations
import os, re, time, requests, urllib3, sqlite3
from pathlib import Path

urllib3.disable_warnings()

ROOT       = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "BAKABO_IMAGE_FACTORY_v1.1" / "output" / "source"
SOURCE_DIR.mkdir(parents=True, exist_ok=True)

# Leggi .env
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

TOKEN   = env.get("PRINTIFY_API_TOKEN", "")
SHOP_ID = env.get("PRINTIFY_SHOP_ID", "12030061")
BASE    = "https://api.printify.com/v1"
HDR     = {"Authorization": f"Bearer {TOKEN}"}

if not TOKEN:
    print("ERRORE: PRINTIFY_API_TOKEN non trovato nel .env")
    raise SystemExit(1)

def api_get(path, **params):
    r = requests.get(f"{BASE}{path}", headers=HDR, params=params, timeout=30, verify=False)
    r.raise_for_status()
    return r.json()

def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80]

# Recupera lista prodotti già in locale
existing = {f.stem.replace("_source", "") for f in SOURCE_DIR.glob("*_source.*")}
print(f"Source esistenti: {len(existing)}")

# Recupera tutti i prodotti da Printify (paginated)
print("Recupero lista prodotti da Printify...")
all_products = []
page = 1
while True:
    data = api_get(f"/shops/{SHOP_ID}/products.json", page=page, limit=50)
    batch = data.get("data", [])
    all_products.extend(batch)
    if len(batch) < 50:
        break
    page += 1
    time.sleep(0.3)

print(f"Totale prodotti Printify: {len(all_products)}")

# Filtra quelli senza source locale
to_download = []
for p in all_products:
    handle = slug(p.get("title", p.get("id", "unknown")))
    if handle not in existing:
        images = p.get("images", [])
        # prendi immagine default o prima disponibile
        img_url = None
        for img in images:
            if img.get("is_default"):
                img_url = img.get("src")
                break
        if not img_url and images:
            img_url = images[0].get("src")
        if img_url:
            to_download.append((handle, img_url, p.get("title", "")))

print(f"Da scaricare: {len(to_download)}\n")

# Download
ok = 0
fail = 0
for i, (handle, url, title) in enumerate(to_download, 1):
    dest = SOURCE_DIR / f"{handle}_source.jpg"
    try:
        r = requests.get(url, timeout=30, verify=False)
        r.raise_for_status()
        dest.write_bytes(r.content)
        ok += 1
        print(f"[{i:3}/{len(to_download)}] OK  {handle[:60]}")
    except Exception as e:
        fail += 1
        print(f"[{i:3}/{len(to_download)}] ERR {handle[:50]} — {e}")
    time.sleep(0.15)

print(f"\n{'='*60}")
print(f"Scaricati:  {ok}")
print(f"Errori:     {fail}")
print(f"Totale ora: {len(existing) + ok} source images")
