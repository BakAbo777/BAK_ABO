"""Ripristina il design originale di un prodotto usando l'ID immagine precedente."""
import json, sys, requests, urllib3
from pathlib import Path
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

TOKEN   = env.get("PRINTIFY_API_TOKEN", "")
SHOP_ID = env.get("PRINTIFY_SHOP_ID", "12030061")
HDR     = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json;charset=utf-8"}
BASE    = "https://api.printify.com/v1"

PRODUCT_ID   = "651f3b7691a9771a560ac91d"
OLD_DESIGN_ID = "65fc9a5cf4d2aa25a886e107"  # wonder_1710848635576.jpg — originale
BAD_DESIGN_ID = "6a39bb8cbc0eb64699bd253b"  # mockup caricato per errore

# Fetch prodotto
r = requests.get(f"{BASE}/shops/{SHOP_ID}/products/{PRODUCT_ID}.json", headers=HDR, verify=False, timeout=30)
p = r.json()
print(f"Prodotto: {p['title']}")

# Sostituisce BAD con OLD in tutte le print_areas
import copy
areas = copy.deepcopy(p.get("print_areas", []))
replaced = 0
for area in areas:
    for ph in area.get("placeholders", []):
        for img in ph.get("images", []):
            if img.get("id") == BAD_DESIGN_ID:
                img["id"] = OLD_DESIGN_ID
                replaced += 1

print(f"Layer da ripristinare: {replaced}")
r2 = requests.put(
    f"{BASE}/shops/{SHOP_ID}/products/{PRODUCT_ID}.json",
    headers=HDR, json={"print_areas": areas}, verify=False, timeout=30
)
print(f"Status: {r2.status_code}")
if r2.ok:
    print("Ripristinato OK — design originale restored.")
else:
    print(f"Errore: {r2.text[:200]}")
