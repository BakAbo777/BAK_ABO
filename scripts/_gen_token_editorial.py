"""Genera immagine editoriale BKS Token (1536x1024) e carica su Shopify Files."""
import os, sys, time, base64, requests, urllib3
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

OPENAI_KEY = os.environ["OPENAI_API_KEY"]
DOMAIN     = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN      = os.environ["SHOPIFY_ADMIN_TOKEN"]
VER        = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
GQL        = f"https://{DOMAIN}/admin/api/{VER}/graphql.json"
HDR        = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

PROMPT = """BKS Token collection editorial scene — fashion photography.
A puffer jacket with deep purple all-over-print pattern of neon-edge geometric tiles and retro pixel grid lies displayed on satin metal surface. Smoked glass panels in background. Dark concrete architecture. Cool rim light traces neon violet edges on the garment. Warm amber back-light halo. Retro arcade digital atmosphere. Pixel-form abstract repeating pattern across the fabric surface. No faces, no people.
Shot style: Dean Cundey cinematography — Back to the Future, Tron. Magical wonder, retrowave glow, satin metal + dark cement + cool neon rim.
Horizontal editorial format. Pure product artistry. BKS Studio."""

OUT_PATH = ROOT / "output" / "site_images" / "bks-token-editorial.png"
FNAME    = "bks-token-editorial.png"

print("=== Generazione editoriale BKS Token ===\n")
print("Prompt:\n" + PROMPT[:200] + "...\n")

# 1. Generate with OpenAI
print("Generando immagine 1536x1024...")
r = requests.post(
    "https://api.openai.com/v1/images/generations",
    headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
    json={
        "model": "gpt-image-1",
        "prompt": PROMPT,
        "n": 1,
        "size": "1536x1024",
        "quality": "high",
        "output_format": "png",
    },
    timeout=120,
    verify=False,
)
if r.status_code != 200:
    print(f"ERR OpenAI: {r.status_code} {r.text[:300]}")
    sys.exit(1)

resp = r.json()
img_b64 = resp["data"][0].get("b64_json") or ""
img_url = resp["data"][0].get("url", "")

if img_b64:
    img_bytes = base64.b64decode(img_b64)
    OUT_PATH.write_bytes(img_bytes)
    print(f"OK — salvata in {OUT_PATH} ({len(img_bytes)//1024}KB)")
elif img_url:
    img_bytes = requests.get(img_url, timeout=30).content
    OUT_PATH.write_bytes(img_bytes)
    print(f"OK — salvata in {OUT_PATH} ({len(img_bytes)//1024}KB)")
else:
    print("ERR: nessuna immagine restituita"); sys.exit(1)

# 2. Stage upload
def gql_req(q, v=None):
    res = requests.post(GQL, headers=HDR, json={"query": q, "variables": v or {}}, timeout=30, verify=False)
    res.raise_for_status()
    return res.json()

print("\nUploading su Shopify Files...")
q1 = """mutation stagedUploadsCreate($input:[StagedUploadInput!]!) {
  stagedUploadsCreate(input:$input) {
    stagedTargets { url resourceUrl parameters { name value } }
    userErrors { field message }
  }
}"""
d1 = gql_req(q1, {"input": [{"filename": FNAME, "mimeType": "image/png", "httpMethod": "POST", "resource": "FILE"}]})
tgt = d1["data"]["stagedUploadsCreate"]["stagedTargets"][0]
upload_url   = tgt["url"]
resource_url = tgt["resourceUrl"]
params = {p["name"]: p["value"] for p in tgt["parameters"]}

with open(OUT_PATH, "rb") as f:
    r2 = requests.post(upload_url, data=params, files={"file": (FNAME, f, "image/png")}, timeout=60, verify=False)
print(f"Stage HTTP {r2.status_code}")
time.sleep(2)

# 3. Create file
q2 = """mutation fileCreate($files:[FileCreateInput!]!) {
  fileCreate(files:$files) {
    files { id fileStatus ... on MediaImage { image { url } } }
    userErrors { field message }
  }
}"""
d2 = gql_req(q2, {"files": [{"originalSource": resource_url, "filename": FNAME, "contentType": "IMAGE"}]})
pay = d2["data"]["fileCreate"]
if pay.get("userErrors"): print("ERR create:", pay["userErrors"]); sys.exit(1)
fid = pay["files"][0]["id"]
print(f"File ID: {fid}")

# 4. Poll
q3 = """query getFile($id:ID!) { node(id:$id) { ... on MediaImage { id fileStatus image { url } } } }"""
cdn_url = ""
for i in range(20):
    time.sleep(3)
    node = gql_req(q3, {"id": fid})["data"]["node"] or {}
    status = node.get("fileStatus", "")
    print(f"  [{i+1}] {status}")
    if status == "READY":
        cdn_url = node.get("image", {}).get("url", "")
        print(f"\nCDN URL: {cdn_url}")
        break
    if status == "FAILED":
        print("FAILED"); sys.exit(1)

if cdn_url:
    print(f"\n✓ bks-token-editorial.png caricata su Shopify Files")
    print("Prossimo passo: aggiornare index.json da bks-token-puffer.png → bks-token-editorial.png")
