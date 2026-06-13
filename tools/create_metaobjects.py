#!/usr/bin/env python3
"""
BKS Studio - Fase 3
Create the bks_collection metaobject definition and its 8 editorial entries.

Run:
  python tools/create_metaobjects.py --no-verify-ssl
"""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from bks_shopify_api import ShopifyGraphQL, add_shopify_args


BASE_DIR = Path(__file__).resolve().parents[1]
LOG_PATH = BASE_DIR / "output" / "metaobjects_log.csv"
METAOBJECT_TYPE = "bks_collection"


FIELD_DEFINITIONS = [
    {
        "key": "name",
        "name": "Nome",
        "type": "single_line_text_field",
        "required": True,
        "description": "Nome display della collezione editoriale.",
    },
    {
        "key": "editorial_description",
        "name": "Descrizione editoriale",
        "type": "multi_line_text_field",
        "required": False,
        "description": "Descrizione editoriale lunga per sezioni tema.",
    },
    {
        "key": "color_hex",
        "name": "Colore esadecimale",
        "type": "color",
        "required": False,
        "description": "Colore accent editoriale in formato HEX.",
    },
    {
        "key": "shopify_handle",
        "name": "Handle Shopify",
        "type": "single_line_text_field",
        "required": True,
        "description": "Handle della smart collection Shopify collegata.",
    },
]


COLLECTIONS = [
    {
        "handle": "bks-folklore",
        "name": "BKS Folklore",
        "editorial_description": "Invented imagery, private bestiary and naif register. Folklore builds a visual world that belongs only to BKS Studio.",
        "color_hex": "#4A7C59",
        "shopify_handle": "bks-folklore",
    },
    {
        "handle": "bks-glyph",
        "name": "BKS Glyph",
        "editorial_description": "Sign systems, brut geometry and modular codes. Glyph treats surface as structure and pattern as an internal alphabet.",
        "color_hex": "#1A1A2E",
        "shopify_handle": "bks-glyph",
    },
    {
        "handle": "bks-marker",
        "name": "BKS Marker",
        "editorial_description": "Urban gesture, neo-expressionism and the mark as identity. Marker moves through painterly action and city texture.",
        "color_hex": "#C84B31",
        "shopify_handle": "bks-marker",
    },
    {
        "handle": "bks-riviera",
        "name": "BKS Riviera",
        "editorial_description": "Mediterranean register, coastal geometry and islands palette. Riviera works with water, tile, stone and resort rhythm.",
        "color_hex": "#2B7A8D",
        "shopify_handle": "bks-riviera",
    },
    {
        "handle": "bks-pulse",
        "name": "BKS Pulse",
        "editorial_description": "Optical geometry, kinetic fields and chromatic oscillation. Pulse is precise, restless and built from visual tension.",
        "color_hex": "#6B2D8B",
        "shopify_handle": "bks-pulse",
    },
    {
        "handle": "bks-token",
        "name": "BKS Token",
        "editorial_description": "Arcade logic, digital register and vintage electronics as surface. Token turns low-bit memory into wearable code.",
        "color_hex": "#E8A838",
        "shopify_handle": "bks-token",
    },
    {
        "handle": "bks-flag",
        "name": "BKS Flag",
        "editorial_description": "Coded colour fields, neo-dada geometry and signal structure. Flag uses blocks and fields without referencing real flags.",
        "color_hex": "#2C3E7A",
        "shopify_handle": "bks-flag",
    },
    {
        "handle": "bks-hours",
        "name": "BKS Hours",
        "editorial_description": "Urban contemplation, painterly register and hyperrealist surface. Hours holds architecture and figures in stillness.",
        "color_hex": "#8B7355",
        "shopify_handle": "bks-hours",
    },
]


GET_DEFINITION = """
query GetMetaobjectDefinition($type: String!) {
  metaobjectDefinitionByType(type: $type) {
    id
    type
    name
  }
}
"""

CREATE_DEFINITION = """
mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
  metaobjectDefinitionCreate(definition: $definition) {
    metaobjectDefinition {
      id
      type
      name
    }
    userErrors {
      field
      message
    }
  }
}
"""

GET_METAOBJECT = """
query GetMetaobject($handle: MetaobjectHandleInput!) {
  metaobjectByHandle(handle: $handle) {
    id
    handle
    type
  }
}
"""

CREATE_METAOBJECT = """
mutation CreateMetaobject($metaobject: MetaobjectCreateInput!) {
  metaobjectCreate(metaobject: $metaobject) {
    metaobject {
      id
      handle
      type
    }
    userErrors {
      field
      message
    }
  }
}
"""


def ensure_definition(client: ShopifyGraphQL) -> str:
    existing = client.query(GET_DEFINITION, {"type": METAOBJECT_TYPE})
    definition = existing["data"].get("metaobjectDefinitionByType")
    if definition:
        print(f"exists  definition {METAOBJECT_TYPE} {definition['id']}")
        return definition["id"]

    payload = {
        "type": METAOBJECT_TYPE,
        "name": "BKS Collection",
        "displayNameKey": "name",
        "fieldDefinitions": FIELD_DEFINITIONS,
    }
    created = client.query(CREATE_DEFINITION, {"definition": payload})
    result = created["data"]["metaobjectDefinitionCreate"]
    errors = result.get("userErrors") or []
    if errors:
        raise RuntimeError(errors)
    definition = result["metaobjectDefinition"]
    print(f"created definition {METAOBJECT_TYPE} {definition['id']}")
    return definition["id"]


def ensure_metaobject(client: ShopifyGraphQL, collection: dict[str, str]) -> dict[str, str]:
    handle = {"type": METAOBJECT_TYPE, "handle": collection["handle"]}
    existing = client.query(GET_METAOBJECT, {"handle": handle})
    metaobject = existing["data"].get("metaobjectByHandle")
    if metaobject:
        return {
            "status": "exists",
            "handle": collection["handle"],
            "id": metaobject["id"],
            "message": "",
        }

    fields = [
        {"key": "name", "value": collection["name"]},
        {"key": "editorial_description", "value": collection["editorial_description"]},
        {"key": "color_hex", "value": collection["color_hex"]},
        {"key": "shopify_handle", "value": collection["shopify_handle"]},
    ]
    payload = {"type": METAOBJECT_TYPE, "handle": collection["handle"], "fields": fields}
    created = client.query(CREATE_METAOBJECT, {"metaobject": payload})
    result = created["data"]["metaobjectCreate"]
    errors = result.get("userErrors") or []
    if errors:
        return {
            "status": "error",
            "handle": collection["handle"],
            "id": "",
            "message": "; ".join(error.get("message", "") for error in errors),
        }

    metaobject = result["metaobject"]
    return {
        "status": "created",
        "handle": collection["handle"],
        "id": metaobject["id"],
        "message": "",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create BKS collection metaobjects.")
    add_shopify_args(parser)
    args = parser.parse_args()

    client = ShopifyGraphQL.from_args(args)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"Store: {client.shop}")
    print(f"API: {client.api_version}")
    ensure_definition(client)

    results = []
    for collection in COLLECTIONS:
        result = ensure_metaobject(client, collection)
        results.append(result)
        print(f"{result['status']:7} {result['handle']} {result['message']}")
        time.sleep(0.4)

    with LOG_PATH.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["status", "handle", "id", "message"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Log: {LOG_PATH}")


if __name__ == "__main__":
    main()
