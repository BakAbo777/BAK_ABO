import re
from pathlib import Path
for fname in ["bks-responsive.css"]:
    f = Path("I:/BAK ABO/04_TEMA_SHOPIFY/assets") / fname
    text = f.read_text(encoding="utf-8", errors="replace")
    for i, line in enumerate(text.splitlines(), 1):
        if re.search(r"#[0-9a-fA-F]{3,6}\b", line) and "var(" not in line:
            print(f"  L{i}: {line.strip()[:95]}")
