"""Ispeziona print areas e immagini per i 4 puffer needs_rework."""
import json, os, requests as rq
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

TOKEN = env.get("PRINTIFY_API_TOKEN", "")
SHOP  = env.get("PRINTIFY_SHOP_ID", "12030061")
BASE  = "https://api.printify.com/v1"
PH    = {"Authorization": f"Bearer {TOKEN}"}

PIDS = {
    "BKS Weft™ Puffer (score=17)":               "unknown",
    "BKS Folklore Arabesque™ Puffer (score=18)":  "origin",
    "BKS Glyph Mesh™ Puffer (score=19)":          "glyph",
    "BKS Folklore Block™ Puffer (score=15)":      "origin",
}

# Cerca i prodotti nel log per ottenere i PID
log = json.loads(open("ecommerce_automation/design_batch_log.json").read())
rework_puffers = {v["title"]: pid for pid, v in log.items()
                  if v["status"] == "needs_rework" and "puffer" in v["title"].lower()}

print(f"Puffer needs_rework trovati: {len(rework_puffers)}")

# Prendi il primo e ispeziona le print_areas
for title, pid in list(rework_puffers.items())[:2]:
    print(f"\n=== {title} ===")
    r = rq.get(f"{BASE}/shops/{SHOP}/products/{pid}.json", headers=PH, verify=False, timeout=20)
    if not r.ok:
        print(f"  HTTP {r.status_code}: {r.text[:100]}")
        continue
    prod = r.json()
    bp   = prod.get("blueprint_id")
    print(f"  blueprint_id: {bp}")
    for area in prod.get("print_areas", []):
        for ph in area.get("placeholders", []):
            pos  = ph.get("position", "?")
            imgs = ph.get("images", [])
            for img in imgs:
                iid   = img.get("id", "?")[:24]
                x     = round(img.get("x", 0), 3)
                y     = round(img.get("y", 0), 3)
                scale = round(img.get("scale", 0), 3)
                angle = img.get("angle", 0)
                print(f"  pos={pos:25s}  x={x:.3f}  y={y:.3f}  scale={scale:.3f}  a={angle}  id={iid}")
