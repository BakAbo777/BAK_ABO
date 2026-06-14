"""Check Shopify markets and shipping zones for India/Korea policy alignment."""
from __future__ import annotations
import os, requests, urllib3, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env_path = ROOT / ".env"
if env_path.exists():
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, v = line.split("=", 1)
        k = k.strip(); v = v.strip().strip('"').strip("'")
        if k not in os.environ or not os.environ[k]: os.environ[k] = v

DOMAIN  = os.environ.get("SHOPIFY_MYSHOPIFY_DOMAIN", "")
TOKEN   = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
URL     = f"https://{DOMAIN}/admin/api/{VERSION}/graphql.json"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}


def gql(query: str) -> dict:
    try:
        r = requests.post(URL, json={"query": query}, headers=HDR, timeout=30)
    except requests.exceptions.SSLError:
        urllib3.disable_warnings()
        r = requests.post(URL, json={"query": query}, headers=HDR, timeout=30, verify=False)
    r.raise_for_status()
    return r.json()


def main() -> None:
    # 1. Markets
    print("=== MARKETS ===")
    q_markets = """{ markets(first:20){ nodes{ id name enabled handle
        countries{ nodes{ name code{ countryCode } } }
        webPresence{ rootUrls{ locale url } }
    } } }"""
    data = gql(q_markets)
    markets = data.get("data", {}).get("markets", {}).get("nodes", [])
    for m in markets:
        countries = [c["code"]["countryCode"] for c in m["countries"]["nodes"]]
        print(f"  {m['name']} | enabled={m['enabled']} | {countries}")

    # 2. Shipping zones (REST)
    print("\n=== SHIPPING ZONES ===")
    rest_url = f"https://{DOMAIN}/admin/api/{VERSION}/shipping_zones.json"
    try:
        r = requests.get(rest_url, headers={"X-Shopify-Access-Token": TOKEN}, timeout=30)
    except requests.exceptions.SSLError:
        urllib3.disable_warnings()
        r = requests.get(rest_url, headers={"X-Shopify-Access-Token": TOKEN}, timeout=30, verify=False)
    zones = r.json().get("shipping_zones", [])
    target = {"IN", "KR", "IT", "US", "GB"}
    for z in zones:
        codes = {c["code"] for c in z.get("countries", [])}
        flagged = codes & target
        if flagged:
            rates = [rate["name"] for rate in z.get("price_based_shipping_rates", []) + z.get("weight_based_shipping_rates", [])]
            print(f"  Zone: {z['name']} | countries_match={flagged} | rates={rates}")

    # 3. Check if CSV has India/Korea prices
    print("\n=== CSV PRICE COLUMNS ===")
    import csv
    csv_path = ROOT / "output" / "products_export_updated.csv"
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
    india = [h for h in headers if "India" in h or "Corea" in h or "Korea" in h or "KR" in h or "IN" in h]
    print(f"  India/Korea price columns: {india}")


if __name__ == "__main__":
    main()
