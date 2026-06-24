"""Legge i print_areas reali da Printify per ogni blueprint presente nel negozio."""
import os, json, requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get("PRINTIFY_API_TOKEN", "")
SHOP  = "12030061"
HDR   = {"Authorization": f"Bearer {TOKEN}"}

r = requests.get(
    f"https://api.printify.com/v1/shops/{SHOP}/products.json?limit=20&page=1",
    headers=HDR, verify=False, timeout=30
)
prods = r.json().get("data", [])

seen_bp = set()
results = []

for p in prods:
    bp = p.get("blueprint_id")
    if bp in seen_bp:
        continue
    seen_bp.add(bp)
    pid = p["id"]
    r2 = requests.get(
        f"https://api.printify.com/v1/shops/{SHOP}/products/{pid}.json",
        headers=HDR, verify=False, timeout=20
    )
    if not r2.ok:
        continue
    prod = r2.json()
    title = prod.get("title", "")[:50]
    print(f"\n=== {title} | bp={bp} ===")
    for area in prod.get("print_areas", []):
        for ph in area.get("placeholders", []):
            pos = ph.get("position", "")
            for img in ph.get("images", []):
                x     = img.get("x")
                y     = img.get("y")
                scale = img.get("scale")
                angle = img.get("angle")
                iid   = str(img.get("id", ""))[:12]
                print(f"  pos={pos:25s}  x={x}  y={y}  scale={scale}  angle={angle}  id={iid}")
