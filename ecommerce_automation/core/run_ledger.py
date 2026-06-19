from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BAKABO_STORE_DOMAIN = "bakabo.club"
BKS_TM04_THEME_ID = "202392961362"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_utc(iso: str) -> datetime | None:
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso)
    except ValueError:
        return None


def make_idempotency_key(phase_id: str, intent: str, payload: dict[str, Any] | None = None) -> str:
    source = json.dumps({"phase_id": phase_id, "intent": intent, "payload": payload or {}}, sort_keys=True)
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:32]


@dataclass
class RunRecord:
    run_id: int
    phase_id: str
    intent: str
    idempotency_key: str
    status: str
    started_at: str
    finished_at: str = ""
    error: str = ""
    approved: bool = False
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def is_finished(self) -> bool:
        return self.status != "running"

    @property
    def duration_seconds(self) -> float | None:
        start = _parse_utc(self.started_at)
        if start is None:
            return None
        end = _parse_utc(self.finished_at) if self.finished_at else datetime.now(timezone.utc)
        if end is None:
            return None
        return round((end - start).total_seconds(), 2)


class RunLedger:
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
                CREATE TABLE IF NOT EXISTS runs (
                    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phase_id TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT NOT NULL DEFAULT '',
                    metrics_json TEXT NOT NULL DEFAULT '{}',
                    error TEXT NOT NULL DEFAULT '',
                    approved INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_runs_phase ON runs (phase_id, started_at)")
            con.execute("CREATE INDEX IF NOT EXISTS idx_runs_idempotency ON runs (idempotency_key)")
            # migrate existing DBs that predate the approved column
            try:
                con.execute("ALTER TABLE runs ADD COLUMN approved INTEGER NOT NULL DEFAULT 0")
            except sqlite3.OperationalError:
                pass

    def start_run(
        self,
        phase_id: str,
        intent: str,
        payload: dict[str, Any] | None = None,
        *,
        approved: bool = False,
    ) -> RunRecord:
        key = make_idempotency_key(phase_id, intent, payload)
        with self.connect() as con:
            con.execute(
                """
                INSERT INTO runs (phase_id, intent, idempotency_key, status, started_at, approved)
                VALUES (?, ?, ?, 'running', ?, ?)
                """,
                (phase_id, intent, key, utc_now(), int(approved)),
            )
            run_id = int(con.execute("SELECT last_insert_rowid()").fetchone()[0])
        return self.get_run(run_id)

    def finish_run(
        self,
        run_id: int,
        *,
        status: str,
        metrics: dict[str, Any] | None = None,
        error: str = "",
    ) -> RunRecord:
        existing = self.get_run(run_id)
        if existing.is_finished:
            return existing
        with self.connect() as con:
            con.execute(
                """
                UPDATE runs
                SET status = ?, finished_at = ?, metrics_json = ?, error = ?
                WHERE run_id = ?
                """,
                (status, utc_now(), json.dumps(metrics or {}, ensure_ascii=True, sort_keys=True), error, run_id),
            )
        return self.get_run(run_id)

    def get_run(self, run_id: int) -> RunRecord:
        with self.connect() as con:
            row = con.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            raise KeyError(f"Unknown run: {run_id}")
        data = dict(row)
        return RunRecord(
            run_id=data["run_id"],
            phase_id=data["phase_id"],
            intent=data["intent"],
            idempotency_key=data["idempotency_key"],
            status=data["status"],
            started_at=data["started_at"],
            finished_at=data["finished_at"],
            error=data["error"],
            approved=bool(data.get("approved", 0)),
            metrics=json.loads(data["metrics_json"] or "{}"),
        )

    def last_run_for_phase(self, phase_id: str) -> RunRecord | None:
        with self.connect() as con:
            row = con.execute(
                "SELECT * FROM runs WHERE phase_id = ? ORDER BY run_id DESC LIMIT 1",
                (phase_id,),
            ).fetchone()
        if row is None:
            return None
        data = dict(row)
        return RunRecord(
            run_id=data["run_id"],
            phase_id=data["phase_id"],
            intent=data["intent"],
            idempotency_key=data["idempotency_key"],
            status=data["status"],
            started_at=data["started_at"],
            finished_at=data["finished_at"],
            error=data["error"],
            approved=bool(data.get("approved", 0)),
            metrics=json.loads(data["metrics_json"] or "{}"),
        )

    def list_runs(self, limit: int = 50, *, phase_id: str = "") -> list[dict[str, Any]]:
        limit = max(1, min(500, int(limit)))
        params: list[Any] = []
        where = ""
        if phase_id:
            where = "WHERE phase_id = ?"
            params.append(phase_id)
        params.append(limit)
        with self.connect() as con:
            rows = con.execute(
                f"SELECT * FROM runs {where} ORDER BY run_id DESC LIMIT ?",
                params,
            ).fetchall()
        result = []
        for row in rows:
            data = dict(row)
            data["metrics"] = json.loads(data.pop("metrics_json") or "{}")
            data["approved"] = bool(data.get("approved", 0))
            result.append(data)
        return result

    def summary(self) -> dict[str, Any]:
        with self.connect() as con:
            total = con.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
            running = con.execute("SELECT COUNT(*) FROM runs WHERE status = 'running'").fetchone()[0]
            complete = con.execute("SELECT COUNT(*) FROM runs WHERE status = 'complete'").fetchone()[0]
            failed = con.execute("SELECT COUNT(*) FROM runs WHERE status = 'failed'").fetchone()[0]
            approved = con.execute("SELECT COUNT(*) FROM runs WHERE approved = 1").fetchone()[0]
            by_phase = con.execute(
                "SELECT phase_id, COUNT(*) AS count FROM runs GROUP BY phase_id ORDER BY phase_id"
            ).fetchall()
        return {
            "total": int(total),
            "running": int(running),
            "complete": int(complete),
            "failed": int(failed),
            "approved_runs": int(approved),
            "by_phase": {row["phase_id"]: int(row["count"]) for row in by_phase},
        }
