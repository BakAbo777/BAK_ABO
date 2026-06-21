"""
Find and fix legacy Printify descriptions in sneaker products.
Patterns to remove/replace:
- 'Sneaker Artist 2000: Casey Canvases - Modello basso'
- 'Feliz Art.' prefix text
- Any text mentioning generic Printify model names
"""
import os, sys, re, requests, urllib3, time
from pathlib import Path

urllib3.disable_warnings()  # type: ignore
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
DRY_RUN = "--apply" not in sys.argv

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, _, v = line.partition("="); k=k.strip(); v=v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN","")
BASE   = f"https://{DOMAIN}/admin/api/2025-01"
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
print(f"Shop: {DOMAIN} | DRY_RUN={DRY_RUN}\n")

LEGACY_DESC_PATTERNS = [
    # Printify Sneaker model names
    r'Sneaker Artist 2000[:\s][^\n<]*',
    r'Casey Canvases[^\n<]*',
    r'Modello basso',
    r'Feliz Art\.[^\n<]*',
    # Generic Printify product descriptions that sneak through
    r'Unisex low-top sneakers with a classic silhouette',
    r'High-quality sneakers with canvas upper',
]
COMBINED = re.compile('|'.join(LEGACY_DESC_PATTERNS), re.I)

# Fetch all sneaker products
products, page_info = [], None
while True:
    params = "limit=250&fields=id,title,product_type,body_html&status=active"
    if page_info: params += f"&page_info={page_info}"
    r = requests.get(f"{BASE}/products.json?{params}", headers=HDR, verify=False, timeout=30)
    for p in r.json().get("products", []):
        if p.get("product_type","").lower() in ("sneakers", "shoes", "sneaker") or "sneaker" in p["title"].lower():
            products.append(p)
    link = r.headers.get("Link","")
    if 'rel="next"' not in link: break
    m = re.search(r'page_info=([^&>]+)[^>]*>;\s*rel="next"', link)
    page_info = m.group(1) if m else None

print(f"Sneaker products found: {len(products)}")

changes = []
for p in products:
    body = p.get("body_html") or ""
    if COMBINED.search(body):
        # Strip legacy text
        clean = COMBINED.sub("", body)
        # Clean up extra whitespace/empty tags
        clean = re.sub(r'<p>\s*</p>', '', clean)
        clean = re.sub(r'\s{2,}', ' ', clean).strip()
        changes.append((p["id"], p["title"][:50], clean))
        print(f"\n  [{p['id']}] {p['title'][:50]}")
        print(f"  OLD: {body[:120]}...")
        print(f"  NEW: {clean[:120]}...")

print(f"\nTotal with legacy desc: {len(changes)}")

if not DRY_RUN and changes:
    ok = err = 0
    for pid, title, new_body in changes:
        r = requests.put(f"{BASE}/products/{pid}.json", headers=HDR,
            json={"product": {"id": pid, "body_html": new_body}},
            verify=False, timeout=20)
        if r.ok: ok += 1
        else:
            err += 1
            print(f"  ERR [{pid}]: {r.status_code} {r.text[:60]}")
        time.sleep(0.3)
    print(f"\nDone: {ok}/{len(changes)} OK, {err} errors")
elif DRY_RUN and changes:
    print(f"\n[DRY RUN] Run with --apply.")
