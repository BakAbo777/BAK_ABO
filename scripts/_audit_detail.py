import re
from pathlib import Path

def bare_hex_lines(filepath):
    text = filepath.read_text(encoding="utf-8", errors="replace")
    results = []
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        # Skip pure comment lines
        if stripped.startswith("/*") or stripped.startswith("*") or stripped.startswith("//"):
            continue
        # Remove inline comments before checking
        no_comment = re.sub(r"/\*.*?\*/", "", stripped)
        if re.search(r"#[0-9a-fA-F]{3,6}\b", no_comment) and "var(" not in no_comment:
            results.append((i, stripped[:95]))
    return results

for fname in ["bks-responsive.css", "bks-member.css"]:
    f = Path("I:/BAK ABO/04_TEMA_SHOPIFY/assets") / fname
    hits = bare_hex_lines(f)
    print(f"=== {fname}: {len(hits)} bare hex lines ===")
    for lineno, text in hits:
        print(f"  L{lineno}: {text}")
    print()
