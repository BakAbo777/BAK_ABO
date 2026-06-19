"""Push: English-only language fix — it.json override + custom section strings."""
import os, sys, requests, urllib3, time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
VER    = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
THEME  = "202392961362"
BASE   = f"https://{DOMAIN}/admin/api/{VER}"
HDR    = {"X-Shopify-Access-Token": TOKEN}
MERGED = ROOT / "04_TEMA_SHOPIFY" / "_merged_tm04"

FILES = [
    ("locales/it.json",                              MERGED / "locales"   / "it.json"),
    ("assets/bks-member.js",                         MERGED / "assets"    / "bks-member.js"),
    ("sections/bks-members-entry.liquid",            MERGED / "sections"  / "bks-members-entry.liquid"),
    ("sections/bks-member-dashboard.liquid",         MERGED / "sections"  / "bks-member-dashboard.liquid"),
]

print("=== Push language fix (English-only) ===\n")
ok = err = 0
for key, path in FILES:
    body = path.read_text(encoding="utf-8")
    r = requests.put(f"{BASE}/themes/{THEME}/assets.json",
        json={"asset": {"key": key, "value": body}},
        headers=HDR, timeout=30, verify=False)
    status = "OK " if r.status_code in (200, 201) else "ERR"
    print(f"  {status}  HTTP {r.status_code}  {key}")
    if r.status_code not in (200, 201):
        print(f"         {r.text[:300]}")
        err += 1
    else:
        ok += 1
    time.sleep(0.5)

print(f"\nFine: {ok} OK, {err} errori")
