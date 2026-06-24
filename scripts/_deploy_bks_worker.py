"""
Deploy bks-agent Worker v7 via Cloudflare REST API.
Imposta anche i segreti PRINTIFY_API_TOKEN e PRINTIFY_SHOP_ID.
Bypass wrangler (problemi VPN/proxy).
"""
import os, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

CF_ACCOUNT    = "e796d289f744035eee2641e853d8a5af"
CF_TOKEN      = env.get("CLOUDFLARE_API_TOKEN", "")
WORKER_NAME   = "bks-agent"
WORKER_JS     = ROOT / "cloudflare" / "bks-ai-worker.js"

CF_HDR = {"Authorization": f"Bearer {CF_TOKEN}"}

if not CF_TOKEN:
    print("ERRORE: CLOUDFLARE_API_TOKEN non trovato nel .env")
    raise SystemExit(1)


def cf_put_secret(name: str, value: str) -> None:
    r = requests.put(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/workers/scripts/{WORKER_NAME}/secrets",
        headers={**CF_HDR, "Content-Type": "application/json"},
        json={"name": name, "text": value, "type": "secret_text"},
        timeout=20, verify=False,
    )
    r.raise_for_status()
    print(f"  Secret {name}: OK")


def deploy_worker() -> None:
    js_code = WORKER_JS.read_text(encoding="utf-8")
    import io
    metadata = {
        "main_module": "worker.js",
        "bindings": [
            {"type": "kv_namespace", "name": "BKS_AGENT_KV", "namespace_id": "8f6b1e4accae47949b2960735d270a3a"},
            {"type": "ai", "name": "AI"},
        ],
    }
    import json as _json
    files = {
        "metadata": (None, _json.dumps(metadata), "application/json"),
        "worker.js": ("worker.js", js_code.encode(), "application/javascript+module"),
    }
    r = requests.put(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/workers/scripts/{WORKER_NAME}",
        headers=CF_HDR,
        files=files,
        timeout=60, verify=False,
    )
    if r.ok:
        data = r.json()
        etag = data.get("result", {}).get("etag", "?")
        print(f"  Worker deployato: etag={etag}")
    else:
        print(f"  ERRORE deploy: {r.status_code} {r.text[:300]}")
        r.raise_for_status()


print("=== BKS Worker v9 — Deploy + Secrets ===\n")

print("1. Imposto segreti Printify...")
cf_put_secret("PRINTIFY_API_TOKEN", env.get("PRINTIFY_API_TOKEN", ""))
cf_put_secret("PRINTIFY_SHOP_ID",   env.get("PRINTIFY_SHOP_ID", "12030061"))

print("\n2. Deploy worker JS...")
deploy_worker()

print("\n=== COMPLETATO ===")
print(f"Worker: https://bks-agent.bakabo.workers.dev")
print("Endpoint:")
print("  POST /design-generate  -- pipeline autonoma: Printify->OpenAI->upload->update")
print('    Body: {"product_id":"...", "collection":"pulse", "design_description":"...", "dry_run":false}')
print("  POST /printify-update  — aggiorna design da URL esterno")
print("  POST /generate-prompt  — genera prompt stile BakAbo")
print("  POST /style-learn      — feedback apprendimento")
print("  GET  /style?collection=X — DNA visivo + feedback count")
print('  Auth: Authorization: Bearer <BKS_AI_TOKEN>')
