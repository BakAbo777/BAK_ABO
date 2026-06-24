"""Inspect editorial_cutout assets in catalog DB."""
import sqlite3, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "output" / "bks_active_assets.json").read_text())
db_path = data.get("catalog_db", "")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

rows = conn.execute(
    "SELECT file_path, url, collection, product_handle, width, height, meta_json FROM assets WHERE asset_type='editorial_cutout' ORDER BY collection, file_path LIMIT 60"
).fetchall()
print(f"Editorial cutout: {len(rows)} assets\n")
for r in rows:
    meta = {}
    try:
        meta = json.loads(r["meta_json"] or "{}")
    except Exception:
        pass
    fp = str(r["file_path"] or "")
    url = str(r["url"] or "")
    print(f"  col={str(r['collection'] or ''):12s} handle={str(r['product_handle'] or ''):30s} {Path(fp).name if fp else url[-50:]}")

conn.close()
