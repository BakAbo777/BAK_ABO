"""Replace 8 collection hero images in Shopify theme.

Strategy:
  - collection.bks-XXX.json hero_image  → product-only flat shots (no human model)
  - index.json Weekly Editorial images  → on-model windbreaker shots (editorial)

Pipeline:
  1. Upload all images to Shopify Files via GraphQL stagedUploadsCreate
  2. Update collection templates (hero_image)
  3. Update index.json Weekly Editorial blocks
  4. Push all changed templates to live theme (202392961362)
"""
from __future__ import annotations
import os, json, time
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

BKSHERO  = ROOT / "output" / "catalog_images" / "bks_hero"
CANDS    = ROOT / "output" / "catalog_images" / "hero_candidates"
TPLS     = ROOT / "04_TEMA_SHOPIFY" / "templates"

# ── PRODUCT-ONLY heroes for collection templates ─────────────────────────────
# format: handle → (folder_in_bks_hero, filename_in_folder, shopify_dest_name)
COLLECTION_HEROES = {
    "bks-hours":   (BKSHERO / "bks-hours-walker-swim-trunks",     "bks-hours-walker-swim-trunks_hero.png",    "bks-hours-hero.png"),
    "bks-glyph":   (BKSHERO / "bks-glyph-cross-puffer",           "bks-glyph-cross-puffer_hero.png",          "bks-glyph-hero.png"),
    "bks-marker":  (BKSHERO / "bks-marker-hybrid-sneakers",        "bks-marker-hybrid-sneakers_hero.png",      "bks-marker-hero.png"),
    "bks-riviera": (BKSHERO / "bks-riviera-argyle-sneakers",       "bks-riviera-argyle-sneakers_hero.png",     "bks-riviera-hero.png"),
    "bks-pulse":   (BKSHERO / "bks-pulse-wave-sneakers",           "bks-pulse-wave-sneakers_hero.png",         "bks-pulse-hero.png"),
    "bks-token":   (BKSHERO / "bks-token-vault-windbreaker",       "bks-token-vault-windbreaker_hero.png",     "bks-token-hero.png"),
    "bks-flag":    (BKSHERO / "bks-flag-arc-sneakers",             "bks-flag-arc-sneakers_hero.png",           "bks-flag-hero.png"),
    "bks-origin":  (BKSHERO / "folklore-field-windbreaker",        "folklore-field-windbreaker_hero.png",      "bks-origin-hero.png"),
}

# ── ON-MODEL shots for Weekly Editorial section (index.json) ─────────────────
EDITORIAL_IMAGES = {
    "bks-hours":   (CANDS / "bks-hours_best_pullover-hoodie.jpg",      "bks-hours-editorial.jpg"),
    "bks-glyph":   (CANDS / "bks-glyph_best_windbreaker-jacket.jpg",   "bks-glyph-editorial.jpg"),
    "bks-marker":  (CANDS / "bks-marker_best_windbreaker-jacket.jpg",  "bks-marker-editorial.jpg"),
    "bks-riviera": (CANDS / "bks-riviera_best_windbreaker-jacket.jpg", "bks-riviera-editorial.jpg"),
    "bks-pulse":   (CANDS / "bks-pulse_best_windbreaker-jacket.jpg",   "bks-pulse-editorial.jpg"),
    "bks-token":   (CANDS / "bks-token_best_windbreaker-jacket.jpg",   "bks-token-editorial.jpg"),
    "bks-flag":    (CANDS / "bks-flag_best_windbreaker-jacket.jpg",    "bks-flag-editorial.jpg"),
    "bks-origin":  (CANDS / "bks-origin_best_windbreaker-jacket.jpg",  "bks-origin-editorial.jpg"),
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


def upload_image(src_path: Path, dest_name: str) -> str:
    """Upload image to Shopify Files. Returns shopify://shop_images/dest_name."""
    file_size = src_path.stat().st_size
    mime = "image/png" if src_path.suffix.lower() == ".png" else "image/jpeg"

    # 1. Get staged upload URL
    q_stage = """
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
    vars_stage = {"input": [{
        "filename": dest_name,
        "mimeType": mime,
        "httpMethod": "POST",
        "resource": "FILE",
        "fileSize": str(file_size),
    }]}
    result = gql(q_stage, vars_stage)
    errs = result["data"]["stagedUploadsCreate"]["userErrors"]
    if errs:
        raise RuntimeError(f"stagedUploadsCreate errors: {errs}")
    target = result["data"]["stagedUploadsCreate"]["stagedTargets"][0]

    # 2. POST to staged URL
    params = {p["name"]: p["value"] for p in target["parameters"]}
    with open(src_path, "rb") as f:
        r = requests.post(target["url"], data=params,
                          files={"file": (dest_name, f, mime)},
                          timeout=60, verify=False)
    if r.status_code not in (200, 201, 204):
        raise RuntimeError(f"Stage POST failed {r.status_code}: {r.text[:300]}")

    resource_url = target["resourceUrl"]
    time.sleep(1)

    # 3. Finalize in Shopify Files
    q_create = """
    mutation fileCreate($files: [FileCreateInput!]!) {
      fileCreate(files: $files) {
        files { __typename }
        userErrors { field message }
      }
    }
    """
    vars_create = {"files": [{
        "originalSource": resource_url,
        "filename": dest_name,
        "contentType": "IMAGE",
        "alt": dest_name.replace("-", " ").replace(".png", "").replace(".jpg", ""),
    }]}
    result2 = gql(q_create, vars_create)
    errs2 = result2["data"]["fileCreate"]["userErrors"]
    if errs2:
        raise RuntimeError(f"fileCreate errors: {errs2}")

    return f"shopify://shop_images/{dest_name}"


def push_asset(key: str, content: str) -> bool:
    r = requests.put(
        f"{REST_BASE}/themes/{LIVE_THEME}/assets.json",
        headers=HDR_REST,
        json={"asset": {"key": key, "value": content}},
        timeout=30, verify=False,
    )
    if r.status_code in (200, 201):
        return True
    print(f"  ERROR {key}: {r.status_code} {r.text[:200]}")
    return False


# ─────────────────────────────────────────────────────────────────────────────
print("=" * 62)
print("BKS Hero Image Replace Pipeline")
print("=" * 62)

hero_cdn: dict[str, str] = {}     # handle → shopify://shop_images/bks-X-hero.png
editorial_cdn: dict[str, str] = {}  # handle → shopify://shop_images/bks-X-editorial.jpg

# ── STEP 1a: Upload product-only heroes ──────────────────────────────────────
print("\n[1a] Uploading product-only hero images...\n")
for handle, (folder, fname, dest) in COLLECTION_HEROES.items():
    src = folder / fname
    if not src.exists():
        print(f"  SKIP {handle} — not found: {src}")
        continue
    print(f"  {dest} ({src.stat().st_size // 1024}KB)...", end=" ", flush=True)
    try:
        ref = upload_image(src, dest)
        hero_cdn[handle] = ref
        print("OK")
    except Exception as e:
        print(f"FAILED: {e}")

# ── STEP 1b: Upload on-model editorial images ─────────────────────────────────
print(f"\n[1b] Uploading on-model editorial images...\n")
for handle, (src, dest) in EDITORIAL_IMAGES.items():
    if not src.exists():
        print(f"  SKIP {handle} — not found: {src}")
        continue
    print(f"  {dest} ({src.stat().st_size // 1024}KB)...", end=" ", flush=True)
    try:
        ref = upload_image(src, dest)
        editorial_cdn[handle] = ref
        print("OK")
    except Exception as e:
        print(f"FAILED: {e}")

print(f"\n  Heroes: {len(hero_cdn)}/8  |  Editorial: {len(editorial_cdn)}/8")

# ── STEP 2: Update collection templates ──────────────────────────────────────
print("\n[2] Updating collection templates...\n")
changed_files: list[str] = []

for handle, ref in hero_cdn.items():
    tpl_path = TPLS / f"collection.{handle}.json"
    if not tpl_path.exists():
        print(f"  SKIP {handle} — template missing")
        continue
    tpl = json.loads(tpl_path.read_text(encoding="utf-8"))
    changed = False
    for sec in tpl.get("sections", {}).values():
        if "hero_image" in sec.get("settings", {}):
            old = sec["settings"]["hero_image"]
            sec["settings"]["hero_image"] = ref
            print(f"  {handle}: {old.split('/')[-1]} → {ref.split('/')[-1]}")
            changed = True
    if changed:
        tpl_path.write_text(json.dumps(tpl, indent=2, ensure_ascii=False), encoding="utf-8")
        changed_files.append(f"templates/collection.{handle}.json")

# ── STEP 3: Update index.json Weekly Editorial ────────────────────────────────
print("\n[3] Updating index.json Weekly Editorial...\n")
index_path = TPLS / "index.json"
if index_path.exists() and editorial_cdn:
    index = json.loads(index_path.read_text(encoding="utf-8"))
    idx_changed = False

    # Map old editorial filenames to new
    old_to_new: dict[str, str] = {}
    for handle, ref in editorial_cdn.items():
        slug = handle.replace("bks-", "")
        # Match any shopify://shop_images/bks-{slug}-* pattern
        old_to_new[f"bks-{slug}-editorial.png"] = ref
        old_to_new[f"bks-{slug}-editorial.jpg"] = ref
        if handle == "bks-token":
            old_to_new["bks-token-puffer.png"] = ref

    for sec in index.get("sections", {}).values():
        for block in sec.get("blocks", {}).values():
            settings = block.get("settings", {})
            img = settings.get("image", "")
            fname = img.split("/")[-1]
            if fname in old_to_new:
                settings["image"] = old_to_new[fname]
                print(f"  {fname} → {old_to_new[fname].split('/')[-1]}")
                idx_changed = True

    if idx_changed:
        index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
        changed_files.append("templates/index.json")

# ── STEP 4: Push to live theme ────────────────────────────────────────────────
print(f"\n[4] Pushing {len(changed_files)} files to theme {LIVE_THEME}...\n")
pushed = 0
for key in changed_files:
    path = ROOT / "04_TEMA_SHOPIFY" / key
    content = path.read_text(encoding="utf-8")
    print(f"  {key}...", end=" ", flush=True)
    if push_asset(key, content):
        print("OK")
        pushed += 1
    time.sleep(0.3)

print(f"\n{'=' * 62}")
print(f"Done: {pushed}/{len(changed_files)} templates pushed")
print(f"Hero CDN entries: {', '.join(f'{h}={r.split(chr(47))[-1]}' for h, r in hero_cdn.items())}")
print("\nVerify live:")
for h in hero_cdn:
    print(f"  https://bakabo.club/collections/{h}")
