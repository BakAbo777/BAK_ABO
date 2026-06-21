"""
Fix product descriptions:
  1. Remove Italian shipping/production paragraph from 23 products
  2. Rewrite BKS Pullover — Token description (old Printify promo + hashtags)

Run with --apply (default is dry-run).
"""
import os, sys, re, time, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()  # type: ignore
DRY_RUN = "--apply" not in sys.argv
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "") or os.environ.get("SHOPIFY_API_TOKEN", "")
BASE   = f"https://{DOMAIN}/admin/api/2025-01"
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
print(f"Shop: {DOMAIN} | DRY_RUN={DRY_RUN}")

# Regex: remove <p> blocks containing Italian shipping text
# Matches: <p ...><em>...spedizione...</em></p> or <p ...>...spedizione...</p>
IT_P = re.compile(
    r'<p[^>]*>\s*(?:<em>|<strong>)?[^<]*'
    r'(?:spedizione|realizzato su ordinazione|tempi di produzione|'
    r'stampata e assemblata|assemblata per te|giorni lavorativi prima)'
    r'[^<]*(?:</em>|</strong>)?\s*</p>',
    re.I
)

def remove_italian_p(html: str) -> str:
    cleaned = IT_P.sub("", html)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
    return cleaned

# Products with Italian shipping paragraphs
SPEDIZIONE_IDS = [
    10831881142610, 10831625683282, 8674268053842, 8654050820434,
    10768325345618, 10831857484114, 10831643935058, 8652662473042,
    8652755108178, 8648160346450, 8648160772434,
    8603356102994, 8602889290066, 8621387219282, 8914782912850,
    8914709512530, 8602916356434, 8600109089106, 10828998246738,
    10829039108434, 10804874740050, 10822743458130, 8602433421650,
]

# BKS Pullover Token — full description rewrite
TOKEN_PULLOVER_ID = 10866565316946
TOKEN_PULLOVER_TABLE_MARKER = '<table id="size-guide"'
TOKEN_PULLOVER_NEW_INTRO = """\
<p>Pullover hoodie with full-surface BKS Token graphic. Heavyweight fleece, relaxed volume, ribbed cuffs and hem. Designed for layering — urban transitions, studio work, off-season travel.</p>
<p><em>Made to order. Produced and assembled for you after purchase. Allow 7–10 business days for production before shipping. Free shipping on orders over €99.</em></p>
"""

errors = []
ok = 0

print("\n=== SPEDIZIONE CLEANUP ===")
for pid in SPEDIZIONE_IDS:
    r = requests.get(f"{BASE}/products/{pid}.json?fields=id,title,body_html",
                     headers=HDR, verify=False, timeout=20)
    if not r.ok:
        print(f"  SKIP [{pid}]: {r.status_code}")
        continue
    p = r.json()["product"]
    html = p.get("body_html") or ""
    new_html = remove_italian_p(html)
    if new_html == html:
        print(f"  UNCHANGED [{pid}] {p['title'][:45]}")
        continue
    removed = len(html) - len(new_html)
    print(f"  CLEAN [{pid}] {p['title'][:45]} (-{removed} chars)")
    if not DRY_RUN:
        r2 = requests.put(f"{BASE}/products/{pid}.json",
            headers=HDR, json={"product": {"id": pid, "body_html": new_html}},
            verify=False, timeout=20)
        if r2.ok: ok += 1
        else: errors.append(f"{pid}: {r2.text[:80]}")
    time.sleep(0.35)

print("\n=== TOKEN PULLOVER REWRITE ===")
r = requests.get(f"{BASE}/products/{TOKEN_PULLOVER_ID}.json?fields=id,title,body_html",
                 headers=HDR, verify=False, timeout=20)
p = r.json()["product"]
old_html = p.get("body_html") or ""
# Keep from size table onward, prepend new intro, append trust badges
table_idx = old_html.find(TOKEN_PULLOVER_TABLE_MARKER)
trust_badges = (
    "\n<ul>\n"
    "<li>✈️ Free Shipping on orders over €99</li>\n"
    "<li>↩ 30-Day Returns, hassle-free</li>\n"
    "<li>✦ Printed on demand, never overstocked</li>\n"
    "<li>✓ 2-Year EU Warranty</li>\n"
    "</ul>\n"
)
if table_idx > -1:
    new_html = TOKEN_PULLOVER_NEW_INTRO + old_html[table_idx:] + trust_badges
else:
    new_html = TOKEN_PULLOVER_NEW_INTRO + trust_badges
print(f"  [{TOKEN_PULLOVER_ID}] {p['title']} | old={len(old_html)} new={len(new_html)} chars")
if not DRY_RUN:
    r2 = requests.put(f"{BASE}/products/{TOKEN_PULLOVER_ID}.json",
        headers=HDR, json={"product": {"id": TOKEN_PULLOVER_ID, "body_html": new_html}},
        verify=False, timeout=20)
    if r2.ok: ok += 1
    else: errors.append(f"token_pullover: {r2.text[:80]}")
else:
    print(f"  Preview intro: {TOKEN_PULLOVER_NEW_INTRO[:100]}...")

if not DRY_RUN:
    total = len(SPEDIZIONE_IDS) + 1
    print(f"\nDone: {ok}/{total} OK, {len(errors)} errors")
    for e in errors: print(f"  {e}")
else:
    print(f"\n[DRY RUN] Run with --apply to write {len(SPEDIZIONE_IDS)+1} products.")
