"""Push updated bakabo-business.json as catalog_snapshot to Worker KV."""
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

CF_TOKEN    = os.environ["CLOUDFLARE_API_TOKEN"]
ACCOUNT_ID  = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "e796d289f744035eee2641e853d8a5af")
NAMESPACE   = os.environ.get("KV_NAMESPACE_ID", "8f6b1e4accae47949b2960735d270a3a")
HDR = {"Authorization": f"Bearer {CF_TOKEN}"}

business = json.loads((ROOT / "BKS_SKILL/business/bakabo-business.json").read_text(encoding="utf-8"))

snapshot = {
    "as_of": business["system_status"]["as_of"],
    "last_session_fixes": business["system_status"]["last_session_fixes"],
    "store": business["system_status"]["store"],
    "channels": business["system_status"]["channels"],
    "infrastructure": business["system_status"]["infrastructure"],
    "current_priority": business["system_status"]["current_priority"],
    "brand": business.get("brand_positioning", {}).get("tier", "contemporary_premium"),
    "member_tiers": {
        "lead":   {"orders": 0,  "symbol": "◎"},
        "iron":   {"orders": "1-2",  "symbol": "⬡"},
        "brass":  {"orders": "3-5",  "symbol": "◈"},
        "silver": {"orders": "6-10", "symbol": "◇"},
        "gold":   {"orders": "11+",  "symbol": "✦"}
    },
    "session_fixes_26jun": [
        "wishlist hearts: double-listener bug fixed",
        "tier detection: tags first (bks_tier_gold > order count)",
        "header: account icon → /pages/bks-members when logged in",
        "header: Google OAuth button removed (broken with Shopify new accounts)",
        "GMC: excluded_destination set on 115 products",
        "iOS try-on: Safari download → new tab",
        "login DNS: account.bakabo.club → DNS only",
        "bks.member_tier metafield=gold set on Roberto",
    ]
}

url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/storage/kv/namespaces/{NAMESPACE}/values/catalog_snapshot"
r = requests.put(url, headers=HDR, data=json.dumps(snapshot, ensure_ascii=False), timeout=20, verify=False)
print(f"catalog_snapshot: {r.status_code}")
if r.status_code not in (200, 201):
    print(f"  ERR: {r.text[:200]}")

# Also update system_state key
r2 = requests.put(
    f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/storage/kv/namespaces/{NAMESPACE}/values/system_state",
    headers=HDR, data=json.dumps({"updated": "2026-06-26", "status": "all_fixes_applied"}, ensure_ascii=False), timeout=15, verify=False
)
print(f"system_state:     {r2.status_code}")
