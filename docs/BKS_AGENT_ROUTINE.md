# BKS Agent Routine

Routine: si attiva, aggiorna, suggerisce, verifica e passa avanti.

## Cost principle

Use local data first, batch read-only API calls, estimate cost before metered work, and require approval for paid, public, customer-facing or irreversible actions.

## Steps

1. Refresh local truth - automatic - free_local - none.
2. Check Google trust gate - automatic_read - free_low - none for checks; human for appeal.
3. Check network trust gate - automatic_read - free_low - none for checks; human for DNS/email infrastructure changes.
4. Monitor official inbox - read_and_draft - low - required before send for risky cases.
5. Evaluate customer/social signals - automatic_read - low_medium - none for read; required for retarget/send/ad spend.
6. Prepare next action - automatic - free_local - depends on action risk.
7. Generate assets/copy - draft_automatic - medium_controlled - required before public use.
8. Publish or send - supervised_write - variable - explicit human approval.
9. Verify result and learn - automatic_read - low - none unless rollback/publish needed.

## Cost guards

- Local files / SQLite: Use first for every answer and routine update. Approval: none.
- Google/Shopify read checks: Batch reads; avoid repeated live calls during one dashboard refresh. Approval: none for read-only.
- OpenAI reasoning/copy: Use concise prompts, reuse Knowledge DB summaries, generate drafts in batches. Approval: none for internal draft; approval before publication.
- HeyGen rendering: Render pilot first, then batch only approved scripts/images. Approval: required before render batch.
- Social publishing APIs: Prepare posts locally; publish only after trust and approval gates. Approval: required before publish.
- Paid Ads APIs: Never autonomous while Merchant is suspended or trust is red. Approval: explicit budget approval.
- Email campaigns: Segment by consent; include opt-out; do not use deceptive urgency. Approval: required before campaign send.
