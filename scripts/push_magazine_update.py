"""Push magazine-flow update: product grid section + footer-group."""
import os, requests, urllib3, sys, time
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
    ("sections/main-collection-product-grid.liquid", MERGED / "sections" / "main-collection-product-grid.liquid"),
    ("sections/footer-group.json",                   MERGED / "sections" / "footer-group.json"),
    ("sections/footer.liquid",                       MERGED / "sections" / "footer.liquid"),
    # Product system — kicker/label contrast fix (armocromista pass 2026-06-18)
    ("sections/bks-product-system.liquid",           MERGED / "sections" / "bks-product-system.liquid"),
    # Product meta — contrast fixes: kicker/cell span/p on amber bg (armocromista pass 2026-06-18)
    ("sections/bks-product-meta.liquid",             MERGED / "sections" / "bks-product-meta.liquid"),
    # Theme layout — bks-responsive.css added
    ("layout/theme.liquid",                          MERGED / "layout" / "theme.liquid"),
    # Responsive + contrast system
    ("assets/bks-responsive.css",                    ROOT / "04_TEMA_SHOPIFY" / "assets" / "bks-responsive.css"),
    # Collection signal — chip/typo-label accent text fixed (armocromista pass 2)
    ("sections/bks-collection-signal.liquid",        MERGED / "sections" / "bks-collection-signal.liquid"),
]

print("=== Push magazine update ===\n")
for key, path in FILES:
    body = path.read_text(encoding="utf-8")
    r = requests.put(f"{BASE}/themes/{THEME}/assets.json",
        json={"asset": {"key": key, "value": body}},
        headers=HDR, timeout=30, verify=False)
    status = "OK " if r.status_code in (200, 201) else "ERR"
    print(f"  {status}  HTTP {r.status_code}  {key}")
    if r.status_code not in (200, 201):
        print(f"         {r.text[:180]}")
    time.sleep(0.5)

print("\nFine.")
