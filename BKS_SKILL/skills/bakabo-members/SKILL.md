---
name: bakabo-members
description: Use this skill for anything related to BKS member management, tier operations, and member communications. Triggers include: "manda un'email ai members", "chi sono i Gold?", "crea una comunicazione per i Brass", "gestisci l'accesso Try-On", "un membro ha raggiunto Silver", "fai una campagna per i wishlist", "qual è il tier di questo cliente?", "prepara una sequenza di onboarding", or any task involving bakabo.club customer tiers, CRM, loyalty actions, or direct member outreach. Works with bakabo-market-intelligence (campaign timing), bakabo-social (channel distribution), bakabo-art-critic / bakabo-popup-ai (content quality). Email: crew@bakabo.club.
---

# BakAbo — Members & Communications Skill

This skill covers the full lifecycle of a BKS member: from first visit (Lead) to VIP (Gold),
including tier management, communication templates, AI Personal Shopper activation, and
direct outreach via email and messaging channels.

---

## 1. Metal Tier System

| Tier | Symbol | Color | Orders | Key unlock |
| --- | --- | --- | --- | --- |
| Lead | ◎ | `#8c8c8c` | 0 | Wishlist, newsletter |
| Iron | ⬡ | `#607080` | 1–2 | Size history, basic AI recs |
| Brass | ◈ | `#d4a030` | 3–5 | AI Personal Shopper, Try-On Camerino, +48h drops |
| Silver | ◇ | `#b0b8c4` | 6–10 | Curated drops +24h, full archive, advanced customization |
| Gold | ✦ | `#c8a820` | 11+ | VIP private drops, white-glove curation, co-creation |

**How tier is calculated (Shopify Liquid):**
```liquid
{% assign orders = customer.orders_count | plus: 0 %}
{% if orders == 0 %}{% assign tier = "lead" %}
{% elsif orders <= 2 %}{% assign tier = "iron" %}
{% elsif orders <= 5 %}{% assign tier = "brass" %}
{% elsif orders <= 10 %}{% assign tier = "silver" %}
{% else %}{% assign tier = "gold" %}{% endif %}
```

**Reference file:** `BKS_SKILL/members/bks-member-marketing.json`

---

## 2. How to look up a member (Python, Shopify API)

```python
from ecommerce_automation.services.shopify_client import ShopifyClient
from ecommerce_automation.config import settings

client = ShopifyClient(shop=settings.shopify_store, token=settings.shopify_admin_token)

# Get customer by email
import requests, urllib3
urllib3.disable_warnings()
domain = settings.shopify_myshopify_domain
token  = settings.shopify_admin_token
headers = {"X-Shopify-Access-Token": token}

def get_customer_tier(email: str) -> dict:
    r = requests.get(
        f"https://{domain}/admin/api/2025-07/customers/search.json",
        params={"query": f"email:{email}", "limit": 1},
        headers=headers, verify=False
    )
    customers = r.json().get("customers", [])
    if not customers:
        return {"found": False}
    c = customers[0]
    n = c.get("orders_count", 0)
    if n == 0: tier = "lead"
    elif n <= 2: tier = "iron"
    elif n <= 5: tier = "brass"
    elif n <= 10: tier = "silver"
    else: tier = "gold"
    return {
        "id": c["id"],
        "email": c["email"],
        "name": f"{c.get('first_name','')} {c.get('last_name','')}".strip(),
        "orders_count": n,
        "tier": tier,
        "tags": c.get("tags", ""),
    }
```

---

## 3. Automated communication triggers

| Event | Trigger | Audience | Channel | Template key |
| --- | --- | --- | --- | --- |
| First purchase | orders_count = 1 | Lead → Iron | Email | `first_purchase` |
| Brass unlock | orders_count = 3 | Iron → Brass | Email + AI chat | `brass_unlock` |
| Silver unlock | orders_count = 6 | Brass → Silver | Email | `silver_unlock` |
| Gold unlock | orders_count = 11 | Silver → Gold | Email (personal) | `gold_unlock` |
| Tier progress | any purchase | all active | AI chat nudge | `tier_progress` |
| Wishlist + new drop | drop event | has wishlist | Email | `wishlist_nudge` |
| Cart abandon (Brass+) | 6h after abandon | Brass, Silver, Gold | Email + AI bot | `cart_abandon_brass` |
| Try-On gate | Brass unlock | Brass+ | Email | `tryon_access` |
| Early drop preview | 48h before drop | Brass+ | Email + popup | `early_drop_brass` |
| Private drop | 24h before (Silver) / exclusive (Gold) | Silver+, Gold | Email | `curated_drop` |

---

## 4. Communication templates (English — all member-facing content is EN)

### `first_purchase` — Welcome to Iron
```
Subject: You're in. BKS Iron tier is active.

Your first BakAbo piece is confirmed.
Size history is now active in your account.
Two more purchases unlock Brass — and the AI Personal Shopper.

Explore your collection: bakabo.club/collections/bks-[collection]
Your account: bakabo.club/account
```

### `brass_unlock` — AI Personal Shopper active
```
Subject: BKS Brass — your Personal Shopper is ready.

You've reached Brass tier.

AI Personal Shopper: active
Try-On Camerino: active
Early collection previews (+48h): active

Your shopper has your size history and collection affinity.
Start a conversation: bakabo.club/pages/bks-ai-assistant

— BKS Studio
```

### `silver_unlock` — Curated drops + archive
```
Subject: BKS Silver. The archive is open.

Silver tier reached.

Full BKS Archive: unlocked
Curated drops: +24h early access
Advanced customization: active

Your BKS history is now the reference for every recommendation.
Explore: bakabo.club/account

— BKS Studio
```

### `gold_unlock` — VIP (personal tone)
```
Subject: BKS Gold — welcome to the inner circle.

[First name],

You're BKS Gold.

Private drops. White-glove curation. Co-creation invitations.

I'll be in touch personally before the next one.

Roberto
BKS Studio — crew@bakabo.club
```

### `wishlist_nudge` — New drop matches wishlist
```
Subject: Your [Collection] wishlist — new [product type] just arrived.

You have [N] items saved from BKS [Collection].
[Product name] just dropped.

It's made to order — quantities are limited by design.

[CTA button: View piece] → bakabo.club/products/[handle]
```

### `tier_progress` — In-chat nudge (AI Personal Shopper)
```
[N] more purchase[s] and you reach [Next Tier].
[Next tier benefit sentence.]
```

### `cart_abandon_brass` — Personal shopper follow-up
```
Subject: Your BKS piece is still available.

[Product name] is still in your cart.
Made to order — once the drop closes, this won't be re-run.

If you have questions on sizing or how it fits your [collection] pieces,
your Personal Shopper can help: bakabo.club/pages/bks-ai-assistant

— BKS Studio
```

---

## 5. Communication channels

| Channel | Tool | When to use | Who triggers |
| --- | --- | --- | --- |
| Transactional email | `ecommerce_automation/communications.py` | Tier upgrades, order confirmations | Automated |
| Marketing email | Shopify email / external | Campaigns, drops, wishlist | Roberto approves |
| AI chat | `bks-ai-assistant.liquid` | In-session nudges, shopper recommendations | Real-time |
| Popup (site) | `bakabo-popup-ai` skill | Drop announcements, tier progress | AI triggers |
| Personal email | Roberto → `crew@bakabo.club` | Gold tier, co-creation, VIP | Manual |
| Telegram bot (future) | `TELEGRAM_BOT_TOKEN` | Drop alerts, tier upgrades | Automated |

**All external communications must be approved by Roberto before sending.**
**`crew@bakabo.club` is the sender/reply-to address for all outgoing member emails.**

---

## 6. AI Personal Shopper rules (Brass and above)

The Shopper reads:
- `member_tier` (injected in Liquid from `customer.orders_count`)
- `member_name` (first name)
- `member_orders` (count)

These are injected by `sections/bks-ai-assistant.liquid` as `data-member-*` attributes.

Recommendation logic:
1. Customer bought from collection X → suggest compatible collection from `collection_affinity_map`
2. Customer has outerwear → suggest swim/resort from same collection
3. Customer has swim → suggest accessories (bags, towels) from same collection
4. Customer wishlist has items → prioritize those first
5. Never recommend a product the customer already owns (same type + collection)

Armocromia → collection mapping (for quiz and suggestions):
| Season | Collections |
| --- | --- |
| Spring warm/bright | Riviera, Glyph, Origin |
| Summer cool/soft | Pulse, Hours |
| Autumn warm/muted | Marker, Hours, Glyph |
| Winter cool/bright | Token, Flag, Pulse |

---

## 7. Try-On access control

- **Access gate:** `customer.orders_count >= 3` (Brass+)
- **Liquid check:** `{% if customer.orders_count >= 3 %}` → show Try-On button
- **Gated UI:** `sections/bks-member-dashboard.liquid` — desktop QR, mobile redirect
- **Backend:** `ecommerce_automation/member_tryon.py`
- **Environment var:** `TRYON_ENGINE_URL` (port 8503 local / Cloudflare Worker in production)

---

## 8. Shopify customer tag operations

To tag a customer when tier changes:

```python
requests.put(
    f"https://{domain}/admin/api/2025-07/customers/{customer_id}.json",
    headers={**headers, "Content-Type": "application/json"},
    json={"customer": {"id": customer_id, "tags": "bks-tier-brass,bakabo-enriched"}},
    verify=False
)
```

Tier tags: `bks-tier-lead`, `bks-tier-iron`, `bks-tier-brass`, `bks-tier-silver`, `bks-tier-gold`

---

## 9. Member segments for campaigns

| Segment | Query | Campaign type |
| --- | --- | --- |
| All active (Iron+) | `orders_count >= 1` | Drop announcements |
| Brass+ (shopper enabled) | `orders_count >= 3` | Personal shopper campaigns |
| Silver+ (early drop) | `orders_count >= 6` | Exclusive previews |
| Gold (VIP) | `orders_count >= 11` | Private drops, co-creation |
| Wishlist holders | has `bks-wishlist-*` tags | New drop of wishlisted item |
| Cart abandon (24h) | abandoned checkout | Recovery sequence |
| Inactive (90d no purchase) | last_order_date < 90d ago | Re-engagement |

---

## 10. Python modules for member operations

| Module | Function |
| --- | --- |
| `ecommerce_automation/communications.py` | `payload()` — communication status; extend for send operations |
| `ecommerce_automation/growth_crm.py` | `payload()` — member CRM data and segments |
| `ecommerce_automation/official_inbox.py` | Message routing and governance |
| `ecommerce_automation/services/shopify_client.py` | `iter_products()`, customer API base |
| `BKS_SKILL/members/bks-member-marketing.json` | Full tier spec, affinity map, marketing triggers |

---

## 11. Scope and rules

**What this skill handles:**
- Tier assignment and upgrade logic
- Communication template selection and drafting
- Shopper recommendation logic
- CRM segmentation for campaigns
- Try-On access gating

**What requires Roberto approval:**
- Any actual email send to real customers
- Price changes or offer codes in communications
- Gold tier personal messages (Roberto writes these)
- Any new member benefit that changes the tier structure

**Language:** ALL customer-facing content is English. Italian only in internal tools.

Related: `bakabo-master`, `bakabo-market-intelligence`, `bakabo-social`, `bakabo-popup-ai`
