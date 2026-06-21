"""Debug products with no collection assignment."""
import sys, sqlite3
sys.path.insert(0, '.')
from bks_assets import active_catalog_db
from pathlib import Path

db = Path(active_catalog_db())
conn = sqlite3.connect(db)

rows = conn.execute(
    "SELECT title FROM printify_products WHERE collection IS NULL OR collection = '' LIMIT 20"
).fetchall()
print("Sample titles with no collection:")
for r in rows:
    print(" ", repr(r[0][:60]))

# Check for origin
origin = conn.execute(
    "SELECT title FROM printify_products WHERE title LIKE '%Origin%' OR title LIKE '%origin%' LIMIT 5"
).fetchall()
print("\nOrigin titles:", [r[0][:50] for r in origin])

# Check for any bks- in titles
bks = conn.execute(
    "SELECT DISTINCT substr(title, 1, 20) FROM printify_products WHERE title LIKE 'BKS %' LIMIT 30"
).fetchall()
print("\nBKS title prefixes:", [r[0] for r in bks[:15]])
conn.close()
