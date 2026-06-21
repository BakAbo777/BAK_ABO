"""Elimina pagine duplicate confermate come non referenziate nel menu."""
import os, requests, urllib3
urllib3.disable_warnings()  # type: ignore
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
KW      = {"headers": HDR, "timeout": 20, "verify": False}

# Pagine confermate come duplicati non referenziati nel main menu
# - about-bakabo (171938808146): duplicato di about-bakabo-1 (menu usa about-bakabo-1)
# - bks-about-bks (173590118738): duplicato di about-bks-studio (contenuto già migrato)
PAGES = [
    (171938808146, "about-bakabo",  "duplicato di about-bakabo-1"),
    (173590118738, "bks-about-bks", "duplicato di about-bks-studio"),
]

for pid, handle, note in PAGES:
    # Verifica prima
    r = requests.get(f"{BASE}/pages/{pid}.json", **KW)
    if r.status_code != 200:
        print(f"  SKIP {pid} ({handle}) — non trovata ({r.status_code})")
        continue
    page = r.json().get("page", {})
    print(f"  Elimino: id={page['id']} handle={page['handle']!r} title={page['title']!r} — {note}")
    # Elimina
    d = requests.delete(f"{BASE}/pages/{pid}.json", **KW)
    if d.status_code == 200:
        print(f"    OK — eliminata")
    else:
        print(f"    ERROR {d.status_code}: {d.text[:200]}")
