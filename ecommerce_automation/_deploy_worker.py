"""Deploy Cloudflare Worker via REST API (bypasses wrangler SSL issues)."""
import sys
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

account_id = env["CLOUDFLARE_ACCOUNT_ID"]
api_token = env["CLOUDFLARE_API_TOKEN"]
script_name = "bks-agent"
worker_file = ROOT / "cloudflare" / "bks-ai-worker.js"

script_content = worker_file.read_text(encoding="utf-8")

url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/scripts/{script_name}"
headers = {"Authorization": f"Bearer {api_token}"}

resp = requests.put(
    url,
    headers=headers,
    files={
        "metadata": (None, '{"main_module":"worker.js","bindings":[{"type":"kv_namespace","name":"BKS_AGENT_KV","namespace_id":"8f6b1e4accae47949b2960735d270a3a"},{"type":"ai","name":"AI"}],"compatibility_date":"2025-01-01","compatibility_flags":["nodejs_compat"]}', "application/json"),
        "worker.js": ("worker.js", script_content, "application/javascript+module"),
    },
    verify=False,
    timeout=60,
)

data = resp.json()
if data.get("success"):
    print(f"OK: Worker '{script_name}' deployed successfully")
else:
    print(f"ERROR: {data.get('errors')}")
