"""
Push BKS token system update to Shopify TM04.
Deploys: bks-tokens.css (new) + all modified theme files.
"""
import os, sys, requests, urllib3
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
THEME_DIR = ROOT / "04_TEMA_SHOPIFY"

for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]:
        os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
VER    = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
THEME  = "202392961362"
BASE   = f"https://{DOMAIN}/admin/api/{VER}"
HDR    = {"X-Shopify-Access-Token": TOKEN}

FILES = [
    # (theme_key, local_relative_path)
    # ── NEW: global token system ──────────────────────────────────────────────
    ("assets/bks-tokens.css",                      "assets/bks-tokens.css"),
    # ── Layout (loads bks-tokens.css globally) ───────────────────────────────
    ("layout/theme.liquid",                         "layout/theme.liquid"),
    # ── Assets ───────────────────────────────────────────────────────────────
    ("assets/bks-member.css",                       "assets/bks-member.css"),
    ("assets/bks-piano-hero.css",                   "assets/bks-piano-hero.css"),
    ("assets/bks-piano-hero.js",                    "assets/bks-piano-hero.js"),
    # ── Sections ─────────────────────────────────────────────────────────────
    ("sections/bks-ai-assistant.liquid",            "sections/bks-ai-assistant.liquid"),
    ("sections/bks-faq.liquid",                     "sections/bks-faq.liquid"),
    ("sections/bks-impact-home.liquid",             "sections/bks-impact-home.liquid"),
    ("sections/bks-piano-hero.liquid",              "sections/bks-piano-hero.liquid"),
    ("sections/main-collection-product-grid-bks.liquid", "sections/main-collection-product-grid-bks.liquid"),
    # ── Snippets ─────────────────────────────────────────────────────────────
    ("snippets/bakabo-header.liquid",               "snippets/bakabo-header.liquid"),
]

ok = 0; errors = []
for theme_key, local_path in FILES:
    src = THEME_DIR / local_path
    if not src.exists():
        print(f"  SKIP (not found): {local_path}")
        continue
    body = src.read_text(encoding="utf-8")
    r = requests.put(
        f"{BASE}/themes/{THEME}/assets.json",
        json={"asset": {"key": theme_key, "value": body}},
        headers=HDR,
        timeout=30,
        verify=False,
    )
    status = "✅" if r.status_code in (200, 201) else "❌"
    print(f"  {status} HTTP {r.status_code}  {theme_key}")
    if r.status_code in (200, 201):
        ok += 1
    else:
        errors.append((theme_key, r.status_code, r.text[:300]))

print(f"\n{'='*55}")
print(f"  Deployed: {ok}/{len(FILES)}  |  Errors: {len(errors)}")
if errors:
    print("\nErrors:")
    for k, s, t in errors:
        print(f"  [{s}] {k}: {t}")
