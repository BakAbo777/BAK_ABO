---
name: bakabo-openai-alliance
description: OpenAI alliance operating skill for BakAbo/BKS. Use when structuring OpenAI, ChatGPT Projects, OpenAI API, knowledge memory, realtime voice, image/copy generation, safety preflight, customer assistant, or agent workflows inside the BKS Master.
---

# BakAbo / BKS OpenAI Alliance

## Operating Rule

Use OpenAI as the allied intelligence layer of the BKS Master. OpenAI must adapt to BKS identity, data, phases, approvals and tone. It reasons, drafts, summarizes and checks; it does not publish, spend, message customers or make legal/payment decisions without approval.

## Capabilities

### ChatGPT Project
- Area: Strategic workspace
- Use: Founder-level project room for BKS memory, prompts, decisions and cross-tool coordination.
- Env: `OPENAI_CHATGPT_PROJECT_URL`
- Agent rule: Use as an allied workspace; do not expose private project URLs in public repo files.

### OpenAI API
- Area: Agent reasoning
- Use: Draft, classify, summarize, plan, write product/social copy and operate the Master assistant.
- Env: `OPENAI_API_KEY;OPENAI_PROJECT_ID`
- Agent rule: Use project-scoped credentials when available; keep high-risk actions behind approval.

### Knowledge / Vector Memory
- Area: BKS database
- Use: Ground customer assistant, official inbox replies, policy answers and product knowledge.
- Env: `OPENAI_VECTOR_STORE_ID`
- Agent rule: Answer from stored BKS evidence; if evidence is missing, say so and route to human review.

### Realtime Voice
- Area: Conversational interface
- Use: Future low-latency voice layer for the Master or customer assistant.
- Env: `OPENAI_REALTIME_ENABLED`
- Agent rule: Enable only after consent, logging and customer safety rules are ready.

### Images / Creative Prompts
- Area: Visual production
- Use: Generate or improve prompts for product shots, collection hero images and campaign visuals.
- Env: `OPENAI_API_KEY`
- Agent rule: Never invent finished product photography; label AI drafts and verify against real product data.

### Safety / Transparency
- Area: Trust gate
- Use: Check copy for misleading claims, unsupported urgency and policy-sensitive language.
- Env: `OPENAI_API_KEY`
- Agent rule: Use as a preflight assistant, not as legal approval or Google appeal authority.

## Workflows

### Master Next Action
- Sequence: Read dashboard snapshot -> detect blockers -> propose one action -> verify result -> write memory.
- Output: Operational recommendation such as: fix DMARC first, remove emoji titles, verify Merchant trust page.

### Customer Assistant
- Sequence: Read BKS knowledge -> answer with disclosure -> cite policy/source link -> hand off on risk.
- Output: Safe multilingual support reply inside Shopify theme.

### Creative Production
- Sequence: Collection brief -> script/copy/prompt -> Canva/HyperFrames/HeyGen handoff -> review metadata.
- Output: Avatar scripts, social captions, design briefs and motion storyboards.

### Official Inbox
- Sequence: Classify incoming email -> draft reply -> check legal/payment/privacy risk -> request approval.
- Output: Crew@bakabo.club customer/support response draft.

## Guardrails

- OpenAI aligns to the BKS project; BKS does not reshape itself around OpenAI defaults.
- BKS identity, product data, series/collection system, legal duties and Google trust rules are the source of truth.
- OpenAI is an allied reasoning layer, not an unattended business owner.
- The Master must answer from BKS data, local database, verified APIs and policy documents.
- High-risk actions require approval: customer messages, legal claims, payments, ads, public publishing and Google appeals.
- Private ChatGPT Project links belong in `.env`, not tracked source files.
- Use OpenAI to prepare clear options; the interface should keep the user in one flow.
- Record decisions and outcomes so the agent learns from verified results, not guesses.
