---
name: bakabo-pages-design
description: Use this skill when redesigning, auditing, or producing a brief for any page of bakabo.club — page-by-page methodology covering scope, mandatory content, block structure, UX rules, KPIs, and accessibility per page type. Triggers include "redesign the homepage", "what should go on the product page", "audit the cart flow", "what does the about page need", producing acceptance criteria for a designer's deliverable, or planning the site's information architecture. Works alongside bakabo-design-system (visual tokens) and bakabo-brand (voice). Do not use for code-level theme work (use bakabo-theme-build) or for individual product copy structure (use bakabo-product-copy).
---

# BakAbo Pages — Redesign Methodology

The companion to `bakabo-design-system`. The design system defines *how things should look*; this skill defines *what each page must contain, in what order, and why*. Together they cover the full target.

Use this skill in three modes:
1. **Generative:** starting from scratch, produce a complete brief for a given page type
2. **Audit:** open the current page and check it against the spec; output what's missing or misplaced
3. **Acceptance:** evaluate a designer's deliverable against the same spec

## 1. The page-design framework

Every page in the site, regardless of type, is analyzed across six dimensions. When auditing or producing a brief, walk all six.

| # | Dimension | Question |
|---|---|---|
| 1 | **Scope** | What is the *one* job this page must do? |
| 2 | **Content** | What must be present? What must not? |
| 3 | **Structure** | What is the block order, top to bottom? |
| 4 | **UX rules** | What page-specific interaction rules apply? |
| 5 | **KPIs** | How do we measure this page is working? |
| 6 | **Accessibility** | What page-specific a11y checkpoints apply? |

Anything outside these six is decoration. The framework keeps redesigns disciplined and reviewable.

## 2. Cross-page baseline (true for every page)

These rules apply to every page without exception. They are not repeated in each page section below.

- **Header and footer** are persistent and identical across the site (definition in `bakabo-design-system` §7 and below)
- **Single language selector,** never duplicated (a recurring problem — see audit in `bakabo-theme-build`)
- **One H1 per page,** sequential heading hierarchy
- **Focus states visible,** keyboard navigable
- **Above-the-fold within 1.5s** on 4G (LCP < 2.5s target)
- **No autoplay video with sound** (autoplay muted is allowed, with controls)
- **Service line visible** at least once: Free Shipping >€60 · 30-Day Returns · 2-Year EU Warranty · Made to Order
- **Voice follows `bakabo-brand`** — editorial register, no urgency tactics, no exclamation marks

### Persistent header (every page)

Block order, left to right: **Logo · Main nav (Man · Woman · Accessories · Drops) · Search icon · Account icon · Cart icon · Language (single, minimal)**.

### Persistent footer (every page)

Four columns, top to bottom:
1. **Brand block** — short tagline + AI-art line
2. **Shop** — links to main collections
3. **Help** — Shipping, Returns, FAQ, Contact
4. **Legal** — Privacy, Terms, Cookie preferences, P.IVA, registered address

Below: newsletter signup (one-line, no popup), social icons (small, line-style), copyright line.

---

## 3. HOMEPAGE

**Scope.** Communicate *what BKS Studio is* within the first scroll. A visitor who sees only the hero must understand: AI-generated wearable art, accessible-designer band, printed on demand — and have an obvious next step.

**Content (must be present).**
- Hero image with strong identity headline + one primary CTA
- Current drop or featured collection (visual entry point)
- The "AI-art as design" narrative (one section)
- Featured collections by line (max 3 surfaced at once)
- Editorial moment — a film, lookbook, or story
- Service commitments (bar or row)
- Newsletter capture (inline, not popup)

**Content (must NOT be present).**
- Countdown timers
- "Best-seller" star ratings spam
- Discount banners as default state
- More than one language selector
- Carousel that auto-rotates faster than 6s
- Multiple competing CTAs in the hero

**Structure (block order, top to bottom).**

```
1. Hero            — full-bleed image + headline + 1 CTA
2. Current drop    — large visual, link to collection
3. AI-art panel    — short copy + visual proof
4. Featured lines  — 3 collection cards, equal weight
5. Editorial slot  — film / lookbook / story
6. Service row     — 4 commitments, restrained
7. Newsletter      — 1 input, 1 button
```

**UX rules.**
- One primary CTA in the hero. Secondary CTAs go below the fold.
- Hero headline is a brand statement, not a problem/solution headline
- Navigation surfaces the current drop without making the homepage redundant
- All "Featured" cards lead to actual collections, not search results pages

**AI-art panel — background choice.** The panel's role is to declare *"this is why BakAbo is different"*, so it should visually break the page rhythm rather than blend. Preferred default: dark backdrop with `--bks-shadow` (#242833). This amplifies the prints as art rather than decoration, holds the cool temperature lane when paired with `--bks-ink` as page accent, and creates the editorial cadence of light → light → dark → light that magazines like 032c and SSENSE use. Light backgrounds (`--bks-bone`, `--bks-salt`) are acceptable when the page-level temperature is warm or when AI-art swatches are themselves dark/saturated and would lose contrast on shadow. Inside the panel, primary text in `--bks-salt`, secondary text and ™ labels in `--bks-dune`, no color accents (the AI-art carries the color).

**KPIs.**
- Homepage bounce rate (target < 50%)
- Click-through to a collection (target > 30% of sessions)
- Hero CTA click-through (target > 8%)
- Scroll depth past block 4 (target > 60%)

**Accessibility.**
- Hero image has descriptive alt text or `role="presentation"` if purely decorative
- Headline contrast ≥ 4.5:1 over the image (use overlay if needed)
- Carousels (if any): pause control, keyboard navigation, ARIA live region for slide changes

---

## 4. COLLECTION PAGE

**Scope.** Let the visitor browse the collection efficiently and find a product they want to open.

**Content.**
- Collection title and 1–2 sentence intro (from `bakabo-product-copy` §5)
- Filter and sort controls (size, color, type)
- Product grid
- Pagination or infinite scroll (one, not both)

**Content NOT present.**
- "You may also like" cross-sell rows in the middle of the grid
- Sponsored or "trending" injections
- Active sale stickers on more than 20% of products (signals brand devaluation)

**Structure.**

```
1. Breadcrumb           — Home / Collections / [Name]
2. Title + intro        — H1, 1–2 sentences below
3. Filter bar           — sticky on desktop scroll, drawer on mobile
4. Product grid         — 4 cols desktop, 2 mobile, 4:5 cards
5. Pagination / "Load more"
6. Collection footer    — optional editorial closing line
```

**UX rules.**
- Filters apply without full page reload (URL-stateful for shareability)
- Selected filters visible as removable chips above the grid
- "No results" state: friendly message + clear filters CTA, never empty page
- Product hover: subtle image swap to back/detail shot if available, no shadows or scale jumps

**KPIs.**
- Filter usage rate
- Product click-through rate
- Time-to-first-product-click (target < 15s)
- Collection-to-product conversion

**Accessibility.**
- Filter controls are real `<button>` / `<input>` elements with labels
- Active filter state announced to screen readers
- Grid items are individually keyboard reachable

---

## 5. PRODUCT PAGE

**Scope.** Convert interest into purchase by removing every doubt — about the product, the timing, the fit, the trust.

**Content.** Six blocks from `bakabo-product-copy` §1 (title, hero line, description, spec, made-to-order, service) plus the visual and interaction layer specified here.

**Structure.**

```
1. Breadcrumb               — Home / [Collection] / [Product]
2. Two-column layout (desktop) / Stacked (mobile)
   LEFT:
     · Image gallery (5–8 images, 4:5 ratio, zoom on click)
   RIGHT (sticky on desktop):
     · Title (H1)
     · Hero line (italic, one sentence)
     · Price (tabular numerals)
     · Variant selectors (size, color — color in BakAbo names)
     · Size guide link (opens modal with size chart)
     · Add to cart button (primary, full width)
     · Service bullets (compact)
     · Description (collapsible if long)
     · Spec block (4 bullets, always expanded)
     · Made-to-order block (always visible, never hidden behind "read more")
3. FAQ accordion            — 4–6 questions, made-to-order is question #1
4. Related products         — 4 from same collection, no "best sellers" logic
5. Editorial footer         — link to collection or campaign
```

**UX rules.**
- Add-to-cart button is **always reachable**: sticky on mobile, in viewport on desktop via right-column stickiness
- Variant selectors use color swatches (no dropdowns) and size pills (no dropdown unless >10 sizes)
- "Out of stock" only when truly out — made-to-order items are never sold out by default
- Image zoom on click, not on hover (predictability)
- The made-to-order lead time is stated **before** the add-to-cart button is pressed, never as a checkout surprise

**KPIs.**
- Product page → add-to-cart rate (target > 5%)
- Add-to-cart → checkout rate (target > 60%)
- Size guide open rate (high open rate signals sizing anxiety — investigate copy)
- FAQ engagement (high engagement = objections to address upstream)

**Accessibility.**
- Gallery has keyboard navigation (arrow keys) and screen reader image descriptions
- Variant selection state is announced
- Add-to-cart button announces success via ARIA live region

---

## 6. CART & CHECKOUT

**Scope.** Move the customer from intent to paid without introducing doubt or friction.

### Cart

**Content.** Line items with image/title/variant/quantity/price, subtotal, shipping estimate (with free-shipping threshold), single CTA to checkout, made-to-order reminder per line.

**Structure.**

```
1. Heading: "Cart" (count)
2. Line items list
3. Subtotal + shipping threshold progress bar
4. Made-to-order notice (production lead time)
5. Primary CTA: "Checkout"
6. Continue shopping link (tertiary)
```

**UX rules.**
- No upsells in the cart — they cause abandonment more than they add revenue at BakAbo's price point
- Quantity edit is inline (- 1 +), not a separate page
- Removing an item asks for no confirmation (it's reversible by adding it back)

### Checkout

Use Shopify's native checkout. Customize only what brand consistency requires:
- Logo placement
- Color tokens applied via Shopify Checkout Editor / Branding settings
- Confirmation page (next section)

**Do not** rebuild checkout. Custom checkouts on Shopify are a maintenance and conversion liability unless on Shopify Plus with a real budget.

**KPIs.**
- Cart → checkout rate (target > 70%)
- Checkout completion rate (target > 65%)
- Average order value vs the €60 free-shipping threshold

---

## 7. ORDER CONFIRMATION (post-purchase)

**Scope.** Confirm the order arrived, reduce buyer's remorse, set lead-time expectations clearly.

**Content.**
- Confirmation message (warm, calm — "Thanks. Your order is in production.")
- Order number, items summary, shipping address
- Production timeline: when production starts, when it ships, when it likely arrives
- Tracking link (ParcelPanel) — even if not yet active, set expectation that it will arrive
- Social / community CTA (Instagram follow, newsletter) — only one, not three

**UX rules.**
- Lead off with the lead-time. Confirmation is good; *clarity about when the order arrives* is better.
- No discount code for "your next order" here — it discounts the moment. Send it later by email.

---

## 8. ABOUT PAGE

**Scope.** Build trust and identity in one read. Answer: who runs this, what do they believe, why should I care.

**Content.**
- Brand origin story (200–400 words, in `bakabo-brand` voice)
- The AI-art process (a section, with visual or video proof)
- Founders / studio note (a face or a place — humans trust humans)
- Press / editorial mentions (if any — restrained, no logo soup)
- Values or principles (3–5, in your own voice, not generic)
- Contact / studio location

**Structure.**

```
1. Hero image / video       — studio, process shot, or pattern-generation moment
2. Origin paragraph         — 1–2 paragraphs
3. AI-art process panel     — visual + 100 words
4. Studio / founders block  — name + portrait + one-sentence position
5. Press / editorial (if applicable)
6. Values block             — 3–5 short statements
7. Contact CTA              — link to contact page or email
```

**UX rules.** Long-form is fine here, but no walls of text. Break copy with images every 2–3 paragraphs. Read time visible at top (optional but appreciated).

**Voice.** This is where `bakabo-brand` does its heaviest work. Editorial, confident, no chest-beating. The page should read like an artist's statement.

---

## 9. SEARCH RESULTS

**Scope.** Get the visitor to a product as fast as possible.

**Content.**
- Search input (echo of the query)
- Result count
- Results grid (same card format as collection grid)
- Empty state: friendly suggestion + popular collections

**UX rules.**
- Search suggests as the user types (predictive)
- Misspellings tolerated (fuzzy match)
- Results scope: products by default, with optional toggle to "Pages" for blog/about results
- No paid sponsored placements

---

## 10. 404 / ERROR PAGE

**Scope.** Don't lose the visitor. Acknowledge the dead end and offer a way back in.

**Content.**
- Calm headline (e.g. *"This page is in another collection."*)
- Search bar
- Links to: Homepage, current drop, all collections
- A visual asset (small) — never a frowny face emoji or "Oops!"

**UX rules.** Short, brand-consistent, calm. Never apologetic.

---

## 11. POLICY PAGES (Shipping, Returns, Privacy, Terms, Cookies)

**Scope.** Provide complete, legally-required information in a form humans can actually read.

**Common content.**
- Last-updated date at the top
- Table of contents (anchor links) for pages > 1000 words
- Sections with clear H2 headings
- Plain-language summary at the top of each major section (for Privacy and Terms especially)
- Contact email for questions

**UX rules.**
- Single-column, max 680px content width (readability)
- Body text `--text-base`, line-height 1.6
- No marketing copy inside these pages; they are reference material
- Print-friendly (works without backgrounds)

**KPIs.**
- Time on page (longer ≠ better here; it suggests confusion)
- Bounce vs return to site (returning to site = trust restored)

**Specific notes.**
- **Returns** must address the made-to-order question explicitly (see `bakabo-shopify-ops` §3)
- **Privacy** must list all data processors (Shopify, Printify, ParcelPanel, payment, analytics, marketing tools) — see `bakabo-theme-build` Security & GDPR section
- **Cookies** must offer granular consent (functional / analytics / marketing) — not just "Accept all" / "Reject all"

---

## 12. CONTACT PAGE

**Scope.** Make it easy and credible to reach someone.

**Content.**
- One contact email (not a generic "info@")
- Optional contact form (4 fields max: name, email, subject, message)
- Studio address + map (builds trust enormously for a young brand)
- Response time expectation ("we reply within 2 business days")
- Customer service hours (if applicable)

**UX rules.**
- No phone unless it's actually answered
- No chatbot pretending to be human
- Form submission confirmation is immediate and clear (success state, not a generic toast)

---

## 13. FAQ / HELP CENTER

**Scope.** Pre-empt customer service tickets by answering the predictable questions clearly.

**Structure.**

```
1. Hero search bar (search inside FAQs)
2. Category tiles: Orders · Shipping · Returns · Sizing · Products · Account
3. Accordion list per category
4. Contact CTA at the bottom ("Didn't find your answer?")
```

**Content priorities (the questions to definitely answer for BakAbo):**
- "How long does production take?" (the #1 made-to-order question)
- "Can I return a made-to-order item?" (yes — clarify per §3 of `bakabo-shopify-ops`)
- "What size should I buy?" (link to size guide per collection)
- "How is shipping cost calculated?"
- "Where do I track my order?"
- "Is the print really AI-generated?" (lean into this, don't hide it)

---

## 14. ACCOUNT PAGES (login, register, orders, addresses)

**Scope.** Functional, fast, low-friction. Account pages are where loyal customers live; they should feel like a calm continuation of the brand, not a different app.

**Content.**
- Login / register with email + password and optional social/Shop login
- Order history (most recent first, with status: in production → shipped → delivered)
- Saved addresses
- Newsletter preferences
- Account deletion (GDPR requirement)

**UX rules.**
- "Continue as guest" must be at least equally prominent as "create account" at checkout
- Order status uses production lead time language (not generic "fulfilled" / "unfulfilled")
- Password reset works in one email click, no security theater

---

## 15. Auditing a designer's delivery

When a designer hands back a redesigned page, walk this checklist:

- [ ] Does it match the six dimensions for that page type (above)?
- [ ] Does it respect every token in `bakabo-design-system` §2–6?
- [ ] Does the body copy follow `bakabo-brand` voice (no urgency, no exclamations)?
- [ ] If it's a product page, does the body match `bakabo-product-copy` six-block anatomy?
- [ ] Is accessibility hit (keyboard, focus, contrast, headings, labels)?
- [ ] Mobile and desktop both delivered?
- [ ] No emoji in structural elements?

Zero violations on tokens + zero violations on principles = approved. Otherwise, send back with the exact list.

## 16. What this skill cannot do

- Cannot replace user research, A/B testing, or real analytics data
- Cannot judge whether a specific composition is *beautiful* — that's design judgment
- Cannot guarantee conversion improvements; it guarantees structural soundness and brand consistency

The skill ensures every page has the **right content in the right order with no obvious holes**. Excellence beyond that is human work.
