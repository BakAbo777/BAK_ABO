"""Carica il video hero (Spot 2025.mp4) come Shopify File nativo via GraphQL,
poi aggiorna templates/index.json (sezione bks_hero) e pusha il tema live TM04.

Flusso: stagedUploadsCreate -> upload binario su URL staged -> fileCreate ->
poll fino a READY -> prendi GID -> scrivi hero_video nel template -> PUT assets.json.
"""
from __future__ import annotations
import os, sys, json, time, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()
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
GQL     = f"https://{DOMAIN}/admin/api/{VERSION}/graphql.json"
REST    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

VIDEO_PATH = Path(r"I:\BKS database\BKS_ORGANIZED_20260615_225737"
                   r"\22_VIDEO_GENERICI\_Senza_collezione\Generico\Spot 2025.mp4")
THEME_ID = "202392961362"
INDEX_JSON = ROOT / "04_TEMA_SHOPIFY" / "_merged_tm04" / "templates" / "index.json"


def gql(query: str, variables: dict) -> dict:
    r = requests.post(GQL, headers=HDR, json={"query": query, "variables": variables}, timeout=60, verify=False)
    r.raise_for_status()
    data = r.json()
    if data.get("errors"):
        raise RuntimeError(json.dumps(data["errors"], indent=2))
    return data["data"]


def staged_upload(filename: str, filesize: int) -> dict:
    q = """
    mutation($input: [StagedUploadInput!]!) {
      stagedUploadsCreate(input: $input) {
        stagedTargets { url resourceUrl parameters { name value } }
        userErrors { field message }
      }
    }"""
    variables = {"input": [{
        "resource": "VIDEO",
        "filename": filename,
        "mimeType": "video/mp4",
        "fileSize": str(filesize),
        "httpMethod": "POST",
    }]}
    data = gql(q, variables)
    res = data["stagedUploadsCreate"]
    if res["userErrors"]:
        raise RuntimeError(res["userErrors"])
    return res["stagedTargets"][0]


def upload_binary(target: dict, path: Path) -> str:
    form = {p["name"]: p["value"] for p in target["parameters"]}
    key = form.get("key")
    with path.open("rb") as f:
        files = {"file": (path.name, f, "video/mp4")}
        r = requests.post(target["url"], data=form, files=files, timeout=600, verify=False)
    if r.status_code not in (200, 201, 204):
        raise RuntimeError(f"Upload binario fallito [{r.status_code}]: {r.text[:400]}")
    return target["resourceUrl"]


def file_create(resource_url: str, alt: str) -> str:
    q = """
    mutation($files: [FileCreateInput!]!) {
      fileCreate(files: $files) {
        files { id fileStatus ... on Video { id } }
        userErrors { field message }
      }
    }"""
    variables = {"files": [{"originalSource": resource_url, "contentType": "VIDEO", "alt": alt}]}
    data = gql(q, variables)
    res = data["fileCreate"]
    if res["userErrors"]:
        raise RuntimeError(res["userErrors"])
    return res["files"][0]["id"]


def poll_ready(file_id: str, timeout: int = 180) -> None:
    q = """
    query($id: ID!) {
      node(id: $id) {
        ... on Video { id fileStatus }
      }
    }"""
    start = time.time()
    while time.time() - start < timeout:
        data = gql(q, {"id": file_id})
        status = data["node"]["fileStatus"]
        print(f"  fileStatus = {status}")
        if status == "READY":
            return
        if status == "FAILED":
            raise RuntimeError("Shopify ha segnato il file come FAILED")
        time.sleep(5)
    raise RuntimeError("Timeout in attesa che il video diventi READY")


def update_index_json(video_gid: str) -> None:
    data = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    sections = data["sections"]
    hero_key = None
    for key, sec in sections.items():
        if sec.get("type") == "bks-hero-video-image":
            hero_key = key
            break
    if not hero_key:
        raise RuntimeError("Sezione bks-hero-video-image non trovata in index.json")
    sections[hero_key]["settings"]["hero_video"] = video_gid
    INDEX_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  index.json aggiornato: sezione '{hero_key}'.hero_video = {video_gid}")


def push_template_to_live_theme() -> None:
    content = INDEX_JSON.read_text(encoding="utf-8")
    payload = {"asset": {"key": "templates/index.json", "value": content}}
    for attempt in range(5):
        r = requests.put(
            f"{REST}/themes/{THEME_ID}/assets.json",
            headers=HDR, json=payload, timeout=60, verify=False,
        )
        if r.status_code == 429:
            wait = float(r.headers.get("Retry-After", 2 ** attempt + 1))
            time.sleep(wait)
            continue
        r.raise_for_status()
        print(f"  Pushato su tema live {THEME_ID}: templates/index.json")
        return
    raise RuntimeError("Rate-limit retries esauriti nel push del tema")


def main():
    if not VIDEO_PATH.exists():
        raise SystemExit(f"Video non trovato: {VIDEO_PATH}")
    filesize = VIDEO_PATH.stat().st_size
    print(f"=== Upload hero video ===\nFile: {VIDEO_PATH.name}  ({filesize/1_048_576:.1f} MB)")

    print("\n[1/5] stagedUploadsCreate...")
    target = staged_upload(VIDEO_PATH.name, filesize)

    print("[2/5] Upload binario (puo' richiedere qualche minuto per ~100MB)...")
    resource_url = upload_binary(target, VIDEO_PATH)

    print("[3/5] fileCreate...")
    file_id = file_create(resource_url, "BakAbo / BKS — hero spot")
    print(f"  file id: {file_id}")

    print("[4/5] Attendo elaborazione Shopify (fileStatus -> READY)...")
    poll_ready(file_id)

    print("[5/5] Aggiorno template e pusho sul tema live...")
    update_index_json(file_id)
    push_template_to_live_theme()

    print(f"\n=== COMPLETATO ===\nhero_video = {file_id}")
    print(f"Editor: https://{DOMAIN}/admin/themes/{THEME_ID}/editor")


if __name__ == "__main__":
    main()
