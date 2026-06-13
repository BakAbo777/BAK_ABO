---
name: bakabo-canva-connectors
description: Canva connector operating skill for BakAbo/BKS. Use when creating or managing Canva social posts, presentations, catalog sheets, brand templates, resize workflows, asset upload, comments/review, exports, or AI-generated Canva designs from BKS briefs.
---

# BakAbo / BKS Canva Connectors

## Operating Rule

Treat Canva as a native design connector inside the BKS workflow, not as a separate design island. The Master prepares drafts, reviews evidence and asks approval before public output.

## Tool Groups

### Interactive AI
- Tools: Generate Design with AI; Generate Structured Design with AI; Request User Review of Presentation Outline; Search Designs
- Use: Create candidate visuals, structured documents and presentation outlines from BKS briefs.
- Agent rule: Use for drafts and candidates; request review before converting into official assets.

### Discovery / Read
- Tools: Search Designs; Search Brand Templates; Search Folders; List Folder Items; Resolve Shortlink
- Use: Find existing BKS designs, folders, brand templates and shared links.
- Agent rule: Use Search Brand Templates for templates/autofill; use Search Designs only for existing designs.

### Brand / Dataset
- Tools: List Brand Kits; Get Brand Template Dataset; Get Assets Metadata
- Use: Understand BKS brand kits, fillable template fields and reusable assets.
- Agent rule: Prefer Brand Kit and dataset-backed templates before free generation.

### Design Readback
- Tools: Get Design Information; Get Design Text Content; Get Design Pages; Get Design Page Thumbnail; Get Presenter Notes; Get Export Formats
- Use: Audit text, pages, thumbnails, notes and export options before editing or exporting.
- Agent rule: Read design content before making edits; preserve BKS naming, series and typography.

### Collaboration
- Tools: List Design Comments; List Comment Replies; Add Comment To Design; Reply To Comment; Resolve Comment
- Use: Run human review loops on campaigns, presentations and social packs.
- Agent rule: Use comments for approvals and change requests; never silently overwrite reviewed work.

### Create / Edit
- Tools: Create Design From Candidate; Create Design from Brand Template; Create Brand Template Draft; Start Editing Design; Edit Design; Save Design Edits; Discard Design Edits
- Use: Turn candidates/templates into editable BKS assets, edit them and save only approved changes.
- Agent rule: A generated candidate must become a design before edit/export/resize; official saves require review.

### Asset / Layout Ops
- Tools: Copy Design; Merge Designs; Resize Design; Import Design From Public HTTPS URL; Upload Asset From URL; Move Item To Folder; Create Folder
- Use: Build campaign packs, adapt formats and organize Canva assets by collection/channel.
- Agent rule: Resize for each channel after source approval; keep collection folders tidy.

### Output
- Tools: Export Design; Publish Brand Template
- Use: Export approved visuals or publish reusable BKS brand templates.
- Agent rule: Export is allowed after review; publishing brand templates requires explicit approval.

## Workflows

### BKS Social Pack
- Input: Collection, product URL, approved image/video, caption brief, language.
- Sequence: Brand Kit -> brand template search -> dataset/autofill or AI candidate -> review -> resize -> export.
- Output: Instagram, TikTok, YouTube Shorts thumbnail/story, Pinterest pin and email visual.

### Avatar Campaign Visual
- Input: HeyGen script, 9:16 hero image, collection identity, CTA.
- Sequence: Read social render sheet -> generate/resize Canva layouts -> comment review -> export.
- Output: Video cover, thumbnail, story frame and post carousel.

### BKS Presentation / Pitch
- Input: Campaign brief, product logic, Google trust status, catalog metrics.
- Sequence: Request outline review -> generate structured design -> readback -> comment review -> export.
- Output: Pitch deck, internal report or partner presentation.

### Catalog / Collection Sheet
- Input: Shopify/Printify CSV, product titles, collection images, price/status data.
- Sequence: Search template -> get dataset -> autofill -> inspect pages/text -> save approved design.
- Output: Collection catalogue, product one-pager or sales sheet.

## Guardrails

- Read before write: inspect designs, templates and datasets before editing.
- Use Brand Kit when available; otherwise use bakabo-design-system tokens.
- Generated designs are candidates until converted and reviewed.
- Use templates/autofill for repeated catalog and campaign formats.
- Do not invent discounts, partnerships, certifications, awards or product claims.
- Do not publish brand templates, overwrite official designs or export public campaign assets without approval.
- Preserve BKS plus collection/series naming and remove emoji/decorative symbols from public titles.
