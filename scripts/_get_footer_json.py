"""Dump full footer-group.json from live theme to find Italian sections."""
import os, requests, urllib3, json
urllib3.disable_warnings()  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

r = requests.get(f"{BASE}/themes/202392961362/assets.json?asset[key]=sections/footer-group.json",
                 headers=HDR, verify=False, timeout=20)
val = r.json().get("asset", {}).get("value", "")
try:
    data = json.loads(val)
    # Pretty print the relevant footer sections
    for k, v in data.get("sections", {}).items():
        settings = v.get("settings", {})
        blocks = v.get("blocks", {})
        for sk, sv in settings.items():
            if isinstance(sv, str) and any(x in sv for x in ["Normativa", "rimborsi", "Informativa", "BAKABO", "privacy"]):
                print(f"section[{k}].settings[{sk}] = {sv!r}")
        for bk, bv in blocks.items():
            for sk, sv in bv.get("settings", {}).items():
                if isinstance(sv, str) and any(x in sv for x in ["Normativa", "rimborsi", "Informativa", "BAKABO", "privacy"]):
                    print(f"section[{k}].blocks[{bk}].settings[{sk}] = {sv!r}")

    # Also dump top-level keys
    print("\n--- SECTION KEYS ---")
    for k, v in data.get("sections", {}).items():
        print(f"  {k}: type={v.get('type')} settings_keys={list(v.get('settings',{}).keys())[:6]}")
        for bk, bv in v.get("blocks", {}).items():
            btype = bv.get("type","")
            bsettings = {sk: sv for sk, sv in bv.get("settings",{}).items() if sk in ("heading","label","title","menu","menu_id","link","text")}
            if bsettings:
                print(f"    block[{bk}] type={btype} {bsettings}")
except Exception as e:
    print(f"Parse error: {e}")
    print(val[:2000])
