"""Write Roberto's Gold profile directly to Worker KV via Cloudflare REST API."""
import os, json, requests, urllib3
from pathlib import Path
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

CF_TOKEN      = os.environ.get("CLOUDFLARE_API_TOKEN", "")
ACCOUNT_ID    = "e796d289f744035eee2641e853d8a5af"
NAMESPACE_ID  = "8f6b1e4accae47949b2960735d270a3a"
KEY           = "customer:9137173365074:profile"

if not CF_TOKEN:
    print("ERROR: CLOUDFLARE_API_TOKEN not found in .env")
    exit(1)

profile = {
    "tier": "gold",
    "email": "bakabofirm@gmail.com",
    "name": "Roberto",
    "role": "bks_studio_admin",
    "preferences": {
        "language": "it",
        "access_level": "full",
        "try_on": True,
        "verse": True,
        "archive": True,
        "ai_shopper": True
    },
    "interaction_count": 0,
    "last_seen": None
}

url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/storage/kv/namespaces/{NAMESPACE_ID}/values/{KEY}"
r = requests.put(
    url,
    data=json.dumps(profile),
    headers={"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"},
    verify=False, timeout=15
)
print(f"Status: {r.status_code}")
print(r.json())
