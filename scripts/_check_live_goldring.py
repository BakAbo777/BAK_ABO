"""Confronta file locali vs live theme per member area — gold ring + header."""
import os, requests, urllib3
from pathlib import Path
urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, _, v = line.partition("=")
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v
SH_DOM = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
SH_TOK = os.environ["SHOPIFY_ADMIN_TOKEN"]
SH_HDR = {"X-Shopify-Access-Token": SH_TOK}
THEME  = "202392961362"
BASE   = f"https://{SH_DOM}/admin/api/2025-01"

def get_live(key):
    r = requests.get(f"{BASE}/themes/{THEME}/assets.json",
        headers=SH_HDR, params={"asset[key]": key}, verify=False)
    if r.status_code == 200:
        return r.json().get("asset", {}).get("value", "")
    return None

CHECK_KEYS = [
    ("snippets/bakabo-header.liquid", "04_TEMA_SHOPIFY/snippets/bakabo-header.liquid"),
    ("assets/bks-member.css",         "04_TEMA_SHOPIFY/assets/bks-member.css"),
    ("assets/bks-member.js",          "04_TEMA_SHOPIFY/assets/bks-member.js"),
    ("sections/bks-member-dashboard.liquid", "04_TEMA_SHOPIFY/sections/bks-member-dashboard.liquid"),
]

RING_MARKERS = ["bks-member-halo", "bks-ring-pulse", "bks-ring-spin", "bks-arrival", "bks-member-avatar"]
WISHLIST_MARKERS = ["bks-wl-toast", "wlToggle", "wishlist"]
TIER_MARKERS = ["orders_count", "bks_tier", "data-tier"]

print("CONFRONTO LOCAL vs LIVE THEME\n")
needs_push = []

for (shopify_key, local_path) in CHECK_KEYS:
    local_file = ROOT / local_path
    local = local_file.read_text(encoding="utf-8") if local_file.exists() else ""
    live  = get_live(shopify_key) or ""

    local_size = len(local)
    live_size  = len(live)
    same = (local.strip() == live.strip())

    print(f"{'=' * 55}")
    print(f"FILE: {shopify_key}")
    print(f"  Local: {local_size:,} chars | Live: {live_size:,} chars | {'SAME' if same else 'DIFFERENT'}")

    for markers, label in [(RING_MARKERS, "Gold Ring"), (WISHLIST_MARKERS, "Wishlist"),
                            (TIER_MARKERS, "Tier Detection")]:
        local_has = [m for m in markers if m in local]
        live_has  = [m for m in markers if m in live]
        if local_has != live_has:
            print(f"  !! {label}: local={local_has} | live={live_has}")
        else:
            present = local_has if local_has else "absent"
            print(f"  OK {label}: {present}")

    if not same:
        needs_push.append(shopify_key)

print(f"\n{'=' * 55}")
if needs_push:
    print(f"FILE DA PUSHARE ({len(needs_push)}):")
    for k in needs_push:
        print(f"  {k}")
else:
    print("Tutti i file sono sincronizzati con il live theme.")
