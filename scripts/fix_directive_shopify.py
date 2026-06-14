"""Update Shopify product descriptions: replace legacy EU Directive 1999/44/EC → 2019/771."""
from __future__ import annotations

import csv
import os
import time
from pathlib import Path
import requests
import urllib3

ROOT = Path(__file__).resolve().parent.parent
env_path = ROOT / ".env"
if env_path.exists():
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip(); v = v.strip().strip('"').strip("'")
        if k not in os.environ or not os.environ[k]:
            os.environ[k] = v

DOMAIN  = os.environ.get("SHOPIFY_MYSHOPIFY_DOMAIN", "")
TOKEN   = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
GQL_URL = f"https://{DOMAIN}/admin/api/{VERSION}/graphql.json"
HEADERS = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

OLD = "1999/44/EC"
NEW = "2019/771"


def gql(query: str, variables: dict) -> dict:
    payload = {"query": query, "variables": variables}
    try:
        r = requests.post(GQL_URL, json=payload, headers=HEADERS, timeout=30)
    except requests.exceptions.SSLError:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        r = requests.post(GQL_URL, json=payload, headers=HEADERS, timeout=30, verify=False)
    r.raise_for_status()
    return r.json()


def get_product(handle: str) -> dict | None:
    q = """
    query($handle: String!) {
      productByHandle(handle: $handle) {
        id
        descriptionHtml
      }
    }"""
    data = gql(q, {"handle": handle})
    return data.get("data", {}).get("productByHandle")


def update_description(gid: str, html: str) -> str:
    q = """
    mutation($input: ProductInput!) {
      productUpdate(input: $input) {
        product { id handle }
        userErrors { field message }
      }
    }"""
    data = gql(q, {"input": {"id": gid, "descriptionHtml": html}})
    errs = data.get("data", {}).get("productUpdate", {}).get("userErrors", [])
    if errs:
        return f"ERROR {errs}"
    p = data.get("data", {}).get("productUpdate", {}).get("product", {})
    return f"OK {p.get('handle')}"


def main() -> None:
    csv_path = ROOT / "output" / "products_export_updated.csv"
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    # Collect unique handles
    seen: set[str] = set()
    handles: list[str] = []
    for row in rows:
        h = row.get("Handle", "").strip()
        if h and h not in seen:
            seen.add(h)
            handles.append(h)

    log: list[dict] = []
    updated = skipped = errors = 0

    for handle in handles:
        product = get_product(handle)
        if not product:
            print(f"MISS  {handle}")
            log.append({"handle": handle, "result": "not found"})
            errors += 1
            time.sleep(0.2)
            continue

        html = product.get("descriptionHtml", "") or ""
        if OLD not in html:
            skipped += 1
            time.sleep(0.1)
            continue

        fixed_html = html.replace(OLD, NEW)
        msg = update_description(product["id"], fixed_html)
        print(f"FIX   {handle} — {msg}")
        log.append({"handle": handle, "result": msg})
        if msg.startswith("OK"):
            updated += 1
        else:
            errors += 1
        time.sleep(0.3)

    log_path = ROOT / "output" / "directive_fix_log.csv"
    with log_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["handle", "result"])
        w.writeheader()
        w.writerows(log)

    print(f"\nDone. updated={updated} skipped={skipped} errors={errors}")
    print(f"Log: {log_path}")


if __name__ == "__main__":
    main()
