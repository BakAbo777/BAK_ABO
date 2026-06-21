"""Print full Shopify shipping zones with all countries and rates."""
from __future__ import annotations
import os, requests, urllib3, json
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

zones = get("shipping_zones.json").get("shipping_zones", [])
for z in zones:
    countries = sorted([c["code"] for c in z.get("countries", [])])
    rates_p = [f"{r['name']} ({r.get('min_order_subtotal') or '0'}–{r.get('max_order_subtotal') or '∞'} → {r['price']})"
               for r in z.get("price_based_shipping_rates", [])]
    rates_w = [r["name"] for r in z.get("weight_based_shipping_rates", [])]
    print(f"\nZONE id={z['id']} name={z['name']!r}")
    print(f"  Countries ({len(countries)}): {countries}")
    if rates_p: print(f"  Price-based rates: {rates_p[:5]}")
    if rates_w: print(f"  Weight-based rates: {rates_w[:5]}")
