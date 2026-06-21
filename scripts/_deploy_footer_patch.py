"""
Patch footer.liquid: replace linklists.support.links loop with hardcoded English links.
Deploy to live theme.
"""
import os, re, requests, urllib3, sys
urllib3.disable_warnings()  # type: ignore
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
from pathlib import Path

for raw in Path("I:/BAK ABO/.env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ:
            os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

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
print(f"Replaced {count}x  ({len(content)} -> {len(new_content)} chars)")

if count == 0:
    print("ERR: pattern not found")
    sys.exit(1)

# Deploy
r = requests.put(
    f"{BASE}/themes/202392961362/assets.json",
    headers=HDR,
    json={"asset": {"key": "sections/footer.liquid", "value": new_content}},
    verify=False, timeout=30
)
if r.ok:
    asset = r.json().get("asset", {})
    print(f"OK — sections/footer.liquid  updated_at={asset.get('updated_at')}")
else:
    print(f"ERR: {r.status_code} {r.text[:300]}")
