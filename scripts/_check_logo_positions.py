"""Verifica posizioni logo per blueprint: lounge_pants, slippers, travel_bag, backpack, hawaiian, etc."""
import os, requests, time
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get("PRINTIFY_API_TOKEN", "")
SHOP  = "12030061"
HDR   = {"Authorization": f"Bearer {TOKEN}"}

LOGO_IDS = {"6a217ca23d24179e1f1eaf5f", "660d81c6209c2958d2f0bb75"}

TARGET_BP = {
    739:  "lounge_pants",
    1095: "slippers",
    587:  "flip_flops",
    888:  "travel_bag",
    581:  "backpack",
    924:  "hawaiian",
    372:  "duffel_bag",
    371:  "beach_towel",
    212:  "hoodie",
    291:  "sneakers",
    279:  "tee",
    934:  "puffer",
}

# Pagina tutti i prodotti con limit=20
all_prods = []
for pg in range(1, 20):
    r = requests.get(
        f"https://api.printify.com/v1/shops/{SHOP}/products.json?limit=20&page={pg}",
        headers=HDR, verify=False, timeout=30
    )
    if not r.ok:
        break
    batch = r.json().get("data", [])
    all_prods.extend(batch)
    if len(batch) < 20:
        break
    time.sleep(0.1)

print(f"Totale prodotti caricati: {len(all_prods)}")

seen_bp = {}
for p in all_prods:
    bp = p.get("blueprint_id")
    if bp in TARGET_BP and bp not in seen_bp:
        seen_bp[bp] = p

print(f"Blueprint trovati: {len(seen_bp)}/{len(TARGET_BP)}")
missing = set(TARGET_BP) - set(seen_bp)
if missing:
    print(f"  Mancanti: {[TARGET_BP[bp] for bp in missing]}")
print()

for bp, p in sorted(seen_bp.items()):
    r_full = requests.get(
        f"https://api.printify.com/v1/shops/{SHOP}/products/{p['id']}.json",
        headers=HDR, verify=False, timeout=20
    )
    if not r_full.ok:
        print(f"=== bp={bp} ({TARGET_BP[bp]}) — ERRORE ===\n")
        continue

    prod = r_full.json()
    print(f"=== {prod['title'][:55]} | bp={bp} ({TARGET_BP[bp]}) ===")

    has_logo = False
    for area in prod.get("print_areas", []):
        for ph in area.get("placeholders", []):
            pos = ph.get("position", "")
            for img in ph.get("images", []):
                iid = img.get("id", "")
                nm  = (img.get("name") or "").lower()
                if iid in LOGO_IDS or any(n in nm for n in ["logo","bks","sd0","barra"]):
                    has_logo = True
                    note = "WARN scale=1 full" if (img.get("scale") or 0) >= 0.9 else "OK"
                    print(f"  LOGO  pos={pos:28s}  x={str(img.get('x',''))[:6]:<8}  y={str(img.get('y',''))[:6]:<8}  scale={str(img.get('scale',''))[:6]:<8}  angle={img.get('angle')}  {note}")
    if not has_logo:
        print("  (nessun logo)")
    print()
    time.sleep(0.1)
