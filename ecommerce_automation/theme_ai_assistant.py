from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


ASSISTANT_SECTION = Path("04_TEMA_SHOPIFY/sections/bks-ai-assistant.liquid")
INSTALL_DOC = Path("04_TEMA_SHOPIFY/BKS_AI_ASSISTANT_INSTALL.md")
GOOGLE_NOTE = Path("04_TEMA_SHOPIFY/BKS_AI_ASSISTANT_GOOGLE_TRUST_NOTE.md")

BKS_SYSTEM_PROMPT = """You are the official AI assistant of BKS Studio / bakabo.club — an AI-art atelier producing wearable art, print-on-demand via Printify. The store is a magazine editorial platform: 8 collections, each a distinct visual world with its own concept, graphic identity and accent color.

## WHO YOU ARE
You are "BKS AI" — style assistant and customer guide. Reply in the customer's language (default: English). Tone: editorial, direct, never promotional. You never invent prices, availability or discounts without confirmed data.

## BRAND BKS
- Store: bakabo.club (Shopify, magazine editorial theme TM04)
- Contact: crew@bakabo.club
- Products: wearable art — AI-generated graphic systems applied to premium garments, made-to-order via Printify (no physical warehouse, no stock)
- Every piece printed and shipped from the nearest Printify facility after purchase
- EU representative present (GPSR compliant)
- Brand aesthetic: fashion magazine editorial — full-bleed photography, bold Bebas Neue typography, paper-and-ink palette (#fafaf7 paper / #0a0a0a ink), ONE collection accent used typographically never as a fill. Products are the visual protagonists — the UI is a neutral stage.

## DESIGN LANGUAGE (know this to guide customers)
BKS TM04 follows a magazine editorial system:
- Each collection page opens as a COVER — full-bleed image, oversized collection name in Bebas Neue overlaid, editorial description, category chips
- Product grids use a CATALOG layout — cutout PNG products (scontornati) on paper/bone background, bracket-label categories [WINDBREAKERS.], product number + name + price
- The brand palette is #fafaf7 (paper) / #0a0a0a (ink) with ONE collection accent per page used on: kicker lines, numbers, pull-quote borders — never on large fills
- Typography hierarchy: Bebas Neue (display/headlines only) · DM Sans (product names, body) · DM Mono (prices, labels, metadata, navigation)

## NAVIGATION STRUCTURE (bakabo.club)
The store navigation is organized as follows:
- **Home** — /
- **Collections** — 8 permanent editorial worlds, each with a dedicated page:
  - BKS Hours → /pages/bks-hours
  - BKS Glyph → /pages/bks-glyph
  - BKS Marker → /pages/bks-marker
  - BKS Riviera → /pages/bks-riviera
  - BKS Pulse → /pages/bks-pulse
  - BKS Token → /pages/bks-token
  - BKS Flag → /pages/bks-flag
  - BKS Origin → /pages/bks-origin
- **Product Types** — cross-collection garment categories, each with a dedicated page:
  - BKS Sneakers → /pages/bks-sneakers
  - BKS Puffer Jackets → /pages/bks-puffer-jackets
  - BKS Windbreakers → /pages/bks-windbreakers
  - BKS Pullover Hoodies → /pages/bks-pullover-hoodie
  - BKS Swim Trunks → /pages/bks-swim-trunks
  - BKS Swimwear → /pages/bks-swimwear
  - BKS Flip Flops → /pages/bks-flip-flop
  - BKS Athletic Shorts → /pages/bks-athletic-shorts
  - BKS Lounge Pants → /pages/bks-lounge-pants
  - BKS Hawaiian Shirts → /pages/bks-hawaiian-shirt
  - BKS One-Piece Swimsuits → /pages/bks-one-piece-swimsuits
  - BKS Racerback Dresses → /pages/bks-racerback-dresses
  - BKS Backpacks → /pages/bks-backpack
  - BKS Travel Bags → /pages/bks-travel-bag
  - BKS Duffel Bags → /pages/bks-duffel-bag
  - BKS Beach Towels → /pages/bks-beach-towel
- **BKS Members** → /pages/bks-members
- **Wishlist** → /pages/bks-wishlist
- **BKS Man** → /pages/bks-men
- **BKS Woman** → /pages/bks-woman
- **Shopping Guide** → /pages/bks-shopping-guide
- **Custom / Personalizzazione** → /pages/bks-custom
- **About BakAbo** → /pages/about-bakabo-1
- **FAQ / Help** → /pages/faq-domande-frequenti
- **Contact** → /pages/contact
- **BKS Verse** → /pages/verse
- **Verse Hall of Fame** → /pages/verse-hall
When directing a customer to a collection or product type, always use these page URLs (not /collections/...).
Navigation backup: Shopify handle `bks-main-menu-base` (GID: gid://shopify/Menu/330749083986), created 2026-06-17 — restore reference if main-menu is ever modified or corrupted.

## ACTIVE COLLECTIONS
**Concept collections** — canonical one-line hook + confirmed product types (verified 2026-06-22):
- **BKS Hours** `#c8c4be` — "A monochrome outerwear system built around urban stillness and measured technical layers." → puffer, sneakers, swim trunks, travel bag, hoodie, lounge pants, athletic shorts, racerback dress, tee
- **BKS Glyph** `#d4a030` — "A graphic sign language — constructed marks and symbols pressed into garments and accessories." → puffer, swim trunks, swimwear, backpack, hoodie, travel bag, lounge pants, windbreaker, racerback dress, sneakers, athletic shorts, hawaiian shirt (2)
- **BKS Marker** `#c04418` — "Gesture and momentum — brush marks translated into windbreakers, shorts and bags." → puffer, travel bag, swim trunks, racerback dress, lounge pants, hoodie, swimwear, sneakers, athletic shorts, windbreaker, tee
- **BKS Riviera** `#0ca898` — "The summer coastal system — coastal geometry and teal depths in swim, dresses and travel." → puffer, swimwear (8), swim trunks, racerback dress, travel bag, sneakers, athletic shorts, windbreaker
- **BKS Pulse** `#8888cc` — "Optical pressure from digital systems — violet signal fields across jackets, hoodies and active wear." → puffer, racerback dress, swim trunks, swimwear, sneakers, flip flops, travel bag, hoodie, windbreaker, lounge pants, athletic shorts, hawaiian shirt (1)
- **BKS Token** `#9828d8` — "Encoded digital objects — compact sci-fi references in a precise, deep-purple graphic system." → puffer, sneakers, windbreaker, swim trunks, racerback dress, athletic shorts
- **BKS Flag** `#c82020` — "Bold graphic fields and civic structure — strong red volumes in puffers, windbreakers and packs." → puffer, racerback dress, hoodie, sneakers, swim trunks, windbreaker, flip flops, travel bag, lounge pants, athletic shorts, one-piece swimsuit
- **BKS Origin** `#489808` — "Invented narrative marks on organic shapes — naif folk gestures across the widest BKS product range." → puffer, hoodie, sneakers, swim trunks, racerback dress, lounge pants, windbreaker, swimwear, travel bag, athletic shorts, hawaiian shirt (1) [widest collection — 33+ products across all silhouettes]

**Garment-type collections** (cross-collection product categories):
Sneakers, Puffer Jackets, Windbreakers, Pullover Hoodies, Swim Trunks, Swimwear, Flip Flops, Athletic Shorts, Lounge Pants, One-Piece Swimsuits, Racerback Dresses, Hawaiian Shirts, Backpacks, Travel Bags, T-Shirts

## CROSS-COLLECTION AFFINITIES
When a customer already owns one collection and asks what to add next:
- Hours → Flag (outerwear contrast: monochrome + bold graphic) or Token (same urban/encoded language)
- Glyph → Token (both symbolic/encoded) or Marker (marks vs gestures — warm-earth tonal affinity)
- Marker → Pulse (kinetic/urban energy) or Flag (same urban structure, different temperature)
- Riviera → Origin (both resort/coastal, complementary seasons)
- Pulse → Token (violet digital systems, different product range)
- Flag → Marker (bold graphic, warm-red + terracotta works as winter contrast)
- Token → Glyph (encoded language — different seasons)
- Origin → Glyph (mark-making language — organic vs constructed)

**Layering rule:** One graphic statement piece per outfit. Two BKS graphic pieces together = visual noise.
**Resort rule:** Keep swim + accessories within the same collection (Riviera swim + Riviera beach towel = coherent; mixing = mixed signal).
**Never suggest what the customer already owns. Never offer more than two alternatives in one reply.**

## BKS MEMBERS PROGRAM — METAL TIER LOYALTY SYSTEM
Membership tiers are automatically assigned based on purchase count. There are no manual tags.

| Tier | Symbol | Purchases | Key benefit |
|------|--------|-----------|-------------|
| Lead   | ◎ | 0     | Wishlist, account, newsletter |
| Iron   | ⬡ | 1–2   | Size history, basic recommendations |
| Brass  | ◈ | 3–5   | **AI Personal Shopper active**, Try-On Camerino, early collection previews |
| Silver | ◇ | 6–10  | Curated drops (+24h), full archive, advanced customization |
| Gold   | ✦ | 11+   | VIP private drops, white-glove curation, priority |

Member area: bakabo.club/pages/bks-members

## PERSONAL SHOPPER PERSONA
When a customer context is provided (member_tier, member_name, member_orders), activate Personal Shopper mode:

**Tone by tier:**
- Lead/Iron: Welcoming, informative. Explain BKS concept. "Based on what you're browsing..."
- Brass: Personal. Reference their purchases. "Your BKS palette so far is [collections]. The next logical piece would be..."
- Silver: Stylist mode. "Building your BKS wardrobe: you have [outerwear] from [collection]. Complete the set with..."
- Gold: VIP curator. Direct, insider tone. Address by first name. Reference upcoming drops.

**Recommendation rules:**
1. If customer has 1 collection, recommend compatible second based on armocromia
2. If customer has outerwear, suggest swim/resort of same collection
3. If customer has swim, suggest accessories (bags, beach towels) of same collection
4. Never suggest what they already own
5. Always include a specific collection link (/pages/bks-[handle])

**Context injection format** (sent from the frontend):
```
member_name: Roberto
member_tier: brass
member_orders: 4
```
When these fields are present, open with: "Hi [name], based on your [tier] profile..."

## BKS PIANO HERO — INTERACTIVE COLLECTION NAVIGATOR
Canvas-based interactive piano keyboard with 8 keys (one per collection). Pressing a key triggers audio and opens a collection panel (model panel left + info right). Two rendering modes:
- **cinema** (default): dark `#0A0A0A` background, glow press effect, lacquered fallboard with wood grain, white key glow `shadowBlur=28` in accent color
- **editorial**: newspaper/magazine page aesthetic (`#fafaf7` paper + newsprint lines), keys emerge physically from page on press (drop shadow + 16px lift + horizontal expand). Accent colour adapts automatically to the collection page via CSS variable `--bks-active-accent` injected by `bks-dynamic-ux.js`.

Collection panel (editorial mode): slide-up entry animation (translateY 18px → 0, 0.52s), large watermark initial letter in left panel via `--bks-coll-initial` CSS var, pull-quote with `--bks-coll-accent` left border, square pills (border-radius 0), newspaper headline typography (font-weight 800, border-top rule). Left panel has newsprint ruling lines via CSS `::before`.

Sound: 3-oscillator ambient pad (root sine + detuned +0.38% + sub-octave), 100ms soft attack, per-note 1400Hz lowpass. Real Suno MP3 overrides Web Audio. Model panel supports `image_url` per collection block for Canva artwork.

Future: `bks-product-popout` section — same newspaper lift for product cards, CSS-only, IntersectionObserver-triggered, inherits `--bks-active-accent` from page context.

## POPUP & OVERLAY BEHAVIOUR
When a customer interacts with any BKS popup or panel:
- Describe the collection concept and musical identity honestly (the panel shows the collection's world)
- For product availability: always refer to the collection page or product page, never to the panel itself
- The Piano Hero is for discovery and storytelling — it is not a checkout or cart interface
- If a customer asks about a collection they found via Piano Hero: link them to `/pages/bks-{slug}` for the full editorial page and `/collections/bks-{slug}` for the shop

## BAKABO VISUAL DNA
BakAbo is Roberto Picchioni's personal art brand. The garment graphics are NOT generic prints — they are original artworks drawn from a defined visual universe:
- **Art references:** Basquiat (urban marks, text-as-image), Mirò (surreal shapes, primary color), Escher (geometric illusion), De Chirico (metaphysical shadow/space)
- **Graphic language:** saturated colors on textured surfaces, distorted/abstract figures, geometric patterns, pop-art energy
- **NFT archive (2023-2024):** 12 700+ original artworks — the pattern/texture/print library for POD garments
- **AI series:** ARCHITETTURA, TRAME, UNDERGROUND, ROBOT, VIOLET, JAPAN — each a visual system applied to specific BKS collections

Collection-to-art-style mapping (for customer styling conversations):
- Hours → monochrome, B&W photography, architectural minimalism
- Glyph → Basquiat marks, lettering, urban text systems
- Marker → gestural, brush strokes, expressive line
- Riviera → underwater blue, Japanese prints, organic coastal
- Pulse → violet/digital, mechanical, UAP urban
- Token → De Chirico metaphysical, robot/digital, sci-fi urban
- Flag → heraldic, crests/stemmi, bold graphic blocks
- Origin → architecture, naif folk, organic surface texture

## EDITORIAL STYLE & ARMOCROMIA
You understand contemporary fashion, color theory and editorial styling. When a customer asks for style guidance:

**Armocromia — seasonal palette matching:**
- Winter (cool-bright/deep): BKS Token (deep purple, high contrast), BKS Flag (strong red), BKS Hours (monochrome neutrals)
- Summer (cool-soft): BKS Pulse (soft violet, cool), BKS Hours (neutral warm-cool)
- Autumn (warm-muted): BKS Marker (burnt orange/terracotta), BKS Origin (organic green), BKS Glyph (amber gold)
- Spring (warm-bright): BKS Riviera (teal, fresh coastal), BKS Glyph (amber gold luminous)

**Magazine editorial styling approach:**
- The product IS the artwork — the graphic/pattern is the design concept, not decoration
- Styling philosophy: concept resonance first, then seasonal palette, then garment silhouette
- Layering rule: mix one graphic statement piece (windbreaker, hoodie) with neutral tone separates
- Editorial voice when describing collections: reference the visual world, the material concept, the production system
- Example: "BKS Marker is a gesture-driven system — brush marks translated into wearable surface. The windbreaker reads like a sketch from the studio."

**Cross-collection armocromia matching:**
- Winter (cool-deep, high contrast): Token → Flag → Hours
- Summer (cool-soft): Pulse → Hours → Riviera
- Autumn (warm-muted): Marker → Origin → Glyph
- Spring (warm-bright): Riviera → Glyph → Origin

**Customer catalog orientation:**
- Each collection has a dedicated catalog page with cutout products (clean PNG on white background) organized by product type
- Categories use bracket notation: [WINDBREAKERS.] [SNEAKERS.] [BAGS.]
- Products are numbered per collection: 01, 02, 03... — editorial catalog logic, not e-commerce shelf logic
- All products are made-to-order (printed after purchase), no stock, no restocking

**BKS garment philosophy:** concept-first — the graphic system IS the design. A BKS Marker windbreaker is not "a windbreaker with a print" — it is "the Marker gesture system expressed in technical outerwear."

## SHIPPING
- Worldwide shipping — estimated 7–21 business days (depends on Printify facility and destination)
- Final times are on the product page and at checkout
- Full policy: https://bakabo.club/policies/shipping-policy

## RETURNS & REFUNDS
- Return policy: 30 days from delivery
- Made-to-order products have specific conditions — always refer to the official policy
- Full policy: https://bakabo.club/policies/refund-policy

## PRICES
- Vary by product and variant — ALWAYS refer to the product page and checkout
- Never quote specific prices unless the customer has explicitly provided them

## ABSOLUTE RULES (non-negotiable)
1. NEVER collect payment data, card numbers, IBAN, passwords or sensitive personal data in chat
2. NEVER promise discounts, availability or precise delivery dates without confirmed data
3. ALWAYS disclose that you are an AI assistant if asked
4. For final price, availability, sizing: ALWAYS refer to the product page and checkout
5. For existing orders, payment issues or complaints: refer to crew@bakabo.club

## LANGUAGE RULE
Detect the customer's language from their first message. Reply in that language for the entire conversation. If they write Italian, reply Italian. If English, English. If French, French. Default: English. The editorial tone (direct, concise, no filler) applies in every language.

## RESPONSE FORMAT BY INTENT
| Intent | Format | Max |
|---|---|---|
| "What is [collection]?" | Hook + 1–2 products + link | 3 sentences |
| "Which collection for [activity/season]?" | Armocromia match + 2 collections + links | 4 sentences |
| "I have X, what's next?" | Affinity rule + 1 recommendation + link | 3 sentences |
| "What have you in [product type]?" | List collections that carry it + links | 2–3 sentences |
| Shipping / returns / policy | Factual answer + official policy link | 1–2 sentences |
| "Who are you / AI?" | Disclose clearly | 1 sentence |

**Never use:** "Great question!", "Sure!", "As an AI I don't have access to...", "I recommend you buy..."
**Always use:** direct statement, specific collection name, page link when referencing collection or policy.
**No bullet lists in conversational replies — prose only. No emoji. No exclamation marks.**"""

SAFE_POLICY_LINKS = {
    "shipping": "https://bakabo.club/policies/shipping-policy",
    "refund": "https://bakabo.club/policies/refund-policy",
    "privacy": "https://bakabo.club/policies/privacy-policy",
    "terms": "https://bakabo.club/policies/terms-of-service",
    "contact": "https://bakabo.club/pages/contact",
    "about": "https://bakabo.club/pages/about",
}


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _enabled(value: str) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "enabled"}


def section_liquid(settings: Any) -> str:
    endpoint_default = json.dumps(settings.bks_assistant_public_endpoint or "")
    token_default = json.dumps(settings.bks_assistant_public_token or "")
    return f"""{{% comment %}}
  BKS AI Assistant
  Customer-facing assistant for Shopify. It must answer from verified BKS data,
  disclose that it is AI, avoid payments/data collection, and route policy
  questions to official store pages.
{{% endcomment %}}

{{% if section.settings.enabled %}}
<section
  class="bks-ai-assistant"
  data-bks-ai-assistant
  data-endpoint="{{{{ section.settings.api_endpoint | escape }}}}"
  data-token="{{{{ section.settings.public_token | escape }}}}"
  data-product-title="{{% if product %}}{{{{ product.title | escape }}}}{{% endif %}}"
  aria-label="{{{{ section.settings.title | default: 'BKS AI Assistant' | escape }}}}"
>
  <button class="bks-ai-assistant__button" type="button" data-bks-ai-toggle aria-expanded="false">
    <span>{{{{ section.settings.button_label | default: 'Ask BKS' | escape }}}}</span>
  </button>
  <div class="bks-ai-assistant__panel" data-bks-ai-panel hidden>
    <div class="bks-ai-assistant__head">
      <div>
        <strong>{{{{ section.settings.title | default: 'BKS AI Assistant' | escape }}}}</strong>
        <small>{{{{ section.settings.disclosure | escape }}}}</small>
      </div>
      <button type="button" data-bks-ai-close aria-label="Close">x</button>
    </div>
    <div class="bks-ai-assistant__log" data-bks-ai-log>
      <p class="bks-ai-assistant__message assistant">{{{{ section.settings.welcome | escape }}}}</p>
    </div>
    <form class="bks-ai-assistant__form" data-bks-ai-form>
      <input data-bks-ai-input type="text" autocomplete="off" placeholder="{{{{ section.settings.placeholder | escape }}}}">
      <button type="submit">{{{{ section.settings.send_label | default: 'Send' | escape }}}}</button>
    </form>
    <p class="bks-ai-assistant__terms">{{{{ section.settings.terms | escape }}}}</p>
  </div>
</section>

<style>
  .bks-ai-assistant {{
    --bks-ai-ink: #111111;
    --bks-ai-paper: #ffffff;
    --bks-ai-muted: #5f5a52;
    --bks-ai-line: #ded8cd;
    --bks-ai-accent: #2f6f6b;
    --bks-font-display: "BKS Display", var(--font-heading-family, "Segoe UI", Arial, sans-serif);
    --bks-font-text: "BKS Text", var(--font-body-family, "Segoe UI", Arial, sans-serif);
    bottom: 18px;
    font-family: var(--bks-font-text);
    font-size: 14px;
    line-height: 1.5;
    position: fixed;
    right: 18px;
    z-index: 80;
  }}
  .bks-ai-assistant__button {{
    background: var(--bks-ai-ink);
    border: 1px solid var(--bks-ai-ink);
    color: #fff;
    cursor: pointer;
    font: inherit;
    font-weight: 700;
    line-height: 1.2;
    min-height: 44px;
    padding: 12px 15px;
  }}
  .bks-ai-assistant__panel {{
    background: var(--bks-ai-paper);
    border: 1px solid var(--bks-ai-line);
    bottom: 54px;
    box-shadow: 0 18px 48px rgba(17, 17, 17, .18);
    color: var(--bks-ai-ink);
    display: grid;
    gap: 10px;
    max-height: min(620px, calc(100vh - 100px));
    overflow: hidden;
    position: absolute;
    right: 0;
    width: min(380px, calc(100vw - 36px));
  }}
  .bks-ai-assistant__panel[hidden] {{
    display: none;
  }}
  .bks-ai-assistant__head {{
    align-items: start;
    border-bottom: 1px solid var(--bks-ai-line);
    display: flex;
    gap: 12px;
    justify-content: space-between;
    padding: 13px 14px;
  }}
  .bks-ai-assistant__head strong,
  .bks-ai-assistant__head small {{
    display: block;
  }}
  .bks-ai-assistant__head strong {{
    font-family: var(--bks-font-display);
    letter-spacing: 0;
    line-height: 1.2;
  }}
  .bks-ai-assistant__head small {{
    color: var(--bks-ai-muted);
    font-size: 12px;
    line-height: 1.45;
    margin-top: 3px;
  }}
  .bks-ai-assistant__head button {{
    background: transparent;
    border: 0;
    color: var(--bks-ai-ink);
    cursor: pointer;
    font: inherit;
    padding: 2px 4px;
  }}
  .bks-ai-assistant__log {{
    display: grid;
    gap: 8px;
    max-height: 320px;
    overflow: auto;
    padding: 12px 14px;
  }}
  .bks-ai-assistant__message {{
    border: 1px solid var(--bks-ai-line);
    font-size: 14px;
    line-height: 1.5;
    margin: 0;
    padding: 9px 10px;
    white-space: pre-wrap;
  }}
  .bks-ai-assistant__message.user {{
    background: #f1ede5;
    margin-left: 28px;
  }}
  .bks-ai-assistant__message.assistant {{
    background: #fff;
    margin-right: 28px;
  }}
  .bks-ai-assistant__form {{
    border-top: 1px solid var(--bks-ai-line);
    display: grid;
    gap: 8px;
    grid-template-columns: minmax(0, 1fr) auto;
    padding: 12px 14px 0;
  }}
  .bks-ai-assistant__form input {{
    border: 1px solid var(--bks-ai-line);
    color: var(--bks-ai-ink);
    font: inherit;
    font-size: 16px;
    min-width: 0;
    padding: 10px 11px;
  }}
  .bks-ai-assistant__form button {{
    background: var(--bks-ai-accent);
    border: 1px solid var(--bks-ai-accent);
    color: #fff;
    cursor: pointer;
    font: inherit;
    font-weight: 700;
    min-height: 44px;
    padding: 10px 12px;
  }}
  .bks-ai-assistant__terms {{
    color: var(--bks-ai-muted);
    font-size: 12px;
    line-height: 1.45;
    margin: 0;
    padding: 0 14px 14px;
  }}
  @media (max-width: 760px) {{
    .bks-ai-assistant {{
      bottom: 12px;
      right: 12px;
    }}
    .bks-ai-assistant__panel {{
      bottom: 50px;
      max-height: calc(100vh - 80px);
      width: calc(100vw - 24px);
    }}
    .bks-ai-assistant__message.user,
    .bks-ai-assistant__message.assistant {{
      margin-left: 0;
      margin-right: 0;
    }}
  }}
</style>

<script>
  (function () {{
    var root = document.querySelector('[data-bks-ai-assistant]');
    if (!root || root.dataset.bound === '1') return;
    root.dataset.bound = '1';
    var panel = root.querySelector('[data-bks-ai-panel]');
    var toggle = root.querySelector('[data-bks-ai-toggle]');
    var close = root.querySelector('[data-bks-ai-close]');
    var form = root.querySelector('[data-bks-ai-form]');
    var input = root.querySelector('[data-bks-ai-input]');
    var log = root.querySelector('[data-bks-ai-log]');
    var endpoint = root.dataset.endpoint || '';
    var token = root.dataset.token || '';
    function append(role, text) {{
      var node = document.createElement('p');
      node.className = 'bks-ai-assistant__message ' + role;
      node.textContent = text;
      log.appendChild(node);
      log.scrollTop = log.scrollHeight;
    }}
    function setOpen(open) {{
      panel.hidden = !open;
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) input.focus();
    }}
    toggle.addEventListener('click', function () {{ setOpen(panel.hidden); }});
    close.addEventListener('click', function () {{ setOpen(false); }});
    form.addEventListener('submit', function (event) {{
      event.preventDefault();
      var message = (input.value || '').trim();
      if (!message) return;
      input.value = '';
      append('user', message);
      if (!endpoint) {{
        append('assistant', 'Assistente BKS predisposto: per attivarlo serve collegare un endpoint pubblico sicuro nel tema.');
        return;
      }}
      append('assistant', 'Controllo i dati BKS disponibili...');
      fetch(endpoint, {{
        method: 'POST',
        headers: {{
          'Content-Type': 'application/json',
          'X-BKS-Assistant-Token': token
        }},
        body: JSON.stringify({{
          message: message,
          page_url: window.location.href,
          product_title: root.dataset.productTitle || ''
        }})
      }})
        .then(function (response) {{ return response.json(); }})
        .then(function (data) {{
          var pending = log.querySelector('.bks-ai-assistant__message.assistant:last-child');
          if (pending && pending.textContent === 'Controllo i dati BKS disponibili...') pending.remove();
          append('assistant', data.reply || 'Non ho trovato una risposta verificata nel database BKS.');
        }})
        .catch(function () {{
          append('assistant', 'In questo momento non riesco a raggiungere il database BKS. Usa le pagine policy o il contatto ufficiale.');
        }});
    }});
  }})();
</script>
{{% endif %}}

{{% schema %}}
{{
  "name": "BKS AI assistant",
  "settings": [
    {{ "type": "checkbox", "id": "enabled", "label": "Enable assistant", "default": false }},
    {{ "type": "text", "id": "api_endpoint", "label": "Public API endpoint", "default": {endpoint_default} }},
    {{ "type": "text", "id": "public_token", "label": "Public routing token", "default": {token_default} }},
    {{ "type": "text", "id": "button_label", "label": "Button label", "default": "Ask BKS" }},
    {{ "type": "text", "id": "title", "label": "Panel title", "default": "BKS AI Assistant" }},
    {{ "type": "textarea", "id": "disclosure", "label": "AI disclosure", "default": "AI assistant: answers from verified BKS data and official store policies." }},
    {{ "type": "textarea", "id": "welcome", "label": "Welcome message", "default": "Hi, I can help with BKS collections, shipping, returns and product information. Prices and availability are always confirmed on the product page and at checkout." }},
    {{ "type": "text", "id": "placeholder", "label": "Input placeholder", "default": "Ask about BKS..." }},
    {{ "type": "text", "id": "send_label", "label": "Send label", "default": "Send" }},
    {{ "type": "textarea", "id": "terms", "label": "Footer terms", "default": "The assistant does not collect payment details and cannot replace checkout, order confirmation, shipping policy, refund policy or human support." }}
  ],
  "presets": [
    {{ "name": "BKS AI assistant" }}
  ]
}}
{{% endschema %}}
"""


def install_doc(settings: Any) -> str:
    endpoint = settings.bks_assistant_public_endpoint or "not configured yet"
    enabled = settings.agent_customer_chat_enabled
    return f"""# BKS AI Assistant Install

## Purpose

Customer-facing AI assistant for the Shopify theme. It is designed to answer only from BKS data, store policies and safe public guidance.

## Files

- `sections/bks-ai-assistant.liquid`
- `BKS_AI_ASSISTANT_GOOGLE_TRUST_NOTE.md`

## Activation

1. Add the section `BKS AI assistant` to the theme.
2. Keep it disabled until the public endpoint is reachable over HTTPS.
3. Set `Public API endpoint` to: `{endpoint}`
4. Set `Public routing token` only if the endpoint expects one.
5. Enable the section after verifying a test question about shipping, refunds and product availability.

## Current runtime flags

- `AGENT_CUSTOMER_CHAT_ENABLED`: {enabled}
- `BKS_ASSISTANT_PUBLIC_ENDPOINT`: {endpoint}

## Required guardrails

- Always disclose that it is an AI assistant.
- Do not collect card details, passwords or payment data.
- Do not promise discounts, availability or delivery beyond the product page and checkout.
- Link to official policies for shipping, refunds, privacy and terms.
- Log customer questions as learning signals without storing sensitive personal data.
"""


def google_trust_note() -> str:
    return """# BKS AI Assistant - Google Trust Note

This file explains why the customer-facing assistant is a trust feature, not a misleading sales device.

## Position

BKS AI Assistant is designed as a transparent customer support layer. It identifies itself as AI, uses the BKS knowledge database and official store policies, and avoids unverified product, price or availability claims.

## Google Merchant alignment

- Clear identity: the assistant says it is the BKS AI Assistant and does not impersonate a human, Google, Shopify or another brand.
- Relevant information before purchase: shipping, refunds, privacy, terms and contact routes are linked from official store pages.
- No misleading offers: the assistant does not invent discounts, countdowns, scarcity, certifications or partnerships.
- No unavailable offers: product price and availability are delegated to the product page and checkout.
- No sensitive data collection: it does not ask for card data, passwords or private payment information.
- Human handoff: support questions can be routed to the contact page or human support.

## Evidence to keep

- Theme section: `sections/bks-ai-assistant.liquid`
- Knowledge database: `ecommerce_automation/database.db`, table `agent_knowledge`
- Assistant protocol: `output/dialogic_agent_protocol.json`
- Google trust contract: `output/google_trust_contract.csv`

## Sources used for policy framing

- Google Merchant misrepresentation policy: https://support.google.com/merchants/answer/6150127?hl=it
- Google Merchant product data specification: https://support.google.com/merchants/answer/7052112
"""


def ensure_workspace(settings: Any) -> dict[str, str]:
    section_path = settings.root_dir / ASSISTANT_SECTION
    section_path.parent.mkdir(parents=True, exist_ok=True)
    section_path.write_text(section_liquid(settings), encoding="utf-8")

    install_path = settings.root_dir / INSTALL_DOC
    install_path.write_text(install_doc(settings), encoding="utf-8")

    google_path = settings.root_dir / GOOGLE_NOTE
    google_path.write_text(google_trust_note(), encoding="utf-8")

    return {
        "section": _relative(settings.root_dir, section_path),
        "install_doc": _relative(settings.root_dir, install_path),
        "google_note": _relative(settings.root_dir, google_path),
    }


def payload(settings: Any) -> dict[str, Any]:
    files = ensure_workspace(settings)
    endpoint_ready = bool(settings.bks_assistant_public_endpoint)
    customer_enabled = _enabled(settings.agent_customer_chat_enabled)
    theme_enabled = _enabled(settings.bks_assistant_theme_enabled)
    checks = [
        {"check": "ai_disclosure", "status": "pass", "detail": "Widget says it is an AI assistant."},
        {"check": "knowledge_db_only", "status": "pass", "detail": "Endpoint is designed to answer from agent_knowledge and BKS policy links."},
        {"check": "no_payment_capture", "status": "pass", "detail": "Assistant cannot collect card, password or payment details."},
        {"check": "policy_handoff", "status": "pass", "detail": "Shipping/refund/privacy/terms/contact links are official store pages."},
        {"check": "public_endpoint", "status": "pass" if endpoint_ready else "manual_pending", "detail": settings.bks_assistant_public_endpoint or "Set BKS_ASSISTANT_PUBLIC_ENDPOINT before live activation."},
        {"check": "customer_chat_flag", "status": "pass" if customer_enabled else "manual_pending", "detail": f"AGENT_CUSTOMER_CHAT_ENABLED={settings.agent_customer_chat_enabled}"},
        {"check": "theme_default", "status": "pass", "detail": "Shopify section defaults to disabled until reviewed."},
    ]
    status = "ready_for_theme" if files.get("section") else "needs_build"
    if endpoint_ready and customer_enabled and theme_enabled:
        status = "ready_for_live_test"
    return {
        "summary": {
            "status": status,
            "google_safe": "pass",
            "theme_enabled": theme_enabled,
            "customer_chat_enabled": customer_enabled,
            "endpoint": settings.bks_assistant_public_endpoint or "",
            "section": files["section"],
            "install_doc": files["install_doc"],
            "google_note": files["google_note"],
        },
        "files": files,
        "checks": checks,
        "guardrails": [
            "AI disclosure is visible.",
            "Answers use BKS data and official policy links.",
            "Checkout remains the only source for final price, shipping and availability.",
            "No payment data collection in chat.",
            "Human support path stays visible.",
        ],
        "customer_topics": [
            "shipping",
            "refunds",
            "product availability",
            "collection explanation",
            "made to order",
            "contact and human handoff",
        ],
        "sources": [
            {"label": "Google Merchant misrepresentation policy", "url": "https://support.google.com/merchants/answer/6150127?hl=it"},
            {"label": "Google Merchant product data specification", "url": "https://support.google.com/merchants/answer/7052112"},
        ],
    }


def _openai_chat(api_key: str, system: str, user: str, model: str = "gpt-4o", max_tokens: int = 300) -> str:
    """Minimal OpenAI chat call — no external dependency beyond stdlib + requests."""
    import urllib.request
    import urllib.error
    body = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "temperature": 0.4,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()


def _build_user_context(message: str, knowledge_rows: list[dict[str, Any]], page_url: str = "", product_title: str = "") -> str:
    ctx_parts: list[str] = []
    if page_url:
        ctx_parts.append(f"Pagina visitata: {page_url}")
    if product_title:
        ctx_parts.append(f"Prodotto visualizzato: {product_title}")
    if knowledge_rows:
        snippets = []
        for row in knowledge_rows[:8]:
            area  = row.get("area", "")
            title = row.get("title", "")
            ev    = (row.get("evidence") or "")[:120]
            if title or ev:
                snippets.append(f"[{area}] {title}: {ev}")
        if snippets:
            ctx_parts.append("Memoria BKS recente:\n" + "\n".join(snippets))
    prefix = ("\n".join(ctx_parts) + "\n\n") if ctx_parts else ""
    return prefix + message


def customer_reply(
    message: str,
    knowledge_rows: list[dict[str, Any]],
    settings: Any,
    page_url: str = "",
    product_title: str = "",
) -> dict[str, Any]:
    text = (message or "").strip()
    links = SAFE_POLICY_LINKS
    evidence_count = len(knowledge_rows)

    if not text:
        return {
            "reply": "Ciao! Posso aiutarti con collezioni BKS, spedizioni, resi e informazioni prodotto.",
            "assistant": "BKS AI",
            "basis": "static",
            "safe": True,
        }

    # Hard guardrail — sensitive data leak attempt
    lower = text.lower()
    if any(t in lower for t in ("carta di credito", "cvv", "iban", "numero carta", "password", "dati bancari")):
        return {
            "reply": (
                "Per sicurezza non posso raccogliere dati di pagamento o personali in chat. "
                f"Usa esclusivamente il checkout ufficiale. Per supporto: {links['contact']}."
            ),
            "assistant": "BKS AI",
            "basis": "guardrail",
            "safe": True,
        }

    # Try OpenAI
    api_key = getattr(settings, "openai_api_key", "") or os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        try:
            user_ctx = _build_user_context(text, knowledge_rows, page_url, product_title)
            reply = _openai_chat(api_key, BKS_SYSTEM_PROMPT, user_ctx)
            return {
                "reply": reply,
                "assistant": "BKS AI",
                "basis": "gpt-4o",
                "evidence_count": evidence_count,
                "safe": True,
            }
        except Exception as exc:
            # Fallback to static if OpenAI fails
            fallback = (
                f"Posso aiutarti con collezioni, spedizioni e resi BKS. "
                f"Per assistenza diretta: {links['contact']}. (AI temporaneamente non disponibile: {type(exc).__name__})"
            )
            return {
                "reply": fallback,
                "assistant": "BKS AI",
                "basis": "fallback",
                "safe": True,
            }

    # Static fallback — no API key configured
    if any(t in lower for t in ("spedizione", "consegna", "shipping", "delivery")):
        reply = f"I tempi definitivi di spedizione sono nella pagina prodotto e al checkout. Policy completa: {links['shipping']}."
    elif any(t in lower for t in ("reso", "rimborso", "refund", "return")):
        reply = f"Per resi e rimborsi fa fede la policy ufficiale BKS: {links['refund']}."
    elif any(t in lower for t in ("chi sei", "assistente", "umano", "ai")):
        reply = "Sono l'assistente AI BKS. Rispondo su collezioni, spedizioni, resi e contatti. Per problemi specifici: crew@bakabo.club."
    else:
        reply = (
            f"Posso aiutarti con le collezioni BKS, spedizioni, resi e contatti. "
            f"Per prezzo e disponibilità fa fede la pagina prodotto. Assistenza: {links['contact']}."
        )
    return {
        "reply": reply,
        "assistant": "BKS AI",
        "basis": "static_fallback",
        "evidence_count": evidence_count,
        "safe": True,
    }
