"""Create BKS-BIRTHDAY discount: 10% off, min €80, 1 use per customer, all markets."""
import os, requests, urllib3, json
from pathlib import Path
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1); k=k.strip(); v=v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
HDR = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
BASE = f"https://{DOMAIN}/admin/api/2025-01"

# Check via GraphQL first
GQL = f"https://{DOMAIN}/admin/api/2025-01/graphql.json"
query = """
{
  codeDiscountNodes(first: 20) {
    nodes {
      id
      codeDiscount {
        ... on DiscountCodeBasic {
          title
          codes(first: 5) { nodes { code } }
          status
        }
      }
    }
  }
}
"""
rg = requests.post(GQL, json={"query": query}, headers=HDR, verify=False, timeout=15)
data = rg.json() or {}
nodes = (data.get("data") or {}).get("codeDiscountNodes", {}).get("nodes", [])
print(f"GraphQL discounts found: {len(nodes)}")
for n in nodes:
    cd = n.get("codeDiscount", {})
    codes = [c["code"] for c in cd.get("codes", {}).get("nodes", [])]
    print(f"  '{cd.get('title')}' status={cd.get('status')} codes={codes}")

# Create via REST price_rules if not exists
birthday_exists = any(
    "BKS-BIRTHDAY" in [c["code"] for c in n.get("codeDiscount", {}).get("codes", {}).get("nodes", [])]
    for n in nodes
)

if birthday_exists:
    print("\n-> BKS-BIRTHDAY già esiste ✓")
else:
    print("\n-> Creo BKS-BIRTHDAY via REST...")
    import datetime
    pr_body = {
        "price_rule": {
            "title": "BKS-BIRTHDAY",
            "value_type": "percentage",
            "value": "-10.0",
            "customer_selection": "all",
            "target_type": "line_item",
            "target_selection": "all",
            "allocation_method": "across",
            "once_per_customer": True,
            "usage_limit": None,
            "starts_at": "2026-01-01T00:00:00Z",
            "prerequisite_subtotal_range": {"greater_than_or_equal_to": "80.00"}
        }
    }
    r1 = requests.post(f"{BASE}/price_rules.json", json=pr_body, headers=HDR, verify=False, timeout=15)
    print(f"  PriceRule: {r1.status_code}")
    if r1.status_code in (200, 201):
        rule_id = r1.json()["price_rule"]["id"]
        r2 = requests.post(
            f"{BASE}/price_rules/{rule_id}/discount_codes.json",
            json={"discount_code": {"code": "BKS-BIRTHDAY"}},
            headers=HDR, verify=False, timeout=10
        )
        print(f"  DiscountCode: {r2.status_code} -> {r2.json().get('discount_code',{}).get('code','?')}")
    else:
        print(f"  ERR: {r1.text[:200]}")
