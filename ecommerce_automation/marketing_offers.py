from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OFFER_DIR = Path("output/marketing_timers")
OFFER_FILE = OFFER_DIR / "active_offer.json"
THEME_SECTION = Path("04_TEMA_SHOPIFY/sections/bks-timed-offer.liquid")
INSTALL_DOC = Path("04_TEMA_SHOPIFY/BKS_TIMED_OFFER_INSTALL.md")


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _parse_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _now() -> datetime:
    return datetime.now(timezone.utc)


def default_offer(settings: Any) -> dict[str, Any]:
    code = settings.marketing_offer_code.strip()
    return {
        "id": "bks-launch-window",
        "name": settings.marketing_offer_name or "BKS Launch Window",
        "status": "active" if settings.marketing_offer_enabled.lower() in {"1", "true", "yes", "on"} else "draft",
        "starts_at": "2026-06-13T00:00:00+02:00",
        "ends_at": settings.marketing_offer_ends_at or "2026-06-20T23:59:59+02:00",
        "headline": "BKS Launch Window",
        "subheadline": "A timed shopping window for the current BKS Studio drop.",
        "cta": "Shop the drop",
        "target_url": settings.marketing_offer_url or "https://bakabo.club/collections/new-arrivals",
        "discount_code": code,
        "price_claim": "",
        "terms": (
            "Valid only while this campaign is active. Final prices, taxes, shipping and delivery times "
            "are shown at checkout. Products are made to order. This campaign does not imply affiliation "
            "with third-party brands."
        ),
        "google_safe_rules": [
            "Timer has a real end date and must hide after expiry.",
            "No discount percentage is shown unless a real Shopify discount code is configured.",
            "Terms stay visible near the CTA.",
            "Landing page must match the offer and remain available.",
        ],
    }


def offer_path(root_dir: Path) -> Path:
    return root_dir / OFFER_FILE


def load_offer(settings: Any) -> dict[str, Any]:
    path = offer_path(settings.root_dir)
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return default_offer(settings) | data
        except json.JSONDecodeError:
            return default_offer(settings)
    return default_offer(settings)


def save_offer(settings: Any, offer: dict[str, Any]) -> dict[str, Any]:
    path = offer_path(settings.root_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(offer, indent=2, ensure_ascii=False), encoding="utf-8")
    return offer


def compliance(offer: dict[str, Any]) -> dict[str, Any]:
    ends_at = _parse_date(offer.get("ends_at", ""))
    starts_at = _parse_date(offer.get("starts_at", ""))
    now = _now()
    checks = [
        {"check": "real_deadline", "status": "pass" if ends_at and ends_at > now else "fail", "detail": offer.get("ends_at", "")},
        {"check": "real_start", "status": "pass" if starts_at else "fail", "detail": offer.get("starts_at", "")},
        {"check": "target_url", "status": "pass" if offer.get("target_url", "").startswith("https://") else "fail", "detail": offer.get("target_url", "")},
        {"check": "terms_visible", "status": "pass" if len(offer.get("terms", "")) > 40 else "fail", "detail": "terms text"},
        {
            "check": "discount_claim",
            "status": "pass" if not offer.get("price_claim") or offer.get("discount_code") else "fail",
            "detail": "price claim requires configured discount code",
        },
    ]
    failed = sum(1 for row in checks if row["status"] != "pass")
    return {
        "status": "google_safe" if failed == 0 else "needs_fix",
        "failed": failed,
        "checks": checks,
        "expired": bool(ends_at and ends_at <= now),
    }


def section_liquid() -> str:
    return r"""{% comment %}
  BKS Timed Offer
  Google-safe countdown: requires a real end date, visible terms, and no fake discount claims.
{% endcomment %}

{%- assign sid = section.id -%}
{%- assign ends_at = section.settings.ends_at | strip -%}
{%- assign starts_at = section.settings.starts_at | strip -%}

<style>
  #shopify-section-{{ sid }} .bks-timed-offer {
    --bks-ink: #111111;
    --bks-paper: #fafaf7;
    --bks-line: #ded8cd;
    --bks-accent: #2f6f6b;
    --bks-font-display: "BKS Display", var(--font-heading-family, "Segoe UI", Arial, sans-serif);
    --bks-font-text: "BKS Text", var(--font-body-family, "Segoe UI", Arial, sans-serif);
    background: var(--bks-ink);
    color: var(--bks-paper);
    font-family: var(--bks-font-text);
    padding: 18px 20px;
  }
  #shopify-section-{{ sid }} .bks-timed-offer[hidden] { display: none; }
  #shopify-section-{{ sid }} .bks-timed-offer__inner {
    align-items: center;
    display: grid;
    gap: 14px;
    grid-template-columns: minmax(0, 1fr) auto auto;
    margin: 0 auto;
    max-width: 1320px;
  }
  #shopify-section-{{ sid }} .bks-timed-offer__kicker {
    color: #bfcfca;
    font-size: 11px;
    letter-spacing: 0;
    line-height: 1.3;
    margin: 0 0 4px;
    text-transform: uppercase;
  }
  #shopify-section-{{ sid }} .bks-timed-offer__title {
    font-family: var(--bks-font-display);
    font-size: 28px;
    font-weight: 600;
    letter-spacing: 0;
    line-height: 1.12;
    margin: 0;
  }
  #shopify-section-{{ sid }} .bks-timed-offer__copy {
    color: #e7e0d6;
    font-size: 14px;
    line-height: 1.5;
    margin: 6px 0 0;
    max-width: 760px;
  }
  #shopify-section-{{ sid }} .bks-timed-offer__clock {
    display: grid;
    gap: 6px;
    grid-template-columns: repeat(4, 54px);
    text-align: center;
  }
  #shopify-section-{{ sid }} .bks-timed-offer__unit {
    border: 1px solid rgba(250,250,247,.28);
    padding: 8px 6px;
  }
  #shopify-section-{{ sid }} .bks-timed-offer__num {
    display: block;
    font-size: 20px;
    font-weight: 700;
  }
  #shopify-section-{{ sid }} .bks-timed-offer__label {
    color: #bfcfca;
    display: block;
    font-size: 9px;
    letter-spacing: 0;
    line-height: 1.2;
    text-transform: uppercase;
  }
  #shopify-section-{{ sid }} .bks-timed-offer__cta {
    border: 1px solid var(--bks-paper);
    color: var(--bks-paper);
    display: inline-flex;
    font-size: 12px;
    font-weight: 700;
    justify-content: center;
    line-height: 1.2;
    min-height: 44px;
    min-width: 150px;
    padding: 12px 16px;
    text-decoration: none;
    text-transform: uppercase;
  }
  #shopify-section-{{ sid }} .bks-timed-offer__terms {
    color: #bfcfca;
    font-size: 12px;
    grid-column: 1 / -1;
    line-height: 1.45;
    margin: 0;
  }
  @media (max-width: 760px) {
    #shopify-section-{{ sid }} .bks-timed-offer__inner {
      grid-template-columns: 1fr;
    }
    #shopify-section-{{ sid }} .bks-timed-offer__clock {
      grid-template-columns: repeat(4, minmax(0, 1fr));
      width: 100%;
    }
    #shopify-section-{{ sid }} .bks-timed-offer__title {
      font-size: 22px;
    }
    #shopify-section-{{ sid }} .bks-timed-offer__copy {
      font-size: 14px;
      line-height: 1.55;
    }
  }
</style>

<section
  class="bks-timed-offer"
  data-bks-timed-offer
  data-starts-at="{{ starts_at | escape }}"
  data-ends-at="{{ ends_at | escape }}"
  aria-label="{{ section.settings.kicker | default: 'Timed offer' | escape }}"
>
  <div class="bks-timed-offer__inner">
    <div>
      <p class="bks-timed-offer__kicker">{{ section.settings.kicker | default: 'Timed offer' | escape }}</p>
      <h2 class="bks-timed-offer__title">{{ section.settings.heading | default: 'BKS Launch Window' | escape }}</h2>
      <p class="bks-timed-offer__copy">{{ section.settings.copy | escape }}</p>
    </div>
    <div class="bks-timed-offer__clock" aria-live="polite">
      <span class="bks-timed-offer__unit"><b class="bks-timed-offer__num" data-bks-days>0</b><small class="bks-timed-offer__label">Days</small></span>
      <span class="bks-timed-offer__unit"><b class="bks-timed-offer__num" data-bks-hours>0</b><small class="bks-timed-offer__label">Hours</small></span>
      <span class="bks-timed-offer__unit"><b class="bks-timed-offer__num" data-bks-minutes>0</b><small class="bks-timed-offer__label">Min</small></span>
      <span class="bks-timed-offer__unit"><b class="bks-timed-offer__num" data-bks-seconds>0</b><small class="bks-timed-offer__label">Sec</small></span>
    </div>
    <a class="bks-timed-offer__cta" href="{{ section.settings.link }}">{{ section.settings.cta | default: 'Shop now' | escape }}</a>
    <p class="bks-timed-offer__terms">{{ section.settings.terms | escape }}</p>
  </div>
</section>

<script>
  (function () {
    var root = document.querySelector('#shopify-section-{{ sid }} [data-bks-timed-offer]');
    if (!root) return;
    var end = new Date(root.dataset.endsAt || '').getTime();
    var start = new Date(root.dataset.startsAt || '').getTime();
    var days = root.querySelector('[data-bks-days]');
    var hours = root.querySelector('[data-bks-hours]');
    var minutes = root.querySelector('[data-bks-minutes]');
    var seconds = root.querySelector('[data-bks-seconds]');
    function tick() {
      var now = Date.now();
      if (!end || (start && now < start) || now >= end) {
        root.hidden = true;
        return;
      }
      var diff = end - now;
      days.textContent = Math.floor(diff / 86400000);
      hours.textContent = Math.floor((diff % 86400000) / 3600000);
      minutes.textContent = Math.floor((diff % 3600000) / 60000);
      seconds.textContent = Math.floor((diff % 60000) / 1000);
      root.hidden = false;
    }
    tick();
    setInterval(tick, 1000);
  })();
</script>

{% schema %}
{
  "name": "BKS timed offer",
  "settings": [
    { "type": "text", "id": "kicker", "label": "Kicker", "default": "Timed offer" },
    { "type": "text", "id": "heading", "label": "Heading", "default": "BKS Launch Window" },
    { "type": "textarea", "id": "copy", "label": "Copy", "default": "A timed shopping window for the current BKS Studio drop." },
    { "type": "text", "id": "link", "label": "CTA link", "default": "/collections/new-arrivals" },
    { "type": "text", "id": "cta", "label": "CTA", "default": "Shop the drop" },
    { "type": "text", "id": "starts_at", "label": "Start ISO date", "default": "2026-06-13T00:00:00+02:00" },
    { "type": "text", "id": "ends_at", "label": "End ISO date", "default": "2026-06-20T23:59:59+02:00" },
    { "type": "textarea", "id": "terms", "label": "Visible terms", "default": "Valid only while this campaign is active. Final prices, taxes, shipping and delivery times are shown at checkout. Products are made to order." }
  ],
  "presets": [
    { "name": "BKS timed offer" }
  ]
}
{% endschema %}
"""


def install_doc(offer: dict[str, Any]) -> str:
    return f"""# BKS Timed Offer Install

Generated for: {offer.get("name")}

## Files

- `sections/bks-timed-offer.liquid`

## Activation

1. Add the section to the Shopify theme.
2. Place it above the target collection or homepage product band.
3. Keep `ends_at` as a real ISO date: `{offer.get("ends_at")}`.
4. Keep terms visible. Do not show a discount percentage unless the Shopify discount code exists.

## Current Offer

- CTA: {offer.get("cta")}
- URL: {offer.get("target_url")}
- Discount code: {offer.get("discount_code") or "not configured"}
- Terms: {offer.get("terms")}
"""


def ensure_workspace(settings: Any) -> dict[str, Any]:
    offer = load_offer(settings)
    save_offer(settings, offer)
    section_path = settings.root_dir / THEME_SECTION
    section_path.parent.mkdir(parents=True, exist_ok=True)
    section_path.write_text(section_liquid(), encoding="utf-8")
    install_path = settings.root_dir / INSTALL_DOC
    install_path.write_text(install_doc(offer), encoding="utf-8")
    return {
        "offer": offer,
        "section": _relative(settings.root_dir, section_path),
        "install_doc": _relative(settings.root_dir, install_path),
    }


def payload(settings: Any) -> dict[str, Any]:
    workspace = ensure_workspace(settings)
    offer = workspace["offer"]
    checks = compliance(offer)
    return {
        "offer": offer,
        "summary": {
            "status": offer.get("status", "draft"),
            "compliance": checks["status"],
            "expired": checks["expired"],
            "section": workspace["section"],
            "install_doc": workspace["install_doc"],
            "discount_code": "configured" if offer.get("discount_code") else "not_configured",
        },
        "checks": checks["checks"],
        "theme": {
            "section": workspace["section"],
            "install_doc": workspace["install_doc"],
            "latest_zip": "04_TEMA_SHOPIFY/BKS_TM03_clean_12JUN2026_SEO_READY_CORRETTO.zip",
            "live_publish": "not_pushed_by_master",
        },
    }
