"""
Audit completo area members BKS:
1. Pagina /pages/bks-members esiste e usa template corretto
2. Flow attivi Shopify
3. App installate
4. Tier detection via customer.orders_count
5. Email flows attivi (Messaging app)
6. Wishlist / Try-On endpoint
7. Gold Ring CSS vars nel tema live
"""
import os, requests, urllib3, json
from pathlib import Path
urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, _, v = line.partition("=")
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

SH_DOM = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
SH_TOK = os.environ["SHOPIFY_ADMIN_TOKEN"]
SH_HDR = {"X-Shopify-Access-Token": SH_TOK, "Content-Type": "application/json"}
BASE   = f"https://{SH_DOM}/admin/api/2025-01"

def get(path, **params):
    return requests.get(f"{BASE}{path}", headers=SH_HDR, params=params, verify=False).json()

print("=" * 60)
print("AUDIT AREA MEMBERS BKS")
print("=" * 60)

# ── 1. Pagina bks-members
print("\n[1] PAGINA /pages/bks-members")
pages = get("/pages.json", limit=250, fields="id,handle,title,template_suffix")
bks_pages = {p["handle"]: p for p in pages.get("pages", [])}
for handle in ["bks-members", "bks-ai-assistant", "verse", "verse-hall", "faq",
               "bks-hawaiian-shirt", "bks-one-piece-swimsuits", "bks-beach-towel",
               "bks-puffer-jacket", "bks-racerback-dresses", "bks-travel-bag"]:
    p = bks_pages.get(handle)
    if p:
        print(f"  OK  /{handle} (template_suffix: '{p['template_suffix'] or 'default'}')")
    else:
        print(f"  MISSING  /{handle}")

# ── 2. Template members nel tema live
print("\n[2] TEMPLATE MEMBERS NEL TEMA LIVE")
THEME_ID = "202392961362"
tmpl_r = requests.get(f"{BASE}/themes/{THEME_ID}/assets.json",
    headers=SH_HDR, params={"asset[key]": "templates/page.bks-members.json"}, verify=False)
if tmpl_r.status_code == 200:
    asset = tmpl_r.json().get("asset", {})
    val = json.loads(asset.get("value","{}"))
    secs = list(val.get("sections", {}).keys())
    print(f"  OK  templates/page.bks-members.json — sections: {secs}")
else:
    print(f"  MISSING  templates/page.bks-members.json ({tmpl_r.status_code})")

# ── 3. Asset CSS/JS members nel tema
print("\n[3] ASSET CSS/JS MEMBERS NEL TEMA")
for asset_key in ["assets/bks-member.css", "assets/bks-member.js"]:
    ar = requests.get(f"{BASE}/themes/{THEME_ID}/assets.json",
        headers=SH_HDR, params={"asset[key]": asset_key}, verify=False)
    if ar.status_code == 200:
        asset = ar.json().get("asset", {})
        size = asset.get("size", 0)
        updated = asset.get("updated_at", "?")
        print(f"  OK  {asset_key} ({size:,} bytes — {updated[:10]})")
    else:
        print(f"  MISSING  {asset_key}")

# ── 4. App installate
print("\n[4] APP SHOPIFY INSTALLATE")
apps_r = requests.get(f"{BASE}/script_tags.json", headers=SH_HDR, verify=False).json()
scripts = apps_r.get("script_tags", [])
print(f"  Script tags attivi: {len(scripts)}")
for s in scripts[:5]:
    print(f"    {s.get('src','?')[:80]}")

# Prova a leggere app via GraphQL
gql_headers = {**SH_HDR, "Content-Type": "application/json"}
gql_r = requests.post(
    f"https://{SH_DOM}/admin/api/2025-01/graphql.json",
    headers=gql_headers,
    json={"query": "{ app { title } currentAppInstallation { activeSubscriptions { name status } } }"},
    verify=False
)

# ── 5. Flow / Automation
print("\n[5] SHOPIFY FLOW — WEBHOOK AUTOMATION")
wh_r = get("/webhooks.json", limit=50)
webhooks = wh_r.get("webhooks", [])
print(f"  Webhook attivi: {len(webhooks)}")
for w in webhooks:
    print(f"    [{w['topic']}] -> {w['address'][:70]}")

# ── 6. Email flows (check Messaging via metafields o custom flow)
print("\n[6] FLOW SHOPIFY (check topics rilevanti)")
flow_topics = [w["topic"] for w in webhooks]
member_topics = ["orders/create", "orders/fulfilled", "customers/create",
                 "customers/update", "app/uninstalled"]
for t in member_topics:
    status = "OK" if t in flow_topics else "non registrato"
    print(f"  {t}: {status}")

# ── 7. Gold Ring / Tier CSS vars nel tema
print("\n[7] GOLD RING / TIER CSS VARS")
css_r = requests.get(f"{BASE}/themes/{THEME_ID}/assets.json",
    headers=SH_HDR, params={"asset[key]": "assets/bks-member.css"}, verify=False)
if css_r.status_code == 200:
    css = css_r.json().get("asset", {}).get("value", "")
    # Check per tier colors e gold ring
    checks = {
        "--bks-tier-gold": "--bks-tier-gold" in css,
        "--bks-tier-silver": "--bks-tier-silver" in css,
        "gold-ring / @keyframes": "@keyframes" in css and "ring" in css.lower(),
        "bks-wl-toast (wishlist)": "bks-wl-toast" in css,
        "bks-wl-badge": "bks-wl-badge" in css,
    }
    for key, ok in checks.items():
        print(f"  {'OK' if ok else 'MISSING'}  {key}")

# ── 8. Sezione header (gold ring)
print("\n[8] GOLD RING HEADER (bakabo-header.liquid)")
hdr_r = requests.get(f"{BASE}/themes/{THEME_ID}/assets.json",
    headers=SH_HDR, params={"asset[key]": "snippets/bakabo-header.liquid"}, verify=False)
if hdr_r.status_code == 200:
    hdr = hdr_r.json().get("asset", {}).get("value", "")
    checks2 = {
        "gold-ring CSS class": "gold-ring" in hdr or "bks-gold-ring" in hdr,
        "tier detection Liquid": "orders_count" in hdr or "member_tier" in hdr,
        "account dropdown": "account" in hdr.lower() and "dropdown" in hdr.lower(),
        "MutationObserver (locale killer)": "MutationObserver" in hdr,
    }
    for key, ok in checks2.items():
        print(f"  {'OK' if ok else 'MISSING'}  {key}")
else:
    print(f"  MISSING  snippets/bakabo-header.liquid")

print("\n" + "=" * 60)
print("AUDIT COMPLETATO")
