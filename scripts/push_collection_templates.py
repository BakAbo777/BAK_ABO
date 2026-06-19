"""Pusha tutti i template collection da _merged_tm04 al tema live."""
import os, json, time, requests, urllib3, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
urllib3.disable_warnings()

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
THEME  = "202392961362"
BASE   = f"https://{DOMAIN}/admin/api/{VER}"
HDR    = {"X-Shopify-Access-Token": TOKEN}

TMPL_DIR = ROOT / "04_TEMA_SHOPIFY" / "_merged_tm04" / "templates"

collection_templates = sorted(TMPL_DIR.glob("collection*.json"))
product_templates    = sorted(TMPL_DIR.glob("product*.json"))
templates = collection_templates + product_templates
print(f"Template locali trovati: {len(collection_templates)} collection + {len(product_templates)} product\n")

ok = err = 0
for path in templates:
    key  = f"templates/{path.name}"
    body = path.read_text(encoding="utf-8")

    # Valida JSON
    try:
        json.loads(body)
    except json.JSONDecodeError as e:
        print(f"  ERR  {key}  (json invalido: {e})")
        err += 1
        continue

    r = requests.put(
        f"{BASE}/themes/{THEME}/assets.json",
        json={"asset": {"key": key, "value": body}},
        headers=HDR, timeout=20, verify=False
    )
    if r.status_code in (200, 201):
        print(f"  PUSH {key}")
        ok += 1
    elif r.status_code == 422:
        errors = r.json().get("errors", r.text[:120])
        print(f"  422  {key}  {errors}")
        err += 1
    else:
        print(f"  ERR  {key}  HTTP {r.status_code}")
        err += 1

    time.sleep(0.35)

print(f"\nFine: {ok} pushati, {err} errori")
