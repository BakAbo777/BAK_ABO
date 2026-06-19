---
name: bakabo-commercial-strategy
description: Use this skill for commercial growth strategy, conversion optimization, drop mechanics, member retention, and mobile UX decisions at BKS Studio / bakabo.club. Triggers include: "how do we convert more visitors?", "plan the next drop campaign", "increase member LTV", "why are users leaving?", "mobile retention strategy", "immediate value for members", "re-engagement campaign", "gold ring commercial value", "wishlist-to-purchase funnel", "referral mechanics". Works with bakabo-members (tier CRM), bakabo-business (pricing), bakabo-social (channels), bakabo-market-intelligence (timing). Primary output: actionable tactics, copy briefs, funnel improvements.
---

# BakAbo — Commercial Strategy Skill

Core framework for converting visitors → members → repeat buyers at BKS Studio.

---

## 1. The 60-Second Rule (Mobile)

When a member opens the app or member area, they must receive **one clear value signal within 60 seconds**:
- Gold ring visible on account icon (identity confirmation)
- Wishlist count or new item suggestion in hero
- Early Access banner if a drop is live or upcoming
- If nothing to show: display tier progress bar ("3 orders to Brass")

**If no value signal appears in 60 seconds → user exits.** Every tab/section should have a non-empty default state.

---

## 2. Drop Mechanics — BKS Release Formula

```
72h before drop  → Email to Brass+ (Early Access confirmed)
48h before drop  → Push to wishlist owners of similar items
24h before drop  → Silver+ preview access (private collection URL)
0h               → Public drop live (all members + social push)
+12h             → "Only X left" signal if stock below threshold
+48h             → Closed — archive entry created
```

**Scarcity is real** (POD, but limited colorways per collection). Communicate it.

---

## 3. Gold Ring — Commercial Identity

The animated gold ring around the member icon/avatar is not just decorative:
- **Belonging signal**: member sees their status on every page load
- **Social proof prompt**: "show friends your member status" referral hook
- **Upgrade incentive**: showing iron/brass members what gold ring looks like

Use the ring color in email headers for members (match their tier color).

---

## 4. Wishlist → Purchase Funnel

| Signal | Trigger | Action |
|--------|---------|--------|
| Item restocked | Product back in Printify | Email member with wishlist item |
| Price drop | Printify cost reduction passed through | Push notification + email |
| Drop preview | New collection containing similar style | "Your wishlist matches this drop" |
| Camerino preview ready | AI try-on complete | Email with image + direct "Buy now" CTA |

---

## 5. Tier Progression Mechanics

**Lead → Iron** (first order): Unlock: size history, AI recs.
CTA: "Your first BKS piece unlocks the Metal tier and AI size recommendations."

**Iron → Brass** (3 orders): Unlock: Camerino Try-On, +48h drop access.
CTA: "One more order opens the Camerino and Early Access. You're almost there."

**Brass → Silver** (6 orders): Unlock: +24h access, full archive.
CTA: "Silver members get exclusive 24h head-start on every new collection drop."

**Silver → Gold** (11 orders): Unlock: VIP private drops, white-glove curation.
CTA: "Gold is invitation only — earned through loyalty, never purchased."

---

## 6. Re-engagement (30-day inactive)

Segment: members with 0 purchases in 30 days.
Email subject: `You haven't visited the Camerino yet.`
Body: show 1 product from their wishlist + Camerino CTA + progress to next tier.

---

## 7. Mobile-First Principles

- All CTAs: min height 48px (touch target)
- Hero loads in < 2s (no heavy images above fold)
- Avatar + gold ring: visible immediately (CSS-only, no JS dependency)
- Tab navigation: horizontal scroll, no wrapping
- Tier progress: visible in hero without scrolling
- Error states: never show empty sections — always a CTA fallback

---

## 8. Google Trust Contract Gate

Before any growth action, check `google_trust_contract.csv → summary.merchant_appeal_ready`.

**P0 blockers** (block Merchant appeal, paid ads, and campaign layer):

| Need | What blocks it |
|------|---------------|
| Business identity | About or Contact page missing/broken |
| Product truth | `local_inventory_errors > 0` or `unavailable_pages > 0` |
| Collection and theme identity | TM04 not published, Origin collection missing, or `folklore` still in feed |
| Returns and refunds | Refund policy page broken |
| Secure checkout | Bitcoin framed as investment (never acceptable) |

**Commercial stage gating** — do not advance to the next stage until P0 blockers for that stage are clear:

```
Trust foundation (P0 green)  → Collection identity stage (hero banners, TM04 collections live)
Collection identity           → Conversion support (first orders confirmed, P1 shots)
Conversion support            → Campaign layer (paid ads, avatar video, timed offer, Meta 9:16)
Campaign layer                → Merchant appeal (all P0+P1 green, evidence package ready)
```

**Agent rule**: Never propose paid ads or aggressive email campaigns while `p0_blockers` is non-empty.
Read `trust_contract.summary.p0_blockers` before every campaign recommendation.

---

## Related Skills

- [[bakabo-members]] — tier CRM, email templates, individual outreach
- [[bakabo-business]] — pricing, margins, break-even
- [[bakabo-social]] — channel distribution, content calendar
- [[bakabo-market-intelligence]] — timing, competitor analysis
- [[bakabo-google-trust]] — P0/P1 trust needs, merchant_appeal_ready gate, feed diagnostics
