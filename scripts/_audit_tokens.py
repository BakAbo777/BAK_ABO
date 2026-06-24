import re
from pathlib import Path
css_dir = Path("I:/BAK ABO/04_TEMA_SHOPIFY/assets")
results = []
for f in sorted(css_dir.glob("bks-*.css")):
    text = f.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    bare = []
    for line in lines:
        stripped = line.strip()
        # Skip comment lines
        if stripped.startswith("/*") or stripped.startswith("*") or stripped.startswith("//"):
            continue
        if re.search(r"#[0-9a-fA-F]{3,6}\b", stripped) and "var(" not in stripped:
            bare.append(stripped)
    total_hex = sum(1 for l in lines if re.search(r"#[0-9a-fA-F]{3,6}", l))
    results.append((f.name, total_hex, len(bare)))
print(f"  {'File':<42} {'Total':>6}  {'Bare (excl comments)'}")
print("  " + "-"*64)
for name, total, bare in sorted(results, key=lambda x: -x[2]):
    flag = " !" if bare > 0 else ""
    print(f"  {name:<42} {total:>6}  {bare}{flag}")
