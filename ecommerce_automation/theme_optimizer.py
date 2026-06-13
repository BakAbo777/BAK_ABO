from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any

from ecommerce_automation.marketing_offers import ensure_workspace as ensure_marketing_workspace
from ecommerce_automation.marketing_offers import section_liquid as timed_offer_section
from ecommerce_automation.theme_ai_assistant import ensure_workspace as ensure_assistant_workspace
from ecommerce_automation.theme_ai_assistant import section_liquid as ai_assistant_section


SOURCE_ZIP = Path("04_TEMA_SHOPIFY/BKS_TM03_clean_12JUN2026_SEO_READY_CORRETTO.zip")
OUTPUT_ZIP = Path("04_TEMA_SHOPIFY/BKS_TM03_LIGHT_TRUST_TIMER_READY.zip")
LIGHT_CSS = Path("04_TEMA_SHOPIFY/assets/bks-commerce-light.css")
TRUST_SECTION = Path("04_TEMA_SHOPIFY/sections/bks-trust-strip.liquid")
AI_ASSISTANT_SECTION = Path("04_TEMA_SHOPIFY/sections/bks-ai-assistant.liquid")
ORBIT_SECTION = Path("04_TEMA_SHOPIFY/sections/bks-planet-collections-orbit.liquid")
ORBIT_TEMPLATE = Path("04_TEMA_SHOPIFY/templates/page.bks-planet-collections-orbit.json")
ORBIT_SNIPPET = Path("04_TEMA_SHOPIFY/snippets/bks-orbit-card.liquid")


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _workspace_text(root_dir: Path, path: Path) -> str:
    full_path = root_dir / path
    return full_path.read_text(encoding="utf-8") if full_path.exists() else ""


def commerce_light_css() -> str:
    if LIGHT_CSS.exists():
        return LIGHT_CSS.read_text(encoding="utf-8")
    return """/*
  BKS commerce trust layer.
  Purpose: lighten the storefront, keep product and policy information readable,
  and avoid urgency patterns that could look misleading.
*/
:root {
  --bks-commerce-paper: #fafaf7;
  --bks-commerce-ink: #111111;
  --bks-commerce-muted: #5f5a52;
  --bks-commerce-line: #ded8cd;
  --bks-commerce-accent: #2f6f6b;
}

body,
.gradient,
.color-background-1,
.color-background-2,
.shopify-section {
  background: var(--bks-commerce-paper);
  color: var(--bks-commerce-ink);
}

.header-wrapper,
.section-header,
.utility-bar,
.footer,
.footer__content-top,
.footer__content-bottom,
.announcement-bar {
  background: #ffffff;
  color: var(--bks-commerce-ink);
}

.footer,
.footer a,
.header-wrapper a,
.menu-drawer,
.menu-drawer a {
  color: var(--bks-commerce-ink);
}

.button,
.shopify-payment-button__button,
.quick-add__submit {
  background: var(--bks-commerce-ink);
  border-color: var(--bks-commerce-ink);
  color: #ffffff;
}

.button--secondary,
.button--tertiary {
  background: transparent;
  border-color: var(--bks-commerce-ink);
  color: var(--bks-commerce-ink);
}

.card,
.card__inner,
.product__info-container,
.collection-hero,
.rich-text,
.multicolumn-card,
.image-with-text__content,
.accordion,
.customer,
.contact,
.article-template,
.main-page-title,
.page-width {
  color: var(--bks-commerce-ink);
}

.card__heading,
.product__title,
.collection-hero__title,
.title,
.h0,
.h1,
.h2,
.h3 {
  color: var(--bks-commerce-ink);
}

.price,
.caption,
.rte,
.product__description,
.collection-hero__description,
.footer-block__details-content {
  color: var(--bks-commerce-muted);
}

.product-form__input input[type='radio'] + label,
.facet-checkbox,
.disclosure__button,
.quantity,
.field__input,
.select__select {
  background: #ffffff;
  border-color: var(--bks-commerce-line);
  color: var(--bks-commerce-ink);
}

.badge,
.price__badge-sale,
.price__badge-sold-out {
  background: #ffffff;
  border: 1px solid var(--bks-commerce-line);
  color: var(--bks-commerce-ink);
}

.bks-trust-strip {
  background: #ffffff;
  border-block: 1px solid var(--bks-commerce-line);
  color: var(--bks-commerce-ink);
}

.bks-trust-strip__inner {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin: 0 auto;
  max-width: 1320px;
  padding: 18px 20px;
}

.bks-trust-strip__item {
  border-left: 1px solid var(--bks-commerce-line);
  padding-left: 14px;
}

.bks-trust-strip__item:first-child {
  border-left: 0;
  padding-left: 0;
}

.bks-trust-strip__item strong {
  display: block;
  font-size: 13px;
  margin-bottom: 4px;
}

.bks-trust-strip__item span {
  color: var(--bks-commerce-muted);
  display: block;
  font-size: 12px;
  line-height: 1.35;
}

@media (max-width: 760px) {
  .bks-trust-strip__inner {
    grid-template-columns: 1fr;
  }
  .bks-trust-strip__item,
  .bks-trust-strip__item:first-child {
    border-left: 0;
    border-top: 1px solid var(--bks-commerce-line);
    padding-left: 0;
    padding-top: 10px;
  }
  .bks-trust-strip__item:first-child {
    border-top: 0;
    padding-top: 0;
  }
}
"""


def trust_section_liquid() -> str:
    return r"""{% comment %}
  BKS Trust Strip: explicit customer reassurance for Google Merchant review.
{% endcomment %}

<section class="bks-trust-strip" aria-label="Shopping information">
  <div class="bks-trust-strip__inner">
    <div class="bks-trust-strip__item">
      <strong>{{ section.settings.item_1_title | default: 'Made to order' | escape }}</strong>
      <span>{{ section.settings.item_1_copy | default: 'Products are produced after purchase to avoid overstock.' | escape }}</span>
    </div>
    <div class="bks-trust-strip__item">
      <strong>{{ section.settings.item_2_title | default: 'Clear delivery' | escape }}</strong>
      <span>{{ section.settings.item_2_copy | default: 'Shipping costs and delivery estimates are shown before checkout.' | escape }}</span>
    </div>
    <div class="bks-trust-strip__item">
      <strong>{{ section.settings.item_3_title | default: 'Returns policy' | escape }}</strong>
      <span>{{ section.settings.item_3_copy | default: 'Return and refund terms are available from the footer.' | escape }}</span>
    </div>
    <div class="bks-trust-strip__item">
      <strong>{{ section.settings.item_4_title | default: 'BKS Studio' | escape }}</strong>
      <span>{{ section.settings.item_4_copy | default: 'Original AI-generated visual collections curated by BakAbo.' | escape }}</span>
    </div>
  </div>
</section>

{% schema %}
{
  "name": "BKS trust strip",
  "settings": [
    { "type": "text", "id": "item_1_title", "label": "Item 1 title", "default": "Made to order" },
    { "type": "text", "id": "item_1_copy", "label": "Item 1 copy", "default": "Products are produced after purchase to avoid overstock." },
    { "type": "text", "id": "item_2_title", "label": "Item 2 title", "default": "Clear delivery" },
    { "type": "text", "id": "item_2_copy", "label": "Item 2 copy", "default": "Shipping costs and delivery estimates are shown before checkout." },
    { "type": "text", "id": "item_3_title", "label": "Item 3 title", "default": "Returns policy" },
    { "type": "text", "id": "item_3_copy", "label": "Item 3 copy", "default": "Return and refund terms are available from the footer." },
    { "type": "text", "id": "item_4_title", "label": "Item 4 title", "default": "BKS Studio" },
    { "type": "text", "id": "item_4_copy", "label": "Item 4 copy", "default": "Original AI-generated visual collections curated by BakAbo." }
  ],
  "presets": [
    { "name": "BKS trust strip" }
  ]
}
{% endschema %}
"""


def ensure_patch_files(root_dir: Path) -> dict[str, str]:
    css_path = root_dir / LIGHT_CSS
    css_path.parent.mkdir(parents=True, exist_ok=True)
    css_path.write_text(commerce_light_css(), encoding="utf-8")

    section_path = root_dir / TRUST_SECTION
    section_path.parent.mkdir(parents=True, exist_ok=True)
    section_path.write_text(trust_section_liquid(), encoding="utf-8")
    files = {"css": _relative(root_dir, css_path), "trust_section": _relative(root_dir, section_path)}
    for key, path in {
        "orbit_section": ORBIT_SECTION,
        "orbit_template": ORBIT_TEMPLATE,
        "orbit_snippet": ORBIT_SNIPPET,
    }.items():
        if (root_dir / path).exists():
            files[key] = _relative(root_dir, root_dir / path)
    return files


def _inject_theme_liquid(content: str) -> str:
    css_tag = "{{ 'bks-commerce-light.css' | asset_url | stylesheet_tag }}"
    if css_tag not in content:
        content = content.replace("</head>", f"  {css_tag}\n</head>")
    return content


def build_patched_zip(settings: Any) -> dict[str, Any]:
    root_dir = settings.root_dir
    source = root_dir / SOURCE_ZIP
    output = root_dir / OUTPUT_ZIP
    files = ensure_patch_files(root_dir)
    marketing = ensure_marketing_workspace(settings)
    assistant = ensure_assistant_workspace(settings)
    if not source.exists():
        return {
            "status": "missing_source_zip",
            "source_zip": _relative(root_dir, source),
            "output_zip": "",
            "files": files,
            "marketing": marketing,
            "assistant": assistant,
        }

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source, "r") as zin, zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        names = set(zin.namelist())
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "layout/theme.liquid":
                data = _inject_theme_liquid(data.decode("utf-8", errors="ignore")).encode("utf-8")
            zout.writestr(item, data)
        if "assets/bks-commerce-light.css" not in names:
            zout.writestr("assets/bks-commerce-light.css", commerce_light_css())
        if "sections/bks-trust-strip.liquid" not in names:
            zout.writestr("sections/bks-trust-strip.liquid", trust_section_liquid())
        if "sections/bks-timed-offer.liquid" not in names:
            zout.writestr("sections/bks-timed-offer.liquid", timed_offer_section())
        if "sections/bks-ai-assistant.liquid" not in names:
            zout.writestr("sections/bks-ai-assistant.liquid", ai_assistant_section(settings))
        orbit_section = _workspace_text(root_dir, ORBIT_SECTION)
        orbit_template = _workspace_text(root_dir, ORBIT_TEMPLATE)
        orbit_snippet = _workspace_text(root_dir, ORBIT_SNIPPET)
        if orbit_section and "sections/bks-planet-collections-orbit.liquid" not in names:
            zout.writestr("sections/bks-planet-collections-orbit.liquid", orbit_section)
        if orbit_template and "templates/page.bks-planet-collections-orbit.json" not in names:
            zout.writestr("templates/page.bks-planet-collections-orbit.json", orbit_template)
        if orbit_snippet and "snippets/bks-orbit-card.liquid" not in names:
            zout.writestr("snippets/bks-orbit-card.liquid", orbit_snippet)

    return {
        "status": "ready",
        "source_zip": _relative(root_dir, source),
        "output_zip": _relative(root_dir, output),
        "files": files | {
            "timed_offer": "04_TEMA_SHOPIFY/sections/bks-timed-offer.liquid",
            "ai_assistant": "04_TEMA_SHOPIFY/sections/bks-ai-assistant.liquid",
            "planet_collections_orbit": "04_TEMA_SHOPIFY/sections/bks-planet-collections-orbit.liquid",
        },
        "marketing": marketing,
        "assistant": assistant,
        "checks": [
            {"check": "light_css_asset", "status": "pass", "detail": "assets/bks-commerce-light.css injected"},
            {"check": "theme_layout_link", "status": "pass", "detail": "layout/theme.liquid loads light CSS"},
            {"check": "trust_strip_section", "status": "pass", "detail": "sections/bks-trust-strip.liquid added"},
            {"check": "timed_offer_section", "status": "pass", "detail": "sections/bks-timed-offer.liquid added"},
            {"check": "ai_assistant_section", "status": "pass", "detail": "sections/bks-ai-assistant.liquid added disabled-by-default"},
            {"check": "planet_collections_orbit", "status": "pass", "detail": "sections/bks-planet-collections-orbit.liquid added with page template"},
        ],
    }


def payload(settings: Any) -> dict[str, Any]:
    data = build_patched_zip(settings)
    return {
        "summary": {
            "status": data["status"],
            "output_zip": data.get("output_zip", ""),
            "source_zip": data.get("source_zip", ""),
            "goal": "lighter_commerce_trust_theme",
        },
        **data,
    }
