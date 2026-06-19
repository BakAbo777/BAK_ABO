---
name: bakabo-multilingual
description: BKS Multilingual System — language selector, Shopify Markets/Geolocation, theme locale files, and AI-assisted content translation for bakabo.club. Covers: header language switcher, locale JSON files, product/collection copy translation, SEO hreflang, and the entry-page language detection flow. Priority languages: EN (primary), IT, FR, DE.
---

# BakAbo — Multilingual Skill

Translation and localization system for bakabo.club. Priority languages: **EN** (primary), **IT**, **FR**, **DE**.

---

## 1. Architecture

### Shopify Markets
- Shopify Markets handles currency, tax, and domain routing
- Language switching: Shopify native `localization` object + `form action="/localization"`
- Theme locale files: `04_TEMA_SHOPIFY/locales/en.default.json` + `it.json`, `fr.json`, `de.json`

### Entry Language Detection
The header language selector issue: the current `bakabo-header.liquid` does not include a language switcher. The selector appears broken/missing at entry because:
1. No `<form action="/localization">` in the header
2. No Shopify Markets language routing configured

### Fix Plan
1. Add BKS language selector to header (minimal, DM Mono, pill style)
2. Configure Shopify Markets in admin to enable IT/FR/DE
3. Create/expand locale JSON files for theme strings
4. Add `hreflang` to `layout/theme.liquid`

---

## 2. Language Selector — Header Implementation

Add to `bakabo-header.liquid` right section (before cart icon):

```liquid
{%- if localization.available_languages.size > 1 -%}
<div class="bks-lang-selector">
  <form action="/localization" method="POST" id="bks-lang-form">
    <input type="hidden" name="return_to" value="{{ request.path }}">
    <select name="locale_code" id="bks-lang-select" onchange="this.form.submit()"
            aria-label="Language / Lingua">
      {%- for lang in localization.available_languages -%}
        <option value="{{ lang.iso_code }}"
          {% if lang.iso_code == localization.language.iso_code %}selected{% endif %}>
          {{ lang.endonym_name }}
        </option>
      {%- endfor -%}
    </select>
  </form>
</div>
{%- endif -%}
```

CSS (add to header `<style>`):
```css
.bks-lang-selector select {
  font-family: var(--bks-font-mono, 'DM Mono', monospace);
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  background: transparent;
  border: 1px solid rgba(10,10,10,0.18);
  border-radius: 4px;
  padding: 4px 8px;
  color: #0a0a0a;
  cursor: pointer;
  appearance: none;
}
.bks-lang-selector select:focus {
  outline: none;
  border-color: var(--bks-active-accent, #c8c4be);
}
```

---

## 3. Locale Files — Strings to Translate

Priority strings (added to `locales/`):

| Key | EN | IT | FR | DE |
|---|---|---|---|---|
| `general.made_to_order` | Made to order | Prodotto su ordinazione | Fabriqué à la commande | Auf Bestellung gefertigt |
| `general.collection` | Collection | Collezione | Collection | Kollektion |
| `general.members` | Members | Membri | Membres | Mitglieder |
| `general.wishlist` | Wishlist | Lista desideri | Liste de souhaits | Wunschliste |
| `general.try_on` | Try On | Prova il capo | Essayer | Anprobieren |
| `cart.title` | Your cart | Il tuo carrello | Votre panier | Ihr Warenkorb |
| `products.facets.filter_by` | Filter | Filtra | Filtrer | Filtern |

---

## 4. Product Copy Translation Workflow

For translating product titles, descriptions, SEO:

1. **Source**: Shopify Admin → Translations → Products
2. **AI assist**: Use this prompt template:

```
Translate the following Shopify product copy for BakAbo fashion brand.
Brand voice: editorial, minimal, premium, DM Mono aesthetic.
Tone: confident but not overcooked.
Keep: product handle unchanged, BKS collection name unchanged.
Translate TITLE and DESCRIPTION to: {target_language}

Product title: {title}
Description: {description}
SEO title: {seo_title}
SEO description: {seo_desc}
```

3. **Output**: Shopify Translations API `PUT /admin/api/2025-01/translations/{resource_id}.json`

---

## 5. SEO Hreflang

Add to `layout/theme.liquid` inside `<head>`:

```liquid
{%- for lang in localization.available_languages -%}
  <link rel="alternate" hreflang="{{ lang.iso_code }}"
    href="{{ request.origin }}/{{ lang.iso_code }}{{ request.path }}">
{%- endfor -%}
<link rel="alternate" hreflang="x-default" href="{{ request.origin }}{{ request.path }}">
```

---

## 6. Shopify Markets Setup (Admin Steps)

1. Shopify Admin → Settings → Markets → Add market
2. Add: Italy (IT/EUR), France + Belgium (FR/EUR), Germany + Austria (DE/EUR)
3. Enable translated domains OR path-based routing (`/it/`, `/fr/`, `/de/`)
4. Set primary language EN → all other languages as secondary
5. After Markets enabled: the `localization.available_languages` object will populate

---

## 7. Priority Fixes

1. **Language selector broken at entry** → Add form to header (§2 above)
2. **Shopify Markets not configured** → Admin setup (§6)
3. **No locale files for IT/FR/DE** → Create `locales/it.json`, `fr.json`, `de.json` with the table from §3
4. **No hreflang** → Add to `theme.liquid` (§5)
5. **Product copy untranslated** → Use AI translation workflow (§4) per collection

---

## 8. Autonomous AI Actions

When user asks to translate:
1. Check `localization.available_languages` is populated (Markets configured)
2. Identify untranslated strings via Shopify Translations API
3. Generate translations using §4 prompt template
4. Upload via API or CSV import
5. Verify with Playwright audit at `/?locale={lang.iso_code}`
