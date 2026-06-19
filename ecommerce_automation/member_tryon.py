from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATABASE_ROOT = Path(r"I:\BKS database\members_tryon")
INCOMING_DIR = DATABASE_ROOT / "incoming"
PREVIEWS_DIR = DATABASE_ROOT / "previews"
LOGS_DIR = DATABASE_ROOT / "logs"
PRESETS_DIR = DATABASE_ROOT / "presets"
PRESETS_FILE = PRESETS_DIR / "bks_tryon_background_presets.json"

ALLOWED_PHOTO_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}
MAX_PHOTO_BYTES = 12 * 1024 * 1024


def ensure_workspace() -> dict[str, str]:
    for path in (INCOMING_DIR, PREVIEWS_DIR, LOGS_DIR, PRESETS_DIR):
        path.mkdir(parents=True, exist_ok=True)
    return {
        "incoming": str(INCOMING_DIR),
        "previews": str(PREVIEWS_DIR),
        "logs": str(LOGS_DIR),
        "presets": str(PRESETS_DIR),
    }


def _safe_fragment(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]", "", (value or "").strip())[:40]
    return value or "anonymous"


def _hash_email(email: str) -> str:
    email = (email or "").strip().lower()
    if not email:
        return ""
    return hashlib.sha256(email.encode("utf-8")).hexdigest()[:16]


def load_presets() -> dict[str, Any]:
    if not PRESETS_FILE.exists():
        return {"ready": False, "presets": [], "default": ""}
    data = json.loads(PRESETS_FILE.read_text(encoding="utf-8"))
    presets = data.get("presets", [])
    return {
        "ready": True,
        "presets": [p.get("id") for p in presets if p.get("id")],
        "default": data.get("recommendation", {}).get("default", ""),
    }


def _log_request(entry: dict[str, Any]) -> None:
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    log_path = LOGS_DIR / f"requests_{day}.jsonl"
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def pending_count() -> int:
    if not INCOMING_DIR.exists():
        return 0
    return sum(1 for _ in INCOMING_DIR.iterdir() if _.is_file())


def handle_submission(photo: Any, form: dict[str, str]) -> tuple[dict[str, Any], int]:
    """Receive a Mobile Try-On request and queue it for manual review.

    v1 deliberately does not call any image-generation model: the contract in
    bks-ai-control-map.json (member_tryon_system) explicitly accepts a
    message-only async response while the real renderer is not wired yet.
    """
    ensure_workspace()

    if photo is None or not getattr(photo, "filename", ""):
        return {"error": "missing_photo", "message": "Nessuna foto ricevuta."}, 400

    content_type = (getattr(photo, "mimetype", "") or "").lower()
    if content_type not in ALLOWED_PHOTO_TYPES:
        return {"error": "unsupported_photo_type", "message": "Formato foto non supportato."}, 415

    try:
        item = json.loads(form.get("item") or "{}")
    except json.JSONDecodeError:
        item = {}
    try:
        cart = json.loads(form.get("cart") or "{}")
    except json.JSONDecodeError:
        cart = {}

    customer_fragment = _safe_fragment(form.get("customer_id", ""))
    request_id = uuid.uuid4().hex[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    suffix = Path(photo.filename).suffix.lower() or ".jpg"
    incoming_name = f"{stamp}_{customer_fragment}_{request_id}{suffix}"
    incoming_path = INCOMING_DIR / incoming_name
    photo.save(incoming_path)

    size_bytes = incoming_path.stat().st_size if incoming_path.exists() else 0
    if size_bytes == 0 or size_bytes > MAX_PHOTO_BYTES:
        incoming_path.unlink(missing_ok=True)
        return {"error": "invalid_photo_size", "message": "Foto troppo grande o vuota."}, 413

    _log_request(
        {
            "request_id": request_id,
            "received_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "customer_id": form.get("customer_id", ""),
            "customer_email_hash": _hash_email(form.get("customer_email", "")),
            "source": form.get("source", ""),
            "item_title": item.get("product_title") or item.get("title") or "",
            "item_key": item.get("key", ""),
            "cart_item_count": len(cart.get("items", [])) if isinstance(cart, dict) else 0,
            "incoming_photo": incoming_name,
            "status": "queued_manual_review",
        }
    )

    return (
        {
            "request_id": request_id,
            "status": "queued",
            "message": "Richiesta ricevuta. L'anteprima Try-On verra' elaborata dal team BKS.",
        },
        200,
    )


def payload(settings: Any) -> dict[str, Any]:
    workspace = ensure_workspace()
    presets = load_presets()
    endpoint_ready = bool(getattr(settings, "bks_assistant_public_endpoint", ""))
    checks = [
        {"check": "workspace", "status": "pass", "detail": "incoming/previews/logs/presets pronti su I:\\BKS database\\members_tryon."},
        {"check": "presets", "status": "pass" if presets["ready"] else "manual_pending", "detail": f"{len(presets['presets'])} preset Camerino caricati, default={presets['default']}" if presets["ready"] else "bks_tryon_background_presets.json non trovato."},
        {"check": "auto_render", "status": "disabled_by_design", "detail": "v1: nessuna generazione AI automatica, solo ricezione + coda manuale (alternativa accettata dal contratto member_tryon_system)."},
        {"check": "public_proxy", "status": "pass" if endpoint_ready else "manual_pending", "detail": "Serve Shopify App Proxy + tunnel pubblico verso porta 8600 perche' il tema possa raggiungere /apps/bks-tryon dal vivo."},
    ]
    return {
        "summary": {
            "status": "queue_only_v1",
            "pending_requests": pending_count(),
            "presets_default": presets["default"],
            "presets_count": len(presets["presets"]),
            "endpoint": "/apps/bks-tryon",
        },
        "workspace": workspace,
        "presets": presets,
        "checks": checks,
    }
