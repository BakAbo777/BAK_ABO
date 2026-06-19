---
name: bakabo-sound
description: Use this skill whenever working with the BakAbo sound library — the brand's collection of AI-generated music tracks (from Suno/Udio). Triggers include cataloging or renaming audio files, classifying tracks by mood or genre, deciding which track fits a collection, drop, or campaign, planning a Spotify playlist or site background audio, choosing music for social/lookbook video, or any question about how BakAbo uses music in its brand identity. Also use when checking AI-music usage rights before publishing. Works alongside bakabo-brand (voice) and the bakabo-sound-catalog.xlsx file. Do not use for product copy, Shopify ops, or Printify sync.
---

# BakAbo — Sound Library & Sonic Identity

BakAbo's music is AI-generated (Suno/Udio), which makes it the sonic twin of the brand's AI-generated visual design. This is a strategic asset: **fashion AI + music AI = one coherent creative DNA.** This skill defines how to catalog, name, classify, deploy, and clear that library.

The master inventory lives in `bakabo-sound-catalog.xlsx` (5 sheets: README, Catalog, Naming, Folders, Stats). This skill is the logic; the spreadsheet is the data.

## 1. The five sonic moods

Every BakAbo track belongs to one of six categories. Five map to a design system; one is reserved.

| Mood | Sound | Design system | Feeling |
|---|---|---|---|
| **Café Lounge** | Jazz, piano, café ambient, lounge | Mediterranean Lines | Resort mornings, gallery openings |
| **Cyber Electronic** | Tech house, synth, electro | Neo Matrix | Digital, nocturnal, future-urban |
| **Drop Energy** | Moombahton, club, high-BPM | Lava Motion | Launch moments, hype, motion |
| **Deep Session** | Deep house, Chicago house, slow electronic | Neo Citizens | City nights, considered cool |
| **Funk Soul** | Funk, soul, nu-disco, groove | (unassigned) | Warmth, movement, character |
| **Concept** | Surreal, cinematic, ambient | (reserved) | Lookbook films, art pieces |

When a new track arrives, the first decision is always: *which of these six is it?* Everything else follows.

## 2. Naming convention

Format: `BKS-[Mood]-[Genre]-[NNN]`

- **Mood codes:** `Cafe`, `Cyber`, `Drop`, `Deep`, `Funk`, `Concept`
- **Genre tags:** `JazzPiano`, `JazzViolin`, `CafeAmbient`, `LoungeBeats`, `TechHouse`, `Synth`, `Cyberbeat`, `Moombahton`, `ClubBeat`, `DeepHouse`, `ChicagoHouse`, `Funk`, `Soul`, `NuDisco`, `Surreal`, `Cinematic`, `Ambient`
- **Number:** three digits, padded, global and sequential — never reset, never reused

Examples:
- `BKS-Cafe-JazzPiano-007.wav`
- `BKS-Cyber-TechHouse-012.mp3`
- `BKS-Drop-Moombahton-019.mp3`

Rules: lowercase mood and genre codes after the `BKS-` prefix is fine, but be consistent; no spaces, hyphens only; keep the original file in `99_Archive` before renaming.

## 3. Folder structure (Google Drive)

```
BakAbo Sound Library/
├── 00_Inbox             ← new raw Suno/Udio exports, untagged
├── 01_Cafe_Lounge
├── 02_Cyber_Electronic
├── 03_Drop_Energy
├── 04_Deep_Session
├── 05_Funk_Soul
├── 06_Concept
├── 07_Approved_Master   ← final, named, cleared, ready to use
└── 99_Archive           ← original files, never deleted
```

## 4. Cataloging workflow

When the user has new tracks to process, walk this loop:

1. **Land** — new exports go to `00_Inbox`, added as rows in the Catalog sheet with status `To Review`.
2. **Listen** — for each track, fill BPM, Key, Energy (1–5), and a one-line Note. (Claude cannot listen to audio — the user does this step, or uses tunebat.com / mixedinkey.com for BPM and key.)
3. **Classify** — assign Mood Category → this determines the destination folder and the linked design system.
4. **Clear rights** — set the Rights OK column (see section 6). Do not skip this.
5. **Rename** — apply the naming convention; new name goes in the New BakAbo Name column.
6. **Move** — file moves to its mood folder; original copy stays in `99_Archive`.
7. **Promote** — when cleared and named, status → `Approved`, file → `07_Approved_Master`.

Claude's role in this loop: help classify from descriptions the user gives, propose names, propose mood→design-system matches, propose use cases, and keep the catalog consistent. Claude does **not** invent BPM, key, or energy values it cannot hear — those come from the user or a detection tool.

## 5. Strategic use — where music meets the brand

Each mood has a natural home in the BakAbo ecosystem:

| Use case | Best mood | Why |
|---|---|---|
| **Site background / Shopify** | Café Lounge, Deep Session | Low-distraction, premium, long-listen friendly |
| **Drop launch video** | Drop Energy | Hype moment, matches the reveal |
| **Lookbook film** | Concept, Café Lounge | Cinematic, lets the garments lead |
| **Instagram / TikTok reel** | Drop Energy, Cyber Electronic | Short, punchy, algorithm-friendly hooks |
| **Spotify brand playlist** | All moods, sequenced | A "BakAbo Sound" playlist is a brand-world artifact |

Two strategic principles:

1. **Pair sound to collection, not to product.** When a drop launches under, say, `Mediterranean Lines`, its launch content uses Café Lounge tracks. The sound reinforces the design system, building a multi-sensory line identity.
2. **The AI-music story is itself content.** BakAbo can openly frame its music as AI-generated, the same way it frames its prints. "Sound designed the same way we design our prints" is an on-brand narrative — do not hide it, feature it. (Voice: keep it editorial per `bakabo-brand`, never gimmicky.)

### Spotify playlist concept

A flagship "BakAbo Sound" playlist should be sequenced as a journey, not a dump: open with Café Lounge, build through Deep Session and Funk Soul, peak on Drop Energy and Cyber Electronic, resolve back to Concept/ambient. Name sub-playlists after design systems (`Mediterranean Lines — Sound`, `Neo Matrix — Sound`) so they tie back to the fashion lines.

## 6. Rights & clearance — mandatory before publishing

AI-music rights depend on the **platform and the plan** the track was generated on. This is not optional diligence — it gates publishing.

Core rules:
- **Suno:** free plan = personal use only, no commercial use. Paid plans (Pro/Premier) grant commercial use and output ownership, subject to their terms.
- **Udio:** similar tiering — paid grants commercial rights, free does not.
- **"Commercial use"** for BakAbo means anything tied to selling: site background, social ads, paid promos, product/lookbook videos.
- **Keep proof:** screenshot the generation and the active plan; save the platform's terms as a dated PDF.
- **Royalties:** purely AI tracks usually cannot be registered with collection societies (SIAE/ASCAP/etc.) for authorship royalties. Do not claim what you are not entitled to.
- **Imitation risk:** if a track mimics a real artist's voice or a recognizable song, do not use it.
- **Streaming distribution:** releasing on Spotify needs a distributor (DistroKid, TuneCore) that accepts AI music — verify current policy, it changes often.

The Catalog's `Rights OK` column must read `OK Commercial` or `Cleared` before any track goes live. Default is `Check Plan` — treat that as "blocked."

When Claude is asked to suggest a track for any public-facing use, Claude always checks the track's Rights OK status first and flags it if the status is `Check Plan`, `Unknown`, or `Free-Personal Only`.

> This is practical guidance, not legal advice. For high-stakes campaigns, recommend the user consult an IP lawyer.

## 7. What Claude can and cannot do here

**Can:** classify from the user's descriptions, propose names and mood→line matches, plan playlists and use cases, maintain catalog consistency, draft the AI-music brand narrative, advise on rights workflow.

**Cannot:** listen to or analyze audio files, detect BPM/key/tempo by ear, or judge how a track actually sounds. For anything requiring listening, Claude asks the user or points to a detection tool — it never fabricates audio characteristics.
