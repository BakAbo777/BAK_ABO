# BakAbo — Editorial Typographer

`bakabo-editorial-typographer` — Composition and typography rules for placing cutout/staged product images on BakAbo editorial surfaces. Senior art director level: 5 composition schemes, full typography scale, cutout placement rules, armocromia handoff protocol.

## The 5 composition schemes

| Scheme | Use case | Key rule |
|---|---|---|
| **A — Drop** | Product card, PDP gallery, Piano Hero panel | Product centered 60-70%, minimal type below |
| **B — Float** | Collection hero, editorial panel, lookbook | Product right (cols 5-12), headline left, can bleed top |
| **C — Stamp** | Product pop-out card, newspaper effect | Black ruled border, reversed bar at bottom in accent color |
| **D — Bleed** | Hero banners, full-width headers, Instagram | Product fills frame, text in negative space only |
| **E — Newspaper column** | Product grid, bks-product-popout section | 4 columns, 1px rules, no shadow, flat newspaper |

## Typography scale

| Role | Size | Weight | Tracking |
|---|---|---|---|
| Display headline | 48–80px | 800 | -0.02em |
| Section head | 26–44px | 700 | -0.015em |
| Eyebrow/kicker | 9px | 700 | 0.28em |
| Caption/body | 11–14px | 400 | 0.02em |
| Product label | 9–11px | 600 | 0.14–0.22em |
| Price | 13–15px | 600 | 0 + tabular |

All fonts: DM Mono. Never pure `#000000` — use `#0A0A0A` (warm dark) on paper, `#fafaf7` on dark.

## Cutout placement rules

- Scale: 60–75% of frame height for garments
- Shadow: paper mode → `rgba(20,14,6,0.09) 0 10px 32px`; cinema → accent glow
- Background: always `--bks-active-accent` wash or `#0A0A0A`/`#fafaf7` — never arbitrary
- Cutout ratio: 70% cutout (scalable) / 30% staged (emotional/narrative)

## Autonomous AI actions

1. Identify surface type → select scheme A–E
2. Check `output/cutout/{slug}/{slug}_cutout_safe.png` — if missing, flag for pipeline run
3. Select `overlay_{collection}.jpg` matching page's collection color from manifest
4. Apply typography scale, never mix more than 2 font sizes per card/panel

## Armocromia handoff

- Armocromia → which model palette (skin/hair) fits the collection
- Typographer → what background, typography, composition the product and model sit in
- Handoff sequence: collection seasonal type → background pole (paper/dark) → accent auto → scheme → typography

Related: `bakabo-armocromia`, `bakabo-popup-ai`, `bakabo-manual-product-photo-generation`, `bakabo-design-system`
