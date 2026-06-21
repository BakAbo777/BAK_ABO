"""
Audit variant option names/values for Italian text, and check CTA language.
Specifically: look for "Uomo", "Donna", "Taglia", "Colore" in option names/values.
"""
import os, re, time, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ:
        os.environ[k] = v

DOMAIN = os.environ.get("SHOPIFY_MYSHOPIFY_DOMAIN", "")
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "") or os.environ.get("SHOPIFY_API_TOKEN", "")
BASE   = f"https://{DOMAIN}/admin/api/2024-04"
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

def get(path):
    return requests.get(f"{BASE}{path}", headers=HDR, verify=False, timeout=20)

ITALIAN_OPTION_NAMES  = ["taglia", "colore", "dimensione", "misura", "genere", "uomo", "donna"]
ITALIAN_OPTION_VALUES = ["uomo", "donna", "taglia", "piccolo", "medio", "grande", "molto grande"]

page_info = None
issues = []

while True:
    if page_info:
        url = f"/products.json?limit=50&fields=id,title,options&page_info={page_info}"
    else:
        url = "/products.json?limit=50&fields=id,title,options"

    r = get(url)
    prods = r.json().get("products", [])
    if not prods:
        break

    for p in prods:
        pid   = p["id"]
        title = p.get("title", "")
        for opt in p.get("options", []):
            name = opt.get("name", "")
            vals = opt.get("values", [])
            has_it_name = name.lower() in ITALIAN_OPTION_NAMES
            it_vals = [v for v in vals if v.lower() in ITALIAN_OPTION_VALUES]
            if has_it_name or it_vals:
                issues.append({
                    "id": pid,
                    "title": title[:60],
                    "option": name,
                    "values": vals[:6],
                    "it_name": has_it_name,
                    "it_vals": it_vals,
                })

    link = r.headers.get("Link", "")
    nxt  = re.search(r'<[^>]+page_info=([^&>]+)[^>]*>;\s*rel="next"', link)
    page_info = nxt.group(1) if nxt else None
    if not page_info:
        break
    time.sleep(0.3)

print(f"Italian option names/values found: {len(issues)}")
for issue in issues[:20]:
    flags = []
    if issue["it_name"]: flags.append(f"name='{issue['option']}'")
    if issue["it_vals"]: flags.append(f"values={issue['it_vals']}")
    print(f"  [{issue['id']}] {issue['title']}")
    print(f"    Option: '{issue['option']}' | values: {issue['values'][:5]}")

# Unique option names across all products
r2 = get("/products.json?limit=50&fields=id,options")
all_option_names = set()
prods2 = r2.json().get("products", [])
for p in prods2:
    for opt in p.get("options", []):
        all_option_names.add(opt.get("name","").lower())
print(f"\nAll unique option names (sample): {sorted(all_option_names)}")
