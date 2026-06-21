"""Sync patched footer.liquid to local theme folder."""
import re
from pathlib import Path

content = Path("I:/BAK ABO/scripts/_footer_live.liquid").read_text(encoding="utf-8")
pattern = re.compile(
    r'\{%-?\s*for link in linklists\.support\.links\s*-?%\}.*?\{%-?\s*endfor\s*-?%\}',
    re.DOTALL
)
replacement = (
    '<li><a href="/pages/help-faq">Help &amp; FAQ</a></li>\n'
    '          <li><a href="/policies/shipping-policy">Shipping</a></li>\n'
    '          <li><a href="/policies/refund-policy">Returns</a></li>\n'
    '          <li><a href="/policies/privacy-policy">Privacy</a></li>\n'
    '          <li><a href="/policies/terms-of-service">Terms</a></li>\n'
    '          <li><a href="/pages/contact">Contact</a></li>'
)
new_content, count = pattern.subn(replacement, content)
Path("I:/BAK ABO/04_TEMA_SHOPIFY/sections/footer.liquid").write_text(new_content, encoding="utf-8")
print(f"Local copy updated ({count} replacement, {len(new_content)} chars)")
