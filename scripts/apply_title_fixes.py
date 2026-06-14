"""Apply product title fixes from product_name_audit.csv to Shopify.

Actions:
- Delete: apparel-accessories-clothing-sleepwear-loungewear (duplicate)
- Rename handle + title: inspire-artista-low-top -> bks-glyph-lattice-sneakers
- Skip: bks-riviera-blocks™-athletic-long-shorts (draft)
- Update title (remove ™): all remaining 182 products
"""
from __future__ import annotations

import csv
import os
import time
from pathlib import Path
import requests

# Load .env from project root
ROOT = Path(__file__).resolve().parent.parent
env_path = ROOT / ".env"
if env_path.exists():
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k not in os.environ or not os.environ[k]:
            os.environ[k] = v

DOMAIN   = os.environ.get("SHOPIFY_MYSHOPIFY_DOMAIN", "")
TOKEN    = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
VERSION  = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
GQL_URL  = f"https://{DOMAIN}/admin/api/{VERSION}/graphql.json"
HEADERS  = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

SKIP_HANDLE   = "bks-riviera-blocks™-athletic-long-shorts"
DELETE_HANDLE = "apparel-accessories-clothing-sleepwear-loungewear"
RENAME_HANDLE = "inspire-artista-low-top"
RENAME_NEW    = "bks-glyph-lattice-sneakers"


def gql(query: str, variables: dict) -> dict:
    import urllib3
    payload = {"query": query, "variables": variables}
    try:
        r = requests.post(GQL_URL, json=payload, headers=HEADERS, timeout=30)
    except requests.exceptions.SSLError:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        r = requests.post(GQL_URL, json=payload, headers=HEADERS, timeout=30, verify=False)
    r.raise_for_status()
    return r.json()


def get_product_gid(handle: str) -> str | None:
    q = """
    query($handle: String!) {
      productByHandle(handle: $handle) { id }
    }"""
    data = gql(q, {"handle": handle})
    p = data.get("data", {}).get("productByHandle")
    return p["id"] if p else None


def update_product(gid: str, title: str = None, handle: str = None) -> str:
    input_vars: dict = {"id": gid}
    if title:
        input_vars["title"] = title
    if handle:
        input_vars["handle"] = handle
    q = """
    mutation($input: ProductInput!) {
      productUpdate(input: $input) {
        product { id title handle }
        userErrors { field message }
      }
    }"""
    data = gql(q, {"input": input_vars})
    errs = data.get("data", {}).get("productUpdate", {}).get("userErrors", [])
    if errs:
        return f"ERROR: {errs}"
    p = data.get("data", {}).get("productUpdate", {}).get("product", {})
    return f"OK title={p.get('title')} handle={p.get('handle')}"


def delete_product(gid: str) -> str:
    q = """
    mutation($id: ID!) {
      productDelete(input: {id: $id}) {
        deletedProductId
        userErrors { field message }
      }
    }"""
    data = gql(q, {"id": gid})
    errs = data.get("data", {}).get("productDelete", {}).get("userErrors", [])
    if errs:
        return f"ERROR: {errs}"
    return f"DELETED {gid}"


def main() -> None:
    audit_path = ROOT / "output" / "product_name_audit.csv"
    rows = list(csv.DictReader(audit_path.read_text(encoding="utf-8-sig").splitlines()))

    log_rows = []
    ok = err = skipped = deleted = 0

    for row in rows:
        handle = row["handle"].strip()
        suggested = row["suggested_title"].strip()

        # Skip draft
        if handle == SKIP_HANDLE:
            print(f"SKIP  {handle}")
            log_rows.append({"handle": handle, "action": "skip", "result": "draft - skipped"})
            skipped += 1
            continue

        # Delete duplicate
        if handle == DELETE_HANDLE:
            gid = get_product_gid(handle)
            if not gid:
                msg = "not found on Shopify"
                print(f"DELETE {handle} — {msg}")
                log_rows.append({"handle": handle, "action": "delete", "result": msg})
            else:
                msg = delete_product(gid)
                print(f"DELETE {handle} — {msg}")
                log_rows.append({"handle": handle, "action": "delete", "result": msg})
                deleted += 1
            time.sleep(0.3)
            continue

        # Rename handle
        gid = get_product_gid(handle)
        if not gid:
            print(f"MISS  {handle}")
            log_rows.append({"handle": handle, "action": "update", "result": "product not found"})
            err += 1
            time.sleep(0.2)
            continue

        if handle == RENAME_HANDLE:
            msg = update_product(gid, title=suggested, handle=RENAME_NEW)
            print(f"RENAME {handle} -> {RENAME_NEW} — {msg}")
            log_rows.append({"handle": handle, "action": "rename+title", "result": msg})
        else:
            msg = update_product(gid, title=suggested)
            print(f"TITLE  {handle} — {msg}")
            log_rows.append({"handle": handle, "action": "title", "result": msg})

        if msg.startswith("OK"):
            ok += 1
        else:
            err += 1
        time.sleep(0.25)

    # Write log
    log_path = ROOT / "output" / "title_fix_log.csv"
    with log_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["handle", "action", "result"])
        w.writeheader()
        w.writerows(log_rows)

    print(f"\nDone. OK={ok} deleted={deleted} skipped={skipped} errors={err}")
    print(f"Log: {log_path}")


if __name__ == "__main__":
    main()
