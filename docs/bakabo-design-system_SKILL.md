---
name: bakabo-design-system
description: Brand and UI design system guidance for BakAbo/BKS. Use when working on BKS typography, official fonts, mobile readability, dashboard proportions, Shopify theme text sizing, product description hierarchy, product naming with BKS plus collection/series, or when the user says not to radically redesign the interface.
---

# BakAbo / BKS Design System

## Principle

Preserve the BKS identity. Improve proportion, legibility and trust without changing the character of the project unless explicitly requested.

## Official Type System

- Use `BKS Display` for page titles, section titles, product titles and collection titles.
- Use `BKS Text` for descriptions, support copy, table text, chat messages and mobile UI.
- Use `BKS Mono` only for logs, IDs, CSV paths, API diagnostics and machine-readable status blocks.
- Implement them as CSS token names with reliable system fallbacks until a licensed font file is installed.

Recommended CSS tokens:

```css
--bks-font-display: "BKS Display", "Segoe UI", Arial, sans-serif;
--bks-font-text: "BKS Text", "Segoe UI", Arial, sans-serif;
--bks-font-mono: "BKS Mono", Consolas, "Liberation Mono", monospace;
```

## Mobile Text Rules

- Product and panel descriptions: 14-15px minimum, line-height 1.55-1.62.
- Inputs: 16px minimum to avoid mobile browser zoom.
- Buttons and tappable controls: 44px minimum height.
- Status labels and metadata: 12px minimum, line-height at least 1.35.
- Do not scale font size directly with viewport width for controls, descriptions or dashboard text. Use breakpoints.
- Keep `letter-spacing: 0`. Avoid negative tracking and decorative spacing.

## BKS Naming

- Public naming should preserve `BKS` plus the visible collection or series identity.
- Preferred public language: collection, visual system, drop, archive.
- Treat technical `series` metadata as internal unless a public page explicitly requires it.
- Product cleanup must not reorder titles aggressively. Remove emojis, decorative symbols and refusi first; preserve the original name structure when BKS and the collection/series are already present.

## Dashboard Proportion

- The Master panel should feel operational, not like a landing page.
- Keep compact cards, clear status text, visible progress and charts.
- Descriptions must explain the current state in one or two readable lines on mobile.
- When adding new panels, reuse existing rows, status colors and chart cards before inventing new layout patterns.

## Shopify Theme Proportion

- Keep the light commerce trust layer.
- Product title desktop target: about 30-32px.
- Product title mobile target: about 26px.
- Product descriptions: 15px, line-height 1.6.
- Trust strip text: 13-14px on mobile.
- Timed offers must stay sober, real and legible: no fake urgency, no hidden terms, no oversized countdowns.
