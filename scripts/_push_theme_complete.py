"""Push completo tema TM04 — tutti i file modificati da 04_TEMA_SHOPIFY/
Legge da 04_TEMA_SHOPIFY/ (source of truth, non _merged_tm04).
"""
import os, time, requests, urllib3, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
urllib3.disable_warnings()  # type: ignore

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
SRC    = ROOT / "04_TEMA_SHOPIFY"

FILES = [
    # ── LAYOUT ─────────────────────────────────────────────────────────
    "layout/theme.liquid",

    # ── SNIPPETS ───────────────────────────────────────────────────────
    "snippets/bakabo-header.liquid",        # collection colors nav
    "snippets/bks-json-ld.liquid",          # FAQPage + Organization + CollectionPage
    "snippets/bks-ai-assistant-embed.liquid",
    "snippets/bks-ai-context.liquid",
    "snippets/bks-gdpr-banner.liquid",
    "snippets/bks-member-tier.liquid",
    "snippets/bks-member-tracker.liquid",

    # ── SECTIONS ───────────────────────────────────────────────────────
    "sections/bks-store-reviews.liquid",
    "sections/bks-impact-home.liquid",
    "sections/bks-member-dashboard.liquid",
    "sections/bks-trust-strip.liquid",
    "sections/bks-ai-assistant.liquid",
    "sections/main-collection-product-grid-bks.liquid",
    # newly added from _merged_tm04
    "sections/bks-editorial-matrix.liquid",
    "sections/bks-product-meta.liquid",
    "sections/bks-collections-index.liquid",
    "sections/bks-care-guide.liquid",
    "sections/bks-collection-list-v2.liquid",
    "sections/bks-dedicated-collection-page.liquid",
    "sections/bks-editorial-page-hero.liquid",
    "sections/bks-help-faq.liquid",
    "sections/bks-measure-diagram.liquid",
    "sections/bks-product-grid.liquid",
    "sections/bks-product-type-guide.liquid",
    "sections/bks-product-type-hub.liquid",
    "sections/bks-rich-text.liquid",
    "sections/bks-shopping-guide.liquid",
    "sections/bks-size-guide.liquid",
    "sections/bks-trust-reviews.liquid",
    "sections/bks-universal-size-guide.liquid",

    # ── TEMPLATES — Home ───────────────────────────────────────────────
    "templates/index.json",

    # ── TEMPLATES — Cart ───────────────────────────────────────────────
    "templates/cart.json",

    # ── TEMPLATES — Product ────────────────────────────────────────────
    "templates/product.bks.json",

    # ── TEMPLATES — Collections BKS ────────────────────────────────────
    "templates/collection.bks-flag.json",
    "templates/collection.bks-glyph.json",
    "templates/collection.bks-hours.json",
    "templates/collection.bks-marker.json",
    "templates/collection.bks-origin.json",
    "templates/collection.bks-pulse.json",
    "templates/collection.bks-riviera.json",
    "templates/collection.bks-token.json",

    # ── ASSETS — CSS ───────────────────────────────────────────────────
    "assets/bks-cart.css",
    "assets/bks-commerce-light.css",
    "assets/bks-dynamic-theme.css",
    "assets/bks-future.css",
    "assets/bks-home-hero.css",
    "assets/bks-member.css",
    "assets/bks-mobile.css",
    "assets/bks-piano-hero.css",
    "assets/bks-responsive.css",
    "assets/bks-theme-effects.css",
    "assets/bks-tokens.css",
    "assets/bks-tryon.css",
    "assets/bks-typography.css",

    # ── ASSETS — JS ────────────────────────────────────────────────────
    "assets/bks-dynamic-ux.js",
    "assets/bks-member.js",
    "assets/bks-piano-hero.js",
    "assets/bks-tryon.js",
]

ok = 0
err = 0

print(f"=== Push completo TM04 — {len(FILES)} file ===\n")
for key in FILES:
    path = SRC / key
    if not path.exists():
        print(f"  SKIP  {key}  (file non trovato)")
        continue
    body = path.read_text(encoding="utf-8")
    r = requests.put(
        f"{BASE}/themes/{THEME}/assets.json",
        json={"asset": {"key": key, "value": body}},
        headers=HDR, timeout=30, verify=False
    )
    if r.status_code in (200, 201):
        print(f"  OK    {key}")
        ok += 1
    else:
        print(f"  ERR   HTTP {r.status_code}  {key}")
        print(f"        {r.text[:200]}")
        err += 1
    time.sleep(0.4)

print(f"\n=== Fine — OK: {ok}  ERR: {err} ===")
