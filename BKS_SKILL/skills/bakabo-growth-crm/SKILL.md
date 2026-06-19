---
name: bakabo-growth-crm
description: Lightweight CRM, Metal tier member area, gold ring identity system, Camerino Try-On gate, welcome/re-engagement flows, PDP conversion diagnostics and loyalty logic for BKS Studio / bakabo.club. Triggers: 'draft welcome email', 'member area health', 'gold ring not showing', 'tier upgrade CTA', 're-engage dormant member', 'Camerino gate logic', 'PDP clarity', 'size guide', 'review anchor', 'loyalty mechanics'. Works with bakabo-members (tier CRM), bakabo-commercial-strategy (drop timing, 60-second rule), bakabo-photo-studio (PDP gallery).
---

# BKS Growth CRM & Member Area

Lightweight member system built on TM04 + Shopify tags. No heavy apps. Manual gestures beat automation at current scale.

---

## 1. Metal Tier System

Computed from Shopify order count. CSS color applied to gold ring (`--bks-tier-color`) and tier badge.

| Tier | Orders | Color | Unlocks | CTA |
|------|--------|-------|---------|-----|
| **Lead** | 0–0 | `#7a7a7a` | Size history, AI recommendations. | *Your first BKS piece unlocks the Metal tier and AI size recommendations.* |
| **Iron** | 1–2 | `#8a8a8a` | Wishlist, post-purchase cross-sell. | *One more order opens the Camerino and Early Access. You're almost there.* |
| **Brass** | 3–5 | `#c8a96e` | Camerino Try-On, +48h drop early access. | *Brass members get Early Access to every new drop 48 hours before the public.* |
| **Silver** | 6–10 | `#b0b0c8` | +24h drop access, full BKS Studio Archive. | *Silver members get exclusive 24h head-start on every new collection drop.* |
| **Gold** | 11+ | `#d4a030` | VIP private drops, white-glove curation, invitation-only access. | *Gold is earned through loyalty, never purchased.* |

---

## 2. Email Segments

| Segment | Tag | Metal tier | Size | Trigger | Action |
|---------|-----|-----------|------|---------|--------|
| BKS Subscriber | `bks-subscriber` | Lead | 12 | email subscriber, 0 orders | Welcome flow: 3 emails in 7 days. Frame around BKS world + Camerino teaser. No coupon, no urgency. |
| BKS Drop | `bks-drop` | Iron | 1 | 1-2 orders | Post-purchase flow after delivery. Second-purchase cross-sell keyed to collection. Show Brass tier progress bar. |
| BKS Archive | `bks-archive` | Brass+ | 1 | 3+ orders | Manual Roberto founder email. Archive access unlocked. Permanent free shipping. Show Silver/Gold progress. |
| Dormant | `no marketing tag` | Lead | 20 | account with 0 orders, no subscriber tag, no signal in 30 days | One re-engagement email: 1 wishlist product + Camerino CTA + tier progress bar. Subject: You haven't visited the Camerino yet. Suppress if no response. |

---

## 3. Member Area Features (TM04)

All active features depend on TM04 theme ID `202392961362` being the published Shopify theme.

| Feature | Status | Rule | Metric |
|---------|--------|------|--------|
| Gold ring (account icon) | `active` | CSS-only animated gold ring around account icon in header. Tier color from CSS var --bks-tier-color. Must be visible immediately on every page load — no JS dependency. | belonging signal, upgrade incentive |
| Account dashboard / Metal tier card | `active` | Show tier name, tier color badge, order count, progress to next tier. Must deliver value within 60 seconds of page load — no empty state. | repeat purchase path |
| Camerino / Try-On | `active` | Unlocked at Brass tier (3 orders). AI virtual try-on via HeyGen. Gate with tier check before rendering. Tab visible to all; content locked with upgrade CTA for Lead/Iron. | wishlist-to-purchase conversion |
| Tier progress bar | `active` | Visible in member dashboard hero without scrolling. Shows orders to next tier. Use in every re-engagement email. | tier upgrade rate |
| Wishlist | `planned` | Available from Iron tier. Simple heart save, no extra app. Used as signal for drop notifications and Camerino briefs. | wishlist-to-cart |
| Order timeline | `planned` | Made-to-order states: in production → printed → shipped → delivered. Show in dashboard, not just Shopify native. | support reduction |
| Early access (drop gate) | `planned` | Tag-gated Shopify page. Brass+: +48h. Silver+: +24h. No separate portal. | subscriber engagement |
| BKS Studio Archive | `planned` | Gold tier only. Process notes and selected prompt library. Not full private library. Gated by bks-archive tag. | VIP retention |
| Referral | `future` | Manual metafields until 50 acquirers. Avoid apps until justified by scale and privacy cost. | referral conversion |
| GDPR profile controls | `legal_required` | Export/delete data paths must remain visible and human-reviewed at all times. | compliance |

---

## 4. Conversion Diagnostics

| Check | Status | Target | Why |
|-------|--------|--------|-----|
| Gold ring visible on header | `needs_review` | CSS ring loads on every page, tier color matches Metal tier var, no JS required. | The ring is the primary belonging signal. If it fails, member identity collapses. |
| Member area 60-second rule | `needs_review` | https://bakabo.club/pages/bks-members delivers one clear value signal within 60 seconds of page load. | Empty sections or slow loads cause exit before member engagement. Rule applies to every tab. |
| TM04 theme active | `needs_review` | Shopify published theme ID == 202392961362. | All member features, gold ring and dark editorial layout depend on TM04. |
| PDP made-to-order clarity | `needs_review` | Made-to-order disclosure visible before add-to-cart. | 0 abandoned checkout suggests drop before checkout. Expectation must be set early. |
| Gallery depth | `needs_review` | 5+ images per PDP including front, back, detail and lifestyle. | Customer needs product reality before purchase. P0 photo shots must be live first. |
| Size guide | `needs_review` | Size guide prominent near size selector on all garment PDPs. | Reduces uncertainty and support load for a made-to-order model. |
| Welcome flow | `ready_to_draft` | >40% open rate, 2 orders / 30 days from 12 active subscribers. | 12 subscribers are the immediate CRM opportunity. Priority action. |
| Reviews anchor | `planned` | >8% review rate after delivery. | Transparent social proof supports Google Merchant trust and PDP conversion. |
| No app bloat | `pass` | Build for 200 customers, not 2000. | Avoid performance hit, extra data processors and unnecessary cost at current scale. |

---

## 5. Voice Rules

- Subject line under 50 characters.
- Email body under 150 words for automated flows.
- No exclamation marks, no emoji, no urgency language.
- No coupon in the first welcome email.
- Use tier progress bar in every re-engagement email.
- Always include unsubscribe link and BKS email footer.

---

## 6. Agent Rules

- Draft welcome/post-purchase/VIP emails; always request Roberto approval before sending.
- Never add fake urgency or coupon pressure in early CRM flows.
- Use Shopify native email first; add apps only when scale justifies cost and privacy impact.
- Gold ring must be CSS-only — no JS dependency. If it fails, flag to Roberto before any member campaign.
- 60-second rule: every tab in the member area must show a value signal within 60s. Empty = broken.
- Record CRM outcomes in Knowledge DB so the agent learns which email and PDP changes convert.

---

## Related Skills

- [[bakabo-members]] — tier CRM detail, email templates, Personal Shopper, Try-On gate
- [[bakabo-commercial-strategy]] — drop timing, 60-second rule, gold ring commercial value
- [[bakabo-photo-studio]] — PDP gallery P0 shots required before conversion diagnostics pass
- [[bakabo-google-trust]] — Google trust P0 must pass before CRM scaling and reviews
