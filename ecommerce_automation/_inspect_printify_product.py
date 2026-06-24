"""Inspect a specific Printify product and its print_areas."""
import requests, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

TOKEN = env["PRINTIFY_API_TOKEN"]
SHOP  = "12030061"
HDR   = {"Authorization": f"Bearer {TOKEN}"}

PROD_ID = "651c452249ddc69dc20d0dc6"

r = requests.get(f"https://api.printify.com/v1/shops/{SHOP}/products/{PROD_ID}.json",
    headers=HDR, verify=False, timeout=30)
prod = r.json()

print(f"Title: {prod.get('title')}")
print(f"Blueprint: {prod.get('blueprint_id')}")
print(f"Visible: {prod.get('visible')}")
print()
print("Print areas images:")
for area in prod.get("print_areas", []):
    for ph in area.get("placeholders", []):
        pos = ph.get("position","")
        for img in ph.get("images", []):
            img_id = img.get("id","")
            print(f"  pos={pos:20s}  id={img_id}  src={img.get('src','')[:60]}")
