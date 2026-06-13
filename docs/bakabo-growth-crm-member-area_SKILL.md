# bakabo-growth-crm-member-area

Skill for lightweight CRM, member area, social proof, reviews, wishlist and loyalty logic.

## Core constraints

- Voice is editorial, cool, no urgency, no exclamation marks, no emoji in body copy.
- Current scale is small: manual gestures beat heavy automation.
- Build for 200 customers, not 2000.
- PDP clarity comes before abandoned checkout or aggressive email flows.

## Segments

- BKS Archive (bks-archive): Manual founder email, archive access, permanent free shipping.
- BKS Drop (bks-drop): Post-purchase flow after delivery, second-purchase cross-sell.
- BKS Subscriber (bks-subscriber): Welcome flow: 3 emails in 7 days, no coupon, no urgency.
- Dormant (no marketing tag): One re-engagement email; suppress if no signal in 30 days.

## Agent rules

- Draft welcome/post-purchase/manual VIP email, but request approval before sending.
- Never use fake urgency or coupon pressure in early CRM.
- Use Shopify native tools first; add apps only when scale justifies cost and privacy impact.
- Save CRM signals into Knowledge DB so the agent learns which PDP and email changes work.
