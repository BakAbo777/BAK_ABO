"""Check Shopify markets, shipping zones, and return policies for India/Korea."""
from __future__ import annotations
import os, requests, urllib3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
HDR     = {"X-Shopify-Access-Token": TOKEN}

def get(path: str) -> dict:
    url = f"https://{DOMAIN}/admin/api/{VERSION}/{path}"
    try:
        r = requests.get(url, headers=HDR, timeout=30)
    except requests.exceptions.SSLError:
        urllib3.disable_warnings()  # type: ignore
        r = requests.get(url, headers=HDR, timeout=30, verify=False)
    r.raise_for_status()
    return r.json()

TARGET = {"IN", "KR", "IT", "US", "GB"}

print("=== SHIPPING ZONES ===")
zones = get("shipping_zones.json").get("shipping_zones", [])
country_to_zone: dict[str, str] = {}
for z in zones:
    for c in z.get("countries", []):
        code = c.get("code", "")
        if code in TARGET:
            country_to_zone[code] = z["name"]
for code in sorted(TARGET):
    print(f"  {code}: {'IN zone: ' + country_to_zone[code] if code in country_to_zone else 'NO SHIPPING ZONE'}")

print("\n=== POLICIES ===")
policies = get("policies.json")
for key in ("refund_policy", "privacy_policy", "shipping_policy", "terms_of_service"):
    p = policies.get(key) or {}
    print(f"  {key}: {'OK' if p.get('body') else 'MISSING'}")

print("\n=== RETURN SUMMARY ===")
print("  India  (IN):", "Shipping zone: " + country_to_zone.get("IN", "MISSING"))
print("  Korea  (KR):", "Shipping zone: " + country_to_zone.get("KR", "MISSING"))
print("  Italy  (IT):", "Shipping zone: " + country_to_zone.get("IT", "MISSING"))
print("  US     (US):", "Shipping zone: " + country_to_zone.get("US", "MISSING"))
