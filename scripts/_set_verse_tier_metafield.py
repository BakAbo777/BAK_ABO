"""Set bks.member_tier metafield on Roberto's account for Verse eligibility."""
import os, requests, urllib3
from pathlib import Path
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"
CID    = "9137173365074"

r = requests.post(
    f"{BASE}/customers/{CID}/metafields.json",
    json={"metafield": {
        "namespace": "bks",
        "key": "member_tier",
        "value": "gold",
        "type": "single_line_text_field"
    }},
    headers=HDR, verify=False, timeout=15
)
print(f"Status: {r.status_code}")
data = r.json()
if r.status_code in (200, 201):
    mf = data.get("metafield", {})
    print(f"OK — bks.member_tier = {mf.get('value')} (id:{mf.get('id')})")
else:
    # Might already exist — try to find and update
    if "already" in str(data) or r.status_code == 422:
        r2 = requests.get(
            f"{BASE}/customers/{CID}/metafields.json?namespace=bks&key=member_tier",
            headers=HDR, verify=False, timeout=15
        )
        existing = r2.json().get("metafields", [])
        if existing:
            mid = existing[0]["id"]
            r3 = requests.put(
                f"{BASE}/customers/{CID}/metafields/{mid}.json",
                json={"metafield": {"id": mid, "value": "gold", "type": "single_line_text_field"}},
                headers=HDR, verify=False, timeout=15
            )
            print(f"Updated: {r3.status_code} — value={r3.json().get('metafield',{}).get('value')}")
    else:
        print(data)
