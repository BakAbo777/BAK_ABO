---
name: bakabo-brand
description: Use this skill whenever working on content, copy, communication, or design decisions for the BKS Studio / BakAbo brand (bakabo.club). Triggers include writing product descriptions, captions, newsletters, ads, push notifications, homepage copy, naming new products or collections, deciding tone in Italian or English, reviewing existing copy, or any task where output must sound and feel like BKS. Do not use for pure operational Shopify tasks (orders, inventory, app config) — those belong to a separate skill.
---

# BKS Studio — Brand Identity, Voice & Editorial Architecture

This skill encodes how BKS Studio / BakAbo communicates and how its catalog is structured. Apply it whenever producing text, naming, or creative direction for the brand. When in doubt, prefer **silence over a generic phrase**: it is better to ask the user for a missing detail than to fill a description with filler that breaks the voice.

## 1. What BKS Studio is (positioning)

BKS Studio is a **digital atelier** producing **AI-generated wearable art** distributed via on-demand production (print-on-demand infrastructure). Italian operator, EU + US market, operating under the **BKS** commercial code, sold via Shopify on bakabo.club.

The brand sits in the **accessible designer** segment: prices €40–140, editorial presentation, original AI-driven design language. **It is not luxury**, and does not pretend to be — that would require atelier-grade materials and small-series construction that the production model doesn't support. It is also not fast fashion: every piece is conceived as a designed artifact, not a trend chase.

Three positioning pillars, in priority order:

1. **AI-art as a design language** — every print, pattern and graphic originates from an AI-driven creative process built on a curated library of art-movement prompts (Neo-Dada, Neo-Expressionism, Espressionismo, Hyperrealism, Optical, Brut, Naïf, Arcade, and more). This is the differentiator: not "AI gimmick", but **AI as the new craft tool** of a digital studio.
2. **Accessible designer, not mass-market** — curated catalog, editorial presentation, prices that respect the buyer's intelligence. Reference set: Études, Daily Paper, Carne Bollente, Drôle de Monsieur, Tealer.
3. **On-demand by design** — every piece is printed and produced after purchase. No warehouse, no overstock, every piece travels from prompt to wardrobe.

Tagline anchors. Use these or close variants:
- *AI-Art Atelier*
- *Wearable art, on demand*
- *Prompts to pieces*
- *Designed by AI, curated by hand*

## 2. The three-level architecture (CRITICAL)

Three levels must remain separate. Mixing them is the most common branding error and must be avoided systematically:

| Level | Customer sees it? | Function | Example |
|---|---|---|---|
| **Collection name** | ✅ Yes | Editorial / commercial label | `BKS Hours` |
| **Series identity** | ❌ No (internal metadata only) | Creative DNA, prompt source, workflow tag | `series:hyperrealism` |
| **Product title** | ✅ Yes | Shopify title, SEO, ads | `BKS Sneakers — Hours` |

The customer **must never** read the metadata terms (Neo-Dada, Hyperrealism, Brut, Naïf, Optical, Neo-Expressionism, Arcade, Islands). These are internal production codes — they live in Excel, Make.com, Shopify tags, SEO metadata, and database. They do not appear on labels, product pages, ads, or homepage.

The customer reads only the **8 Collection names** listed in §3.

## 3. The 8 BKS Collections (permanent editorial system)

These are the brand's permanent collection identities. They are not seasonal — they are the editorial architecture of BKS Studio. New products are always assigned to one of these 8.

Listed by **strategic priority**, not alphabetically:

### 3.1 BKS Hours — *Signature collection*
- **Internal metadata:** `series:hyperrealism`
- **Role:** signature / city mood / hero collection
- **What it is:** city, windows, interiors, light, waiting, daily life. Edward Hopper energy. The most adult, curated, restrained side of BKS.
- **Visual register:** monochrome, abstract-realist, urban silhouettes, muted palette, contemplative.
- **What it is not:** colorful, playful, decorative, busy.
- **Editorial guardrail:** Hours is the most curated collection. Fewer products, better images, sparser copy. It carries the brand on homepage and campaigns.

### 3.2 BKS Glyph — *Brand DNA*
- **Internal metadata:** `series:brut`
- **Role:** symbolic code, visual alphabet, BKS signs, urban hieroglyphs
- **What it is:** the bridge between BakAbo as fashion brand and BKS as graphic code. Symbols, primitives, fragments, an internal alphabet built over time. The Glyph Index is a permanent editorial asset.
- **Visual register:** symbolic, coded, hand-drawn, internal-system signs, abstract marks.
- **What it is NOT** *(critical guardrail)*: tribal, ethnic, primitive, pseudo-African, pseudo-Mayan, "ancient symbols". Never use those words in prompts or copy.
- **Future development:** evolves into a proprietary BKS asset — BKS Glyph Index, BKS Symbol Library, BKS Studio Codes.

### 3.3 BKS Marker — *Urban graphic*
- **Internal metadata:** `series:neo-expressionism`
- **Role:** street graphic, hand sign, drawing, urban mark
- **What it is:** the mark, the hand, the urban wall, the drawing. Basquiat/Haring energy without naming them. Confident, gestural, contemporary.
- **Visual register:** brush, drip, marker stroke, urban surface, color blocks with hand-applied text or figure.
- **Separation from Glyph:** Marker = gesture, line, urban sign (action). Glyph = symbol, code, system (alphabet).

### 3.4 BKS Riviera — *Resort permanent*
- **Internal metadata:** `series:islands`
- **Role:** Mediterranean lifestyle / coastal / resort accessories
- **What it is:** swim trunks, Hawaiian shirts, beach towels, resort accessories. Mediterranean, not generic-tropical.
- **Visual register:** sun, palm, coast, salt, marble, terracotta, deep blue, faded summer.
- **Guardrail:** always brand it as `BKS Riviera`, never just `Riviera` — single-word is undefendable.

### 3.5 BKS Pulse — *Kinetic / optical*
- **Internal metadata:** `series:optical`
- **Role:** geometric, kinetic, rhythm
- **What it is:** optical patterns, geometric repetitions, visual vibration, modular rhythm. More alive than "Grid".
- **Visual register:** op-art, kinetic, repetition, modular grids with movement, monochrome or duotone.
- **Guardrail:** reserve only for products with genuinely optical/kinetic patterns. If a pattern is just decorative geometric without movement, it does not belong to Pulse.

### 3.6 BKS Token — *Digital / arcade*
- **Internal metadata:** `series:arcade`
- **Role:** pixel, game, digital collectible object
- **What it is:** arcade aesthetics, pixel art, game references, kaleidoscopic digital fields.
- **Visual register:** pixel, low-bit, kaleidoscope, gamer-era colors, joystick / token / quarter references.
- **CRITICAL guardrail:** never use crypto / NFT / web3 / "digital asset" copy. Token here is the physical object — a coin, a counter, a unit. Not blockchain.

### 3.7 BKS Flag — *Pop collage*
- **Internal metadata:** `series:neo-dada`
- **Role:** pop-collage, coded fields, graphic blocks
- **What it is:** abstract flags, coded color fields, graphic blocks, Jasper Johns indirect references (without naming him). Pop-Dada energy.
- **Visual register:** color blocks, stenciled fields, abstract banners, geometric color compositions.
- **CRITICAL guardrail:** Flag does NOT mean national flags, political flags, or territorial identity. Never use "USA flag", "Italian flag", "national flag", "political flag" in copy or prompts. Define Flag as **abstract flags, coded fields, graphic blocks** only.

### 3.8 BKS Folklore — *Narrative / figurative*
- **Internal metadata:** `series:naif`
- **Role:** figurative, story, memory, gardens, animals, fable
- **What it is:** imaginary folklore, private mythology, drawn stories, animals as narrative, gardens, fables.
- **Visual register:** flat-drawn, illustrative, painterly, warm palette, storytelling figures.
- **CRITICAL guardrail:** Folklore is **imaginary, private, invented**. It is NOT a reference to specific real cultures. Never use "tribal folklore", "ethnic folklore", "ancient folklore", "native symbols", or names of real ethnic groups in copy or prompts.

## 4. Collection priority (not all carry equal weight)

| Priority | Collection | Strategic role |
|---|---|---|
| 1 | **Hours** | Signature, hero |
| 2 | **Glyph** | Brand DNA, proprietary system |
| 3 | **Marker** | Urban graphic |
| 4 | **Riviera** | Resort permanent |
| 5 | **Pulse** | Optical / kinetic |
| 6 | **Token** | Digital / arcade |
| 7 | **Flag** | Pop collage |
| 8 | **Folklore** | Narrative / figurative |

Hero space (homepage hero, campaign opener, press features) goes by default to **Hours** or **Glyph**. The other six rotate based on season, drop, or campaign theme.

## 5. Site navigation architecture

**Customer-facing navigation has two axes**, never 24 cross-product pages:

```
Header navigation:
  MAN      → /collections/bks-man
  WOMAN    → /collections/bks-woman
  ACCESSORIES → /collections/bks-accessories
  COLLECTIONS → /collections (entry to the 8 BKS collections)
```

Inside `COLLECTIONS` the customer finds the 8 collection landing pages (Hours, Glyph, Marker, Riviera, Pulse, Token, Flag, Folklore).

Each collection page contains **filters**: Man / Woman / Accessories / Shoes / Outerwear / Bags / AOP. So the customer navigates either **by use** (MAN/WOMAN/ACCESSORIES) or **by visual world** (the 8 collections), never through cross-product matrix pages.

## 6. Product title system

**Single formula, no exceptions:**

```
BKS [Product Type] — [Collection]
```

Examples (correct):
- `BKS Sneakers — Pulse`
- `BKS Backpack — Glyph`
- `BKS Swim Trunks — Riviera`
- `BKS Windbreaker — Marker`
- `BKS T-Shirt — Hours`
- `BKS Travel Bag — Flag`

Never (legacy errors to avoid):
- `BKS Pulse™ Urban Luxury Sneakers` — wrong (™, "luxury", over-long)
- `BKS Neo Citizens Digital Art Premium Shoes` — wrong (legacy proprietary name, "premium", "digital art" fluff)
- `Hiroto Yamamoto (BKS)🍀 Sneakers` — wrong (random AI-generated name, emoji)

For multiple variants inside the same collection-type combination, use a two-digit suffix:
- `BKS Sneakers — Pulse 01`, `BKS Sneakers — Pulse 02`, `BKS Sneakers — Pulse 03`

Later evolution (Phase 2, after catalog is stable) may introduce editorial variant names: `BKS Sneakers — Pulse / Mesh`, `BKS Sneakers — Pulse / Signal`. **Not in Phase 1.**

## 7. Shopify tag system (metadata)

Every active product carries this tag set. Tags drive collection assignment, internal filters, automation, and Make workflows.

**Always present:**
```
brand:bks
collection:[hours | glyph | marker | riviera | pulse | token | flag | folklore]
series:[hyperrealism | brut | neo-expressionism | islands | optical | arcade | neo-dada | naif]
macro:[man | woman | accessories]   ← may have multiple (e.g. man + accessories)
type:[shoes | outerwear | aop | backpack | bags | tee | home-decor]
status:active
curation:keep
drop:catalog-reset-2026
```

**Optional / contextual:**
```
prompt-source:[sheet-name-row-NN]   ← link back to Excel prompt file
curation-score:[1-5]                 ← internal quality rating
limited:[true|false]                 ← only when genuinely limited drop
```

**Customer-visible tags (Shopify storefront):** only the `BKS Hours` style display, derived from `collection:hours`.

**Invisible to customer, used by Make:** everything else.

## 8. Tone of voice

Four dials. Hold all four at the same time — they define a single voice.

| Dial | Setting | What it means in practice |
|---|---|---|
| Register | **Editorial** | Short, declarative sentences. Magazine captions, not marketing copy. |
| Warmth | **Cool but accessible** | Confident but never aloof. The brand is for design-curious people, not for an elite. No exclamation marks. No emoji inside body copy. |
| Density | **Minimal** | Cut every adjective that does not earn its place. Two strong words beat five soft ones. |
| Posture | **Curator** | Speak as someone who has chosen the prompts, the styles, the references — and who shares the work. |

**Voice in one line:** *A digital art studio talking through its work, in editorial Italian and English.*

## 9. Brand lexicon

**Use freely** — these belong to the BKS dictionary:
*series · prompt · pattern · field · typography · silhouette · edge-to-edge · graphic · technical · resort · lounge · editorial · drop · collection code · on-demand · printed-on-order · movement · reference · composition · monochrome · iconography · digital craft · studio · code · index · archive · system · fragment · sign · alphabet*

**Avoid** — these break the voice on contact:
*amazing · stunning · must-have · trendy · cute · cool · fashionista · stylish · gorgeous · perfect for · level up · vibes · slay · iconic (overused) · game-changer · exclusive offer · sale · cheap · affordable · best price · "wear your story" · "express yourself" · "one-of-a-kind"*

**Removed permanently** (would mislead about the production model):
*luxury · premium · made-to-order craft · couture · bespoke · atelier-produced · handcrafted · made in Italy (for production) · each piece unique*

## 10. Honest claims (AI-art transparency)

The brand can — and should — be **explicit and proud** about the AI-art process. Hiding it would be a mistake; the audience values transparency about creative tools.

✅ True claims the brand can make:
- *"Each print originates from an AI-driven process, prompted and curated by the studio."*
- *"Built on a library of art-movement references — Neo-Dada, Optical, Brut, more."*
- *"Printed on demand, no warehouse, no overstock."*
- *"Designed in Italy."*

❌ Claims the brand cannot make:
- *"Handcrafted."* — no, it's printed.
- *"Atelier-produced."* — the studio is digital, not a physical atelier.
- *"Made in Italy."* — the design is, the production happens through global POD networks.
- *"Each piece unique."* — no, printed on demand from a fixed design.
- *"Limited edition"* — only if the drop is actually capped and numbered.

## 11. Roadmap (4 phases)

The collection system is built to support all phases without name changes.

**Phase 1 — 2026: Catalog Reset**
- 90 active products, 940 archived as Draft
- 8 collections live on site
- 3-macro navigation (MAN / WOMAN / ACCESSORIES) + COLLECTIONS
- SEO rewritten, images coherent, editorial homepage

**Phase 2 — 2026/2027: Drops**
- No mass additions. Small editorial drops, 8–12 products each.
- One drop per collection, rotating: Drop 01 — Hours, Drop 02 — Riviera, Drop 03 — Glyph, Drop 04 — Marker, etc.
- Each drop: hero image, story page, newsletter, micro-campaign, homepage update.
- Editorial scarcity, never advertised as "limited edition" unless capped.

**Phase 3 — 2027: Signature products**
- Beyond collections, recurring iconic objects: `BKS Hours Jacket`, `BKS Glyph Backpack`, `BKS Riviera Swim Trunks`, `BKS Marker Sneakers`.
- Recognizable silhouettes + visual worlds — the future of BKS is not more graphics, it's recurring forms with strong identities.

**Phase 4 — 2027/2028: Proprietary BKS system**
- Glyph becomes the foundation of: BKS Glyph Index, BKS Symbol Library, BKS Pattern Archive, BKS Studio Codes.
- Editorial site content (not just e-commerce): *"The Glyph Index — A visual archive of BKS signs, fields and fragments."*
- Brand evolves from e-commerce store to cultural system.

## 12. Trademark strategy

Single-word collection names ("Hours", "Pulse") are weak as standalone marks. The defensible asset is the **portfolio**: `BKS Hours` + `BKS Pulse` + `BKS Marker` + ... as a system.

Always brand collections as `BKS [Collection]`, never as standalone words. Customer mentions on social/press: encourage the `BKS [Collection]` form.

For future trademark filing (Phase 2-3, with IP lawyer):
- Class 25 (clothing, footwear, headgear) — primary
- Class 18 (bags, backpacks, leather goods) — secondary
- Class 14 (jewelry, watches) — only if relevant
- Geographic scope: EU (EUIPO) + UK + US (USPTO) + Italy national

The current quick-checks performed in May 2026 found:
- `Target` blocked by Target Corp Class 25 (registered + renewed 1981) — eliminated, replaced with `Flag`
- `Hours` — pending application "HOURS CLOTHING" (low conflict, manageable with BKS prefix)
- `Folklore` — pending application "FOLKLORE FLANNEL" (manageable with BKS prefix)
- `Marker`, `Riviera`, `Pulse`, `Token`, `Glyph`, `Flag` — no immediate conflicts in surface check

These are preliminary checks, not legal opinions. IP counsel required before any actual filing.

## 13. Quick self-check before publishing any content

Run any copy through this six-point check:

1. Could a fast-fashion or POD-spam brand have written this exact sentence? → rewrite.
2. Could a true luxury brand (Acne, Bottega) legitimately use this sentence? If yes, we are over-claiming. → tone down.
3. Are there exclamation marks or body-copy emoji? → remove.
4. Does any word from the "Avoid" or "Removed permanently" list appear? → replace.
5. Does the copy mention metadata terms (Neo-Dada, Hyperrealism, Brut, Naïf, Optical, Neo-Expressionism, Arcade, Islands) to the customer? → replace with collection names (Flag, Hours, Glyph, Folklore, Pulse, Marker, Token, Riviera).
6. Is the on-demand/AI-art nature acknowledged where relevant (without apologising)? → if missing, add.

If all six pass, ship it.
