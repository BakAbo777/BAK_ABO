import sqlite3, json
from pathlib import Path
meta = json.loads((Path("I:/BAK ABO/output/bks_active_assets.json")).read_text())
conn = sqlite3.connect(meta["catalog_db"])
n = conn.execute("DELETE FROM assets WHERE asset_type='bks_hero'").rowcount
conn.commit(); conn.close()
print(f"Cancellati {n} record bks_hero dal DB")
