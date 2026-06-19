---
name: bakabo-identity
description: Use this skill whenever making decisions about the brand name, wordmark, label format, product iconography, or naming rules for BKS Studio / BakAbo. Triggers include choosing which name to use in a given context (site, product, label, social, email), designing or reviewing a label or hangtag, assigning an icon to a product category, briefing a designer or Printify on brand identity assets, or any question about how the brand name appears publicly. Works alongside bakabo-brand (voice), bakabo-design-system (visual tokens), and bakabo-product-copy (product page rules). Do not use for product copy, theme code, or Shopify operations.
---

# BKS Studio — Brand Identity & Naming System

This skill governs how the brand name appears, where and how each form is used, what appears on product labels, and how product categories are identified visually. It is the single source of truth for identity decisions across all touchpoints.

---

## 1. Brand name — three forms, three contexts

The brand has three legitimate name forms. Each has a specific context. Mixing them is an error.

| Form | Correct spelling | Context | Never use here |
|---|---|---|---|
| **BKS Studio** | `BKS Studio` | Public-facing: site, social, ads, email, press | On labels, on product titles |
| **BAK\|ABO** | `BAK\|ABO` (with vertical bar separator) | Secondary visual use: hangtag, packaging, banner, footer credit | As the primary site name, in body copy |
| **bakabo.club** | `bakabo.club` (lowercase) | Technical: domain, URL, email addresses only | In any customer-facing visual communication |

### Rules enforced across all forms

- **BAKABO as a single unspaced word is prohibited in all public contexts.** Search results for "bakabo" surface a jihadist figure (Baye Ag Bakabo, AQMI, Mali 2013). This association is permanent and unrecoverable for a fashion brand. The word must never appear unspaced in any public material — site, label, social, ad, press, or packaging.
- The domain `bakabo.club` is a technical asset. It is not a brand name. It does not appear in headlines, product pages, ads, or printed materials.
- `BAK|ABO` with separator is acceptable for visual identity use (label, hangtag, banner) because the split reading creates visual distance from the problematic single-word form.
- `BKS Studio` is the public brand name. All customer communication uses this form.

---

## 2. Public name — BKS Studio

**BKS Studio** is the brand the customer knows. It appears:

- Site header / navigation
- Product titles (as `BKS [Collection] [Design]™ [Type]`)
- Social media bios and posts
- Email sender name and subject lines
- Ads and campaigns
- Press mentions and interviews
- Homepage hero copy
- Collection page intros

It never appears as `BKS STUDIO` (all caps) or `Bks Studio` (incorrect case). Always `BKS Studio`.

---

## 3. Product label system

The label is the physical or printed identity mark that appears on the product itself. Two label contexts exist.

### 3.1 Internal sewn label (inside garment / accessory)

**Confirmed format (approved via mockup comparison, June 2026):**

```
┌─────────────┐
│  ■          │  ← small white square, top left — structural accent
│  BKS        │  ← acronym only, white on black, clean sans-serif
└─────────────┘
```

- **Label:** black background, white text
- **Content:** `BKS` only — acronym, no tagline, no shark, no BAK|ABO
- **Position on garment:** center back, below neckline seam — vertical orientation, narrow format
- **Why BKS only:** at label scale (approx 3×2cm on swimwear) the tagline "BUILT DIFFERENT. MADE TO MOVE." becomes illegible noise. The full lockup with shark works at hangtag scale, not sewn label scale.
- **The white square accent** (top of label) is a design detail confirmed in the approved mockup — carry it forward on all sewn labels for consistency.

**Three formats tested, one approved:**

| Format tested | Verdict | Reason |
|---|---|---|
| `BAK ABO` horizontal, white on white/black | ❌ Rejected — archived | Reads as two words; brand defect |
| `BKS` + shark + tagline, black label | ⚠️ Acceptable but verbose | Tagline illegible at label scale |
| `BKS` only + white square accent, black label | ✅ **Approved** | Maximum legibility, clean identity |

**Prohibited on sewn label:**
- `BAK ABO` with space — structural defect, existing products archived
- `BAKABO` unspaced — search association risk
- Tagline at sewn label scale
- Color backgrounds other than black

### 3.2 External hangtag / packaging label

**Correct form:** `BAK|ABO` split with separator + `BKS` + product category subtitle

Structure (as developed in the existing label system):
```
BAK | ABO          ← secondary wordmark, small, flanking
BKS                ← primary acronym, large, center
[PRODUCT CATEGORY] ← subtitle, e.g. SWIM TRUNKS COLLECTION
[ICON]             ← category icon (see §4)
BAK | ABO          ← repeated on right side for symmetry
```

This system is already developed and functional. It is the approved hangtag format.

---

## 4. Product category icons

Each product category carries a distinct icon on the hangtag and in visual communication. Icons are black, minimal, line or silhouette style — consistent with bakabo-design-system §10 (line, 1.5px stroke, 24px artboard).

| Category | Icon | Notes |
|---|---|---|
| Swimwear (trunks + one-piece) | Shark silhouette | Directional, facing right |
| Outerwear (puffer, windbreaker) | Triangle / mountain with horizontal lines | Layered structure = warmth/altitude |
| Footwear (sneakers, flip flops) | Waves with horizontal bar | Fluid movement |
| Bags (backpack, travel bag) | Abstract carry form | TBD — needs professional design |
| T-shirts / tops | TBD | Needs professional design |

**Icons that need professional design:** bag and tee categories are not yet defined. Do not improvise — flag as "pending" and brief a designer using the style reference (shark and mountain icons as the established baseline).

**Icons are for hangtag and packaging only.** They do not appear on product pages, site navigation, or in the body of emails. The site uses the standard icon library (Lucide / Phosphor / Heroicons — see bakabo-design-system §10).

---

## 5. The BKS shark mark

The shark is the brand's primary pictorial mark, appearing in the BKS Studio lockup alongside the acronym.

**Correct use:**
- In the BKS Studio brand lockup (BKS + shark + tagline)
- On swimwear hangtag as category icon
- As a standalone mark in contexts where the full lockup is too large

**Never use:**
- As a decorative print element on garments
- As a repeating pattern
- Distorted, rotated, or recolored
- In combination with the BAK|ABO wordmark (the shark belongs to the BKS lockup only)

**Tagline in the lockup:** `BUILT DIFFERENT. MADE TO MOVE.` — this tagline is fixed to the full BKS Studio lockup. Do not use it standalone or with BAK|ABO.

---

## 6. Naming rules summary (quick reference)

| Context | Use | Never use |
|---|---|---|
| Site header | `BKS Studio` | bakabo, BAKABO, bak abo |
| Product title | `BKS [Collection]...` | bakabo, bak abo |
| Sewn label | `BKS` or `BKS STUDIO` | BAK ABO with space, BAKABO unspaced |
| Hangtag | `BAK\|ABO` + `BKS` | BAKABO unspaced |
| Social bio | `BKS Studio` | bakabo, bak abo |
| Domain / URL | `bakabo.club` | — |
| Email sender | `BKS Studio` | bakabo |
| Footer credit | `© BKS Studio` or `BAK\|ABO` | BAKABO unspaced |
| Press / interview | `BKS Studio` | bakabo |
| Internal files / Make / Excel | `bakabo` (technical code only) | — |

---

## 7. Designer brief — identity assets needed

These assets exist in draft form and need professional refinement before they are production-ready. When briefing a designer or agency, provide this list:

**Priority 1 — Critical:**
- Sewn label file: `BKS STUDIO` in clean sans-serif, black/white, production-ready for Printify label upload. Dimensions: standard woven label format.
- Hangtag master file: BAK|ABO + BKS + [category] layout in vector, with all five category variants.

**Priority 2 — Important:**
- Category icons for: bags (backpack + travel bag), t-shirts/tops — to match the style of existing shark and mountain icons.
- BKS Studio full lockup in vector (BKS + shark + tagline) — clean production file, all formats (SVG, PNG transparent, EPS).

**Priority 3 — Useful:**
- BAK|ABO wordmark in vector — the split form with proper kerning and separator weight, all color variants (black on white, white on black, tonal).
- Color variants of hangtag system for limited use (black label, white label, kraft).

**Style reference for designer:** existing shark icon (clean silhouette, no detail), existing mountain/triangle icon (geometric, structured lines). All new icons must match this register.

---

## 8. What this skill cannot resolve

- Which specific font was used for the existing BAK|ABO wordmark — identify this before briefing a designer so they can match or deliberately replace it.
- Whether the existing hangtag files are vector or raster — check source files before sending to production.
- Trademark status of `BKS Studio` as a combined mark — requires IP counsel before filing (see bakabo-brand §12 for trademark strategy context).

---

## 9. Relationship to other skills

| Skill | Relationship |
|---|---|
| `bakabo-brand` | Voice, tone, positioning — the identity skill governs names and marks, brand governs language |
| `bakabo-design-system` | Visual tokens (color, type, spacing) — this skill governs identity assets specifically |
| `bakabo-product-copy` | Product title formula uses `BKS [Collection]` — always consistent with §2 here |
| `bakabo-printify-sync` | Label format on Printify products must match §3.1 — sewn label = `BKS` or `BKS STUDIO` only |
| `bakabo-shopify-ops` | Site name in all Shopify settings = `BKS Studio` |
