"""BKS Studio — Upload Site Images to Shopify CDN + Update Theme Sections.

Legge output/site_images/manifest.json, carica ogni file su Shopify Files API
(graphql files.create), salva i CDN URL nel manifest.

Opzionalmente aggiorna anche:
  - Metafield collection.image per ogni collezione (hero_banner)
  - JSON settings del template piano-hero (piano_square)

Uso:
  python scripts/upload_site_images.py             # carica tutto il manifest
  python scripts/upload_site_images.py --type hero # solo hero_banner
  python scripts/upload_site_images.py --collection bks-riviera
  python scripts/upload_site_images.py --dry-run   # mostra cosa verrebbe caricato
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
import requests
import urllib3

urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_env = ROOT / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        _k = _k.strip(); _v = _v.strip().strip('"').strip("'")
        if _k not in os.environ:
            os.environ[_k] = _v

DOMAIN  = os.environ.get("SHOPIFY_MYSHOPIFY_DOMAIN", "")
TOKEN   = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-01")
MANIFEST_PATH = ROOT / "output" / "site_images" / "manifest.json"

GRAPHQL_URL = f"https://{DOMAIN}/admin/api/{VERSION}/graphql.json"
REST_BASE   = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR_REST    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
HDR_GQL     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}


def _out(msg: str) -> None:
    sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
    sys.stdout.flush()


def _gql(query: str, variables: dict | None = None) -> dict:
    body: dict = {"query": query}
    if variables:
        body["variables"] = variables
    r = requests.post(GRAPHQL_URL, headers=HDR_GQL,
                      json=body, timeout=30, verify=False)
    r.raise_for_status()
    return r.json()


def stage_upload(filename: str, mime: str = "image/png") -> tuple[str, list[dict]]:
    """Request a staged upload target from Shopify."""
    q = """
    mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
      stagedUploadsCreate(input: $input) {
        stagedTargets {
          url
          resourceUrl
          parameters { name value }
        }
        userErrors { field message }
      }
    }
    """
    variables = {
        "input": [{
            "filename": filename,
            "mimeType": mime,
            "httpMethod": "POST",
            "resource": "FILE",
        }]
    }
    data = _gql(q, variables)
    targets = data["data"]["stagedUploadsCreate"]["stagedTargets"]
    if not targets:
        errors = data["data"]["stagedUploadsCreate"].get("userErrors", [])
        raise RuntimeError(f"stagedUploadsCreate failed: {errors}")
    target = targets[0]
    return target["url"], target["parameters"], target.get("resourceUrl", "")


def upload_to_stage(upload_url: str, params: list[dict], file_path: Path) -> None:
    """POST the file to the staged upload URL."""
    fields = {p["name"]: p["value"] for p in params}
    with open(file_path, "rb") as f:
        r = requests.post(upload_url, data=fields,
                          files={"file": (file_path.name, f, "image/png")},
                          timeout=60, verify=False)
    if r.status_code not in (200, 201, 204):
        raise RuntimeError(f"Stage upload failed: {r.status_code} {r.text[:200]}")


def create_file(resource_url: str, filename: str) -> str:
    """Create a Shopify File from the staged resource URL; return CDN URL."""
    q = """
    mutation fileCreate($files: [FileCreateInput!]!) {
      fileCreate(files: $files) {
        files { url fileStatus }
        userErrors { field message }
      }
    }
    """
    variables = {
        "files": [{
            "originalSource": resource_url,
            "filename": filename,
            "contentType": "IMAGE",
        }]
    }
    data = _gql(q, variables)
    files = data["data"]["fileCreate"].get("files", [])
    errors = data["data"]["fileCreate"].get("userErrors", [])
    if errors:
        raise RuntimeError(f"fileCreate errors: {errors}")
    return files[0]["url"] if files else ""


def upload_file(file_path: Path) -> str:
    """Full upload pipeline: stage → upload → create → return CDN URL."""
    filename = file_path.name
    upload_url, params, resource_url = stage_upload(filename)
    upload_to_stage(upload_url, params, file_path)
    time.sleep(1)
    cdn_url = create_file(resource_url, filename)
    return cdn_url


def update_collection_image(handle: str, cdn_url: str) -> bool:
    """Set collection.image via REST API using the CDN URL."""
    r = requests.get(f"{REST_BASE}/collections.json?handle={handle}",
                     headers=HDR_REST, timeout=20, verify=False)
    if not r.ok:
        return False
    cols = r.json().get("collections", [])
    if not cols:
        return False
    col_id = cols[0]["id"]

    payload = {"collection": {"id": col_id, "image": {"src": cdn_url}}}
    r2 = requests.put(f"{REST_BASE}/collections/{col_id}.json",
                      headers=HDR_REST, json=payload, timeout=20, verify=False)
    return r2.ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload BKS site images to Shopify CDN")
    parser.add_argument("--type", choices=["hero", "piano", "all"], default="all")
    parser.add_argument("--collection", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--update-collection-images", action="store_true",
                        help="Also update collection.image in Shopify Admin for hero_banner")
    args = parser.parse_args()

    if not MANIFEST_PATH.exists():
        _out("✗ Manifest not found. Run generate_site_images.py first.")
        sys.exit(1)

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    if not DOMAIN or not TOKEN:
        _out("✗ SHOPIFY_MYSHOPIFY_DOMAIN or SHOPIFY_ADMIN_TOKEN not set.")
        sys.exit(1)

    type_filter = set()
    if args.type in ("hero", "all"):
        type_filter.add("hero_banner")
    if args.type in ("piano", "all"):
        type_filter.add("piano_square")

    uploaded = 0
    skipped = 0
    errors = 0

    _out(f"=== BKS Site Images Upload ({'DRY RUN' if args.dry_run else 'LIVE'}) ===\n")

    for handle, entries in manifest.items():
        if args.collection and handle != args.collection:
            continue

        _out(f"── {handle} ──────────────────────────")

        for type_key, info in entries.items():
            if type_key not in type_filter:
                continue

            file_path = ROOT / info["path"]
            existing_url = info.get("shopify_url", "")

            if existing_url and not args.dry_run:
                _out(f"  ✓ {type_key} already uploaded: {existing_url[:60]}...")
                skipped += 1
                continue

            if not file_path.exists():
                _out(f"  ✗ File not found: {info['path']}")
                errors += 1
                continue

            _out(f"  → Uploading {type_key} ({file_path.name})...")

            if args.dry_run:
                _out(f"    [DRY] would upload {file_path.name}")
                skipped += 1
                continue

            try:
                cdn_url = upload_file(file_path)
                info["shopify_url"] = cdn_url
                MANIFEST_PATH.write_text(
                    json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
                )
                _out(f"  ✓ {cdn_url[:80]}...")
                uploaded += 1

                if type_key == "hero_banner" and args.update_collection_images:
                    ok = update_collection_image(handle, cdn_url)
                    _out(f"  {'✓' if ok else '✗'} collection.image updated" if ok else "  ✗ collection.image update failed")

                time.sleep(0.5)
            except Exception as exc:
                _out(f"  ✗ Error: {exc}")
                errors += 1

    _out(f"\n=== DONE === uploaded={uploaded} skipped={skipped} errors={errors}")

    if uploaded > 0:
        _out("\nURL salvati in output/site_images/manifest.json")
        _out("Prossimo passo: aggiornare le section settings nel tema con i CDN URL")
        _out("  → Online Store > Themes > Customize > Piano Hero (block image_url)")
        _out("  → oppure usa scripts/patch_theme_site_images.py")


if __name__ == "__main__":
    main()
