import sqlite3

conn = sqlite3.connect("I:/BAK ABO/ecommerce_automation/database.db")
cur = conn.cursor()
cur.execute("""
    SELECT bks_collection, product_type, title, handle
    FROM external_references
    ORDER BY bks_collection, product_type, title
""")
rows = cur.fetchall()
conn.close()

print(f"Total: {len(rows)} products")

by_col = {}
for col, ptype, title, handle in rows:
    c = (col or "unknown").lower()
    by_col.setdefault(c, []).append((ptype or "", title, handle))

for c in sorted(by_col):
    print(f"\n=== {c.upper()} ({len(by_col[c])}) ===")
    for ptype, title, handle in by_col[c][:10]:
        print(f"  [{ptype:30s}] {title}")
