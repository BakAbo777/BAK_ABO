"""Upload BKS setstyle hero images to Shopify + aggiorna i template.

Usage:
  python scripts/upload_setstyle_heroes.py                  # usa setstyle_ai/ (OpenAI)
  python scripts/upload_setstyle_heroes.py --source setstyle  # usa setstyle/ (Pillow)

Pipeline:
  1. Carica le 8 immagini da output/catalog_images/[source]/
  2. Aggiorna collection templates hero_image
  3. Aggiorna Weekly Editorial in index.json (con on-model da hero_candidates)
  4. Pusha tutto al tema live 202392961362
"""
from __future__ import annotations
import os, json, sys, time
import requests, urllib3
from pathlib import Path

urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent

for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ:
        os.environ[k] = v

DOMAIN     = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN      = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION    = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
LIVE_THEME = "202392961362"
GQL_URL    = f"https://{DOMAIN}/admin/api/{VERSION}/graphql.json"
REST_BASE  = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR_GQL    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
HDR_REST   = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

# Source selection
source = "setstyle_ai"
if "--source" in sys.argv:
    idx = sys.argv.index("--source")
    if idx + 1 < len(sys.argv):
        source = sys.argv[idx + 1]

SETSTYLE_DIR = ROOT / "output" / "catalog_images" / source
CANDS_DIR    = ROOT / "output" / "catalog_images" / "hero_candidates"
TPLS         = ROOT / "04_TEMA_SHOPIFY" / "templates"

COLLECTIONS = ["bks-hours", "bks-glyph", "bks-marker", "bks-riviera",
               "bks-pulse", "bks-token", "bks-flag", "bks-origin"]

# On-model editorial images for Weekly Editorial (index.json)
EDITORIAL_FILES = {
    "bks-hours":   CANDS_DIR / "bks-hours_best_pullover-hoodie.jpg",
    "bks-glyph":   CANDS_DIR / "bks-glyph_best_windbreaker-jacket.jpg",
    "bks-marker":  CANDS_DIR / "bks-marker_best_windbreaker-jacket.jpg",
    "bks-riviera": CANDS_DIR / "bks-riviera_best_windbreaker-jacket.jpg",
    "bks-pulse":   CANDS_DIR / "bks-pulse_best_windbreaker-jacket.jpg",
    "bks-token":   CANDS_DIR / "bks-token_best_windbreaker-jacket.jpg",
    "bks-flag":    CANDS_DIR / "bks-flag_best_windbreaker-jacket.jpg",
    "bks-origin":  CANDS_DIR / "bks-origin_best_windbreaker-jacket.jpg",
}


def gql(query: str, variables: dict | None = None) -> dict:
    payload: dict = {"query": query}
    if variables:
        payload["variables"] = variables
    r = requests.post(GQL_URL, headers=HDR_GQL, json=payload, timeout=30, verify=False)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(f"GQL errors: {data['errors']}")
    return data


def upload_image(src: Path, dest_name: str) -> str:
    """Upload to Shopify Files. Returns shopify://shop_images/dest_name."""
    file_size = src.stat().st_size
    mime = "image/png" if src.suffix.lower() == ".png" else "image/jpeg"

    q_stage = """
    mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
      stagedUploadsCreate(input: $input) {
        stagedTargets { url resourceUrl parameters { name value } }
        userErrors { field message }
      }
    }
    """
    result = gql(q_stage, {"input": [{
        "filename": dest_name, "mimeType": mime,
        "httpMethod": "POST", "resource": "FILE",
        "fileSize": str(file_size),
    }]})
    errs = result["data"]["stagedUploadsCreate"]["userErrors"]
    if errs:
        raise RuntimeError(f"stagedUploadsCreate: {errs}")
    target = result["data"]["stagedUploadsCreate"]["stagedTargets"][0]
    params = {p["name"]: p["value"] for p in target["parameters"]}

    with open(src, "rb") as f:
        r = requests.post(target["url"], data=params,
                          files={"file": (dest_name, f, mime)},
                          timeout=90, verify=False)
    if r.status_code not in (200, 201, 204):
        raise RuntimeError(f"Stage POST failed {r.status_code}: {r.text[:300]}")

    time.sleep(1)

    q_create = """
    mutation fileCreate($files: [FileCreateInput!]!) {
      fileCreate(files: $files) {
        files { __typename }
        userErrors { field message }
      }
    }
    """
    result2 = gql(q_create, {"files": [{
        "originalSource": target["resourceUrl"],
        "filename": dest_name, "contentType": "IMAGE",
        "alt": dest_name.replace("-", " ").replace(".jpg", "").replace(".png", ""),
    }]})
    errs2 = result2["data"]["fileCreate"]["userErrors"]
    if errs2:
        raise RuntimeError(f"fileCreate: {errs2}")

    return f"shopify://shop_images/{dest_name}"


def push_asset(key: str, content: str) -> bool:
    r = requests.put(f"{REST_BASE}/themes/{LIVE_THEME}/assets.json",
                     headers=HDR_REST,
                     json={"asset": {"key": key, "value": content}},
                     timeout=30, verify=False)
    return r.status_code in (200, 201)


# ─────────────────────────────────────────────────────────────────────────────
print("=" * 62)
print(f"BKS Setstyle Upload Pipeline (source: {source})")
print("=" * 62)

hero_cdn: dict[str, str] = {}
editorial_cdn: dict[str, str] = {}

# ── Upload setstyle heroes ────────────────────────────────────────────────────
print(f"\n[1/3] Uploading setstyle heroes from {source}/...\n")
for handle in COLLECTIONS:
    # Try .jpg first, then .png
    src = SETSTYLE_DIR / f"{handle}-hero.jpg"
    if not src.exists():
        src = SETSTYLE_DIR / f"{handle}-hero.png"
    if not src.exists():
        print(f"  SKIP {handle} — not found in {source}/")
        continue
    dest = f"{handle}-hero.jpg"
    print(f"  {dest} ({src.stat().st_size // 1024}KB)...", end=" ", flush=True)
    try:
        ref = upload_image(src, dest)
        hero_cdn[handle] = ref
        print("OK")
    except Exception as e:
        print(f"FAILED: {e}")

# ── Upload on-model editorial (Weekly Editorial) ──────────────────────────────
print(f"\n[2/3] Uploading on-model editorial images...\n")
for handle, src in EDITORIAL_FILES.items():
    if not src.exists():
        print(f"  SKIP {handle} editorial — not found")
        continue
    dest = f"{handle}-editorial.jpg"
    print(f"  {dest} ({src.stat().st_size // 1024}KB)...", end=" ", flush=True)
    try:
        ref = upload_image(src, dest)
        editorial_cdn[handle] = ref
        print("OK")
    except Exception as e:
        print(f"FAILED: {e}")

# ── Update + push templates ───────────────────────────────────────────────────
print(f"\n[3/3] Updating and pushing templates...\n")
changed: list[str] = []

for handle, ref in hero_cdn.items():
    tpl_path = TPLS / f"collection.{handle}.json"
    if not tpl_path.exists():
        continue
    tpl = json.loads(tpl_path.read_text(encoding="utf-8"))
    updated = False
    for sec in tpl.get("sections", {}).values():
        if "hero_image" in sec.get("settings", {}):
            sec["settings"]["hero_image"] = ref
            updated = True
    if updated:
        tpl_path.write_text(json.dumps(tpl, indent=2, ensure_ascii=False), encoding="utf-8")
        changed.append(f"templates/collection.{handle}.json")

# Update index.json Weekly Editorial
index_path = TPLS / "index.json"
if index_path.exists() and editorial_cdn:
    index = json.loads(index_path.read_text(encoding="utf-8"))
    old_map: dict[str, str] = {}
    for handle, ref in editorial_cdn.items():
        slug = handle.replace("bks-", "")
        old_map[f"bks-{slug}-editorial.png"] = ref
        old_map[f"bks-{slug}-editorial.jpg"] = ref
        if handle == "bks-token":
            old_map["bks-token-puffer.png"] = ref
    idx_changed = False
    for sec in index.get("sections", {}).values():
        for block in sec.get("blocks", {}).values():
            img = block.get("settings", {}).get("image", "")
            fname = img.split("/")[-1]
            if fname in old_map:
                block["settings"]["image"] = old_map[fname]
                idx_changed = True
    if idx_changed:
        index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
        changed.append("templates/index.json")

# Push all changed files
pushed = 0
for key in changed:
    path = ROOT / "04_TEMA_SHOPIFY" / key
    content = path.read_text(encoding="utf-8")
    print(f"  Pushing {key}...", end=" ", flush=True)
    if push_asset(key, content):
        print("OK")
        pushed += 1
    else:
        print("FAILED")
    time.sleep(0.3)

print(f"\n{'=' * 62}")
print(f"Heroes uploaded: {len(hero_cdn)}/8")
print(f"Editorial uploaded: {len(editorial_cdn)}/8")
print(f"Templates pushed: {pushed}/{len(changed)}")
if hero_cdn:
    print("\nVerify:")
    for h in list(hero_cdn.keys())[:3]:
        print(f"  https://bakabo.club/collections/{h}")
