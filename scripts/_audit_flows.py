"""Verifica Flow Shopify attivi + Gold Ring header + FAQ page handle."""
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
THEME  = "202392961362"

def gql(query):
    r = requests.post(f"https://{SH_DOM}/admin/api/2025-01/graphql.json",
        headers=SH_HDR, json={"query": query}, verify=False)
    return r.json()

# ── 1. Flow workflows via GraphQL
print("[1] FLOW WORKFLOWS (GraphQL)")
flow_q = """{ flowTriggerDefinitions(first: 20) { nodes { title description } } }"""
fr = gql(flow_q)
if "errors" not in fr:
    nodes = fr.get("data", {}).get("flowTriggerDefinitions", {}).get("nodes", [])
    for n in nodes[:10]:
        print(f"  {n.get('title','?')}")
else:
    print(f"  GraphQL: {fr.get('errors','?')}")

# ── 2. Pagine FAQ — cerca handle alternativi
print("\n[2] PAGINE FAQ — handle alternativi")
r = requests.get(f"{BASE}/pages.json", headers=SH_HDR,
    params={"limit":250,"fields":"id,handle,title,template_suffix"}, verify=False)
pages = r.json().get("pages", [])
faq_candidates = [p for p in pages if "faq" in p["handle"].lower() or "faq" in p["title"].lower()]
for p in faq_candidates:
    print(f"  /{p['handle']} ('{p['title']}' — template: {p['template_suffix'] or 'default'})")
if not faq_candidates:
    print("  NESSUNA pagina FAQ trovata")

# Cerca anche puffer, hawaiian, beach
for kw in ["puffer", "hawaiian", "beach", "shopping", "guide"]:
    hits = [p for p in pages if kw in p["handle"].lower() or kw in p["title"].lower()]
    if hits:
        for p in hits:
            print(f"  [{kw}] /{p['handle']} ('{p['title'][:40]}')")

# ── 3. Gold Ring nel header — cerca classe nel file
print("\n[3] GOLD RING — analisi bakabo-header.liquid")
hr = requests.get(f"{BASE}/themes/{THEME}/assets.json",
    headers=SH_HDR, params={"asset[key]": "snippets/bakabo-header.liquid"}, verify=False)
if hr.status_code == 200:
    hdr = hr.json().get("asset", {}).get("value", "")
    # Cerca pattern gold ring
    patterns = {
        "bks-gold-ring": "bks-gold-ring",
        "gold-ring": "gold-ring",
        "ring-animation": "ring-animation",
        "tier-ring": "tier-ring",
        "--bks-tier-": "--bks-tier-",
        "account-icon / account__icon": "account__icon",
        "customer.orders_count": "customer.orders_count",
        "member_tier CSS class": "member_tier",
    }
    for label, kw in patterns.items():
        print(f"  {'OK' if kw in hdr else 'MISSING'}  {label}")
    # Mostra il blocco account icon se presente
    if "account__icon" in hdr or "account-icon" in hdr:
        # Trova contesto
        idx = hdr.find("account__icon")
        if idx < 0: idx = hdr.find("account-icon")
        print(f"\n  CONTEXT account icon (±200 chars):")
        print(f"  {hdr[max(0,idx-100):idx+200].strip()[:300]}")

# ── 4. Member CSS — verifica gold ring @keyframes
print("\n[4] GOLD RING @keyframes nel CSS")
cr = requests.get(f"{BASE}/themes/{THEME}/assets.json",
    headers=SH_HDR, params={"asset[key]": "assets/bks-member.css"}, verify=False)
if cr.status_code == 200:
    css = cr.json().get("asset", {}).get("value", "")
    import re
    rings = re.findall(r'@keyframes\s+\w*ring\w*', css, re.I)
    classes = re.findall(r'\.(bks-[\w-]*ring[\w-]*)', css, re.I)
    print(f"  @keyframes ring: {rings}")
    print(f"  .classes ring: {classes[:10]}")
