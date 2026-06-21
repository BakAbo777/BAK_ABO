"""Backfill Printify product collection from title."""
import sys, sqlite3
sys.path.insert(0, '.')
from scripts.sync_printify_library import backfill_collections
from bks_assets import active_catalog_db
from pathlib import Path

db = Path(active_catalog_db())
n = backfill_collections(db)
print(f"Updated: {n} products")

conn = sqlite3.connect(db)
rows = conn.execute("SELECT collection, COUNT(*) FROM printify_products GROUP BY collection ORDER BY collection").fetchall()
conn.close()
for k, v in rows:
    label = k if k else "(no collection)"
    print(f"  {label}: {v}")
