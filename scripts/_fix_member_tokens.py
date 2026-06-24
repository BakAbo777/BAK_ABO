"""Tokenize remaining bare hex values in bks-member.css."""
import re
from pathlib import Path

f = Path("I:/BAK ABO/04_TEMA_SHOPIFY/assets/bks-member.css")
text = f.read_text(encoding="utf-8")

# Map of exact string replacements (context-sensitive)
replacements = [
    # Toast dark bg + text
    ("background: #111;",       "background: var(--bks-bg, #111);"),
    ("color: #f0ece4;",         "color: var(--bks-text, #f0ece4);"),
    # Heart icon stroke (white) + wishlist badge text
    ("stroke: #fff;",           "stroke: var(--bks-paper, #fff);"),
    ("color: #fff;",            "color: var(--bks-paper, #fff);"),
    # Gold button text — all 3 occurrences (#000 on gold bg)
    # Use replace_all approach for #000 followed by semicolon
    # Status pills + indicators
    ("color: #4ade80; }",       "color: var(--bks-status-ok-bright, #4ade80); }"),
    ("color: #f87171; }",       "color: var(--bks-status-err-bright, #f87171); }"),
    ("background: #4ade80;",    "background: var(--bks-status-ok-bright, #4ade80);"),
]

for old, new in replacements:
    count = text.count(old)
    if count > 0:
        text = text.replace(old, new)
        print(f"  {count}x  {old[:60]}")

# Fix all `color: #000;` occurrences (3 on separate lines)
count = text.count("color: #000;")
text = text.replace("color: #000;", "color: var(--bks-ink, #000);")
print(f"  {count}x  color: #000;")

f.write_text(text, encoding="utf-8")
print("  Done.")
