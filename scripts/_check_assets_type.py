"""Check asset types in catalog DB."""
import sqlite3, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
assets_json = ROOT / "output" / "bks_active_assets.json"
data = json.loads(assets_json.read_text())
db_path = data.get("catalog_db", "")
print("DB:", db_path)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

rows = conn.execute(
    "SELECT asset_type, COUNT(*) as n FROM assets GROUP BY asset_type ORDER BY n DESC"
).fetchall()
print("\nAsset per tipo:")
for r in rows:
    print(f"  {r['asset_type']:<22} {r['n']}")

cutouts = conn.execute(
    "SELECT file_path, url, collection FROM assets WHERE asset_type='cutout' LIMIT 5"
).fetchall()
print(f"\nCutout: {len(cutouts)} trovati")
for c in cutouts:
    print(f"  col={c['collection']}  {str(c['file_path'])[-60:]}")

gen = conn.execute(
    "SELECT file_path, url, collection, meta_json FROM assets WHERE asset_type='generated' LIMIT 10"
).fetchall()
print(f"\nGenerated: {len(gen)} trovati")
for g in gen:
    print(f"  col={g['collection']}  {str(g['file_path'])[-60:]}")

shopify = conn.execute(
    "SELECT file_path, url, collection FROM assets WHERE asset_type='shopify_web' LIMIT 5"
).fetchall()
print(f"\nShopify web: {len(shopify)} trovati")
for s in shopify:
    print(f"  col={s['collection']}  {str(s['url'])[-80:]}")

conn.close()
