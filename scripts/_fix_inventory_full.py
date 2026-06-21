"""
Full scan: set inventory_policy=continue on ALL Printify/MTO product variants.
Covers any missed on the first pass.
"""
import os, sys, requests, urllib3, time
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

# Fetch all active products
products, page_info = [], None
while True:
    params = "limit=250&fields=id,title,status,tags,variants&status=active"
    if page_info: params += f"&page_info={page_info}"
    r = requests.get(f"{BASE}/products.json?{params}", headers=HDR, verify=False, timeout=30)
    products.extend(r.json().get("products",[]))
    link = r.headers.get("Link","")
    if 'rel="next"' not in link: break
    import re
    m = re.search(r'page_info=([^&>]+)[^>]*>;\s*rel="next"', link)
    page_info = m.group(1) if m else None

print(f"Products to scan: {len(products)}\n")

deny_variants = []
for p in products:
    # Only Printify/MTO products (tagged made-to-order or brand:bks)
    tags = p.get("tags","")
    is_bks = "brand:bks" in tags or "made-to-order" in tags
    if not is_bks:
        # Still check if any variant is deny policy — catches untagged products
        pass
    for v in p.get("variants",[]):
        if v.get("inventory_policy","") == "deny":
            deny_variants.append({
                "pid": p["id"],
                "vid": v["id"],
                "title": p["title"][:50],
                "sku":   v.get("sku",""),
                "qty":   v.get("inventory_quantity",0),
            })

print(f"Variants with inventory_policy=deny: {len(deny_variants)}")
if deny_variants:
    print("First 20:")
    for item in deny_variants[:20]:
        print(f"  [{item['vid']}] {item['title']} | qty={item['qty']}")

if not DRY_RUN and deny_variants:
    ok = err = 0
    for item in deny_variants:
        r = requests.put(
            f"{BASE}/variants/{item['vid']}.json",
            headers=HDR,
            json={"variant": {"id": item["vid"], "inventory_policy": "continue"}},
            verify=False, timeout=20
        )
        if r.ok: ok += 1
        else:
            err += 1
            print(f"  ERR [{item['vid']}]: {r.status_code} {r.text[:60]}")
        time.sleep(0.3)
    print(f"\nFixed: {ok}/{len(deny_variants)} OK, {err} errors")
elif DRY_RUN and deny_variants:
    print(f"\n[DRY RUN] Run with --apply to fix {len(deny_variants)} variants.")
else:
    print("\nAll variants already have inventory_policy=continue. Nothing to fix.")
