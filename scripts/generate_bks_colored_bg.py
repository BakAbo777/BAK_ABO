"""
BKS Colored Background Generator
Composita ogni editorial_cutout sul colore accent della collezione.
Output: {handle}_bks_bg.png — 1200x1200, product centrato con 12% padding.
"""
from __future__ import annotations
import sqlite3, json, os, requests, urllib3
from pathlib import Path
from PIL import Image

urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent

# ── Env ──────────────────────────────────────────────────────────────────────
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

# ── Colori accent per collezione ──────────────────────────────────────────────
COLLECTION_COLORS: dict[str, tuple[int, int, int]] = {
    "bks-hours":   (200, 196, 190),   # #c8c4be  carta pietra
    "bks-glyph":   (212, 160,  48),   # #d4a030  oro
    "bks-marker":  (192,  68,  24),   # #c04418  terracotta
    "bks-riviera": ( 12, 168, 152),   # #0ca898  teal mediterraneo
    "bks-pulse":   (136, 136, 204),   # #8888cc  lavanda elettrica
    "bks-token":   (152,  40, 216),   # #9828d8  viola digitale
    "bks-flag":    (200,  32,  32),   # #c82020  rosso manifesto
    "bks-origin":  ( 72, 152,   8),   # #489808  verde natura
}

CANVAS_SIZE  = 1200
PADDING_PCT  = 0.12          # 12% su ogni lato — prodotto occupa 76% del canvas

# ── DB ───────────────────────────────────────────────────────────────────────
data = json.loads((ROOT / "output" / "bks_active_assets.json").read_text())
db_path = data.get("catalog_db", "")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

rows = conn.execute(
    "SELECT id, file_path, url, collection, product_handle FROM assets "
    "WHERE asset_type='editorial_cutout' AND collection != 'uncategorized' "
    "ORDER BY collection, file_path"
).fetchall()

print(f"Cutout da processare: {len(rows)}\n")

def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))  # type: ignore

def composite_on_color(cutout_path: Path, bg_rgb: tuple, out_path: Path) -> None:
    """Apre cutout RGBA, crea sfondo colorato, composita, salva 1200x1200."""
    src = Image.open(cutout_path).convert("RGBA")

    # Calcola dimensione target con padding
    pad = int(CANVAS_SIZE * PADDING_PCT)
    max_dim = CANVAS_SIZE - 2 * pad
    src.thumbnail((max_dim, max_dim), Image.LANCZOS)

    # Canvas sfondo colorato
    bg = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), bg_rgb + (255,))

    # Centra il prodotto
    x = (CANVAS_SIZE - src.width)  // 2
    y = (CANVAS_SIZE - src.height) // 2
    bg.paste(src, (x, y), mask=src)

    # Salva come RGB JPEG-compatible PNG
    bg.convert("RGB").save(out_path, "PNG", optimize=True)


def upload_to_shopify(handle: str, img_path: Path) -> str | None:
    """Carica immagine su Shopify come secondo prodotto. Restituisce CDN URL."""
    # Prima trova il product ID dal handle
    r = requests.get(
        f"{BASE}/products.json",
        headers=HDR,
        params={"handle": handle, "fields": "id,title,images", "limit": 1},
        timeout=15, verify=False,
    )
    prods = r.json().get("products", [])
    if not prods:
        return None
    product_id = prods[0]["id"]

    # Carica come binary → base64
    import base64
    img_b64 = base64.b64encode(img_path.read_bytes()).decode()
    r2 = requests.post(
        f"{BASE}/products/{product_id}/images.json",
        headers=HDR,
        json={"image": {"attachment": img_b64, "filename": img_path.name, "position": 2}},
        timeout=30, verify=False,
    )
    if r2.status_code in (200, 201):
        return r2.json().get("image", {}).get("src")
    print(f"    [upload ERR] {r2.status_code}: {r2.text[:80]}")
    return None


generated: list[dict] = []
skipped = 0

for row in rows:
    handle     = row["product_handle"] or ""
    collection = row["collection"] or ""
    fp         = Path(row["file_path"] or "")

    if not fp.exists():
        print(f"  [MISS] {handle}")
        skipped += 1
        continue

    bg_rgb = COLLECTION_COLORS.get(collection)
    if not bg_rgb:
        print(f"  [SKIP] collezione sconosciuta: {collection}")
        skipped += 1
        continue

    out_path = fp.parent / fp.name.replace("_cutout.png", "_bks_bg.png")

    print(f"  [{collection}] {handle}")
    composite_on_color(fp, bg_rgb, out_path)
    print(f"    -> {out_path.name}  ({out_path.stat().st_size // 1024} KB)")

    # Upload su Shopify
    cdn_url = upload_to_shopify(handle, out_path)
    if cdn_url:
        print(f"    -> Shopify OK: {cdn_url[-60:]}")
    else:
        print(f"    -> Shopify: prodotto non trovato / handle non live")

    generated.append({
        "handle": handle,
        "collection": collection,
        "local": str(out_path),
        "shopify_url": cdn_url or "",
    })

# ── Registra nel DB ──────────────────────────────────────────────────────────
for g in generated:
    conn.execute(
        "INSERT OR IGNORE INTO assets (product_handle, asset_type, collection, file_path, url) "
        "VALUES (?, 'generated', ?, ?, ?)",
        (g["handle"], g["collection"], g["local"], g["shopify_url"]),
    )
conn.commit()
conn.close()

# ── Report ───────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"Generati:  {len(generated)}")
print(f"Saltati:   {skipped}")
uploaded = sum(1 for g in generated if g["shopify_url"])
print(f"Su Shopify: {uploaded}/{len(generated)}")

if generated:
    print("\nOutput directory:")
    print(f"  {ROOT / 'output' / 'catalog_images' / 'editorial'}")
