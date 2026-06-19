---
name: bakabo-avatar-resident
description: Use this skill when Roberto asks to work on BKS avatar videos, collection scripts, or HeyGen production WITHOUT going through the Streamlit dashboard. This is the RESIDENT version of the avatar workflow — it runs entirely through Claude Code (internal AI). Triggers include: "fai lo script per [collezione]", "prepara l'avatar", "registra il video", "controlla lo stato degli avatar", "aggiorna il workspace avatar", or any avatar/HeyGen task in a direct conversation. Works with HyperFrames MCP (list_projects, get_render_status) and catalog_db (upsert_asset). Does NOT require Streamlit or Flask to be running.
---

# BakAbo — Avatar Resident Skill

This skill lets the internal AI (Claude Code) operate the avatar production pipeline
directly, without opening the Streamlit dashboard. The workspace lives at
`output/avatar_production/` relative to the project root.

---

## 1. Workspace structure

```
output/avatar_production/
├── scripts/          ← 15s collection scripts (8 files, one per collection)
├── images/           ← selected 9:16 hero images, named BKS_[COLLECTION]_hero_[DATE].jpg
├── exports/          ← final HeyGen MP4 exports
├── metadata/         ← delivery metadata and campaign notes
├── avatar_production_plan.csv     ← current status per collection
├── social_render_links.csv        ← render manifest for all channels
├── heygen_qc_checklist.md         ← QC protocol for every export
└── README.md
```

**Script naming:** `BKS_{Collection}_avatar_15s.md` — e.g. `BKS_Glyph_avatar_15s.md`
**Image naming:** `BKS_{Collection}_hero_{YYYYMMDD}.jpg` — e.g. `BKS_Hours_hero_20260617.jpg`
**Video naming:** any MP4 with the collection name in lowercase anywhere in the filename

---

## 2. Resident workflow — step by step

```
1. CHECK      → read avatar_production_plan.csv to see per-collection status
2. SCRIPT     → read/write BKS_{Collection}_avatar_15s.md (35–50 words, 15s, no exclamation marks)
3. IMAGE      → confirm or place BKS_{Collection}_hero_{DATE}.jpg in images/
4. HEYGEN     → use MCP tools to check project status / render status
5. REGISTER   → upsert completed video into catalog_db (asset_type='avatar')
6. REFRESH    → call ensure_workspace() to regenerate plan + social_render_links.csv
```

---

## 3. Checking workspace status (Python, direct)

```python
from pathlib import Path
from ecommerce_automation.avatar_production import ensure_workspace, summary, collection_rows

root = Path(".")
s = summary(root)
# s["scripts_ready"], s["images_ready"], s["exports_ready"], s["progress"]

rows = collection_rows(root)
for row in rows:
    print(row["collection"], row["progress"], "%", "→", row["next_action"])
```

Or refresh the full workspace (rewrites plan CSV and social render sheet):

```python
result = ensure_workspace(root)
```

---

## 4. Script rules (non-negotiable)

| Rule | Detail |
| --- | --- |
| Length | 35–50 words for exactly 15 seconds |
| Voice | Calm, precise, premium — no exclamation marks, no hard sell |
| Structure | Line 1: BKS + collection name. Body: what makes this collection. Close: one CTA. |
| CTA options | "explore", "save", "follow", "test the drop" — never "buy now" |
| Brand name | Always "BKS [Collection]" on first mention, "bakabo.club" for the URL close |

Script template location: `output/avatar_production/scripts/BKS_{Collection}_avatar_15s.md`

To check word count on any script:

```python
from ecommerce_automation.avatar_production import _word_count
text = Path("output/avatar_production/scripts/BKS_Glyph_avatar_15s.md").read_text()
print(_word_count(text), "words")
```

---

## 5. HeyGen MCP tools available (read-only from CLI)

From Claude Code, compose and render_video are disabled (local filesystem). Use:

- `mcp__claude_ai_HyperFrames_by_HeyGen__list_projects` — list all HeyGen projects
- `mcp__claude_ai_HyperFrames_by_HeyGen__get_project` — get project details by ID
- `mcp__claude_ai_HyperFrames_by_HeyGen__get_render_status` — check render status

Actual video creation must be done in HeyGen directly (web app). These MCP tools are
for checking status and retrieving metadata — not for triggering renders from CLI.

---

## 6. Registering a completed avatar video in BKS database

After Roberto exports an MP4 from HeyGen and places it in `output/avatar_production/exports/`:

```python
from pathlib import Path
from ecommerce_automation.catalog_db import upsert_asset
from bks_assets import active_catalog_db

video_path = Path("output/avatar_production/exports/BKS_Glyph_avatar_15s_20260617.mp4")
db = active_catalog_db()

asset_id = upsert_asset(
    db,
    product_handle="bks-glyph",
    asset_type="avatar",
    file_path=str(video_path),
    collection="Glyph",
    variant="15s-social",
    meta={
        "duration": "15s",
        "format": "9:16 MP4",
        "channels": "Instagram Reels;TikTok;YouTube Shorts;Homepage;Email",
        "script": "output/avatar_production/scripts/BKS_Glyph_avatar_15s.md",
    },
)
print(f"Registered asset id={asset_id}")
```

---

## 7. Collection reference

| Collection | Script file | Accent | CTA target URL |
| --- | --- | --- | --- |
| Hours | BKS_Hours_avatar_15s.md | `#c8c4be` | bakabo.club/collections/bks-hours |
| Glyph | BKS_Glyph_avatar_15s.md | `#d4a030` | bakabo.club/collections/bks-glyph |
| Marker | BKS_Marker_avatar_15s.md | `#c04418` | bakabo.club/collections/bks-marker |
| Riviera | BKS_Riviera_avatar_15s.md | `#0ca898` | bakabo.club/collections/bks-riviera |
| Pulse | BKS_Pulse_avatar_15s.md | `#8888cc` | bakabo.club/collections/bks-pulse |
| Token | BKS_Token_avatar_15s.md | `#9828d8` | bakabo.club/collections/bks-token |
| Flag | BKS_Flag_avatar_15s.md | `#c82020` | bakabo.club/collections/bks-flag |
| Folklore | BKS_Folklore_avatar_15s.md | `#489808` | bakabo.club/collections/bks-folklore |

---

## 8. QC before distribution

File: `output/avatar_production/heygen_qc_checklist.md`

- Script 35–50 words confirmed
- Voice pacing natural, not rushed
- Lip sync acceptable across full export
- Source image 9:16, key product details not cropped
- Audio clean and consistent
- No typo, placeholder, or off-brand claim
- CTA matches target channel
- MP4 + metadata saved together

---

## 9. Resident vs Streamlit

| | Resident (this skill) | Streamlit dashboard |
| --- | --- | --- |
| Requires server | No | Yes (port 8501) |
| Access | Claude Code conversation | Browser |
| Script editing | Direct file read/write | Via UI form |
| Status check | Python call or CSV read | Visual dashboard |
| Asset registration | catalog_db.upsert_asset() | Automatic |
| HeyGen creation | HeyGen web app (manual) | HeyGen web app (manual) |

The resident skill is faster for quick checks, script edits, and asset registration.
The Streamlit dashboard adds a visual overview and history tracking.

Related: `bakabo-master`, `bakabo-popup-ai`, `bakabo-market-intelligence`
