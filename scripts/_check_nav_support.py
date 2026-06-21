"""Check support navigation menu items."""
import os, requests, urllib3, json
urllib3.disable_warnings()  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN}

r = requests.post(
    f"https://{DOMAIN}/admin/api/2025-01/graphql.json",
    headers={**HDR, "Content-Type": "application/json"},
    json={"query": """
    {
      menus(first: 20) {
        nodes {
          id handle title
          items {
            title url
          }
        }
      }
    }
    """},
    verify=False, timeout=20
)
data = r.json()
for m in data.get("data", {}).get("menus", {}).get("nodes", []):
    print(f"\nMenu: {m['handle']!r} title={m['title']!r}")
    for item in m.get("items", []):
        print(f"  - {item['title']!r} -> {item['url']}")
