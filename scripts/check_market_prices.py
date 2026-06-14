import csv
from pathlib import Path

csv_path = Path("output/products_export_updated.csv")
with csv_path.open(encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        it  = row.get("Included / Italy") or ""
        kr  = row.get("Included / Corea del Sud") or ""
        us  = row.get("Included / United States") or ""
        intl = row.get("Included / International") or ""
        if it or kr or us or intl:
            p_it  = row.get("Price / Italy") or ""
            p_kr  = row.get("Price / Corea del Sud") or ""
            p_us  = row.get("Price / United States") or ""
            p_intl = row.get("Price / International") or ""
            handle = row.get("Handle") or ""
            print(f"Row {i+1} handle={handle}")
            print(f"  Italy:  included={it} price={p_it}")
            print(f"  US:     included={us} price={p_us}")
            print(f"  Korea:  included={kr} price={p_kr}")
            print(f"  Intl:   included={intl} price={p_intl}")
            break
    else:
        print("No rows with market data found")
