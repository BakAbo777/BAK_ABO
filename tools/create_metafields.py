#!/usr/bin/env python3
"""
BKS Studio - Fase 2
Create Shopify product metafield definitions for BKS fields.

Run:
  python tools/create_metafields.py --no-verify-ssl
"""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from bks_shopify_api import ShopifyGraphQL, add_shopify_args


BASE_DIR = Path(__file__).resolve().parents[1]
LOG_PATH = BASE_DIR / "output" / "metafield_definitions_log.csv"


BKS_METAFIELD_DEFINITIONS = [
    {
        "name": "BKS Collection",
        "namespace": "bks",
        "key": "collection",
        "type": "single_line_text_field",
        "description": "Editorial collection name: Folklore, Glyph, Marker, Riviera, Pulse, Token, Flag, Hours.",
        "ownerType": "PRODUCT",
        "pin": True,
    },
    {
        "name": "BKS Design",
        "namespace": "bks",
        "key": "design",
        "type": "single_line_text_field",
        "description": "Standalone design name extracted from the product title.",
        "ownerType": "PRODUCT",
        "pin": True,
    },
    {
        "name": "BKS Series",
        "namespace": "bks",
        "key": "series",
        "type": "single_line_text_field",
        "description": "Editorial series label: naif, brut, neo-expressionism, islands, optical, arcade, neo-dada, hyperrealism.",
        "ownerType": "PRODUCT",
        "pin": True,
    },
    {
        "name": "BKS Drop",
        "namespace": "bks",
        "key": "drop",
        "type": "single_line_text_field",
        "description": "Drop reference, for example catalog-reset-2026.",
        "ownerType": "PRODUCT",
        "pin": False,
    },
]

SHOPIFY_STANDARD_DEFINITIONS = [
    {
        "name": "Care Instructions",
        "namespace": "shopify",
        "key": "care-instructions",
        "type": "multi_line_text_field",
        "description": "Product care instructions.",
        "ownerType": "PRODUCT",
        "pin": True,
    },
    {
        "name": "Fabric",
        "namespace": "shopify",
        "key": "fabric",
        "type": "single_line_text_field",
        "description": "Primary fabric composition.",
        "ownerType": "PRODUCT",
        "pin": False,
    },
    {
        "name": "Fit",
        "namespace": "shopify",
        "key": "fit",
        "type": "single_line_text_field",
        "description": "Fit type.",
        "ownerType": "PRODUCT",
        "pin": False,
    },
]

METAFIELD_DEFINITIONS = BKS_METAFIELD_DEFINITIONS


CREATE_DEFINITION = """
mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
  metafieldDefinitionCreate(definition: $definition) {
    createdDefinition {
      id
      name
      namespace
      key
      type { name }
    }
    userErrors {
      field
      message
    }
  }
}
"""


def create_definition(client: ShopifyGraphQL, definition: dict[str, object]) -> dict[str, str]:
    namespace = str(definition["namespace"])
    key = str(definition["key"])
    try:
        data = client.query(CREATE_DEFINITION, {"definition": definition})
    except RuntimeError as exc:
        message = str(exc)
        if "ACCESS_DENIED" in message or "Access denied" in message:
            return {
                "status": "access_denied",
                "namespace": namespace,
                "key": key,
                "id": "",
                "message": "Token cannot create definitions in this namespace.",
            }
        return {"status": "error", "namespace": namespace, "key": key, "id": "", "message": message}

    result = data["data"]["metafieldDefinitionCreate"]
    errors = result.get("userErrors") or []
    created = result.get("createdDefinition")

    if created:
        return {
            "status": "created",
            "namespace": namespace,
            "key": key,
            "id": created["id"],
            "message": "",
        }

    message = "; ".join(error.get("message", "") for error in errors)
    if (
        "already" in message.lower()
        or "taken" in message.lower()
        or "in use" in message.lower()
    ):
        status = "exists"
    else:
        status = "error"
    return {"status": status, "namespace": namespace, "key": key, "id": "", "message": message}


def main() -> None:
    parser = argparse.ArgumentParser(description="Create BKS Shopify metafield definitions.")
    add_shopify_args(parser)
    parser.add_argument(
        "--include-shopify-standard",
        action="store_true",
        help="Also try optional shopify.* standard definitions. Shopify can deny these namespaces.",
    )
    args = parser.parse_args()

    client = ShopifyGraphQL.from_args(args)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    definitions = list(BKS_METAFIELD_DEFINITIONS)
    if args.include_shopify_standard:
        definitions.extend(SHOPIFY_STANDARD_DEFINITIONS)

    print(f"Store: {client.shop}")
    print(f"API: {client.api_version}")
    print(f"Definitions: {len(definitions)}")
    if not args.include_shopify_standard:
        print("Mode: BKS definitions only. Optional shopify.* definitions are skipped.")

    results = []
    for definition in definitions:
        result = create_definition(client, definition)
        if (
            result["status"] == "access_denied"
            and result["namespace"] == "shopify"
            and args.include_shopify_standard
        ):
            result["status"] = "optional_denied"
            result["message"] = "Optional Shopify namespace definition denied; BKS setup can continue."
        results.append(result)
        print(f"{result['status']:13} {result['namespace']}.{result['key']} {result['message']}")
        time.sleep(0.4)

    with LOG_PATH.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["status", "namespace", "key", "id", "message"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Log: {LOG_PATH}")


if __name__ == "__main__":
    main()
