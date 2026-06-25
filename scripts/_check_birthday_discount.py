"""Check and fix BKS-BIRTHDAY discount code."""
import os, requests, urllib3
from pathlib import Path
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

r = requests.get(f"{BASE}/price_rules.json?limit=50", headers=HDR, verify=False, timeout=15)
rules = r.json().get("price_rules", [])
birthday = [x for x in rules if "birthday" in x.get("title","").lower() or "BKS-BIRTHDAY" in x.get("title","")]

if not birthday:
    print("No birthday discount found.")
else:
    for rule in birthday:
        print(f"\nPrice Rule: ID={rule['id']} title='{rule['title']}'")
        print(f"  value={rule.get('value')} type={rule.get('value_type')} status={rule.get('allocation_method')}")
        print(f"  starts={rule.get('starts_at')[:10] if rule.get('starts_at') else 'n/a'}")
        rc = requests.get(f"{BASE}/price_rules/{rule['id']}/discount_codes.json",
                          headers=HDR, verify=False, timeout=10)
        codes = rc.json().get("discount_codes", [])
        if codes:
            for c in codes:
                print(f"  Code: [{c.get('code')}] id={c.get('id')} usage={c.get('usage_count')}")
            # If code is not BKS-BIRTHDAY, update it
            code = codes[0]
            if code.get("code") != "BKS-BIRTHDAY":
                print(f"\n  → Updating code {code['code']} → BKS-BIRTHDAY ...")
                ru = requests.put(
                    f"{BASE}/price_rules/{rule['id']}/discount_codes/{code['id']}.json",
                    json={"discount_code": {"id": code["id"], "code": "BKS-BIRTHDAY"}},
                    headers=HDR, verify=False, timeout=10
                )
                print(f"  Update: {ru.status_code} → {ru.json().get('discount_code',{}).get('code','?')}")
            else:
                print("  → Code already BKS-BIRTHDAY ✓")
        else:
            print("  No discount codes on this rule.")
