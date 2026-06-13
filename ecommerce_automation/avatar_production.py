from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


COLLECTIONS: tuple[str, ...] = (
    "Hours",
    "Glyph",
    "Marker",
    "Riviera",
    "Pulse",
    "Token",
    "Flag",
    "Folklore",
)

SCRIPT_TARGET = "15s social script, 35-50 words, calm premium voice, no exclamation marks."

WORKFLOW_STEPS: tuple[dict[str, str], ...] = (
    {"step": "01", "name": "Brief", "output": "Collection focus, channel, CTA, source visual"},
    {"step": "02", "name": "Script", "output": "35-50 words for 15 seconds"},
    {"step": "03", "name": "Image", "output": "9:16 hero image named BKS_[COLLECTION]_hero_[DATE].jpg"},
    {"step": "04", "name": "HeyGen", "output": "Avatar, voice, script, background image, export"},
    {"step": "05", "name": "Delivery", "output": "MP4, QC checklist, metadata file"},
)

SCRIPT_RULES: tuple[str, ...] = (
    "Use a concise spoken voice. One idea per sentence.",
    "Keep 15 second scripts between 35 and 50 words.",
    "Avoid exclamation marks and hard-sell language.",
    "Mention BKS plus the collection name in the first line.",
    "Close with one practical CTA: explore, save, follow, or test the drop.",
)

HEYGEN_STEPS: tuple[str, ...] = (
    "Create a new portrait video in HeyGen.",
    "Select the approved BakAbo avatar and the matching brand voice.",
    "Paste the final script and preview pacing before export.",
    "Upload the 9:16 hero image as background/source visual.",
    "Export MP4, then run QC for lip sync, crop, audio level, text fit, and CTA.",
)

DISTRIBUTION_ROWS: tuple[dict[str, str], ...] = (
    {"channel": "Homepage", "use": "Collection proof block or launch module", "format": "MP4 9:16 or cropped embed"},
    {"channel": "Instagram Reels", "use": "Visual discovery and save intent", "format": "15s Reel"},
    {"channel": "TikTok", "use": "Creative testing and process narrative", "format": "15s vertical"},
    {"channel": "YouTube Shorts", "use": "Search/social video discovery", "format": "15s vertical Short"},
    {"channel": "Email", "use": "Launch or restock section", "format": "linked thumbnail"},
)

SCRIPT_TEMPLATES: dict[str, str] = {
    "Hours": (
        "BKS Hours turns time into pattern. The print feels precise, archival, and easy to wear, "
        "built for pieces that move from morning errands to late city light. Explore the collection "
        "on bakabo.club and save the drop for your next everyday uniform."
    ),
    "Glyph": (
        "BKS Glyph starts with marks that feel almost like a private alphabet. Lines, signs, and symbols "
        "become wearable structure across made to order pieces. If you like graphic language with quiet "
        "tension, explore Glyph on bakabo.club."
    ),
    "Marker": (
        "BKS Marker keeps the hand in the image. Brush energy, street rhythm, and controlled chaos become "
        "prints made for motion. It is bold without shouting, built for daily wear. Explore Marker on "
        "bakabo.club and test the next drop."
    ),
    "Riviera": (
        "BKS Riviera is sun, travel, and clean graphic rhythm. The collection uses coastal color and sharp "
        "composition for pieces that feel relaxed but intentional. Wear it for movement, weekends, and warm "
        "light. Explore Riviera on bakabo.club."
    ),
    "Pulse": (
        "BKS Pulse is built around movement. Shards, waves, and high energy color create prints that feel "
        "fast without losing control. It is made to order for people who dress with signal. Explore Pulse "
        "on bakabo.club."
    ),
    "Token": (
        "BKS Token treats sport codes, scores, and symbols as visual currency. The collection is graphic, "
        "direct, and easy to place inside a modern street wardrobe. Follow the signal, save the edit, then "
        "explore Token on bakabo.club."
    ),
    "Flag": (
        "BKS Flag turns identity into pattern without becoming literal. Stripes, patches, and color blocks "
        "build a visual signal for travel, streetwear, and daily motion. Explore Flag on bakabo.club and "
        "save the edit for your next drop."
    ),
    "Folklore": (
        "BKS Folklore brings old symbols into a sharper present. Ornament, myth, and digital print meet in "
        "pieces made to order for everyday movement. It feels storied, not nostalgic. Explore Folklore on "
        "bakabo.club and keep the signal close."
    ),
}


def avatar_root(root_dir: Path) -> Path:
    return root_dir / "output" / "avatar_production"


def _slug(value: str) -> str:
    return value.lower().replace(" ", "-")


def _relative(root_dir: Path, path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _word_count(text: str) -> int:
    return len([part for part in text.replace("\n", " ").split(" ") if part.strip()])


def script_path(root_dir: Path, collection: str) -> Path:
    return avatar_root(root_dir) / "scripts" / f"BKS_{collection}_avatar_15s.md"


def metadata_template_path(root_dir: Path) -> Path:
    return avatar_root(root_dir) / "metadata" / "delivery_metadata_template.md"


def qc_checklist_path(root_dir: Path) -> Path:
    return avatar_root(root_dir) / "heygen_qc_checklist.md"


def plan_path(root_dir: Path) -> Path:
    return avatar_root(root_dir) / "avatar_production_plan.csv"


def social_render_sheet_path(root_dir: Path) -> Path:
    return avatar_root(root_dir) / "social_render_links.csv"


def readme_path(root_dir: Path) -> Path:
    return avatar_root(root_dir) / "README.md"


def _discover_selected_image(root_dir: Path, collection: str) -> Path | None:
    image_dir = avatar_root(root_dir) / "images"
    if not image_dir.exists():
        return None
    prefixes = (
        f"BKS_{collection}_hero_",
        f"BKS_{collection.lower()}_hero_",
        f"bks_{collection.lower()}_hero_",
        f"bks-{collection.lower()}-hero-",
    )
    candidates = [
        item
        for item in image_dir.iterdir()
        if item.is_file()
        and item.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        and any(item.name.startswith(prefix) for prefix in prefixes)
    ]
    return sorted(candidates, key=lambda item: item.stat().st_mtime, reverse=True)[0] if candidates else None


def _discover_suggested_image(root_dir: Path, collection: str) -> Path | None:
    slug = _slug(collection)
    search_dirs = (
        root_dir / "output" / "collection_image_program" / "curated" / "contact_sheets",
        root_dir / "output" / "collection_image_program" / "contact_sheets",
        root_dir / "02_COLLEZIONI",
    )
    patterns = (
        f"{slug}-*.jpg",
        f"{slug}-*.png",
        f"BKS_{collection}.png",
        f"BKS {collection}.png",
    )
    candidates: list[Path] = []
    for folder in search_dirs:
        if not folder.exists():
            continue
        for pattern in patterns:
            candidates.extend(item for item in folder.glob(pattern) if item.is_file())
    return sorted(candidates, key=lambda item: item.stat().st_mtime, reverse=True)[0] if candidates else None


def _discover_export(root_dir: Path, collection: str) -> Path | None:
    export_dirs = (
        avatar_root(root_dir) / "exports",
        root_dir / "Video_Avatar",
    )
    candidates: list[Path] = []
    for folder in export_dirs:
        if not folder.exists():
            continue
        candidates.extend(
            item
            for item in folder.glob("*.mp4")
            if item.is_file() and collection.lower() in item.name.lower()
        )
    return sorted(candidates, key=lambda item: item.stat().st_mtime, reverse=True)[0] if candidates else None


def _metadata_file(root_dir: Path, collection: str) -> Path | None:
    metadata_dir = avatar_root(root_dir) / "metadata"
    if not metadata_dir.exists():
        return None
    candidates = [
        item
        for item in metadata_dir.iterdir()
        if item.is_file() and collection.lower() in item.name.lower() and item.suffix.lower() in {".md", ".json", ".csv"}
    ]
    return sorted(candidates, key=lambda item: item.stat().st_mtime, reverse=True)[0] if candidates else None


def _script_status(path: Path) -> tuple[str, int]:
    if not path.exists():
        return "missing", 0
    words = _word_count(path.read_text(encoding="utf-8"))
    if 35 <= words <= 50:
        return "ready", words
    return "review", words


def _script_excerpt(path: Path) -> str:
    if not path.exists():
        return ""
    text = " ".join(path.read_text(encoding="utf-8").split())
    return text[:180] + ("..." if len(text) > 180 else "")


def collection_rows(root_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for collection in COLLECTIONS:
        path = script_path(root_dir, collection)
        script_status, words = _script_status(path)
        selected_image = _discover_selected_image(root_dir, collection)
        suggested_image = _discover_suggested_image(root_dir, collection)
        preview_image = selected_image or suggested_image
        export_file = _discover_export(root_dir, collection)
        metadata_file = _metadata_file(root_dir, collection)
        progress = 0
        if script_status == "ready":
            progress += 25
        elif script_status == "review":
            progress += 10
        if selected_image is not None:
            progress += 25
        if export_file is not None:
            progress += 25
        if metadata_file is not None:
            progress += 25

        if script_status == "missing":
            next_action = "Create 15s script"
        elif selected_image is None:
            next_action = "Select/crop 9:16 hero image"
        elif export_file is None:
            next_action = "Produce in HeyGen"
        elif metadata_file is None:
            next_action = "Add delivery metadata"
        else:
            next_action = "Ready for distribution"

        rows.append(
            {
                "collection": collection,
                "progress": progress,
                "script_status": script_status,
                "script_words": words,
                "script_excerpt": _script_excerpt(path),
                "script_path": _relative(root_dir, path),
                "preview_image": _relative(root_dir, preview_image),
                "selected_image": _relative(root_dir, selected_image),
                "suggested_image": _relative(root_dir, suggested_image),
                "export_file": _relative(root_dir, export_file),
                "metadata_file": _relative(root_dir, metadata_file),
                "next_action": next_action,
            }
        )
    return rows


def video_rows(root_dir: Path) -> list[dict[str, Any]]:
    video_dirs = (
        avatar_root(root_dir) / "exports",
        root_dir / "Video_Avatar",
    )
    videos: list[Path] = []
    for folder in video_dirs:
        if folder.exists():
            videos.extend(item for item in folder.glob("*.mp4") if item.is_file())
    return [
        {
            "name": item.name,
            "path": _relative(root_dir, item),
            "size_mb": round(item.stat().st_size / 1024 / 1024, 2),
        }
        for item in sorted(videos, key=lambda path: path.stat().st_mtime, reverse=True)
    ]


def summary(root_dir: Path) -> dict[str, Any]:
    rows = collection_rows(root_dir)
    scripts_ready = sum(1 for row in rows if row["script_status"] == "ready")
    images_ready = sum(1 for row in rows if row["selected_image"])
    exports_ready = sum(1 for row in rows if row["export_file"])
    metadata_ready = sum(1 for row in rows if row["metadata_file"])
    video_dir = root_dir / "Video_Avatar"
    existing_videos = sorted(video_dir.glob("*.mp4")) if video_dir.exists() else []
    progress = round(((scripts_ready + images_ready + exports_ready + metadata_ready) / (len(COLLECTIONS) * 4)) * 100)
    return {
        "collections": len(COLLECTIONS),
        "scripts_ready": scripts_ready,
        "images_ready": images_ready,
        "exports_ready": exports_ready,
        "metadata_ready": metadata_ready,
        "existing_video_files": len(existing_videos),
        "progress": progress,
        "workspace": _relative(root_dir, avatar_root(root_dir)),
        "plan": _relative(root_dir, plan_path(root_dir)),
        "social_render_sheet": _relative(root_dir, social_render_sheet_path(root_dir)),
        "qc_checklist": _relative(root_dir, qc_checklist_path(root_dir)),
        "metadata_template": _relative(root_dir, metadata_template_path(root_dir)),
    }


def _readme_text() -> str:
    return """# BKS Avatar Production

Operational workspace generated from the bakabo-avatar-production workflow.

## Workflow

1. Brief: collection, channel, CTA, source visual.
2. Script: 15 seconds, 35-50 words, calm premium voice, no exclamation marks.
3. Image: select or crop one 9:16 hero image.
4. HeyGen: avatar, voice, script, source image, export.
5. Delivery: MP4, QC checklist, metadata.

## Folders

- `scripts/`: final 15s scripts per collection.
- `images/`: selected 9:16 hero images, named `BKS_[COLLECTION]_hero_[DATE].jpg`.
- `exports/`: final HeyGen MP4 files.
- `metadata/`: delivery metadata and campaign notes.
"""


def _metadata_template_text() -> str:
    return """# Avatar Delivery Metadata

collection:
video_file:
source_image:
script_file:
duration:
format: 9:16 MP4
avatar:
voice:
created_at:
status: draft
channels: Homepage, Instagram Reels, TikTok, YouTube Shorts, Email
cta:
notes:
"""


def _qc_checklist_text() -> str:
    return """# HeyGen QC Checklist

- Script is 35-50 words for a 15 second social cut.
- Voice pacing is natural and not rushed.
- Lip sync is acceptable across the full export.
- Source image is 9:16 and does not crop key product details.
- Audio level is clean and consistent.
- No visible typo, placeholder, or off-brand claim.
- CTA matches the target channel.
- MP4 file and metadata are saved together.
"""


def social_render_rows(root_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in collection_rows(root_dir):
        slug = _slug(row["collection"])
        ready_for_render = row["script_status"] == "ready" and bool(row["selected_image"])
        ready_for_social = bool(row["export_file"])
        rows.append(
            {
                "collection": row["collection"],
                "render_status": "ready_for_social" if ready_for_social else ("ready_for_heygen" if ready_for_render else "needs_assets"),
                "progress": row["progress"],
                "platforms": "Instagram Reels;TikTok;YouTube Shorts;Homepage;Email",
                "format": "9:16 MP4",
                "duration": "15s",
                "script_path": row["script_path"],
                "script_words": row["script_words"],
                "source_image": row["selected_image"],
                "suggested_image": row["suggested_image"],
                "video_file": row["export_file"],
                "metadata_file": row["metadata_file"],
                "cta": "Explore collection",
                "target_url": f"https://bakabo.club/collections/bks-{slug}",
                "utm_campaign": f"bks-{slug}-avatar",
                "make_event": "avatar.render.request",
                "agent_persona": "BKS Master Agent",
                "audience_variant": "male;female;neutral",
                "customer_interaction": "consent_required",
                "message_channels": "Email;Instagram DM;Telegram Bot;Facebook Messenger;Customer Bot Link",
                "heygen_key_env": "HEYGEN_API_KEY",
                "heygen_avatar_env": "HEYGEN_AVATAR_ID",
                "heygen_voice_env": "HEYGEN_VOICE_ID",
                "next_action": row["next_action"],
            }
        )
    return rows


def write_social_render_sheet(root_dir: Path) -> Path:
    rows = social_render_rows(root_dir)
    path = social_render_sheet_path(root_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path


def ensure_workspace(root_dir: Path) -> dict[str, Any]:
    base = avatar_root(root_dir)
    for folder in ("scripts", "images", "exports", "metadata"):
        (base / folder).mkdir(parents=True, exist_ok=True)

    for collection, script in SCRIPT_TEMPLATES.items():
        path = script_path(root_dir, collection)
        if not path.exists():
            path.write_text(script + "\n", encoding="utf-8")

    if not readme_path(root_dir).exists():
        readme_path(root_dir).write_text(_readme_text(), encoding="utf-8")

    if not metadata_template_path(root_dir).exists():
        metadata_template_path(root_dir).write_text(_metadata_template_text(), encoding="utf-8")

    if not qc_checklist_path(root_dir).exists():
        qc_checklist_path(root_dir).write_text(_qc_checklist_text(), encoding="utf-8")

    rows = collection_rows(root_dir)
    with plan_path(root_dir).open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    write_social_render_sheet(root_dir)

    return {"summary": summary(root_dir), "rows": rows}


def payload(root_dir: Path) -> dict[str, Any]:
    return {
        "summary": summary(root_dir),
        "rows": collection_rows(root_dir),
        "workflow": list(WORKFLOW_STEPS),
        "script_rules": list(SCRIPT_RULES),
        "heygen_steps": list(HEYGEN_STEPS),
        "distribution": list(DISTRIBUTION_ROWS),
        "script_target": SCRIPT_TARGET,
        "videos": video_rows(root_dir),
        "social_render": social_render_rows(root_dir),
        "social_render_sheet": _relative(root_dir, social_render_sheet_path(root_dir)),
    }
