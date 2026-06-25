"""Copy OPENAI_API_KEY from .env to Cloudflare Worker secret."""
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

CF_TOKEN     = os.environ.get("CLOUDFLARE_API_TOKEN", "")
OPENAI_KEY   = os.environ.get("OPENAI_API_KEY", "")
ACCOUNT_ID   = "e796d289f744035eee2641e853d8a5af"
SCRIPT_NAME  = "bks-agent"

if not CF_TOKEN:
    print("ERROR: CLOUDFLARE_API_TOKEN not in .env"); exit(1)
if not OPENAI_KEY:
    print("ERROR: OPENAI_API_KEY not in .env"); exit(1)

print(f"Key found: {OPENAI_KEY[:8]}...{OPENAI_KEY[-4:]}")

url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/workers/scripts/{SCRIPT_NAME}/secrets"
r = requests.put(
    url,
    json={"name": "OPENAI_API_KEY", "text": OPENAI_KEY, "type": "secret_text"},
    headers={"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"},
    verify=False, timeout=15
)
print(f"Status: {r.status_code}")
data = r.json()
if data.get("success"):
    print(f"OK — secret updated: {data['result'].get('name')}")
else:
    print(f"Error: {data.get('errors')}")
