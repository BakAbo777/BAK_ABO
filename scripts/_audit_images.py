"""Audit immagini Printify: cosa è stato importato, cosa manca."""
import sqlite3
from pathlib import Path

SOURCE_DIR = Path("I:/BAK ABO/BAKABO_IMAGE_FACTORY_v1.1/output/source")
CUTOUT_DIR = Path("I:/BAK ABO/BAKABO_IMAGE_FACTORY_v1.1/output/cutout")

conn = sqlite3.connect("I:/BAK ABO/ecommerce_automation/database.db")
cur = conn.cursor()
cur.execute("""
    SELECT handle, title, bks_collection, product_type,
           shopify_product_id, printify_product_id, local_catalog_path
    FROM external_references
    ORDER BY bks_collection, product_type
""")
rows = cur.fetchall()
conn.close()

total = len(rows)
has_source = 0
has_cutout = 0
no_image = []

print(f"{'COLLEZIONE':<12} {'TIPO':<30} {'SRC':>4} {'CUT':>4}  PRODOTTO")
print("-" * 90)

for handle, title, col, ptype, shopify_id, printify_id, local_path in rows:
    # cerca source
    matches_src = list(SOURCE_DIR.glob(f"*{handle}*"))
    if not matches_src and title:
        slug = title.lower().replace(" ","- ").replace("–","-").replace("—","-")[:40]
    src = "OK" if matches_src else "--"

    # cerca cutout
    matches_cut = list(CUTOUT_DIR.glob(f"*{handle}*"))
    cut = "OK" if matches_cut else "--"

    if matches_src:
        has_source += 1
    if matches_cut:
        has_cutout += 1
    if not matches_src:
        no_image.append((col or "?", ptype or "?", title, handle))

    if matches_src or matches_cut:
        print(f"{(col or '?'):<12} {(ptype or '?'):<30} {src:>4} {cut:>4}  {title[:45]}")

print(f"\n{'='*90}")
print(f"Totale prodotti DB:    {total}")
print(f"Con source image:      {has_source}  ({has_source*100//total}%)")
print(f"Con cutout:            {has_cutout}  ({has_cutout*100//total}%)")
print(f"SENZA immagini:        {total - has_source}")

if no_image:
    print(f"\n=== MANCANO SOURCE ({len(no_image)}) ===")
    for col, ptype, title, handle in sorted(no_image):
        print(f"  [{col:<10}] {ptype:<28} {title}")
