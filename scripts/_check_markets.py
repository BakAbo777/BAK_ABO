"""Check Shopify Markets and product publication status."""
import os, requests, urllib3
urllib3.disable_warnings()  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

# Check markets via GraphQL
r = requests.post(
    f"https://{DOMAIN}/admin/api/2025-01/graphql.json",
    headers=HDR,
    json={"query": """
    {
      markets(first: 20) {
        nodes {
          id
          name
          enabled
          primary
          regions { nodes { name } }
          webPresence { rootUrls { locale url } }
        }
      }
      shop {
        primaryDomain { url }
        currencyCode
      }
    }
    """},
    verify=False, timeout=20
)
data = r.json()
if "errors" in data:
    print(f"GraphQL errors: {data['errors']}")
else:
    shop = data["data"]["shop"]
    print(f"Shop: {shop['primaryDomain']['url']} | Currency: {shop['currencyCode']}\n")
    for m in data["data"]["markets"]["nodes"]:
        regions = [x["name"] for x in m.get("regions", {}).get("nodes", [])]
        urls = [f"{x['locale']}:{x['url']}" for x in (m.get("webPresence") or {}).get("rootUrls", [])]
        print(f"Market: {m['name']} (id={m['id']}) enabled={m['enabled']} primary={m['primary']}")
        print(f"  Regions: {', '.join(regions) or '(none)'}")
        print(f"  URLs: {', '.join(urls) or '(none)'}")
