#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create or sync BKS Shopify smart collections.

Default target: the 16 missing V20 collections from the operational plan
(14 product-type collections + Swimwear + Outerwear). Use --all to include
the 8 editorial collections and New Arrivals too.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bks_collection_specs import (  # noqa: E402
    ALL_COLLECTIONS,
    CollectionSpec,
    collection_to_payload,
    specs_for_missing_batch,
)


DEFAULT_API_VERSION = "2025-01"
ENV_PATH = ROOT / ".env"
requests: Any = None


def load_requests() -> None:
    global requests
    if requests is not None:
        return
    try:
        import requests as requests_module
    except ImportError:
        sys.exit("Installa requests: pip install requests")
    requests = requests_module


def get_env_value(*names: str, default: str = "") -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return default


def load_local_env(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class ShopifyAdmin:
    def __init__(self, store: str, token: str, api_version: str) -> None:
        domain = store.replace("https://", "").replace("http://", "").strip("/")
        self.base_url = f"https://{domain}/admin/api/{api_version}"
        self.headers = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        response = requests.request(
            method,
            f"{self.base_url}{path}",
            headers=self.headers,
            timeout=45,
            **kwargs,
        )
        response.raise_for_status()
        return response

    def list_smart_collections(self) -> dict[str, dict[str, Any]]:
        response = self.request(
            "GET",
            "/smart_collections.json",
            params={
                "limit": 250,
                "fields": "id,title,handle,template_suffix,metafields_global_title_tag,metafields_global_description_tag",
            },
        )
        return {item["handle"]: item for item in response.json().get("smart_collections", [])}

    def create_collection(self, spec: CollectionSpec) -> dict[str, Any]:
        response = self.request("POST", "/smart_collections.json", json=collection_to_payload(spec))
        return response.json()["smart_collection"]

    def update_collection(self, collection_id: int | str, spec: CollectionSpec) -> dict[str, Any]:
        payload = collection_to_payload(spec)
        payload["smart_collection"]["id"] = collection_id
        response = self.request("PUT", f"/smart_collections/{collection_id}.json", json=payload)
        return response.json()["smart_collection"]


def parse_args() -> argparse.Namespace:
    load_local_env()
    parser = argparse.ArgumentParser(description="Create or sync BKS V20 Shopify smart collections.")
    parser.add_argument("--all", action="store_true", help="Target all 25 collections instead of the 16 missing batch.")
    parser.add_argument("--upsert", action="store_true", help="Update existing collections with SEO/template/body/rules.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned payloads without writing to Shopify.")
    parser.add_argument("--sleep", type=float, default=0.5, help="Delay between Shopify writes.")
    parser.add_argument("--api-version", default=get_env_value("SHOPIFY_API_VERSION", default=DEFAULT_API_VERSION))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    store = get_env_value("SHOPIFY_MYSHOPIFY_DOMAIN", "SHOPIFY_STORE", "SHOP")
    token = get_env_value("SHOPIFY_ADMIN_TOKEN", "SHOPIFY_TOKEN", "TOKEN")

    specs = ALL_COLLECTIONS if args.all else specs_for_missing_batch()
    print("BKS Studio — Shopify collections V20")
    print(f"Store : {store or '<not set>'}")
    print(f"API   : {args.api_version}")
    print(f"Target: {len(specs)} collection ({'25 complete' if args.all else '16 missing batch'})")
    print(f"Mode  : {'dry-run' if args.dry_run else ('upsert' if args.upsert else 'create-missing')}")
    print("-" * 72)

    if args.dry_run:
        for spec in specs:
            payload = collection_to_payload(spec)["smart_collection"]
            print(f"{spec.handle:24} {spec.effective_template:28} {payload['sort_order']:12} {spec.rule_label}")
        return 0

    if not store or not token:
        print("Errore: imposta SHOPIFY_STORE/SHOPIFY_MYSHOPIFY_DOMAIN e SHOPIFY_TOKEN/SHOPIFY_ADMIN_TOKEN.")
        return 1

    load_requests()
    client = ShopifyAdmin(store, token, args.api_version)
    live = client.list_smart_collections()
    created = updated = skipped = errors = 0

    for spec in specs:
        existing = live.get(spec.handle)
        label = f"{spec.handle:24} {spec.title:28}"
        try:
            if existing and not args.upsert:
                print(f"skip     {label} already exists")
                skipped += 1
            elif existing:
                result = client.update_collection(existing["id"], spec)
                print(f"updated  {label} id={result.get('id')}")
                updated += 1
            else:
                result = client.create_collection(spec)
                print(f"created  {label} id={result.get('id')}")
                created += 1
        except requests.HTTPError as exc:
            body = exc.response.text[:300] if exc.response is not None else ""
            print(f"error    {label} {exc} {body}")
            errors += 1
        except Exception as exc:
            print(f"error    {label} {exc}")
            errors += 1
        time.sleep(args.sleep)

    print("-" * 72)
    print(f"Creati: {created} | Aggiornati: {updated} | Skip: {skipped} | Errori: {errors}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
