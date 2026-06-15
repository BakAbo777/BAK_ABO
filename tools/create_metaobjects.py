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
        "key": "tagline",
        "name": "Tagline",
        "type": "single_line_text_field",
        "required": False,
        "description": "Sottotitolo breve per hero e collection signal.",
    },
    {
        "key": "description",
        "name": "Descrizione",
        "type": "multi_line_text_field",
        "required": False,
        "description": "Descrizione editoriale principale, leggibile dal tema.",
    },
    {
        "key": "series",
        "name": "Serie",
        "type": "single_line_text_field",
        "required": False,
        "description": "Serie o registro creativo della collezione.",
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
    {
        "key": "hero_image",
        "name": "Hero image",
        "type": "file_reference",
        "required": False,
        "description": "Immagine hero della collezione, ideale 1600x900 o superiore.",
    },
    {
        "key": "hero_video",
        "name": "Hero video",
        "type": "url",
        "required": False,
        "description": "URL video MP4 o CDN HeyGen per hero collection.",
    },
]


COLLECTIONS = [
    {
        "handle": "bks-folklore",
        "name": "BKS Folklore",
        "tagline": "Invented imagery and private bestiary",
        "series": "naif",
        "editorial_description": "Invented imagery, private bestiary and naif register. Folklore builds a visual world that belongs only to BKS Studio.",
        "color_hex": "#4A7C59",
        "shopify_handle": "bks-folklore",
    },
    {
        "handle": "bks-glyph",
        "name": "BKS Glyph",
        "tagline": "Sign systems and brut geometry",
        "series": "brut",
        "editorial_description": "Sign systems, brut geometry and modular codes. Glyph treats surface as structure and pattern as an internal alphabet.",
        "color_hex": "#1A1A2E",
        "shopify_handle": "bks-glyph",
    },
    {
        "handle": "bks-marker",
        "name": "BKS Marker",
        "tagline": "Urban gesture and neo-expressionism",
        "series": "neo-expressionism",
        "editorial_description": "Urban gesture, neo-expressionism and the mark as identity. Marker moves through painterly action and city texture.",
        "color_hex": "#C84B31",
        "shopify_handle": "bks-marker",
    },
    {
        "handle": "bks-riviera",
        "name": "BKS Riviera",
        "tagline": "Mediterranean register and coastal geometry",
        "series": "islands",
        "editorial_description": "Mediterranean register, coastal geometry and islands palette. Riviera works with water, tile, stone and resort rhythm.",
        "color_hex": "#2B7A8D",
        "shopify_handle": "bks-riviera",
    },
    {
        "handle": "bks-pulse",
        "name": "BKS Pulse",
        "tagline": "Optical geometry and kinetic fields",
        "series": "optical",
        "editorial_description": "Optical geometry, kinetic fields and chromatic oscillation. Pulse is precise, restless and built from visual tension.",
        "color_hex": "#6B2D8B",
        "shopify_handle": "bks-pulse",
    },
    {
        "handle": "bks-token",
        "name": "BKS Token",
        "tagline": "Arcade logic and digital memory",
        "series": "arcade",
        "editorial_description": "Arcade logic, digital register and vintage electronics as surface. Token turns low-bit memory into wearable code.",
        "color_hex": "#E8A838",
        "shopify_handle": "bks-token",
    },
    {
        "handle": "bks-flag",
        "name": "BKS Flag",
        "tagline": "Coded colour fields and signal structure",
        "series": "neo-dada",
        "editorial_description": "Coded colour fields, neo-dada geometry and signal structure. Flag uses blocks and fields without referencing real flags.",
        "color_hex": "#2C3E7A",
        "shopify_handle": "bks-flag",
    },
    {
        "handle": "bks-hours",
        "name": "BKS Hours",
        "tagline": "Urban contemplation and painterly stillness",
        "series": "hyperrealism",
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
    fieldDefinitions {
      key
      name
      type {
        name
      }
    }
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

UPDATE_DEFINITION = """
mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
  metaobjectDefinitionUpdate(id: $id, definition: $definition) {
    metaobjectDefinition {
      id
      type
      name
      fieldDefinitions {
        key
        name
        type {
          name
        }
      }
    }
    userErrors {
      field
      message
      code
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
        existing_keys = {field["key"] for field in definition.get("fieldDefinitions", [])}
        missing_fields = [field for field in FIELD_DEFINITIONS if field["key"] not in existing_keys]
        if not missing_fields:
            print(f"exists  definition {METAOBJECT_TYPE} {definition['id']}")
            return definition["id"]

        payload = {
            "fieldDefinitions": [{"create": field} for field in missing_fields],
        }
        updated = client.query(UPDATE_DEFINITION, {"id": definition["id"], "definition": payload})
        result = updated["data"]["metaobjectDefinitionUpdate"]
        errors = result.get("userErrors") or []
        if errors:
            raise RuntimeError(errors)
        added = ", ".join(field["key"] for field in missing_fields)
        print(f"updated definition {METAOBJECT_TYPE} {definition['id']} added: {added}")
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
        {"key": "tagline", "value": collection["tagline"]},
        {"key": "description", "value": collection["editorial_description"]},
        {"key": "series", "value": collection["series"]},
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
            "message": "; ".join(error.get("message") or "" for error in errors),
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
