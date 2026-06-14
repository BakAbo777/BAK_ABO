import os, requests, urllib3, json
from pathlib import Path

urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
VER    = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

# Raw HTTP status
r = requests.get(
    f"https://{DOMAIN}/admin/api/{VER}/customers.json",
    headers=HDR, params={"limit": 1}, timeout=10, verify=False
)
print(f"Status: {r.status_code}")
print(f"Body:   {r.text[:300]}")

# Check scopes
q = "{ appInstallation { accessScopes { handle } } }"
r2 = requests.post(
    f"https://{DOMAIN}/admin/api/{VER}/graphql.json",
    json={"query": q}, headers=HDR, timeout=10, verify=False
)
scopes = [s["handle"] for s in r2.json().get("data", {}).get("appInstallation", {}).get("accessScopes", [])]
customer_scopes = [s for s in scopes if "customer" in s]
print(f"\nScope customer: {customer_scopes or 'NESSUNO'}")
print(f"Tutti gli scope: {sorted(scopes)}")
