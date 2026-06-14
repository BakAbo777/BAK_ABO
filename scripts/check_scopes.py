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

q = "{ shop { name } appInstallation { accessScopes { handle } } }"
r = requests.post(
    f"https://{DOMAIN}/admin/api/{VER}/graphql.json",
    json={"query": q},
    headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"},
    timeout=15, verify=False
)
data = r.json()
scopes = [s["handle"] for s in data.get("data", {}).get("appInstallation", {}).get("accessScopes", [])]
print("Shop:", data.get("data", {}).get("shop", {}).get("name", "?"))
print("\nAll scopes:")
for s in sorted(scopes): print(" ", s)
menu_rel = [s for s in scopes if any(k in s for k in ("menu", "content", "navigation", "online_store"))]
print("\nMenu-relevant scopes:", menu_rel or "NONE")

# Try menus query
q2 = "{ menus(first:5) { edges { node { id title handle } } } }"
r2 = requests.post(
    f"https://{DOMAIN}/admin/api/{VER}/graphql.json",
    json={"query": q2},
    headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"},
    timeout=15, verify=False
)
d2 = r2.json()
print("\nGraphQL menus query response:")
print(json.dumps(d2, indent=2)[:800])
