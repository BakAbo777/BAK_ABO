---
name: bakabo-page-by-page
description: >
  Per-page design spec for every page on bakabo.club. Use this skill when:
  designing or auditing a specific page, checking for duplicate content across
  pages, ensuring each page has one clear job, optimizing section order, or
  verifying that all 43 live pages have distinct non-redundant content.
  Works with bakabo-ui-components (card system), bakabo-armocromia (color),
  bakabo-editorial-typographer (type), bakabo-product-copy (product pages).
metadata:
  type: skill
  version: "1.0"
  created: "2026-06-22"
---

# BKS — Per-Page Design Spec

## 0. Anti-duplication rule (critical)

Every page has EXACTLY ONE job. If two pages do the same job, one is eliminated.
Current live pages: 43. Each is mapped below with its single job.

---

## 1. HOME — /

**Job:** Convert the visitor's first 3 scrolls into curiosity about BKS as an AI-art atelier.

**Section order (canonical):**
1. Video Hero (4–8 avatar clips, 95svh) — brand mood
2. Piano Hero (8 collection keys, CDN images) — collection map
3. Weekly Editorial masthead — brand voice
4. Magazine section (featured editorial) — story
5. Trust/service bar — trust signals
6. Store Reviews — social proof

**Anti-patterns:** countdown timers, sale banners, more than 2 CTAs above fold.

---

## 2. COLLECTION EDITORIAL PAGES — /pages/bks-[collection] (×8)

**Job:** Immerse the visitor in ONE collection world and convert to product browsing.

**Sections per page:**
1. Collection Hero (2-col: editorial copy left, lifestyle image right)
2. Collection Signal bar (accent color, tagline, key products)
3. Product grid filtered by collection tag
4. Editorial pull-quote (one line from the collection concept)
5. Cross-collection suggestion (2 affinities max)

**Unique content per collection — NO shared copy blocks:**
- Hours: urban stillness, monochrome, measured layers
- Glyph: graphic sign language, BKS codes, constructed marks
- Marker: gesture and motion, brush energy, urban marks
- Riviera: coastal geometry, Mediterranean resort, teal
- Pulse: optical movement, kinetic fields, geometric rhythm
- Token: digital objects, pixel/arcade, encoded
- Flag: graphic fields, pop-collage, bold color blocks
- Origin: invented narrative marks, figurative, naif widest range

**Duplicate prevention:** Never put the same tagline on two collection pages.

---

## 3. PRODUCT TYPE PAGES — /pages/bks-[type] (×15 confirmed live)

**Job:** Show all products of ONE type across all collections.

**Sections:**
1. Type Hero — DM Mono kicker "PRODUCT TYPE", Bebas Neue name, one-line spec
2. Filter chips — by collection (8 chips, collection color dot only)
3. Product grid — filtered by product_type tag
4. Cross-type suggestion — "You might also like: [related type]"

**Each type page has a distinct spec line:**
- Puffer Jackets: edge-to-edge AOP, water-resistant shell, full front zip
- Windbreakers: lightweight woven, packable, AOP front + back panels
- Pullover Hoodies: mid-weight fleece, kangaroo pocket, ribbed cuffs
- Swim Trunks: quick-dry, mesh lining, drawstring, AOP both sides
- Swimwear: UPF50, one-piece or tankini, chlorine-resistant
- One-Piece Swimsuits: AOP full coverage, UPF50, adjustable straps
- Racerback Dresses: athletic-cut, stretch AOP, racerback silhouette
- Athletic Shorts: moisture-wicking, elastic waist, side pockets
- Lounge Pants: soft knit, elastic waist, full-leg AOP
- Sneakers: canvas/faux-leather, AOP panels, rubber sole
- Flip Flops: EVA sole, AOP strap, beach/pool ready
- Backpacks: structured, AOP front panel, laptop sleeve
- Travel Bags: waterproof AOP shell, carry/shoulder handles
- Hawaiian Shirts: woven AOP, button-front, camp collar
- Beach Towels: 100% microfiber, edge-to-edge AOP

---

## 4. BKS MEMBERS — /pages/bks-members

**Job:** Deliver immediate tier value within 60 seconds of arrival.

**Sections:**
1. Gold Ring + tier badge (account icon top right, arrival animation)
2. Tier dashboard — current tier, progress bar, next unlock
3. Wishlist tab — items saved, quick-add to cart
4. Try-On Camerino tab (Brass+) — AI try-on interface
5. Order history + size memory tab
6. Early Access banner (if drop within 72h)

**Anti-pattern:** Empty tabs. Every tab must have a non-empty default state.

---

## 5. BKS VERSE — /pages/verse

**Job:** Explain the Poesia→Oggetto platform and convert poets to participate.

**Sections:**
1. Intro — "Dalla Poesia all'Oggetto" headline + one-para concept
2. How it works — 3 steps: submit poem → Gran Giudice scores → win production
3. Leaderboard preview (top 5 poets)
4. Submission CTA (Brass+ gate)
5. Hall of Fame teaser → /pages/verse-hall

---

## 6. BKS MAN / BKS WOMAN — /pages/bks-men, /pages/bks-woman

**Job:** Gender-oriented collection and product type navigation guide.

**Sections:**
1. Editorial kicker "For Him" / "For Her"
2. Curated product type chips (top 5 per gender)
3. Recommended collections (3 max with brief)
4. Armocromia quick-reference (seasonal palette → collection match)
5. Featured product grid (filtered by gender-relevant product types)

**Distinct content:** Men: puffer, windbreaker, swim trunks, sneakers, travel bag.
Women: dress, one-piece, swimwear, hoodie, flip flops, beach towel.

---

## 7. SHOPPING GUIDE — /pages/bks-shopping-guide

**Job:** Help undecided visitors find their collection via armocromia/style quiz.

**Sections:**
1. Introduction — "Find your BKS collection"
2. Armocromia guide (season → collection map, visual)
3. Style profile cards (4 archetypes: urban/coastal/graphic/playful)
4. Collection selector → links to editorial pages
5. AI Ask BKS prompt: "Tell me about your style →"

---

## 8. ABOUT BAKABO — /pages/about-bakabo-1

**Job:** Establish brand credibility and the AI-art atelier story.

**Sections:**
1. Studio origin — Roberto Picchioni, BKS Studio, Italy
2. The AI-art process — from prompt to print
3. Print-on-demand model — why no warehouse
4. The 8 collection worlds — quick map
5. Contact + social channels

---

## 9. FAQ — /pages/faq-domande-frequenti

**Job:** Answer the 10 most common questions before checkout to reduce abandonment.

**Top 10 questions (non-negotiable):**
1. Quanto ci vuole per ricevere il mio ordine? (7-14 + 3-5 days)
2. Posso restituire / cambiare taglia? (30 days, crew@)
3. Come funziona il made-to-order? (printed after purchase)
4. I prodotti sono di qualità? (Printify specs, EU warranty)
5. Posso personalizzare un prodotto? (text +€15, crew@)
6. Come funziona il Metal tier? (Lead/Iron/Brass/Silver/Gold)
7. Cos'è il Camerino Try-On? (AI virtual try-on, Brass+)
8. Come pago? (all Shopify methods, Stripe/PayPal)
9. Spedite in tutta Europa / USA? (yes, via Printify)
10. Come contatto l'assistenza? (crew@bakabo.club, Shopify Inbox)

---

## 10. WISHLIST — /pages/bks-wishlist

**Job:** Show the member's saved items and convert wishlist to cart.

**Sections:**
1. Wishlist grid — saved products with price, add-to-cart
2. Empty state: "Save pieces you love — heart any product to add it here"
3. Tier upsell if Lead/Iron: "Brass members get notified on restocks"

---

## 11. CONTACT — /pages/contact

**Job:** Route customer to the right contact channel.

**Content:**
- crew@bakabo.club for orders/returns/general
- Shopify Inbox for quick questions
- Social: @bakabofirm (Instagram, YouTube)
- Response time: within 24h business days

---

## 12. BKS CUSTOM — /pages/bks-custom

**Job:** Convert visitors who want personalization to a custom order inquiry.

**Sections:**
1. What's possible — text on back/front/sleeve, position choice
2. Pricing — +€15 for text customization
3. How to order — email crew@ with product + text + position
4. Examples (if available)

---

## 13. DUPLICATE PREVENTION MAP

| Handle | Status | Action if duplicate found |
|--------|--------|--------------------------|
| /bks-faq | Template: page (wrong template) | Delete or redirect to /faq-domande-frequenti |
| /help-faq | Template: default (wrong template) | Delete or redirect to /faq-domande-frequenti |
| /bks-collections | Panoramica (OK if distinct from collection editorial pages) | Keep if it's an overview grid, delete if it repeats hub |

**Rule:** If two pages answer the same question, the one with the wrong template is deleted.
The canonical page is always the one with the correct template suffix.
