"""
Patch footer.liquid:
  - Replace dynamic linklists.support.links loop with hardcoded English links
  - Fix /pages/contatti -> /pages/contact in fallback block
Then deploy to live theme.
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
original_len = len(content)

# Replace the entire for..endfor block for the support links
# Pattern matches the loop and its else fallback (with possible extra whitespace/newlines)
pattern = re.compile(
    r'\{%-?\s*for link in linklists\.support\.links\s*-?%\}.*?\{%-?\s*endfor\s*-?%\}',
    re.DOTALL
)

replacement = """\
<li><a href="/pages/help-faq">Help &amp; FAQ</a></li>
          <li><a href="/policies/shipping-policy">Shipping</a></li>
          <li><a href="/policies/refund-policy">Returns</a></li>
          <li><a href="/policies/privacy-policy">Privacy</a></li>
          <li><a href="/policies/terms-of-service">Terms</a></li>
          <li><a href="/pages/contact">Contact</a></li>"""

new_content, count = pattern.subn(replacement, content)

if count == 0:
    print("ERR: pattern not found in footer.liquid")
    sys.exit(1)

print(f"Pattern replaced {count}x  ({original_len} -> {len(new_content)} chars)")

# Save patched file
Path("I:/BAK ABO/scripts/_footer_patched.liquid").write_text(new_content, encoding="utf-8")
print("Saved patched file: _footer_patched.liquid")

# Show the patched area
idx = new_content.find("Help &amp; FAQ")
print("\n--- patched section ---")
print(new_content[max(0,idx-120):idx+350])
print("---")

# Deploy to live theme
confirm = input("\nDeploy to live theme? [y/N]: ").strip().lower()
if confirm != "y":
    print("Aborted — patched file saved but not deployed.")
    sys.exit(0)

r = requests.put(
    f"{BASE}/themes/202392961362/assets.json",
    headers=HDR,
    json={"asset": {"key": "sections/footer.liquid", "value": new_content}},
    verify=False, timeout=30
)
if r.ok:
    asset = r.json().get("asset", {})
    print(f"OK — sections/footer.liquid deployed  updated_at={asset.get('updated_at')}")
else:
    print(f"ERR: {r.status_code} {r.text[:200]}")
