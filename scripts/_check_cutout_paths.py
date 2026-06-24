"""Check physical location of editorial_cutout files."""
import sqlite3, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "output" / "bks_active_assets.json").read_text())
db_path = data.get("catalog_db", "")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

rows = conn.execute(
    "SELECT file_path, url, collection, product_handle FROM assets WHERE asset_type='editorial_cutout' AND collection != 'uncategorized' ORDER BY collection, file_path LIMIT 30"
).fetchall()

print("Cutout delle 8 collezioni BKS:\n")
found = 0
for r in rows:
    fp = r["file_path"] or ""
    url = r["url"] or ""
    p = Path(fp) if fp else None
    exists = p.exists() if p else False
    status = "OK  " if exists else "MISS"
    print(f"  [{status}] col={r['collection']:<12} {Path(fp).name if fp else url[-60:]}")
    if exists:
        found += 1

print(f"\nFile trovati su disco: {found}/{len(rows)}")

# Mostra un campione di path per capire la struttura directory
print("\nPath assoluti (primi 3):")
for r in rows[:3]:
    print(f"  '{r['file_path']}'")
conn.close()
