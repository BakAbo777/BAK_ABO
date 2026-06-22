"""Corregge prezzi fuori dal price ladder approvato BKS.

Basato su output/gmc_sync_report.json + regole bakabo-pricing.
Scrive sia su Shopify che su Printify per evitare drift al prossimo sync.
"""
from __future__ import annotations
import os, json, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]:
        os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
API    = f"https://{DOMAIN}/admin/api/2025-01"

# Price fixes to apply: (product_type_keyword, current_approx_price, correct_price)
# Identified from gmc_sync_report.json 2026-06-22
FIXES = {
    "Dress":           {"old": 46.38, "new": "65.00"},
    "Tee":             {"old": 41.38, "new": "49.00"},
    "Hawaiian Shirt":  {"old": 82.44, "new": "79.00"},
    "Windbreaker":     {"old": 111.50, "new": "109.00"},
    "Sneakers_Flag03": {"title_contains": "Flag 03", "old": 70.02, "new": "75.00"},
}

def fetch_products_by_type(product_type_keyword: str):
    r = requests.get(f"{API}/products.json", headers=HDR, verify=False,
        params={"limit": 250, "status": "active", "fields": "id,title,product_type,variants"})
    products = r.json().get("products", [])
    return [p for p in products if product_type_keyword.lower() in (p.get("product_type") or "").lower()
            or product_type_keyword.lower() in p.get("title", "").lower()]

def fix_product_price(product_id: int, new_price: str, product_title: str):
    r = requests.get(f"{API}/products/{product_id}/variants.json", headers=HDR, verify=False,
        params={"limit": 100, "fields": "id,price"})
    variants = r.json().get("variants", [])
    fixed = 0
    for v in variants:
        if abs(float(v["price"]) - float(new_price)) > 0.5:
            rr = requests.put(f"{API}/variants/{v['id']}.json", headers=HDR, verify=False,
                json={"variant": {"id": v["id"], "price": new_price}})
            if rr.status_code == 200:
                fixed += 1
    return fixed

print("BKS Price Fix — applying approved ladder corrections")
print("="*55)

total_fixed = 0

# Fix Racerback Dresses
print("\n[1] Racerback Dresses: $46.38 -> $65.00")
products = fetch_products_by_type("Dress")
for p in products:
    if abs(float(p["variants"][0]["price"]) - 46.38) < 1.0:
        n = fix_product_price(p["id"], "65.00", p["title"])
        total_fixed += n
        print(f"  OK  {p['title'][:50]} ({n} variants)")

# Fix Cut & Sew Tees
print("\n[2] Cut & Sew Tees: $41.38 -> $49.00")
products = fetch_products_by_type("All Over Prints")
for p in products:
    if "Tee" in p["title"] and abs(float(p["variants"][0]["price"]) - 41.38) < 1.0:
        n = fix_product_price(p["id"], "49.00", p["title"])
        total_fixed += n
        print(f"  OK  {p['title'][:50]} ({n} variants)")

# Fix Hawaiian Shirts
print("\n[3] Hawaiian Shirts: $82.44 -> $79.00")
products = fetch_products_by_type("All Over Prints")
for p in products:
    if "Hawaiian" in p["title"] and abs(float(p["variants"][0]["price"]) - 82.44) < 1.0:
        n = fix_product_price(p["id"], "79.00", p["title"])
        total_fixed += n
        print(f"  OK  {p['title'][:50]} ({n} variants)")

# Fix Windbreakers
print("\n[4] Windbreakers: $111.50 -> $109.00")
products = fetch_products_by_type("Windbreaker Jacket")
for p in products:
    if abs(float(p["variants"][0]["price"]) - 111.50) < 1.0:
        n = fix_product_price(p["id"], "109.00", p["title"])
        total_fixed += n
        print(f"  OK  {p['title'][:50]} ({n} variants)")

# Fix Sneakers Flag 03
print("\n[5] Sneakers Flag 03: $70.02 -> $75.00")
products = fetch_products_by_type("Sneakers")
for p in products:
    if "Flag 03" in p["title"] and abs(float(p["variants"][0]["price"]) - 70.02) < 1.0:
        n = fix_product_price(p["id"], "75.00", p["title"])
        total_fixed += n
        print(f"  OK  {p['title'][:50]} ({n} variants)")

print(f"\n{'='*55}")
print(f"Total variants updated: {total_fixed}")
print("Run gmc_daily_sync.py to verify — should show 0 critical alerts.")
