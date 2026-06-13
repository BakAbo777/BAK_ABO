---
name: bakabo-hyperframes-video
description: HyperFrames operating skill for BakAbo/BKS motion graphics. Use when composing animated slides, explainer videos, HTML-to-video scenes, motion product trust clips, checking HyperFrames project/render status, or rendering social videos from approved BKS storyboards.
---

# BakAbo / BKS HyperFrames Video

## Operating Rule

Use HyperFrames as the motion layer of the BKS Master: HTML scenes become explainers, animated slides and social videos. Compose and render only with approval gates and metadata.

## Tools

### Compose HyperFrames Video
- Mode: interactive_write
- Use: Create an HTML-based motion video project from a BKS storyboard, script or explainer brief.
- Agent rule: Use after copy/storyboard approval; keep claims transparent and collection naming intact.

### Get HyperFrames Project
- Mode: interactive_read
- Use: Inspect project structure, scenes and assets before editing or rendering.
- Agent rule: Read project state before any render or iteration.

### Render HyperFrames Video
- Mode: interactive_write
- Use: Render the approved HTML motion project into video.
- Agent rule: Render only draft/approved projects and track cost/time before repeated renders.

### Check HyperFrames Project Status
- Mode: read_only
- Use: Check project generation, validation or composition state.
- Agent rule: Poll lightly; do not create duplicate projects when a project is still processing.

### Check HyperFrames Render Status
- Mode: read_only
- Use: Monitor render progress and final output readiness.
- Agent rule: Use status checks for visible progress in the Master dashboard.

## Workflows

### Animated Collection Explainer
- Input: BKS collection name, 35-50 word script, product/collection images, CTA.
- Sequence: Storyboard -> HTML scenes -> compose project -> check project -> render -> check render -> attach to Social Render.
- Output: 9:16 explainer video for Reels, TikTok, YouTube Shorts and homepage section.

### Motion Presentation
- Input: Pitch outline, metrics, Google trust status, product visuals.
- Sequence: Approved outline -> animated HTML slides -> render preview -> review -> export video.
- Output: Animated founder/customer presentation or internal progress video.

### Product Trust Clip
- Input: Made-to-order explanation, shipping/returns clarity, product photo, trust strip copy.
- Sequence: Compliance copy -> short motion graphic -> render -> review with Google-safe checklist.
- Output: Transparent product/trust clip for PDP, email or social.

## Guardrails

- Use HyperFrames for motion from approved HTML/storyboards, not for unverified product claims.
- Keep render loops cost-aware: compose once, check status, render only after review.
- Use 9:16 as the default social format unless the channel requires another format.
- Do not hide terms, prices, delivery expectations or AI disclosure in motion graphics.
- Every rendered video should write metadata: script, collection, source assets, render ID, channel and approval state.
- Avatar/HeyGen and HyperFrames are complementary: avatar speaks; HyperFrames visualizes.
