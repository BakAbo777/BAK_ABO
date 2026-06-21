"""Check live theme footer section to find which menu handle is used."""
import os, requests, urllib3, sys, json as jsonlib
urllib3.disable_warnings()  # type: ignore
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
from pathlib import Path
for raw in Path("I:/BAK ABO/.env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ:
            os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"
TID    = 202392961362

for key in ["sections/footer.liquid", "config/settings_data.json"]:
    r = requests.get(
        f"{BASE}/themes/{TID}/assets.json?asset[key]={key}",
        headers=HDR, verify=False, timeout=20)
    val = r.json().get("asset", {}).get("value", "") or ""
    print(f"\n=== {key} ({len(val)} chars) ===")
    if key.endswith(".json"):
        try:
            data = jsonlib.loads(val)
            current = data.get("current", {})
            sections = current.get("sections", {})
            for sid, sec in sections.items():
                if "footer" in sid.lower() or "footer" in str(sec.get("type","")).lower():
                    print(f"  Section [{sid}] type={sec.get('type')}")
                    settings = sec.get("settings", {})
                    for k2, v2 in settings.items():
                        if "menu" in k2.lower() or "link" in k2.lower() or "nav" in k2.lower():
                            print(f"    {k2}: {v2}")
        except Exception as e:
            print(f"  parse error: {e}")
    else:
        for i, line in enumerate(val.splitlines(), 1):
            if any(x in line.lower() for x in ["linklist", "menu", "handle", "support", "policy", "linklists"]):
                stripped = line.strip()
                if len(stripped) > 5:
                    print(f"  L{i:4}: {stripped[:120]}")
