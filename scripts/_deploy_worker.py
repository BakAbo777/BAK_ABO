"""Deploy bks-ai-worker.js to Cloudflare (KV + secrets already configured)."""
import os, json, requests, urllib3, warnings
from pathlib import Path

warnings.filterwarnings("ignore")
urllib3.disable_warnings()  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")

TOKEN      = env.get("CLOUDFLARE_API_TOKEN", "")
ACCOUNT_ID = "e796d289f744035eee2641e853d8a5af"
SCRIPT     = "bks-agent"
KV_ID      = "8f6b1e4accae47949b2960735d270a3a"

if not TOKEN:
    raise SystemExit("CLOUDFLARE_API_TOKEN not found in .env")

js = (ROOT / "cloudflare/bks-ai-worker.js").read_text(encoding="utf-8")

metadata = {
    "main_module": "bks-ai-worker.js",
    "bindings": [{"type": "kv_namespace", "name": "BKS_AGENT_KV", "namespace_id": KV_ID}],
    "compatibility_date": "2025-01-01",
    "compatibility_flags": ["nodejs_compat"],
}

files = {
    "metadata":          ("metadata.json", json.dumps(metadata), "application/json"),
    "bks-ai-worker.js":  ("bks-ai-worker.js", js, "application/javascript+module"),
}
r = requests.put(
    f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/workers/scripts/{SCRIPT}",
    headers={"Authorization": f"Bearer {TOKEN}"},
    files=files,
    verify=False,
)
data = r.json()
if data.get("success"):
    print(f"OK — Worker deployed: https://bks-agent.bakabo.workers.dev ({len(js):,} chars)")
else:
    print(f"ERR: {data.get('errors')}")
