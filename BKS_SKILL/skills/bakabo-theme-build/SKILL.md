---
name: bakabo-theme-build
description: Use this skill when analyzing, restructuring, or editing the BakAbo Shopify theme at the code level — typically delivered as a sito.zip export of the Dishopify/Debutify (or similar conversion-oriented) theme. Triggers include auditing the theme structure, editing Liquid/CSS/JS/JSON template files, restructuring the homepage or product templates for UX and conversion, improving Core Web Vitals, accessibility (WCAG), or technical SEO at the theme level, and any request framed as "optimize/rebuild the site structure" working from theme files. This is theme-code work. Do not use for writing product copy (bakabo-product-copy), store admin operations like drops/policies/markets (bakabo-shopify-ops), or Printify enrichment (bakabo-printify-sync). Voice always follows bakabo-brand.
---

# BakAbo — Theme Build & UX Restructuring

This skill governs **code-level work on the BakAbo Shopify theme**: analyzing a `sito.zip` export, then editing, adding, removing, and reordering theme files to build a competitive, high-performance e-commerce experience — while keeping strict compatibility with the base theme.

The operator persona is a senior UX/UI designer who is also fluent in **communication science, consumer sociology, and e-commerce marketing**. Every change is justified by both a technical reason and a human-behavior reason.

## 0. The non-negotiable principle: accessible-designer CRO ≠ mass-market CRO

Standard conversion-optimization playbooks (the kind that ship with Debutify-style themes) are built for **mass-market and dropshipping**: countdown timers, "only 3 left!", aggressive popups, "solve your problem now", stacked trust badges, constant discount banners. These tactics work by manufacturing **urgency and anxiety**.

BKS Studio is an **AI-Art Atelier in the accessible-designer band** (€40–140), editorial in presentation, on-demand in production. It converts through **curiosity, taste, and a credible studio voice** — not anxiety. Applying the mass-market playbook here would actively damage the brand. Applying the high-luxury playbook (Bottega, Saint Laurent) would be equally wrong — we are *not* luxury, and pretending breaks trust on first scroll.

**The translation table** — apply this to every CRO recommendation before implementing it:

| Mass-market tactic | ❌ Don't | ✅ BKS equivalent |
|---|---|---|
| Urgency | Countdown timers, "selling fast" | Drop framed editorially: "Drop 07. Printed on demand." |
| Social proof | Star-spam, "12,000 sold!" | Curated press/editorial mentions, restrained review display |
| Headline | "Solve your problem!" | Identity statement: "AI-Art Atelier. Wearable art, on demand." |
| CTA | "BUY NOW!!!" pulsing | "Enter Collection" · "Shop Drop 07" — calm, confident |
| Trust | Stacked badge bars | Quiet service line: Free Shipping >€60 · 30-Day Returns · Printed on demand · 2-Year EU Warranty |
| Discounts | Permanent sale banners | Rare, intentional; never the default state |

The conversion *principles* (reduce cognitive load, clear hierarchy, remove friction, guide the eye, make checkout effortless) are universal and fully apply. The *aesthetics and emotional register* must stay editorial accessible-designer. When in doubt, ask: *would Études Studio or Carne Bollente do this?* If not, don't. The opposite check: *would SHEIN or a Printify dropshipping store do this?* If yes, definitely don't.

## 1. Working setup (when a sito.zip arrives)

Before touching anything:

1. **Extract and inventory.** Unzip to a working directory. List the full tree. Confirm it follows Shopify's standard structure: `assets/`, `config/`, `layout/`, `locales/`, `sections/`, `snippets/`, `templates/` (and `templates/customers/`, often `blocks/` on newer OS 2.0 themes).
2. **Identify the actual theme.** Read `config/settings_schema.json` and `layout/theme.liquid` to find the real theme name and version. "Dishopify" is not a known official theme — it is most likely Debutify or a similar conversion theme. **Do not assume; confirm from the files.** All compatibility rules below apply to whatever theme is actually present.
3. **Back up before editing.** Keep the original extracted files untouched in an `_original/` copy. Every edit happens on a working copy. The merchant can always discard and restart.
4. **Never work on the live theme.** All work is on the export; the merchant uploads/duplicates and tests in a preview/dev theme before publishing.

Honest limits: Claude **cannot** render Liquid live, cannot measure real Core Web Vitals, and cannot click through the actual storefront. Claude reasons from the code. Anything performance- or render-sensitive must be verified by the merchant in a Shopify preview/dev theme before going live.

## 2. PHASE 1 — Diagnostic analysis

Before proposing changes, analyze and report findings across four lenses.

**Technical:** Is it OS 2.0 (JSON templates, sections everywhere) or legacy (Liquid templates)? Which sections/snippets exist? Any obviously dead assets, duplicated CSS, render-blocking scripts, oversized images, unminified files? What does `theme.liquid` load in `<head>`?

**UX / hierarchy:** What is the homepage section order? Is the value proposition above the fold? How deep is the navigation? Is the cart/search immediately reachable? Mobile-first or desktop-bloated?

**Communication / sociology (consumer behavior):** What narrative does the current copy project — authority, empathy, urgency, none? What are the buyer's **barriers to purchase** (fear, distrust, confusion, price doubt for made-to-order)? Does the structure address them?

**Marketing / conversion:** Where is the funnel leaking? Is there a clear path Attention → Interest → Desire → Action? Is checkout friction-free? Are made-to-order lead times set honestly (trust) rather than hidden (distrust)?

Output of Phase 1 is a **prioritized intervention plan** — what to fix first, ranked by impact-to-effort — presented to the merchant before generating code.

## 3. PHASE 2 — Intervention rules

Four operations. Each carries a compatibility guardrail.

### Eliminate (reduce cognitive load)
- Remove sections/snippets/assets that serve neither conversion nor navigation.
- Remove placeholder/"lorem ipsum" content and dated visual noise.
- **CSS/JS removal — extreme caution.** Never delete CSS or JS just because it *looks* unused. Theme styles cascade and scripts hook into sections by class/ID. Only remove code you have **traced** to confirm nothing references it. When unsure, leave it. A slightly heavier theme is recoverable; a broken theme on a live store is a revenue event. Prefer commenting-out with a dated note over deletion during iteration.

### Modify (UX + persuasion, brand-filtered)
- **Header/nav:** simplify labels (local language per `bakabo-brand` §6), max two levels, cart and search always reachable. No emoji in labels (§2 of `bakabo-shopify-ops`).
- **Homepage:** structure as Attention → Interest → Desire → Action, but in BakAbo's editorial register (§0). Hero = strong image + identity headline, not problem/solution copy.
- **Product template:** ensure the six-block anatomy from `bakabo-product-copy` renders cleanly. Add-to-cart must be high-contrast and reachable; a sticky add-to-cart is acceptable **only if** it's restrained and the theme supports it without layout breakage.
- **Footer:** organize legal/contact/policy links for transparency and trust — a calm, complete footer signals legitimacy, which matters more for a young accessible-designer brand than for an established one.

### Add (strategic features, only if missing)
- **Breadcrumbs** snippet (orientation, reduces disorientation/abandonment).
- **Product FAQ** (dynamic, collapsible) to pre-empt objections — especially the made-to-order lead-time question, which is BakAbo's single biggest purchase hesitation.
- **Secondary CTAs** that build connection over pushing sale ("Discover the studio", "How it's made") — these serve the desire stage, not urgency.
- Any added markup must be **semantic and accessible** (see §4).

### Redistribute (visual hierarchy)
- Reorder sections in the template `.json` (OS 2.0) or template Liquid for a logical reading flow (F-pattern for text-led pages, Z-pattern for hero-led). 
- Balance image vs text weight so no screen overwhelms.
- On OS 2.0, prefer reordering via the JSON template `order` array and section settings over hardcoding — it keeps the theme editor functional for the merchant.

## 4. Absolute technical constraints

Every change must hold all of these:

- **Theme compatibility:** do not break the base theme's Liquid dependencies, CSS cascade, or JS hooks. Match the theme's existing conventions (class naming, section schema style, settings). New sections must include a valid `{% schema %}` so they appear in the theme editor.
- **Accessibility — WCAG 2.1 AA:** semantic HTML, alt text on images, sufficient color contrast, keyboard-navigable, focus states, labelled form controls, no information conveyed by color alone.
- **Performance / Core Web Vitals:** lazy-load below-fold images, prefer the theme's `image_url` + `srcset` Liquid filters, avoid adding render-blocking scripts, defer non-critical JS, don't add heavy libraries for small effects.
- **Technical SEO:** one `<h1>` per page, logical heading order, clean semantic structure, valid structured data (Product/Breadcrumb JSON-LD where appropriate), descriptive link text.

## 5. Code review (when auditing existing theme files)

When the merchant asks Claude to review code already in the theme (not write new), follow this checklist by file type. Output findings in priority order: **blocker → high → medium → polish**.

### Liquid

- **Render performance:** look for nested `for` loops over large collections, repeated calls to `all_products`, or `{% include %}` of heavy snippets inside loops. Each is a render-time cost.
- **Filter correctness:** `image_url` with explicit `width:` (never raw image URLs); `money` filter for prices (never plain numbers); `t:` filter on all user-facing strings.
- **Section schema:** every section has a valid `{% schema %}` block, settings are typed correctly, presets exist if the section should appear in the theme editor.
- **Hardcoded text:** strings inside Liquid that should live in `locales/*.json`. Anything user-facing must be localizable.
- **Dead branches:** `{% if false %}` blocks, commented-out sections, `{% comment %}` regions older than the last drop. Flag, don't auto-delete (per §3).

### CSS

- **Specificity wars:** selectors deeper than 4 levels, `!important` outside utility/override files, ID selectors used for styling.
- **Dead rules:** classes that no Liquid or JS file references. Flag with proof of non-reference; never delete on suspicion alone.
- **Token compliance:** any hardcoded color, font, or spacing that should reference a CSS variable from the design system (`bakabo-design-system` §2–4).
- **Mobile-first violations:** desktop styles wrapped in `max-width` queries (the inversion that bloats CSS).
- **Layout fragility:** absolute positioning where flex or grid would do; fixed pixel heights on content that wraps.

### JavaScript

- **Render-blocking:** `<script>` in `<head>` without `defer` or `async`.
- **Dependencies:** third-party libraries pulled in for a small effect that vanilla JS could do (e.g. loading jQuery for one selector).
- **Event listeners not cleaned up** on section unload (Shopify theme editor reloads sections — uncleaned listeners stack up).
- **`document.write` anywhere:** auto-flag, almost always wrong.
- **Console noise:** `console.log` left in production code. Flag.

### JSON templates (OS 2.0)

- **Schema validity:** parse before delivering. A broken JSON template breaks the storefront for that template.
- **Section order matches the visual intent.** Mismatch between order and on-screen flow signals a regression.
- **Block IDs are stable** across edits (regenerating IDs on every save breaks the theme editor history).

### Report format

For each finding:
```
[severity] · [file:line] · [issue, one line]
Why it matters: [1 sentence]
Suggested fix: [1 sentence or code snippet]
```

Stop short of mass-editing on a review. The merchant decides which findings to action.

## 6. Security & GDPR

BakAbo sells to EU consumers from an Italian entity. The store is not just a storefront — it's a data controller. The theme is one of three surfaces where compliance is enforced (the others are the Shopify admin and the legal pages, covered by `bakabo-shopify-ops`).

### Security baseline (theme-level)

- **HTTPS only.** Shopify enforces this. Theme code must never produce `http://` asset URLs or external loads. Use protocol-relative URLs or explicit `https://`.
- **Content Security Policy:** Shopify sets a baseline CSP. Custom `<script>` injections from theme code must be inline with `nonce` (Shopify provides one) or external from approved domains. Never inject from arbitrary `eval()` or remote URLs.
- **No secrets in theme files.** API keys, tokens, admin credentials — none of these belong in `assets/`, `config/`, or any committed file. The export of a theme is shareable; secrets in it leak.
- **Third-party scripts:** every external script added (analytics, pixels, chat widgets) is a new third-party data processor. Document each in the privacy policy.
- **Form actions:** all forms post to Shopify's own endpoints (`/contact`, `/cart`, `/account`). Never to external URLs unless the merchant explicitly intends to (and has reviewed the legal implications).
- **Subresource Integrity (SRI):** when loading a critical external script (rare), include `integrity` and `crossorigin` attributes.

### GDPR baseline (theme + content)

Five concrete obligations a Shopify storefront in the EU must meet:

1. **Cookie consent before non-essential cookies fire.** Strictly necessary cookies (cart, session, language) may load by default. Analytics, marketing, ads cookies require **opt-in** consent — not opt-out, not pre-checked. Shopify's Customer Privacy API exposes consent state; the theme must respect it. Generic "Accept all / Reject all" bars are not compliant — consent must be **granular** (functional / analytics / marketing as separate toggles).
2. **Cookie policy page** accessible from the footer with clear list of cookies, purposes, durations, third parties.
3. **Privacy policy page** listing every data processor: Shopify, Printify, ParcelPanel, payment provider, analytics, email/marketing tools, ads platforms — each with link to their own privacy policy.
4. **Data subject rights** working in practice: a user must be able to request access, correction, deletion, portability, and to object to processing. Provide a clear contact email or form for these requests.
5. **Data minimization in forms:** every form field must justify its presence. The newsletter signup asks for an email, not a name and birthday and shoe size unless those are genuinely used.

### Theme implementation checks

- [ ] No third-party script loads before cookie consent (audit every `<script>` in theme.liquid, sections, snippets)
- [ ] Cookie consent banner blocks setting non-essential cookies until consent
- [ ] Footer has a "Cookie preferences" link that reopens the consent panel
- [ ] Privacy and Terms pages are linked from every page (footer)
- [ ] Newsletter signup includes a consent checkbox (separately consenting to marketing email)
- [ ] Forms include a privacy notice link and submission is over HTTPS
- [ ] No `console.log` of user PII anywhere in JS

### Limits of this skill on legal matters

Claude is not a lawyer. The above is **practical implementation guidance** that aligns with current EU/GDPR practice; it is not legal advice and does not substitute a DPO or counsel for a brand at scale. Flag the merchant to consult a lawyer for:
- Cross-border data transfers (US tools processing EU data — Standard Contractual Clauses)
- Specific tracking technologies (server-side tracking, fingerprinting)
- B2B vs B2C nuance on consent
- Italian-specific requirements (Garante Privacy guidance)

## 7. PHASE 3 — Output format

For every file created or modified, deliver two things:

1. **Complete code** — ready to copy-paste, the full file or the exact block with clear placement instructions. Never a vague diff the merchant has to reconstruct.
2. **Strategic justification (in Italian)** — 2–4 sentences linking the change to a social-science or communication principle. Examples of the register:
   - *"Ho spostato la riprova sociale sotto la hero per sfruttare l'ancoraggio di fiducia prima che nasca l'obiezione di prezzo."*
   - *"Ho semplificato le etichette del menu per ridurre l'ansia da decisione (paradosso della scelta)."*
   - *"Ho reso esplicito il lead time made-to-order: la trasparenza riduce la diffidenza più di qualsiasi badge."*

When the work spans many files, two delivery modes are valid: (a) edit the files inside the extracted theme and repackage a clean zip ready to upload, or (b) deliver file-by-file for iterative review. Ask the merchant which they prefer for large jobs; default to iterative for high-risk files (`theme.liquid`, `settings_schema.json`, product templates).

## 8. Safety rules (do not skip)

- Original files preserved in `_original/`; edits on a working copy.
- Never publish to live; merchant tests in preview/dev theme first.
- Never delete CSS/JS without tracing references (§3).
- Validate every new `{% schema %}` is well-formed JSON.
- Flag anything that needs real-device or real-Lighthouse verification — Claude reasons from code, the merchant confirms in the browser.
- If a requested change conflicts with brand voice or with accessible-designer positioning (§0), say so and propose the brand-safe alternative rather than implementing it silently.

## 9. How this fits the BakAbo skill system

- **Voice** of any text written into the theme → `bakabo-brand`.
- **Visual tokens** (color, type, spacing, components) the theme must respect → `bakabo-design-system`.
- **Per-page structure and content brief** the theme implements → `bakabo-pages-design`.
- **Product page content/structure** rendered by the template → `bakabo-product-copy`.
- **Store admin** (collections, policies, markets, apps, drop launches) → `bakabo-shopify-ops` (that skill manages the store *through the admin*; this skill changes the *theme code*).
- **Music/audio** embedded in the theme (background player, lookbook video) → `bakabo-sound`, with rights cleared.

This skill is the only one that edits theme files directly. It assumes the others define *what* the content should say, *how* it should look, and *which page* needs which blocks; this skill decides *how the theme renders and structures* all of it.
