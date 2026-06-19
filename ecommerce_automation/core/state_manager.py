from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BAKABO_STORE_DOMAIN = "bakabo.club"
BKS_TM04_THEME_ID = "202392961362"


@dataclass(frozen=True)
class PhaseSpec:
    phase_id: str
    name: str
    objective: str
    owner: str
    external_systems: tuple[str, ...] = ()


PHASE_SPECS: tuple[PhaseSpec, ...] = (
    PhaseSpec("01", "Config & Make setup", "Configure global settings and Make outbound/inbound hooks.", "phase_config", ("Make",)),
    PhaseSpec("02", "Import & Printify sync", "Import catalog data and create or reconcile Printify draft products.", "phase_import", ("Printify",)),
    PhaseSpec("03", "Images base", "Prepare cutouts, base mockups, and optimized product assets.", "phase_images", ("Image Factory", "rembg")),
    PhaseSpec("04", "AI content & video", "Generate lifestyle images, copy blocks, and short-video assets.", "phase_ai", ("OpenAI", "Canva")),
    PhaseSpec("05", "Shopify & Printify publish", "Publish products to Shopify through Printify and keep retry-safe references.", "phase_shopify", ("Shopify", "Printify")),
    PhaseSpec("06", "Google validation", "Validate Merchant Center, GA4, GTM, policy pages, and feeds.", "phase_google", ("Google",)),
    PhaseSpec("07", "Social & marketplaces", "Prepare social payloads and trigger Make scenarios for cross-posting.", "phase_social", ("Make", "Meta", "TikTok", "Etsy")),
    PhaseSpec("08", "Amazon configuration", "Prepare Amazon SP-API listing workflow and FBM/FBA decisions.", "phase_amazon", ("Amazon",)),
    PhaseSpec("09", "Avatar production", "Produce BKS collection avatar videos: scripts, 9:16 images, HeyGen exports, and metadata.", "phase_avatar", ("HeyGen", "Social")),
    PhaseSpec("10", "Project skill registry", "Index BKS resident skills from BKS_SKILL/skills/ and expose them in the Master panel.", "phase_skills", ("Docs", "Project Management")),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class StateManager:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.database_path)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        with self.connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS phase_state (
                    phase_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    progress INTEGER NOT NULL DEFAULT 0,
                    message TEXT NOT NULL DEFAULT '',
                    external_ref TEXT NOT NULL DEFAULT '',
                    metrics_json TEXT NOT NULL DEFAULT '{}',
                    updated_at TEXT NOT NULL
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS event_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    phase_id TEXT NOT NULL DEFAULT '',
                    payload_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                )
                """
            )
            for spec in PHASE_SPECS:
                con.execute(
                    """
                    INSERT OR IGNORE INTO phase_state
                        (phase_id, name, status, progress, message, updated_at)
                    VALUES (?, ?, 'ready', 0, 'Ready', ?)
                    """,
                    (spec.phase_id, spec.name, utc_now()),
                )

    def list_phases(self) -> list[dict[str, Any]]:
        specs = {spec.phase_id: spec for spec in PHASE_SPECS}
        with self.connect() as con:
            rows = con.execute("SELECT * FROM phase_state ORDER BY phase_id").fetchall()
        phases = []
        for row in rows:
            data = dict(row)
            spec = specs.get(data["phase_id"])
            data["metrics"] = json.loads(data.pop("metrics_json") or "{}")
            if spec:
                data.update(
                    {
                        "objective": spec.objective,
                        "owner": spec.owner,
                        "external_systems": list(spec.external_systems),
                    }
                )
            phases.append(data)
        return phases

    def update_phase(
        self,
        phase_id: str,
        *,
        status: str,
        progress: int | None = None,
        message: str = "",
        external_ref: str = "",
        metrics: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        progress_value = max(0, min(100, int(progress if progress is not None else 0)))
        metrics_json = json.dumps(metrics or {}, ensure_ascii=True, sort_keys=True)
        with self.connect() as con:
            con.execute(
                """
                UPDATE phase_state
                SET status = ?, progress = ?, message = ?, external_ref = ?,
                    metrics_json = ?, updated_at = ?
                WHERE phase_id = ?
                """,
                (status, progress_value, message, external_ref, metrics_json, utc_now(), phase_id),
            )
        self.record_event("phase.updated", phase_id=phase_id, payload={"status": status, "message": message})
        return self.get_phase(phase_id)

    def get_phase(self, phase_id: str) -> dict[str, Any]:
        with self.connect() as con:
            row = con.execute("SELECT * FROM phase_state WHERE phase_id = ?", (phase_id,)).fetchone()
        if row is None:
            raise KeyError(f"Unknown phase: {phase_id}")
        data = dict(row)
        data["metrics"] = json.loads(data.pop("metrics_json") or "{}")
        return data

    def record_event(self, event_type: str, *, phase_id: str = "", payload: dict[str, Any] | None = None) -> None:
        with self.connect() as con:
            con.execute(
                """
                INSERT INTO event_log (event_type, phase_id, payload_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (event_type, phase_id, json.dumps(payload or {}, ensure_ascii=True, sort_keys=True), utc_now()),
            )

    def recent_events(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute(
                "SELECT * FROM event_log ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        events = []
        for row in rows:
            data = dict(row)
            data["payload"] = json.loads(data.pop("payload_json") or "{}")
            events.append(data)
        return events

    def phase_specs(self) -> list[dict[str, Any]]:
        return [asdict(spec) | {"external_systems": list(spec.external_systems)} for spec in PHASE_SPECS]
