"""Add Google Search Console TXT verification record to Cloudflare DNS."""
import os, requests, urllib3, sys
urllib3.disable_warnings()  # type: ignore
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
from pathlib import Path

for raw in Path("I:/BAK ABO/.env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ:
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

TOKEN   = os.environ["CLOUDFLARE_API_TOKEN"]
ZONE_NAME = os.environ.get("CLOUDFLARE_ZONE_NAME", "bakabo.club")
HDR = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

GSC_TXT = "google-site-verification=IF-bz0nymn7wvFvneTUr9q3bJxZmnduZGh68FWchmEU"

# 1. Get Zone ID
r = requests.get("https://api.cloudflare.com/client/v4/zones",
                 headers=HDR, params={"name": ZONE_NAME}, verify=False, timeout=20)
zones = r.json().get("result", [])
if not zones:
    print(f"ERROR: Zone '{ZONE_NAME}' not found. Response: {r.text[:200]}")
    sys.exit(1)
zone_id = zones[0]["id"]
print(f"Zone: {ZONE_NAME} (id={zone_id})")

# 2. Check if record already exists
r2 = requests.get(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
                  headers=HDR, params={"type": "TXT", "name": ZONE_NAME}, verify=False, timeout=20)
existing = r2.json().get("result", [])
for rec in existing:
    if "google-site-verification" in rec.get("content", ""):
        print(f"Record already exists: {rec['content']}")
        sys.exit(0)

# 3. Add record
payload = {
    "type": "TXT",
    "name": "@",
    "content": GSC_TXT,
    "ttl": 1,      # 1 = auto
    "proxied": False
}
r3 = requests.post(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
                   headers=HDR, json=payload, verify=False, timeout=20)
if r3.ok:
    rec = r3.json().get("result", {})
    print(f"SUCCESS: TXT record added")
    print(f"  name: {rec.get('name')}")
    print(f"  content: {rec.get('content')}")
    print(f"  id: {rec.get('id')}")
else:
    print(f"ERROR {r3.status_code}: {r3.text[:300]}")
