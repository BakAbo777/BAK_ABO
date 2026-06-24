"""Create bks-page-hero templates for all BKS product type pages."""
import json, time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
THEME_DIR = ROOT / "04_TEMA_SHOPIFY"
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

SHOP  = env["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN = env["SHOPIFY_ADMIN_TOKEN"]
THEME = "202392961362"
API   = "2025-01"

# suffix → (title, lead, accent, bg, quick_links [(label, url)])
PRODUCT_PAGES = {
    "bks-swim-trunks": (
        "SWIM TRUNKS", "All-over AI-art graphics on premium men's swimwear. Built for resort and water movement.",
        "#0ca898", "#04100f",
        [("BKS Riviera", "/collections/bks-riviera"), ("BKS Flag", "/collections/bks-flag"),
         ("BKS Glyph", "/collections/bks-glyph"), ("BKS Pulse", "/collections/bks-pulse")],
    ),
    "bks-puffer-jacket": (
        "PUFFER JACKET", "Geometric all-over prints on lightweight outerwear. Editorial warmth for the winter layer.",
        "#c8c4be", "#121210",
        [("BKS Hours", "/collections/bks-hours"), ("BKS Glyph", "/collections/bks-glyph"),
         ("BKS Marker", "/collections/bks-marker"), ("BKS Pulse", "/collections/bks-pulse")],
    ),
    "bks-windbreaker": (
        "WINDBREAKER", "Technical shell with full-coverage editorial graphics. AI-art built for movement and weather.",
        "#c04418", "#100800",
        [("BKS Marker", "/collections/bks-marker"), ("BKS Hours", "/collections/bks-hours"),
         ("BKS Pulse", "/collections/bks-pulse"), ("BKS Token", "/collections/bks-token"),
         ("BKS Flag", "/collections/bks-flag"), ("BKS Origin", "/collections/bks-origin")],
    ),
    "bks-backpack": (
        "BACKPACK", "Structured carry with AI-art surface treatment. Clean silhouette, editorial presence.",
        "#d4a030", "#0f0e08",
        [("BKS Glyph", "/collections/bks-glyph"), ("BKS Marker", "/collections/bks-marker"),
         ("BKS Pulse", "/collections/bks-pulse"), ("BKS Token", "/collections/bks-token")],
    ),
    "bks-sneakers": (
        "SNEAKERS", "Low-profile sneaker canvas as wearable artwork. AI-generated all-over surface.",
        "#9828d8", "#0a0010",
        [("BKS Glyph", "/collections/bks-glyph"), ("BKS Pulse", "/collections/bks-pulse"),
         ("BKS Token", "/collections/bks-token")],
    ),
    "bks-travel-bag": (
        "TRAVEL BAG", "Oversized carry-all with full editorial surface. From weekender to studio companion.",
        "#C9B79C", "#0a0a08",
        [("BKS Hours", "/collections/bks-hours"), ("BKS Riviera", "/collections/bks-riviera"),
         ("BKS Token", "/collections/bks-token"), ("BKS Flag", "/collections/bks-flag"),
         ("BKS Origin", "/collections/bks-origin")],
    ),
    "bks-beach-towel": (
        "BEACH TOWEL", "Oversized cotton surface for the resort moment. AI-art print, maximum coverage.",
        "#0ca898", "#04100f",
        [("BKS Riviera", "/collections/bks-riviera"), ("BKS Flag", "/collections/bks-flag"),
         ("BKS Origin", "/collections/bks-origin")],
    ),
    "bks-pullover-hoodie": (
        "HOODIE", "Editorial French terry with AI-generated all-over surface. Studio and street.",
        "#c82020", "#100000",
        [("BKS Marker", "/collections/bks-marker"), ("BKS Pulse", "/collections/bks-pulse"),
         ("BKS Flag", "/collections/bks-flag")],
    ),
    "bks-athletic-shorts": (
        "SHORTS", "Active silhouette with AI-art all-over print. From studio to street.",
        "#c82020", "#100000",
        [("BKS Marker", "/collections/bks-marker"), ("BKS Flag", "/collections/bks-flag")],
    ),
    "bks-lounge-pants": (
        "LOUNGE PANTS", "Relaxed knit with editorial all-over treatment. Studio wear redefined.",
        "#c8c4be", "#121210",
        [("BKS Hours", "/collections/bks-hours"), ("BKS Origin", "/collections/bks-origin")],
    ),
    "bks-flip-flop": (
        "FLIP FLOPS", "Resort footwear with AI-art surface. The final touch on the beach look.",
        "#0ca898", "#04100f",
        [("BKS Riviera", "/collections/bks-riviera")],
    ),
    "bks-hawaiian-shirt": (
        "HAWAIIAN", "Resort cut with full-coverage AI-generated graphics. Riviera spirit, all-over print.",
        "#0ca898", "#04100f",
        [("BKS Riviera", "/collections/bks-riviera")],
    ),
    "bks-duffel-bag": (
        "DUFFEL BAG", "Structured sport carry with editorial print coverage. Travel and studio companion.",
        "#C9B79C", "#0a0a08",
        [("BKS Hours", "/collections/bks-hours"), ("BKS Marker", "/collections/bks-marker")],
    ),
    "bks-swimwear": (
        "SWIMWEAR", "AI-art water collection. Resort prints for the Mediterranean moment and beyond.",
        "#0ca898", "#04100f",
        [("BKS Riviera", "/collections/bks-riviera"), ("Shop All", "/collections/all")],
    ),
    "bks-one-piece-swimsuit": (
        "ONE PIECE", "Full-coverage editorial swimwear. AI-generated print on clean minimal silhouette.",
        "#0ca898", "#04100f",
        [("BKS Riviera", "/collections/bks-riviera")],
    ),
    "bks-racerback-dress": (
        "RACERBACK DRESS", "Editorial racerback silhouette with full AI-art surface treatment.",
        "#8888cc", "#0A0A0A",
        [("BKS Riviera", "/collections/bks-riviera"), ("BKS Pulse", "/collections/bks-pulse")],
    ),
    "bks-shoes": (
        "SHOES", "Footwear as wearable art. AI-generated surface print on every pair.",
        "#9828d8", "#0a0010",
        [("BKS Glyph", "/collections/bks-glyph"), ("BKS Pulse", "/collections/bks-pulse"),
         ("BKS Token", "/collections/bks-token")],
    ),
    "bks-men": (
        "MEN", "BKS Studio wearables for men. AI-art fashion across all eight collections.",
        "#C9B79C", "#0a0a08",
        [("BKS Hours", "/collections/bks-hours"), ("BKS Glyph", "/collections/bks-glyph"),
         ("BKS Marker", "/collections/bks-marker"), ("BKS Pulse", "/collections/bks-pulse"),
         ("BKS Flag", "/collections/bks-flag"), ("BKS Origin", "/collections/bks-origin")],
    ),
    "bks-woman": (
        "WOMAN", "BKS Studio wearables for women. AI-art fashion across all eight collections.",
        "#C9B79C", "#0a0a08",
        [("BKS Riviera", "/collections/bks-riviera"), ("BKS Glyph", "/collections/bks-glyph"),
         ("BKS Pulse", "/collections/bks-pulse"), ("BKS Token", "/collections/bks-token"),
         ("BKS Flag", "/collections/bks-flag"), ("BKS Origin", "/collections/bks-origin")],
    ),
    "bks-shopping-guide": (
        "SHOPPING GUIDE", "Everything you need to know about BKS Studio products, sizing, materials and ordering.",
        "#C9B79C", "#0a0a08",
        [("Size Guide", "/pages/bks-size-guide"), ("Collections", "/pages/bks-collections"),
         ("BKS Members", "/pages/bks-members"), ("FAQ", "/pages/bks-faq")],
    ),
    "bks-size-guide": (
        "SIZE GUIDE", "Measurements, fit notes and garment specs for every BKS Studio product type.",
        "#C9B79C", "#0a0a08",
        [("Shopping Guide", "/pages/bks-shopping-guide"), ("All Products", "/collections/all")],
    ),
    "bks-verse-hall": (
        "VERSE HALL", "The BKS Verse Hall of Fame. Poems that crossed the threshold and became objects.",
        "#C9B79C", "#0a0a08",
        [("BKS Verse", "/pages/bks-verse"), ("Collections", "/pages/bks-collections")],
    ),
}

def shopify_put_asset(key, value):
    r = requests.put(
        f"https://{SHOP}/admin/api/{API}/themes/{THEME}/assets.json",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"},
        json={"asset": {"key": key, "value": value}},
        verify=False, timeout=30,
    )
    return "key" in r.json().get("asset", {})

def make_template(suffix, title, lead, accent, bg, links):
    blocks, block_order = {}, []
    for label, url in links:
        bid = f"link_{label.lower().replace(' ', '_')}"
        blocks[bid] = {"type": "quick_link", "settings": {"label": label, "link": url}}
        block_order.append(bid)

    title_words = title.title()
    return {
        "sections": {
            "page_hero": {
                "type": "bks-page-hero",
                "settings": {
                    "kicker": "BKS Studio",
                    "title": title,
                    "lead": lead,
                    "meta_1": "AI-Generated",
                    "meta_2": "Made to Order",
                    "meta_3": "Ships Worldwide",
                    "primary_label": f"Shop {title_words}",
                    "primary_link": f"/collections/all",
                    "secondary_label": "All Collections",
                    "secondary_link": "/pages/bks-collections",
                    "background_color": bg,
                    "text_color": "#FAFAF7",
                    "accent_color": accent,
                },
                "blocks": blocks,
                "block_order": block_order,
            },
            "main": {"type": "main-page", "settings": {}},
        },
        "order": ["page_hero", "main"],
    }

for suffix, (title, lead, accent, bg, links) in PRODUCT_PAGES.items():
    tmpl = make_template(suffix, title, lead, accent, bg, links)
    tmpl_json = json.dumps(tmpl, indent=2)
    key = f"templates/page.{suffix}.json"
    local = THEME_DIR / f"templates/page.{suffix}.json"
    local.write_text(tmpl_json, encoding="utf-8")
    ok = shopify_put_asset(key, tmpl_json)
    print(f"{'OK' if ok else 'ERR'}  {key}")
    time.sleep(0.3)

print("\nAll done.")
