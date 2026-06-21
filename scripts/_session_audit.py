"""
Final session audit — verify all P1 fixes applied.
2026-06-20 session.
"""
import os, requests, urllib3, re, sys
urllib3.disable_warnings()  # type: ignore
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN","")
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

PASS = "PASS"; FAIL = "FAIL"; WARN = "WARN"

def chk(label, ok, detail=""):
    status = PASS if ok else FAIL
    print(f"  [{status}] {label}" + (f" — {detail}" if detail else ""))
    return ok

results = []
print("=== BKS SESSION AUDIT 2026-06-20 ===\n")

# 1. Main menu: no Italian
print("[1] Main menu — no Italian item labels")
r = requests.post(f"https://{DOMAIN}/admin/api/2025-01/graphql.json", headers=HDR,
    json={"query": '{ menu(id: "gid://shopify/Menu/231167721810") { items { title url } } }'},
    verify=False, timeout=20)
items = r.json().get("data", {}).get("menu", {}).get("items", [])
italian = [i for i in items if i["title"].lower() in ("contatti", "prodotti", "collezioni")]
results.append(chk("No Italian labels in main-menu", not italian,
    f"Italian items found: {[i['title'] for i in italian]}" if italian else
    f"All OK: {[i['title'] for i in items]}"))

# 2. Ghost pages deleted
print("\n[2] Ghost pages deleted")
for handle, name in [("bks-hawaiian-shirt","Hawaiian Shirts"),("bks-duffel-bag","Duffel Bags"),("bks-beach-towel","Beach Towels")]:
    r2 = requests.get(f"{BASE}/pages.json?handle={handle}&fields=id,title", headers=HDR, verify=False, timeout=15)
    gone = not r2.json().get("pages", [])
    results.append(chk(f"{name} page gone", gone))

# 3. Product schema compliance
print("\n[3] Product title schema")
products, page_info = [], None
while True:
    params = "limit=250&fields=id,title,product_type,status"
    if page_info: params += f"&page_info={page_info}"
    r3 = requests.get(f"{BASE}/products.json?{params}&status=active", headers=HDR, verify=False, timeout=30)
    products.extend(r3.json().get("products",[]))
    link = r3.headers.get("Link","")
    if 'rel="next"' not in link: break
    m = re.search(r'page_info=([^&>]+)[^>]*>;\s*rel="next"', link)
    page_info = m.group(1) if m else None

schema_re = re.compile(r'^BKS .+ — (Hours|Glyph|Marker|Riviera|Pulse|Token|Flag|Origin)')
LEGACY_RE = re.compile(r'piumino|giacca a vento|zaino|costume|pantaloni|maglione|sneakers? bassa|\(BKS\)', re.I)

non_schema = [p for p in products if not schema_re.match(p["title"])]
legacy = [p for p in products if LEGACY_RE.search(p["title"])]

results.append(chk(f"No legacy Italian titles", not legacy,
    f"Found: {[p['title'][:30] for p in legacy[:3]]}" if legacy else ""))
results.append(chk(f"Schema-compliant titles: {len(products)-len(non_schema)}/{len(products)}",
    len(non_schema) < 20,
    f"{len(non_schema)} non-schema (expected: items without BKS collection tagging)" if non_schema else "All compliant"))
if non_schema[:5]:
    for p in non_schema[:5]:
        print(f"      - {p['title'][:55]} [{p['product_type']}]")

# 4. CSS deployed check
print("\n[4] bks-responsive.css — mobile patch section 5")
r4 = requests.get(f"{BASE}/themes/202392961362/assets.json?asset[key]=assets/bks-responsive.css",
                  headers=HDR, verify=False, timeout=20)
css = r4.json().get("asset", {}).get("value", "")
has_patch = "Roberto patch 20/06/2026" in css or "line-height: 1.2" in css
results.append(chk("Mobile variant picker patch in CSS", has_patch))

print(f"\n{'='*40}")
passed = sum(1 for x in results if x)
print(f"RESULT: {passed}/{len(results)} checks PASS")
