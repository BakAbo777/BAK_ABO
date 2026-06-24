"""
Piano Hero — hero images da prodotti REALI Shopify.
Nessuna generazione AI: usa le immagini CDN già esistenti dei prodotti BKS.
Logica: per ogni collezione prende il prodotto hero (tipo prioritario),
sceglie l'immagine principale e aggiorna index.json + pusha al tema.
"""
from __future__ import annotations
import os, json, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]:
        os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
LIVE_ID = "202392961362"
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

# Per ogni collezione: handle Shopify + tipo prodotto preferito per hero
# L'ordine di HERO_TYPES determina la priorità (primo match vince)
COLLECTIONS = [
    {"slug": "hours",   "handle": "bks-hours",   "hero_types": ["Puffer Jacket", "Hoodie", "Lounge Pants"]},
    {"slug": "glyph",   "handle": "bks-glyph",   "hero_types": ["Puffer Jacket", "Hoodie", "Windbreaker"]},
    {"slug": "marker",  "handle": "bks-marker",  "hero_types": ["Puffer Jacket", "Athletic Shorts", "Swim Trunks"]},
    {"slug": "riviera", "handle": "bks-riviera", "hero_types": ["One-Piece Swimsuit", "Swim Trunks", "Puffer Jacket"]},
    {"slug": "pulse",   "handle": "bks-pulse",   "hero_types": ["Puffer Jacket", "Hoodie", "Sneakers"]},
    {"slug": "token",   "handle": "bks-token",   "hero_types": ["Puffer Jacket", "Hoodie", "Tee"]},
    {"slug": "flag",    "handle": "bks-flag",    "hero_types": ["Puffer Jacket", "Hoodie", "Tee"]},
    {"slug": "origin",  "handle": "bks-origin",  "hero_types": ["Puffer Jacket", "Hoodie", "Tee"]},
]


def get_collection_id(handle: str) -> str | None:
    r = requests.get(
        f"{BASE}/custom_collections.json",
        headers=HDR, params={"handle": handle}, timeout=15, verify=False,
    )
    cols = r.json().get("custom_collections", [])
    if not cols:
        # prova smart_collections
        r2 = requests.get(
            f"{BASE}/smart_collections.json",
            headers=HDR, params={"handle": handle}, timeout=15, verify=False,
        )
        cols = r2.json().get("smart_collections", [])
    return str(cols[0]["id"]) if cols else None


def get_hero_image(handle: str, hero_types: list[str]) -> tuple[str, str]:
    """Restituisce (image_url, product_title) del prodotto hero nella collezione."""
    col_id = get_collection_id(handle)
    if not col_id:
        print(f"    [WARN] Collezione '{handle}' non trovata")
        return "", ""

    # Prende fino a 50 prodotti della collezione
    r = requests.get(
        f"{BASE}/collections/{col_id}/products.json",
        headers=HDR,
        params={"limit": 50, "fields": "id,title,product_type,images,status"},
        timeout=20, verify=False,
    )
    products = [p for p in r.json().get("products", []) if p.get("status") == "active"]

    # Cerca per tipo prioritario
    for hero_type in hero_types:
        for p in products:
            ptype = p.get("product_type", "")
            if hero_type.lower() in ptype.lower():
                imgs = p.get("images", [])
                if imgs:
                    url = imgs[0]["src"]
                    # Rimuovi query string Shopify (serve URL pulito)
                    url = url.split("?")[0]
                    return url, p["title"]

    # Fallback: primo prodotto con immagine
    for p in products:
        imgs = p.get("images", [])
        if imgs:
            url = imgs[0]["src"].split("?")[0]
            return url, p["title"]

    return "", ""


def patch_and_push() -> None:
    index_path = ROOT / "04_TEMA_SHOPIFY" / "templates" / "index.json"
    data = json.loads(index_path.read_text(encoding="utf-8"))
    piano = data["sections"]["bks_piano_hero"]["blocks"]

    updated = 0
    for col in COLLECTIONS:
        slug   = col["slug"]
        handle = col["handle"]
        print(f"\n-- {handle} ------------------")
        img_url, title = get_hero_image(handle, col["hero_types"])
        if img_url:
            block_key = f"piano_{slug}"
            if block_key in piano:
                piano[block_key]["settings"]["image_url"] = img_url
                updated += 1
                print(f"  [OK] {title}")
                print(f"       {img_url[-70:]}")
        else:
            print(f"  [SKIP] Nessuna immagine trovata")

    index_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{'='*60}")
    print(f"index.json aggiornato: {updated}/8 collezioni")

    # Push al tema live
    body = index_path.read_text(encoding="utf-8")
    r = requests.put(
        f"{BASE}/themes/{LIVE_ID}/assets.json",
        headers=HDR,
        json={"asset": {"key": "templates/index.json", "value": body}},
        timeout=30, verify=False,
    )
    if r.status_code in (200, 201):
        print(f"[OK] index.json pushato al tema live")
    else:
        print(f"[ERR] Push fallito: {r.status_code} {r.text[:200]}")


if __name__ == "__main__":
    patch_and_push()
