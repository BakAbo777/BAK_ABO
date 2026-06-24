"""
Download design templates (wonder_*.jpg) da Printify per tutti i prodotti.
Per ogni prodotto: trova il design layer (non-logo) nelle print_areas,
scarica il file originale dal CDN Printify.

Output: BAKABO_IMAGE_FACTORY_v1.1/output/printify_library/designs/{handle}/

Usa:
    python scripts/_download_design_templates.py
    python scripts/_download_design_templates.py --collection pulse
    python scripts/_download_design_templates.py --limit 10
"""
import argparse, json, time, sys
from pathlib import Path

import requests, urllib3
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

TOKEN   = env.get("PRINTIFY_API_TOKEN", "")
SHOP_ID = env.get("PRINTIFY_SHOP_ID", "12030061")
BASE    = "https://api.printify.com/v1"
HDR     = {"Authorization": f"Bearer {TOKEN}"}
OUT_DIR = ROOT / "BAKABO_IMAGE_FACTORY_v1.1" / "output" / "printify_library" / "designs"

LOGO_IDS   = {"6a217ca23d24179e1f1eaf5f", "660d81c6209c2958d2f0bb75"}
LOGO_NAMES = {"bks.png", "bks_logo.png", "lg 002.png", "lg002.png", "lg_002.png"}
# Posizioni placeholder da saltare (etichette interne, neck label)
SKIP_POSITIONS = {"inside_label", "label", "neck_label", "inside label", "label_inside", "inside-label"}

def is_logo(img: dict) -> bool:
    return img.get("id") in LOGO_IDS or (img.get("name", "").lower() in LOGO_NAMES)

def is_skip_position(position: str) -> bool:
    return position.lower().replace(" ", "_") in {p.replace(" ", "_") for p in SKIP_POSITIONS}

def get_collection_from_tags(tags) -> str:
    if isinstance(tags, list):
        tag_list = tags
    else:
        tag_list = [t.strip() for t in (tags or "").split(",")]
    for tag in tag_list:
        t = str(tag).strip().lower()
        if t.startswith("collection:"):
            return t.split(":", 1)[1].strip()
    return "unknown"

def fetch_all_products(collection_filter: str | None = None) -> list[dict]:
    products = []
    page = 1
    while True:
        url = f"{BASE}/shops/{SHOP_ID}/products.json?limit=20&page={page}"
        r = requests.get(url, headers=HDR, verify=False, timeout=30)
        if not r.ok:
            print(f"  WARN pagina {page}: {r.status_code} — stop")
            break
        data = r.json()
        batch = data.get("data", [])
        if not batch:
            break
        for p in batch:
            col = get_collection_from_tags(p.get("tags", ""))
            if collection_filter and col != collection_filter:
                continue
            products.append(p)
        if len(batch) < 20:
            break
        page += 1
        time.sleep(0.3)
    return products

def fetch_product_full(product_id: str) -> dict | None:
    r = requests.get(f"{BASE}/shops/{SHOP_ID}/products/{product_id}.json", headers=HDR, verify=False, timeout=20)
    if r.ok:
        return r.json()
    return None

def get_design_ids(product: dict) -> list[dict]:
    designs = []
    seen = set()
    for area in product.get("print_areas", []):
        for ph in area.get("placeholders", []):
            position = ph.get("position", "?")
            if is_skip_position(position):
                continue  # salta inside_label, neck_label, ecc.
            for img in ph.get("images", []):
                if not is_logo(img) and img["id"] not in seen:
                    seen.add(img["id"])
                    designs.append({"id": img["id"], "name": img.get("name", ""), "position": position})
    return designs

def get_upload_url(image_id: str, cache: dict) -> str | None:
    if image_id in cache:
        return cache[image_id]
    try:
        r = requests.get(f"{BASE}/uploads/{image_id}.json", headers=HDR, verify=False, timeout=15)
        if r.ok:
            url = r.json().get("preview_url")
            cache[image_id] = url
            return url
    except Exception as e:
        print(f"    WARN upload fetch {image_id}: {e}")
    return None

def download_file(url: str, dest: Path) -> bool:
    try:
        r = requests.get(url, timeout=60, verify=False, stream=True)
        r.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(r.content)
        return True
    except Exception as e:
        print(f"    ERR download {dest.name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default=None, help="Filtra per collezione (es. pulse)")
    parser.add_argument("--limit", type=int, default=0, help="Max prodotti da processare (0=tutti)")
    parser.add_argument("--skip-existing", action="store_true", default=True, help="Salta se design gia scaricato")
    args = parser.parse_args()

    print(f"\nBKS Design Template Downloader")
    print(f"  Shop:       {SHOP_ID}")
    print(f"  Collezione: {args.collection or 'tutte'}")
    print(f"  Output:     {OUT_DIR}")
    print()

    print("Carico prodotti da Printify...")
    products = fetch_all_products(args.collection)
    if args.limit:
        products = products[:args.limit]
    print(f"  {len(products)} prodotti trovati\n")

    url_cache: dict[str, str] = {}
    stats = {"products": 0, "designs": 0, "downloaded": 0, "skipped": 0, "errors": 0}

    for prod in products:
        prod_id = prod["id"]
        col     = get_collection_from_tags(prod.get("tags", ""))

        # Fetch prodotto completo per avere print_areas
        full = fetch_product_full(prod_id)
        if not full:
            print(f"  SKIP {prod_id}: fetch failed")
            continue
        time.sleep(0.2)

        handle = full.get("handle") or prod_id
        title  = full.get("title", handle)
        designs = get_design_ids(full)

        if not designs:
            continue

        stats["products"] += 1
        prod_dir = OUT_DIR / col / handle
        prod_dir.mkdir(parents=True, exist_ok=True)

        # Salva manifest prodotto
        manifest = {
            "product_id": prod["id"],
            "handle": handle,
            "title": title,
            "collection": col,
            "blueprint_id": prod.get("blueprint_id"),
            "designs": [],
        }

        for i, design in enumerate(designs, 1):
            stats["designs"] += 1
            dest_name = f"{handle}_design_{i:02d}_{design['name']}"
            dest = prod_dir / dest_name

            if args.skip_existing and dest.exists() and dest.stat().st_size > 10000:
                stats["skipped"] += 1
                manifest["designs"].append({"id": design["id"], "name": design["name"], "local": dest_name, "status": "existing"})
                continue

            url = get_upload_url(design["id"], url_cache)
            if not url:
                stats["errors"] += 1
                print(f"  [{col}] {handle} — design {design['name']}: URL non trovato")
                manifest["designs"].append({"id": design["id"], "name": design["name"], "local": None, "status": "no_url"})
                continue

            ok = download_file(url, dest)
            if ok:
                stats["downloaded"] += 1
                size_kb = dest.stat().st_size // 1024
                print(f"  [{col}] {handle} — {dest_name} ({size_kb}KB)")
                manifest["designs"].append({"id": design["id"], "name": design["name"], "local": dest_name, "status": "ok", "size_kb": size_kb})
            else:
                stats["errors"] += 1
                manifest["designs"].append({"id": design["id"], "name": design["name"], "local": None, "status": "error"})

            time.sleep(0.1)

        # Salva manifest per prodotto
        (prod_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Prodotti processati : {stats['products']}")
    print(f"Design trovati      : {stats['designs']}")
    print(f"Scaricati           : {stats['downloaded']}")
    print(f"Saltati (esistenti) : {stats['skipped']}")
    print(f"Errori              : {stats['errors']}")
    print(f"Output              : {OUT_DIR}")

if __name__ == "__main__":
    main()
