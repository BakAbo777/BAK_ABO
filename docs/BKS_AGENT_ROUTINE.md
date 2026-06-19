# BKS Agent Routine

Routine: si attiva, aggiorna, suggerisce, verifica e passa avanti.

## Cost principle

Use local data first, batch read-only API calls, estimate cost before metered work, and require approval for paid, public, customer-facing or irreversible actions.

## Steps

1. Refresh local truth - automatic - free_local - none.
2. Check master actions progress - automatic_read - free_local - none for read; human to mark verified actions as pass in memory.
3. Check Google trust gate - automatic_read - free_low - none for checks; human for Merchant appeal.
4. Check network trust gate - automatic_read - free_low - none for checks; human for DNS/email infrastructure changes.
5. Verify member area and theme - automatic_read - free_low - none for read; human to publish theme if draft.
6. Monitor official inbox - read_and_draft - low - required before send for risky cases.
7. Evaluate customer/social signals - automatic_read - low_medium - none for read; required for retarget/send/ad spend.
8. Prepare next action - automatic - free_local - depends on action risk (see dialogic_agent rules).
9. Generate assets/copy - draft_automatic - medium_controlled - required before public use.
10. Publish or send - supervised_write - variable - explicit human approval; blocked if master_actions has P0 blockers.
11. Verify result and learn - automatic_read - low - none unless rollback/publish needed.

## Cost guards

- Local files / SQLite: Use first for every answer and routine update. Approval: none.
- Google/Shopify read checks: Batch reads; avoid repeated live calls during one dashboard refresh. Approval: none for read-only.
- OpenAI reasoning/copy: Use concise prompts, reuse Knowledge DB summaries, generate drafts in batches. Approval: none for internal draft; approval before publication.
- HeyGen rendering: Render pilot first, then batch only approved scripts/images. Approval: required before render batch.
- Social publishing APIs: Prepare posts locally; publish only after trust and approval gates. Approval: required before publish.
- Paid Ads APIs: Never autonomous while Merchant is suspended or trust is red. Approval: explicit budget approval.
- Email campaigns: Segment by consent; include opt-out; do not use deceptive urgency. Approval: required before campaign send.
