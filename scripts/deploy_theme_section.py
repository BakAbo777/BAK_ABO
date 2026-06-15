"""Deploy singola sezione o lista di file al tema Shopify attivo."""
from __future__ import annotations
import os, sys, requests, urllib3, time, base64
from pathlib import Path

urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
THEME_DIR = ROOT / "04_TEMA_SHOPIFY"

# File da deployare — aggiungere qui ogni variazione
FILES = [
    # Sezioni principali
    ("sections/bks-piano-hero.liquid",             "sections/bks-piano-hero.liquid"),
    ("sections/bks-impact-home.liquid",            "sections/bks-impact-home.liquid"),
    ("sections/bks-store-reviews.liquid",           "sections/bks-store-reviews.liquid"),
    ("sections/bks-member-dashboard.liquid",        "sections/bks-member-dashboard.liquid"),
    ("sections/bks-member-archive-page.liquid",     "sections/bks-member-archive-page.liquid"),
    ("sections/bks-planet-collections-orbit.liquid","sections/bks-planet-collections-orbit.liquid"),
    ("sections/bks-ai-assistant.liquid",            "sections/bks-ai-assistant.liquid"),
    ("sections/bks-collection-signal.liquid",       "sections/bks-collection-signal.liquid"),
    ("sections/bks-timed-offer.liquid",             "sections/bks-timed-offer.liquid"),
    ("sections/bks-trust-strip.liquid",             "sections/bks-trust-strip.liquid"),
    ("sections/bks-product-editorial-care.liquid",  "sections/bks-product-editorial-care.liquid"),
    # Assets globali
    ("assets/bks-commerce-light.css",              "assets/bks-commerce-light.css"),
    # Assets piano hero
    ("assets/bks-piano-hero.css",                  "assets/bks-piano-hero.css"),
    ("assets/bks-piano-hero.js",                   "assets/bks-piano-hero.js"),
    # Assets member area
    ("assets/bks-member.css",                      "assets/bks-member.css"),
    ("assets/bks-member.js",                       "assets/bks-member.js"),
    # Snippet
    ("snippets/bks-gcr-badge.liquid",              "snippets/bks-gcr-badge.liquid"),
    ("snippets/bks-gcr-survey.liquid",             "snippets/bks-gcr-survey.liquid"),
    # Template membri
    ("templates/customers/account.json",           "templates/customers/account.json"),
    ("templates/customers/account.bks-member.json","templates/customers/account.bks-member.json"),
    # Template pagine custom
    ("templates/page.bks-archive.json",            "templates/page.bks-archive.json"),
    ("templates/page.bks-planet-collections-orbit.json", "templates/page.bks-planet-collections-orbit.json"),
    # Custom request page
    ("sections/bks-custom-request.liquid",              "sections/bks-custom-request.liquid"),
    ("templates/page.bks-custom.json",                  "templates/page.bks-custom.json"),
]


def get_active_theme_id() -> str:
    r = requests.get(f"{BASE}/themes.json", headers=HDR, timeout=15, verify=False)
    r.raise_for_status()
    for t in r.json().get("themes", []):
        if t.get("role") == "main":
            return str(t["id"])
    raise RuntimeError("Nessun tema attivo trovato")


def upload(theme_id: str, src_rel: str, dest_key: str) -> bool:
    src = THEME_DIR / src_rel
    if not src.exists():
        print(f"  SKIP  {dest_key}  (file non trovato: {src})")
        return False

    content = src.read_bytes()
    is_binary = dest_key.split(".")[-1] in {"png","jpg","jpeg","gif","webp","svg","woff","woff2","ttf","ico"}
    payload = {
        "asset": {
            "key": dest_key,
            **({"attachment": base64.b64encode(content).decode()} if is_binary
               else {"value": content.decode("utf-8")}),
        }
    }

    for attempt in range(4):
        r = requests.put(
            f"{BASE}/themes/{theme_id}/assets.json",
            headers=HDR, json=payload, timeout=60, verify=False
        )
        if r.status_code == 429:
            wait = 2 ** attempt + 2
            print(f"    rate limited — attendo {wait}s")
            time.sleep(wait)
            continue
        if r.ok:
            print(f"  OK    {dest_key}")
            return True
        print(f"  ERR   {dest_key}  [{r.status_code}] {r.text[:120]}")
        return False
    return False


def main():
    print("=== Deploy Theme Sections ===\n")
    theme_id = get_active_theme_id()
    print(f"Tema attivo: {theme_id}\n")

    ok = err = 0
    for src_rel, dest_key in FILES:
        if upload(theme_id, src_rel, dest_key):
            ok += 1
        else:
            err += 1
        time.sleep(0.5)

    print(f"\n=== {ok} OK  |  {err} ERRORI ===")


if __name__ == "__main__":
    main()
