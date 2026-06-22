---
name: bakabo-pricing
description: >
  BKS pricing system — approved price ladder, per-category targets, margin
  calculations, rounding rules for marketing, and price audit logic.
  Use this skill when: setting a new product price, auditing live prices,
  rounding off-ladder prices, planning a price update, or running gmc_daily_sync.
  Works with bakabo-business (margin data), bakabo-promotions (discounts),
  bakabo-commercial-strategy (drop mechanics).
metadata:
  type: skill
  version: "1.0"
  created: "2026-06-22"
---

# BKS Pricing Skill

## 1. Approved Price Ladder (USD — only these values)

```
35  39  45  49  55  59  65  69  75  79
85  89  95  99  105 109 115 119 125 129  135  139
```

No product is published at a price outside this list without explicit justification.

---

## 2. Per-Category Targets & Ranges

| Category | Base Cost | Ship avg | Min retail | Target | Premium ceiling |
|----------|-----------|----------|------------|--------|----------------|
| Sneakers | $22 | $11 | $75 | $89 | $105 |
| Backpack | $26 | $11 | $75 | $85 | $95 |
| Swim Trunks | $17 | $8 | $49 | $55 | $65 |
| Puffer Jacket | $46 | $11 | $109 | $125 | $139 |
| Windbreaker | $33 | $10 | $109 | $109 | $125 |
| Travel Bag | $36 | $11 | $85 | $99 | $115 |
| One-Piece Swimsuit | $21 | $8 | $55 | $65 | $75 |
| Hawaiian Shirt | $24 | $8 | $65 | $79 | $85 |
| Lounge Pant | $19 | $8 | $55 | $65 | $75 |
| Pullover Hoodie | $28 | $8 | $65 | $75 | $119 |
| Racerback Dress | $24 | $8 | $65 | $65 | $75 |
| Slipper | $15 | $5.5 | $45 | $45 | $55 |
| Cut & Sew Tee | $19 | $5.5 | $49 | $49 | $59 |
| Athletic Shorts | $17 | $5.5 | $45 | $55 | $65 |
| Flip Flop | $13 | $5.5 | $35 | $45 | $55 |
| Beach Towel | $18 | $8 | $45 | $49 | $55 |
| Swimwear | $21 | $8 | $55 | $65 | $75 |

---

## 3. Margin Formula

```
net_revenue = retail × 0.971 - 0.30     (Shopify Basic: 2.9% + $0.30)
total_cost  = base_cost + shipping_avg
margin_pct  = (net_revenue - total_cost) / net_revenue × 100
```

| Tier | Margin % | Action |
|------|----------|--------|
| Critical | < 40% | DRAFT immediately — never publish |
| Minimum | 40–45% | Only with explicit justification |
| Standard | 45–65% | Normal publishing target |
| Premium | 65–75% | Hero, limited edition, anchors |

---

## 4. Rounding Rules (Marketing)

When a product price is off-ladder (e.g., $46.38, $111.50, $82.44):

**Rule 1 — Round to nearest ladder value.**
  $46.38 → nearest ladder values are $45 and $49 → check margin at both → pick highest with ≥45%

**Rule 2 — If nearest doesn't meet margin minimum, go UP to next ladder value.**
  Example: $46.38 (dress) → $45 gives 39.7% margin (too low) → $49 gives 44.5% (still low) → $55 = 39.7% → $65 = 49.8% ✓

**Rule 3 — Psychological pricing preference (for marketing):**
  - Prefer 9-ending: $79 beats $80, $109 beats $110
  - For items under $60: prefer $39, $45, $49 over $40, $46, $50
  - For items over $100: prefer $109, $119, $129 over $110, $120, $130
  - Never use .99 endings — BKS is editorial, not discount retailer

**Rule 4 — Windbreaker exception:**
  At $111.50, both $109 and $115 are valid on-ladder. Choose $109 (better psychological price,
  meets margin at 59.3%).

**Rule 5 — Same product type = same price.**
  All variants of the same product type should be at the same price unless a premium option exists.
  (e.g., all Racerback Dresses at $65, not some at $46 and some at $65)

---

## 5. Daily Price Audit

Script: `scripts/gmc_daily_sync.py`
Runs: every morning, checks all 202 active products
Output: `output/gmc_sync_report.json`
Alerts: price below minimum OR not on approved ladder → flag for correction

**Known legitimate "off-ladder" cases (do not alert):**
- Pullover Hoodie at $119: intentional premium tier, 68.7% margin — correct
- Future limited editions: document the exception in gmc_sync_report.json

---

## 6. Live Price Issues (verified 2026-06-22)

| Category | Products | Current price | Correct price | Fix |
|----------|----------|--------------|---------------|-----|
| Racerback Dress | 19 | $46.38 | $65 | Apply fix |
| Cut & Sew Tee | 3 | $41.38 | $49 | Apply fix |
| Hawaiian Shirt (AOP) | 3 | $82.44 | $79 | Apply fix |
| Windbreaker | 11 | $111.50 | $109 | Apply fix |
| Sneakers Flag 03 | 1 | $70.02 | $75 | Apply fix |
| Pullover Hoodie | 15 | $118.58 | OK ($119 premium) | No fix needed |

Script to apply: `scripts/fix_price_alerts.py`
