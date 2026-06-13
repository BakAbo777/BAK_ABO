# BKS — Creazione pagine (footer menu)

Ordine operativo: **Online Store → Pages → Add page**, per ognuna: titolo, incolla il body HTML (icona `<>` nell'editor), assegna il Theme template indicato, verifica l'handle. Poi attiva il footer menu.

Le tre voci `/policies/*` NON sono Pages: si generano in **Settings → Policies** (Privacy, Terms, Refund — il refund 30 giorni è già configurato; basta che il testo sia presente e i link si attivano da soli).

Un solo dato da confermare prima di pubblicare: il **tempo di produzione** (segnato `[X–Y]` sotto) — deve combaciare con i tempi reali Printify/Smart Printee/MWW, è una promessa.

---

## 1. About BKS Studio
- **Title:** `About BKS Studio` · **Handle:** `about` · **Template:** `about`

```html
<p><strong>BKS Studio is a digital atelier. Every print begins as a prompt.</strong></p>

<p>We design with artificial intelligence and print on demand. Each graphic originates from an AI-driven process — prompted, selected and refined by the studio — built on a curated library of art-movement references. No warehouse, no overstock: a piece exists only after someone orders it.</p>

<h2>Eight collections, one system</h2>
<p>BKS is organised as a permanent editorial system. Eight visual worlds — Hours, Glyph, Marker, Riviera, Pulse, Token, Flag, Folklore — each with its own graphic language, applied across apparel, swim and accessories. Collections grow piece by piece; they do not expire with seasons.</p>

<h2>How a piece is made</h2>
<p>Designed in Italy. Printed and produced on demand through an international production network, shipped directly to you. Printing to order takes a few days longer than shipping from a shelf — it is also why nothing we design becomes waste.</p>

<h2>What we stand behind</h2>
<p>30-day returns. 2-year EU warranty. Transparent about our tools: the work is AI-assisted by design, and we consider that the craft of a digital studio.</p>

<p><em>BKS Studio — bakabo.club<br>Terni, Italy · P.IVA 00774100556</em></p>
```

---

## 2. Help & FAQ
- **Title:** `Help & FAQ` · **Handle:** `help-faq` · **Template:** `help-faq`

```html
<h2>Production and shipping</h2>

<h3>When will my order ship?</h3>
<p>Every piece is printed after you order it. Production takes [X–Y] business days; shipping adds 7–15 business days depending on destination. The two times are separate — your confirmation email and tracking page show both.</p>

<h3>How do I track my order?</h3>
<p>You receive a tracking link by email as soon as your piece leaves production. The link updates at every step until delivery.</p>

<h3>Do you ship to my country?</h3>
<p>We ship to Italy and the EU, the United States, Canada, India and most other countries. Costs and any free-shipping threshold for your market are shown at checkout.</p>

<h2>Returns and warranty</h2>

<h3>Can I return a piece?</h3>
<p>Yes — 30 days from delivery, free return by mail, in over 80 countries. The piece must be unworn and unwashed. Start a return by writing to us with your order number; full conditions are in our <a href="/policies/refund-policy">Refund Policy</a>.</p>

<h3>Is there a warranty?</h3>
<p>All BKS products carry a 2-year EU warranty covering manufacturing defects.</p>

<h2>Product</h2>

<h3>How do I choose my size?</h3>
<p>Each product page includes a size guide specific to that piece — apparel, sneakers, swim and bags each have their own. When between sizes, we suggest the larger one.</p>

<h3>Are the designs really made with AI?</h3>
<p>Yes. Each print originates from an AI-driven process, prompted and curated by the studio. We treat AI as the design tool of a digital atelier — and we say so openly.</p>

<h3>Why is my piece printed on order?</h3>
<p>On-demand production means no warehouse and no overstock. It takes a few days longer and produces no waste.</p>

<h2>Payment</h2>

<h3>Which payments do you accept?</h3>
<p>All major cards and the payment methods shown at checkout. Prices in the EU include VAT; in the US, tax is calculated at checkout.</p>

<p>Anything else — <a href="/pages/contact">write to us</a>. We reply within one business day.</p>
```

---

## 3. Contact
- **Title:** `Contact` · **Handle:** `contact` · **Template:** `contact` *(il form è già nel template — il body resta breve)*

```html
<p>Questions about an order, a return, or a piece you have in mind — write to us. We reply within one business day.</p>
<p>BKS Studio · Terni, Italy</p>
```

---

## 4. Shipping & Returns
- **Title:** `Shipping & Returns` · **Handle:** `policy` · **Template:** `policy`

```html
<h2>Production</h2>
<p>Every BKS piece is printed after purchase. Production takes [X–Y] business days and is separate from shipping time. You receive an email when your piece enters production and another when it ships.</p>

<h2>Shipping</h2>
<p>Worldwide shipping, 7–15 business days after production. India: 8–21 business days, free shipping. Zones currently active: Italy and Europe, United States, Canada, India, plus most other countries at checkout rates.</p>
<p>Shipping costs and free-shipping thresholds vary by market and are always shown at checkout before payment. Every order ships with a tracking link.</p>

<h2>Returns</h2>
<p>30 days from delivery, free return by mail, available in over 80 countries. Pieces must be unworn, unwashed and in original condition. To start a return, write to us with your order number — we send the return label and instructions.</p>

<h2>Refunds</h2>
<p>Refunds are issued to the original payment method within 14 days of receiving the return. Full terms: <a href="/policies/refund-policy">Refund Policy</a>.</p>

<h2>Warranty</h2>
<p>All BKS products carry a 2-year EU warranty covering manufacturing defects. If a piece arrives damaged or develops a defect, contact us with photos and your order number — we replace or refund.</p>
```

---

## Dopo la creazione — attiva il footer menu

Navigation → `footer`:

```
About BKS Studio   → /pages/about
Help & FAQ         → /pages/help-faq
Contact            → /pages/contact
Shipping & Returns → /pages/policy
Privacy Policy     → /policies/privacy-policy
Terms of Service   → /policies/terms-of-service
Refund Policy      → /policies/refund-policy
```

Verifica finale: ogni pagina aperta dal footer, template corretto assegnato (pannello destro della pagina), nessun 404 sui tre `/policies/*`.
