"""Push corrected image alt texts to Shopify via REST API.

Reads output/products_export_alt_fixed.csv, groups by handle,
then for each product updates only the image alt texts that differ.
"""
from __future__ import annotations
import csv
import os
import time
import requests
import urllib3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]:
        os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

CSV_PATH = ROOT / "output" / "products_export_alt_fixed.csv"

_ssl_ok = True

def _request(method: str, path: str, **kwargs) -> dict:
    global _ssl_ok
    url = f"{BASE}{path}"
    for attempt in range(5):
        try:
            r = getattr(requests, method)(url, headers=HDR, timeout=30, verify=_ssl_ok, **kwargs)
        except requests.exceptions.SSLError:
            urllib3.disable_warnings()  # type: ignore
            _ssl_ok = False
            r = getattr(requests, method)(url, headers=HDR, timeout=30, verify=False, **kwargs)
        if r.status_code == 429:
            wait = 2 ** attempt + 1
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()
    return r.json()

def _get(path: str) -> dict:
    return _request("get", path)

def _put(path: str, payload: dict) -> dict:
    return _request("put", path, json=payload)


def load_csv_alts() -> dict[str, dict[int, str]]:
    """Return {handle: {position: alt_text}} from CSV — only rows with alt text."""
    result: dict[str, dict[int, str]] = {}
    current_handle = ""
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            h = (row.get("Handle") or "").strip()
            if h:
                current_handle = h
            pos_raw = (row.get("Image Position") or "").strip()
            alt     = (row.get("Image Alt Text") or "").strip()
            if current_handle and pos_raw and alt:
                try:
                    pos = int(pos_raw)
                except ValueError:
                    continue
                result.setdefault(current_handle, {})[pos] = alt
    return result


def get_product_id(handle: str) -> str | None:
    data = _get(f"/products.json?handle={handle}&fields=id,handle")
    products = data.get("products", [])
    return str(products[0]["id"]) if products else None


def get_images(product_id: str) -> list[dict]:
    data = _get(f"/products/{product_id}/images.json?fields=id,position,alt")
    return data.get("images", [])


def update_image_alt(product_id: str, image_id: str, alt: str) -> None:
    _put(f"/products/{product_id}/images/{image_id}.json",
         {"image": {"id": image_id, "alt": alt}})


def main() -> None:
    csv_alts = load_csv_alts()
    handles  = list(csv_alts.keys())
    total    = len(handles)
    updated  = 0
    skipped  = 0
    errors   = 0

    print(f"Products to process: {total}")

    for i, handle in enumerate(handles, 1):
        try:
            pid = get_product_id(handle)
            if not pid:
                print(f"  [{i}/{total}] MISS  {handle}")
                skipped += 1
                continue

            images    = get_images(pid)
            pos_map   = {img["position"]: img for img in images}
            want_alts = csv_alts[handle]
            changed   = 0

            for pos, new_alt in want_alts.items():
                img = pos_map.get(pos)
                if not img:
                    continue
                if (img.get("alt") or "").strip() == new_alt:
                    continue  # already correct
                update_image_alt(pid, str(img["id"]), new_alt)
                changed += 1
                time.sleep(0.5)  # stay well under rate limit

            if changed:
                print(f"  [{i}/{total}] OK    {handle}  ({changed} images)")
                updated += 1
            else:
                print(f"  [{i}/{total}] SAME  {handle}")

        except Exception as e:
            print(f"  [{i}/{total}] ERR   {handle}: {e}")
            errors += 1

        time.sleep(0.6)

    print(f"\nDone — updated: {updated}  same: {total-updated-skipped-errors}  miss: {skipped}  err: {errors}")


if __name__ == "__main__":
    main()
