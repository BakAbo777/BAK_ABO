import os, requests, urllib3
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

r = requests.get(
    f"https://{DOMAIN}/admin/api/{VER}/customers.json",
    headers={"X-Shopify-Access-Token": TOKEN},
    params={
        "limit": 250,
        "fields": "id,first_name,last_name,email,orders_count,total_spent,tags,created_at,accepts_marketing"
    },
    timeout=20, verify=False
)
customers = r.json().get("customers", [])
print(f"Totale clienti: {len(customers)}\n")

for c in customers:
    tags   = c.get("tags") or "-"
    name   = f"{c['first_name']} {c['last_name']}".strip()
    spent  = float(c.get("total_spent") or 0)
    print(f"  [{c['id']}] {name}")
    print(f"    Email:    {c['email']}")
    print(f"    Ordini:   {c['orders_count']}   Speso: EUR {spent:.2f}")
    print(f"    Tag:      {tags}")
    marketing = c.get("email_marketing_consent", {}).get("state", c.get("accepts_marketing", "?"))
    print(f"    Iscritto: {c['created_at'][:10]}   Marketing: {marketing}")
    print()
