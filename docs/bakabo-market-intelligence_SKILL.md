# BakAbo — Commercial Intelligence & Market Sensing

`bakabo-market-intelligence` — Commercial strategy, market timing, pricing intelligence, and autonomous growth actions for BakAbo. The AI uses this skill to sense market variables and act proactively, not just reactively.

## BakAbo market position (June 2026)

- Segment: independent luxury wearable art, made-to-order, premium-priced
- Price tier: €69–€249 (entry tees → Archive pieces)
- Stage: pre-traction — 32 customers, editorial identity established, discovery near-zero
- Core bottleneck: awareness. Quality and price-to-value are correct

## Seasonal market calendar

| Window | Date range | BakAbo action |
|---|---|---|
| Summer slowdown | Jul–Aug | Content pipeline, no major drops |
| Back-to-culture | Sep | Pulse, Token — creative reactivation |
| Winter drop | Oct–Nov | Archive, Glyph — max value before Christmas |
| Spring collection | Feb–Mar | Origin, Riviera — lighter pieces |

## Growth patterns (consolidated, proven)

**1. Editorial Halo** — build magazine content before selling. Piano Hero IS the halo. Never shortcut it.

**2. Inner Circle First** — 32 customers. Personal Roberto outreach > mass email. One VIP order with a handwritten note = 100 ad impressions.

**3. Drop Event** — quarterly, date-announced, music-anchored. "On June 28 the Archive opens." Not a sale — a concert.

**4. Channel Compression** — dominate Instagram before expanding. Reels + editorial grid = brand equity. TikTok later.

**5. Price Anchor** — Archive/co-branded at €199–€249 makes €89 hoodie feel accessible. Never go below €69.

**6. Search-First Content** — every product page and collection description targets a real query. "Wearable art fashion", "made-to-order hoodie Italy", each collection name.

## Pricing rules

| Tier | Range | Type |
|---|---|---|
| Entry | €69–€89 | Tees, caps, accessories |
| Core | €109–€149 | Hoodies, sweatshirts |
| Collection | €159–€199 | Co-branded, Origin series |
| Archive | €199–€249 | BKS Archive limited |

- Never below €69 — destroys luxury positioning
- No discounts on new drops — use Archive access as reward
- Free shipping threshold: 1.2× average order value

## Autonomous action triggers

```
New collection ready but not launched?
  → Run launch checklist (bakabo-shopify-ops)
  → Check Piano Hero image_url for that collection
  → If empty → trigger Canva generation (bakabo-popup-ai)

Oct–Nov arrives + Archive/Glyph products exist?
  → Suggest timed drop with Piano Hero cinema mode on homepage
  → Draft editorial email for 12 subscribers

Collection page traffic spiking?
  → Check if Piano Hero is placed on that page
  → If not → suggest adding it (editorial mode)

Subscriber inactive 30+ days?
  → Social post first (Instagram editorial for that collection)
  → Email only if social doesn't convert in 7 days
```

## New sales techniques (2025–2026)

**Narrative commerce** — products embedded in story (collection, music, place). Piano Hero IS narrative commerce. Reinforce at every touchpoint.

**Specificity over generic social proof** — "Renato Tedeschi ordered the Glyph Archive hoodie twice" beats "customers love this."

**Made-to-order transparency** — "7–10 days production" stated clearly. Luxury buyers respect honesty over urgency tactics.

**Collection graph recommendations** — map collections by affinity:
- Hours → Glyph (warmth → amber sophistication)
- Riviera → Pulse (Mediterranean → electronic)
- Origin → Marker (botanical → urban red)
- Token → Flag (purple freedom → red statement)

**Virtual try-on** — `bks-tryon` module in development. High priority for conversion — made-to-order's biggest friction is fit uncertainty.

## Metrics to monitor

| Signal | Alert threshold | Action |
|---|---|---|
| Email open rate | < 30% | Fix subject lines |
| Collection time-on-page | < 40s | Review Piano Hero placement |
| Add-to-cart rate | < 1.5% | Fix PDP (size chart, made-to-order clarity) |
| Instagram Reel views | > 1k | Follow up with drop announcement |
| Zero abandoned checkout | Persistent | Problem is PDP, not checkout — fix product page |

## AI operating principles

1. Scale honesty — 32 customers. Recommend actions executable by 1 person in 30 minutes
2. Editorial first — every commercial move must preserve magazine feel. No "SALE 30% OFF"
3. Quarterly rhythm — big moves quarterly, content and community between drops
4. The 1 person principle — each week, identify 1 person to reach (journalist, brand partner, creator)
5. Data over assumption — if no data, say so. Do not fill gaps with generic e-commerce advice

Related: `bakabo-growth-crm-member-area`, `bakabo-social-campaigns`, `bakabo-popup-ai`, `bakabo-shopify-ops`
