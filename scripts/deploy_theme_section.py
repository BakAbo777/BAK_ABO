"""Deploy singola sezione o lista di file al tema Shopify attivo."""
from __future__ import annotations
import os, sys, requests, urllib3, time, base64
from pathlib import Path

urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
THEME_DIR = ROOT / "04_TEMA_SHOPIFY"

# File da deployare — aggiungere qui ogni variazione
FILES = [
    # Sezioni principali
    ("sections/bks-piano-hero.liquid",             "sections/bks-piano-hero.liquid"),
    ("sections/bks-impact-home.liquid",            "sections/bks-impact-home.liquid"),
    ("sections/bks-store-reviews.liquid",           "sections/bks-store-reviews.liquid"),
    ("sections/bks-member-dashboard.liquid",        "sections/bks-member-dashboard.liquid"),
    ("sections/bks-member-archive-page.liquid",     "sections/bks-member-archive-page.liquid"),
    ("sections/bks-planet-collections-orbit.liquid","sections/bks-planet-collections-orbit.liquid"),
    ("sections/bks-ai-assistant.liquid",            "sections/bks-ai-assistant.liquid"),
    ("sections/bks-collection-signal.liquid",       "sections/bks-collection-signal.liquid"),
    ("sections/bks-timed-offer.liquid",             "sections/bks-timed-offer.liquid"),
    ("sections/bks-trust-strip.liquid",                        "sections/bks-trust-strip.liquid"),
    ("sections/bks-product-editorial-care.liquid",             "sections/bks-product-editorial-care.liquid"),
    ("sections/main-collection-product-grid-bks.liquid",       "sections/main-collection-product-grid-bks.liquid"),
    ("sections/bks-accessories-panel.liquid",                  "sections/bks-accessories-panel.liquid"),
    # Assets globali
    ("assets/bks-commerce-light.css",              "assets/bks-commerce-light.css"),
    # Assets piano hero
    ("assets/bks-piano-hero.css",                  "assets/bks-piano-hero.css"),
    ("assets/bks-piano-hero.js",                   "assets/bks-piano-hero.js"),
    # Assets member area
    ("assets/bks-member.css",                      "assets/bks-member.css"),
    ("assets/bks-member.js",                       "assets/bks-member.js"),
    ("assets/bks-tryon.css",                       "assets/bks-tryon.css"),
    ("assets/bks-tryon.js",                        "assets/bks-tryon.js"),
    # Snippet
    ("snippets/bks-gcr-badge.liquid",              "snippets/bks-gcr-badge.liquid"),
    ("snippets/bks-gcr-survey.liquid",             "snippets/bks-gcr-survey.liquid"),
    # Template membri
    ("templates/customers/account.json",           "templates/customers/account.json"),
    ("templates/customers/account.bks-member.json","templates/customers/account.bks-member.json"),
    # Template pagine custom
    ("templates/page.bks-archive.json",            "templates/page.bks-archive.json"),
    ("templates/page.bks-planet-collections-orbit.json", "templates/page.bks-planet-collections-orbit.json"),
    # Custom request page
    ("sections/bks-custom-request.liquid",              "sections/bks-custom-request.liquid"),
    ("templates/page.bks-custom.json",                  "templates/page.bks-custom.json"),
    # BKS AI Assistant page
    ("templates/page.bks-ai-assistant.json",            "templates/page.bks-ai-assistant.json"),
    # BKS Members login page
    ("sections/bks-members-login.liquid",               "sections/bks-members-login.liquid"),
    ("templates/page.bks-members.json",                 "templates/page.bks-members.json"),
    # Footer (language selector hidden, white text fix)
    ("sections/footer.liquid",                             "sections/footer.liquid"),
    # Collection editorial hero — accent-color bg, same logic as home
    ("sections/bks-collection-hero.liquid",                "sections/bks-collection-hero.liquid"),
    # Home: canvas video hero (4 avatar videos, no audio) + magazine editorial
    ("sections/bks-home-video-canvas.liquid",              "sections/bks-home-video-canvas.liquid"),
    ("sections/bks-home-magazine.liquid",                  "sections/bks-home-magazine.liquid"),
    # Header snippet (nav update: reads main-menu-1)
    ("snippets/bakabo-header.liquid",                   "snippets/bakabo-header.liquid"),
    # AI Assistant global embed
    ("snippets/bks-ai-assistant-embed.liquid",          "snippets/bks-ai-assistant-embed.liquid"),
    # AI context injector (feeds bks-dynamic-ux.js)
    ("snippets/bks-ai-context.liquid",                  "snippets/bks-ai-context.liquid"),
    # Global layout
    ("layout/theme.liquid",                             "layout/theme.liquid"),
    # Dynamic header UX
    ("assets/bks-dynamic-theme.css",                   "assets/bks-dynamic-theme.css"),
    ("assets/bks-dynamic-ux.js",                       "assets/bks-dynamic-ux.js"),
    # Responsive + contrast system + mobile product patch v2 (2026-06-18)
    ("assets/bks-responsive.css",                      "assets/bks-responsive.css"),
    # AI control map — member tryon system + local AI targets (2026-06-18)
    ("assets/bks-ai-control-map.json",                 "assets/bks-ai-control-map.json"),
    # Theme effects layer (bks-theme-effects.css — fixes 404 console error)
    ("assets/bks-theme-effects.css",                   "assets/bks-theme-effects.css"),
    # Collection grid — card visibility + typographer pass (2026-06-18)
    ("sections/main-collection-product-grid-bks.liquid","sections/main-collection-product-grid-bks.liquid"),
    # Collections hub page (2026-06-18)
    ("sections/bks-collections-hub.liquid",            "sections/bks-collections-hub.liquid"),
    ("templates/page.bks-collections.json",            "templates/page.bks-collections.json"),
    # Default collection template + all 8 BKS collection templates → main-collection-product-grid-bks
    ("templates/collection.json",                      "templates/collection.json"),
    ("templates/collection.bks-origin.json",           "templates/collection.bks-origin.json"),
    ("templates/collection.bks-hours.json",            "templates/collection.bks-hours.json"),
    ("templates/collection.bks-glyph.json",            "templates/collection.bks-glyph.json"),
    ("templates/collection.bks-marker.json",           "templates/collection.bks-marker.json"),
    ("templates/collection.bks-riviera.json",          "templates/collection.bks-riviera.json"),
    ("templates/collection.bks-pulse.json",            "templates/collection.bks-pulse.json"),
    ("templates/collection.bks-token.json",            "templates/collection.bks-token.json"),
    ("templates/collection.bks-flag.json",             "templates/collection.bks-flag.json"),
    # Heart buttons on all pages — member wishlist (2026-06-18)
    ("assets/bks-member.js",                           "assets/bks-member.js"),
    ("assets/bks-member.css",                          "assets/bks-member.css"),
    # FAQ page — accordion, category filter, GDPR-safe try-on answer
    ("sections/bks-faq.liquid",                        "sections/bks-faq.liquid"),
    ("templates/page.bks-faq.json",                    "templates/page.bks-faq.json"),
    # About pages — hero + text columns + pull quote + stats
    ("sections/bks-about.liquid",                      "sections/bks-about.liquid"),
    ("templates/page.bks-about-bakabo.json",           "templates/page.bks-about-bakabo.json"),
    ("templates/page.bks-about-bks.json",              "templates/page.bks-about-bks.json"),
    # Member dashboard — photo validation + GDPR consent (2026-06-19)
    ("sections/bks-member-dashboard.liquid",           "sections/bks-member-dashboard.liquid"),
    # Header accent bar per-collection (3px bottom bar, no full bg change)
    ("assets/bks-dynamic-ux.js",                       "assets/bks-dynamic-ux.js"),
    ("assets/bks-dynamic-theme.css",                   "assets/bks-dynamic-theme.css"),
    # Home page template — wires video canvas + magazine + reviews + trust-strip
    ("templates/index.json",                           "templates/index.json"),
    # FAQ — added JSON-LD schema for Google FAQ rich results
    ("sections/bks-faq.liquid",                        "sections/bks-faq.liquid"),
    # Product hero — accent-color hero, auto-rilevamento collezione, img su fondo colorato
    ("sections/bks-product-hero.liquid",               "sections/bks-product-hero.liquid"),
    ("templates/product.bks.json",                     "templates/product.bks.json"),
    # DEFAULT product template — BKS hero per tutti i prodotti (2026-06-19)
    ("templates/product.json",                         "templates/product.json"),
    # Contact page — form + info bicolonna (2026-06-19)
    ("sections/bks-contact.liquid",                    "sections/bks-contact.liquid"),
    ("templates/page.bks-contact.json",                "templates/page.bks-contact.json"),
    # Policy template — privacy, terms, resi, spedizioni (2026-06-19)
    ("sections/bks-policy.liquid",                     "sections/bks-policy.liquid"),
    ("templates/policy.liquid",                        "templates/policy.liquid"),
    # Home magazine — tutti 8 collezioni (2026-06-19)
    ("templates/index.json",                           "templates/index.json"),
    # Product-type collection templates — BKS hero per sneakers, backpack, etc. (2026-06-19)
    ("templates/collection.sneakers.json",             "templates/collection.sneakers.json"),
    ("templates/collection.puffer-jacket.json",        "templates/collection.puffer-jacket.json"),
    ("templates/collection.windbreaker.json",          "templates/collection.windbreaker.json"),
    ("templates/collection.pullover-hoodie.json",      "templates/collection.pullover-hoodie.json"),
    ("templates/collection.swim-trunks.json",          "templates/collection.swim-trunks.json"),
    ("templates/collection.swimwear.json",             "templates/collection.swimwear.json"),
    ("templates/collection.flip-flop.json",            "templates/collection.flip-flop.json"),
    ("templates/collection.athletic-shorts.json",      "templates/collection.athletic-shorts.json"),
    ("templates/collection.lounge-pants.json",         "templates/collection.lounge-pants.json"),
    ("templates/collection.backpack.json",             "templates/collection.backpack.json"),
    ("templates/collection.travel-bag.json",           "templates/collection.travel-bag.json"),
    ("templates/collection.one-piece-swimsuit.json",   "templates/collection.one-piece-swimsuit.json"),
    ("templates/collection.racerback-dress.json",      "templates/collection.racerback-dress.json"),
    # V9: GDPR cookie banner + anatomy-fixed BKS Token templates (19_06_2026)
    ("snippets/bks-gdpr-banner.liquid",                "snippets/bks-gdpr-banner.liquid"),
    ("layout/theme.liquid",                            "layout/theme.liquid"),
    ("templates/collection.bks-token.json",            "templates/collection.bks-token.json"),
    ("templates/index.json",                           "templates/index.json"),
    # V10: Google Shopping XML feed (19_06_2026)
    ("templates/page.bks-google-feed.liquid",          "templates/page.bks-google-feed.liquid"),
    # V11: JSON-LD structured data — Product/WebSite/ItemList + Organization expanded (19_06_2026)
    ("snippets/bks-json-ld.liquid",                    "snippets/bks-json-ld.liquid"),
    # V12: BKS Cart Drawer — ink bg, gold CTA, Bebas/DM Mono typography (19_06_2026)
    ("assets/bks-cart.css",                            "assets/bks-cart.css"),
    ("layout/theme.liquid",                            "layout/theme.liquid"),
    # V13: Fix heart buttons — listener moved to injectHeartButtons, no duplicate listeners (19_06_2026)
    ("assets/bks-member.js",                           "assets/bks-member.js"),
    # V14: Wishlist toast + account badge — feedback visivo su ogni pagina (19_06_2026)
    ("assets/bks-member.js",                           "assets/bks-member.js"),
    ("assets/bks-member.css",                          "assets/bks-member.css"),
    # V15: BKS Weekly Editorial — masthead magazine periodico Vol./Issue (19_06_2026)
    ("sections/bks-weekly-editorial.liquid",           "sections/bks-weekly-editorial.liquid"),
    # V16: Pricing fix — swimsuits $55, slippers $55, flip flops $49 (no theme file changes)
    # V17: Printify image sync (28 uploads), pricing Athletic Shorts $69, naming schema 142 products
    # V18: SESSION_CHANGES compacted, wishlist standalone page, Athletic Shorts $65→$69
    ("sections/bks-wishlist.liquid",                  "sections/bks-wishlist.liquid"),
    ("templates/page.bks-wishlist.json",              "templates/page.bks-wishlist.json"),
]


def get_active_theme_id() -> str:
    r = requests.get(f"{BASE}/themes.json", headers=HDR, timeout=15, verify=False)
    r.raise_for_status()
    for t in r.json().get("themes", []):
        if t.get("role") == "main":
            return str(t["id"])
    raise RuntimeError("Nessun tema attivo trovato")


def upload(theme_id: str, src_rel: str, dest_key: str) -> bool:
    src = THEME_DIR / src_rel
    if not src.exists():
        print(f"  SKIP  {dest_key}  (file non trovato: {src})")
        return False

    content = src.read_bytes()
    is_binary = dest_key.split(".")[-1] in {"png","jpg","jpeg","gif","webp","svg","woff","woff2","ttf","ico"}
    payload = {
        "asset": {
            "key": dest_key,
            **({"attachment": base64.b64encode(content).decode()} if is_binary
               else {"value": content.decode("utf-8")}),
        }
    }

    for attempt in range(4):
        r = requests.put(
            f"{BASE}/themes/{theme_id}/assets.json",
            headers=HDR, json=payload, timeout=60, verify=False
        )
        if r.status_code == 429:
            wait = 2 ** attempt + 2
            print(f"    rate limited — attendo {wait}s")
            time.sleep(wait)
            continue
        if r.ok:
            print(f"  OK    {dest_key}")
            return True
        print(f"  ERR   {dest_key}  [{r.status_code}] {r.text[:120]}")
        return False
    return False


def main():
    print("=== Deploy Theme Sections ===\n")
    theme_id = get_active_theme_id()
    print(f"Tema attivo: {theme_id}\n")

    ok = err = 0
    for src_rel, dest_key in FILES:
        if upload(theme_id, src_rel, dest_key):
            ok += 1
        else:
            err += 1
        time.sleep(0.5)

    print(f"\n=== {ok} OK  |  {err} ERRORI ===")


if __name__ == "__main__":
    main()
