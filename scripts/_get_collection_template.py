"""Get live theme collection templates to find NORMATIVA section."""
import os, requests, urllib3, json
urllib3.disable_warnings()  # type: ignore
from pathlib import Path
for raw in (Path("I:/BAK ABO/.env").read_text(encoding="utf-8")).splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ: os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN","")
HDR    = {"X-Shopify-Access-Token": TOKEN}

# Get the collection.bks-origin template
for key in [
    "templates/collection.bks-origin.json",
    "templates/collection.json",
]:
    r = requests.get(
        f"https://{DOMAIN}/admin/api/2025-01/themes/202392961362/assets.json?asset[key]={key}",
        headers=HDR, verify=False, timeout=20)
    val = r.json().get("asset", {}).get("value", "")
    if not val:
        print(f"{key}: NOT FOUND")
        continue
    data = json.loads(val)
    print(f"\n=== {key} ===")
    sections = data.get("sections", {})
    order = data.get("order", [])
    print(f"Sections order: {order}")
    for sid in order:
        s = sections.get(sid, {})
        stype = s.get("type","?")
        ssettings = s.get("settings", {})
        # Look for Italian text in settings
        it_items = {k: v for k, v in ssettings.items() if isinstance(v, str) and any(x in v.lower() for x in ["normativa", "informativa", "rimborsi", "privacy", "assistenza", "bakabo"])}
        print(f"  [{sid}] type={stype}")
        if it_items:
            for k, v in it_items.items():
                print(f"    ITALIAN: settings[{k}] = {v!r}")
