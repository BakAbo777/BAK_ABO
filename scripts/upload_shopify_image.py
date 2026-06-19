"""Upload a local image to Shopify Files via stagedUploadsCreate → S3 → fileCreate."""
from __future__ import annotations
import os, sys, json, mimetypes, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()
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
GQL     = f"https://{DOMAIN}/admin/api/{VERSION}/graphql.json"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}


def _gql(query: str, variables: dict | None = None) -> dict:
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    r = requests.post(GQL, headers=HDR, json=payload, timeout=60, verify=False)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]


def upload_image(local_path: str | Path, shopify_filename: str | None = None) -> str:
    """Upload image to Shopify Files, return shopify://shop_images/<filename> URL."""
    path = Path(local_path)
    if not path.exists():
        raise FileNotFoundError(path)

    filename = shopify_filename or path.name
    mime = mimetypes.guess_type(filename)[0] or "image/png"
    file_size = path.stat().st_size

    print(f"[1/3] Staging upload: {filename} ({file_size} bytes)")
    stage_data = _gql(
        """
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
        """,
        {"input": [{
            "filename":   filename,
            "mimeType":   mime,
            "resource":   "FILE",
            "fileSize":   str(file_size),
            "httpMethod": "PUT",
        }]}
    )
    errs = stage_data["stagedUploadsCreate"]["userErrors"]
    if errs:
        raise RuntimeError(f"stagedUploadsCreate errors: {errs}")

    target = stage_data["stagedUploadsCreate"]["stagedTargets"][0]
    upload_url   = target["url"]
    resource_url = target["resourceUrl"]
    params       = {p["name"]: p["value"] for p in target["parameters"]}

    print(f"[2/3] Uploading to GCS: {upload_url[:60]}...")
    with open(path, "rb") as fh:
        # For Shopify staged uploads to GCS, parameters are request headers
        put_headers = dict(params)
        put_headers["Content-Type"] = mime
        r = requests.put(upload_url, data=fh, headers=put_headers, timeout=120, verify=False)
        if r.status_code not in (200, 201, 204):
            raise RuntimeError(f"GCS PUT failed: {r.status_code} {r.text[:300]}")

    print(f"[3/3] Registering file in Shopify...")
    file_data = _gql(
        """
        mutation fileCreate($files: [FileCreateInput!]!) {
          fileCreate(files: $files) {
            files { id alt fileStatus }
            userErrors { field message }
          }
        }
        """,
        {"files": [{"contentType": "IMAGE", "originalSource": resource_url, "filename": filename}]}
    )
    errs = file_data["fileCreate"]["userErrors"]
    if errs:
        raise RuntimeError(f"fileCreate errors: {errs}")

    shopify_url = f"shopify://shop_images/{filename}"
    print(f"Done. Shopify URL: {shopify_url}")
    return shopify_url


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload_shopify_image.py <local_path> [shopify_filename]")
        sys.exit(1)
    local   = sys.argv[1]
    sf_name = sys.argv[2] if len(sys.argv) > 2 else None
    result  = upload_image(local, sf_name)
    print(result)
