import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from ecommerce_automation.bks_db import bks_db
print("Tables:", len(bks_db.list_tables()))
rows = bks_db.query('SELECT handle, title FROM bks_collection_plan_v20 WHERE "group"="Editoriali"')
print("Editoriali:", [r["handle"] for r in rows])
rows2 = bks_db.query("SELECT title FROM bks_collection_plan_v20 WHERE handle LIKE '%origin%'")
print("Origin:", rows2[0]["title"] if rows2 else "not found")
