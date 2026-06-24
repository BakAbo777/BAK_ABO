"""Ispeziona print_areas e layer di un prodotto Printify."""
import json, os, requests, urllib3
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
HDR     = {"Authorization": f"Bearer {TOKEN}"}
BASE    = "https://api.printify.com/v1"

import sys
PRODUCT_ID = sys.argv[1] if len(sys.argv) > 1 else "651f3b7691a9771a560ac91d"

r = requests.get(f"{BASE}/shops/{SHOP_ID}/products/{PRODUCT_ID}.json",
                 headers=HDR, verify=False, timeout=30)
r.raise_for_status()
p = r.json()

print(f"Titolo:    {p['title']}")
print(f"Blueprint: {p['blueprint_id']}  Provider: {p['print_provider_id']}")
print(f"Immagini:  {len(p.get('images', []))}")

print("\n=== PRINT AREAS ===")
for area in p.get("print_areas", []):
    print(f"\nArea — {len(area.get('variant_ids', []))} varianti")
    for ph in area.get("placeholders", []):
        pos = ph.get("position", "?")
        imgs = ph.get("images", [])
        print(f"  [{pos}]  {len(imgs)} img")
        for img in imgs:
            print(f"    id={img.get('id')}  name={img.get('name','?')}")
            print(f"    x={round(img.get('x',0),3)}  y={round(img.get('y',0),3)}  scale={round(img.get('scale',0),4)}  angle={img.get('angle',0)}")
