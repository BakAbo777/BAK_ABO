# BKS AI Training Strategy — Internal Document

## The correct formula for BakAbo AI

```
SKILL → KNOWLEDGE BASE → WORKER → LOG → CORRECTION → FINE-TUNING
```

Do not start from fine-tuning. Start from the Worker.

---

## Phase roadmap

### Phase 1 — Now (active)

- [x] KV with brand rules and all skills (75 skills loaded)
- [x] SKILL 2027 pack loaded
- [x] Basic FAQ: shipping, returns, backpack, sneakers, puffer, collections
- [x] Widget "Ask BKS" on store
- [ ] customer_qna.jsonl → curate 200+ approved Q/A pairs
- [ ] Activate AI Gateway logging for all Widget interactions

### Phase 2 — Vector DB

- [ ] Cloudflare Vectorize: embed all skill content
- [ ] Semantic search over collections and policies
- [ ] Log customer questions from Widget → `real_questions.jsonl`
- [ ] Review flagged answers monthly

### Phase 3 — Shopify Live Data

- [ ] Connect Shopify Storefront API to Worker
- [ ] Real product data: names, prices, availability, images
- [ ] Direct product links in AI responses
- [ ] Collection real-time inventory state

### Phase 4 — Internal AI Catalog

- [ ] AI-assisted title renaming (from Printify names to BKS naming rules)
- [ ] AI-generated product descriptions from templates
- [ ] Image quality check AI gate
- [ ] Prompt catalog generation (auto per product)

### Phase 5 — Fine-tuning (only when ready)

Requires before starting:
- Minimum 500–1,000 real customer questions
- Verified correct answers
- Corrected errors logged
- Frequent product/shipping/returns cases covered
- EN + IT coverage minimum

Using fine-tuning before this stage risks:
- Rigidity (AI invents when unsure)
- Hallucinated product details
- Wrong policy claims
- Brand voice drift

---

## Current recommended stack

| Layer | Tool | Status |
|-------|------|--------|
| Routing / API | Cloudflare Worker v10 | ✅ Live |
| Fast rules / skills | Cloudflare KV (75 skills) | ✅ Live |
| Semantic memory | Cloudflare Vectorize | ⏳ Phase 2 |
| Live product data | Shopify Storefront API | ⏳ Phase 3 |
| Generative AI | OpenAI gpt-4o / gpt-image-1 | ✅ Live |
| Logging + caching | Cloudflare AI Gateway | ⏳ Phase 2 |
| Fine-tuning | OpenAI fine-tune API | ⏳ Phase 5 only |

---

## Priority for BakAbo AI quality

The AI must:

1. **Read BakAbo voice first** → never sound generic
2. **Understand customer intent** → classify before responding
3. **Retrieve skill + documents** → KV → Vectorize
4. **Check Shopify if needed** → real prices, real products
5. **Respond without inventing** → refusal > hallucination
6. **Log the case** → feed `real_questions.jsonl` for improvement

---

## What this training folder is for

`BKS_AI_TRAINING/` is the source of truth for:
- Any new AI assistant deployment for BakAbo
- RAG (Retrieval-Augmented Generation) document index
- Fine-tuning dataset (when Phase 5 is reached)
- Onboarding new AI models to BKS brand voice
- Quality gate reference for AI responses

---

## File inventory

```
00_brand/         Brand voice, positioning, fake-luxury rules, llms.txt
01_skills/        5 core skill documents (from 75-skill KV system)
02_collections/   8 collection briefs with DNA, palette, copy, photography
03_products/      Product types, naming rules, live CSV export from Printify
04_policy/        Shipping, returns, warranty, privacy — AI-summarized
05_examples/      Q/A pairs (50+), product recs, image prompts, refusal rules
06_logs/          Real customer question log (populate from live interactions)
```

---

## Update cadence

| File | When to update |
|------|---------------|
| `06_logs/real_questions.jsonl` | Weekly from AI Gateway logs |
| `03_products/products_export.csv` | Monthly or after major catalog changes |
| `00_brand/*.md` | Only if brand positioning changes |
| `02_collections/*.md` | Only if collection DNA changes |
| `04_policy/*.md` | When Shopify policies are updated |
| `05_examples/customer_qna.jsonl` | Monthly: add new cases, correct errors |
