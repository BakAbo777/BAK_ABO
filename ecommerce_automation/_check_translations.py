"""Audit Shopify store for language issues: IT remnants, missing EN, Markets setup."""
import requests, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

SHOP  = env["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN = env["SHOPIFY_ADMIN_TOKEN"]
SH    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
BASE  = f"https://{SHOP}/admin/api/2025-01"

# 1. Check active locales
r = requests.get(f"{BASE}/shop.json", headers=SH, verify=False, timeout=15)
shop = r.json().get("shop", {})
print(f"Primary locale: {shop.get('primary_locale')}")
print(f"Enabled locales: {shop.get('enabled_presentment_currencies', [])}")
print()

# 2. Check Shopify Markets
r2 = requests.get(f"https://{SHOP}/admin/api/2025-01/markets.json",
    headers=SH, verify=False, timeout=15)
markets = r2.json().get("markets", [])
print(f"Markets ({len(markets)}):")
for m in markets:
    print(f"  {m.get('name'):20s}  enabled={m.get('enabled')}  primary={m.get('primary')}")
print()

# 3. Check published locales (for Translate & Adapt)
r3 = requests.post(f"https://{SHOP}/admin/api/2025-01/graphql.json",
    headers=SH,
    json={"query": """{ shopLocales { locale name primary published } }"""},
    verify=False, timeout=15)
locales_data = r3.json().get("data", {}).get("shopLocales", [])
print(f"Shop locales (T&A):")
for loc in locales_data:
    print(f"  {loc.get('locale'):6s}  {loc.get('name'):15s}  primary={loc.get('primary')}  published={loc.get('published')}")
print()

# 4. Sample products for Italian text
r4 = requests.get(f"{BASE}/products.json",
    params={"limit": 20, "fields": "id,title,body_html,product_type"},
    headers=SH, verify=False, timeout=20)
products = r4.json().get("products", [])

import re
IT_PATTERNS = [
    r'\b(il|lo|la|le|gli|un|una|uno)\b',
    r'\b(con|per|del|della|dei|delle|degli|nel|nella)\b',
    r'\b(questo|questa|questi|queste|quello|quella)\b',
    r'\b(prodotto|collezione|colore|taglia|spedizione)\b',
]
it_regex = re.compile('|'.join(IT_PATTERNS), re.IGNORECASE)

print("Products with possible Italian text in body_html:")
it_found = 0
for p in products:
    body = p.get("body_html", "") or ""
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', ' ', body)
    if it_regex.search(text):
        it_found += 1
        print(f"  [{p['id']}] {p['title'][:50]}")
        # Show first matching snippet
        for match in it_regex.finditer(text):
            start = max(0, match.start()-20)
            print(f"    ...{text[start:match.end()+30].strip()[:80]}...")
            break
if it_found == 0:
    print("  None found in sample")
