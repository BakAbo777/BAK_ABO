from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


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
    finished_at: str
    metrics: dict[str, Any]
    error: str


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
                    error TEXT NOT NULL DEFAULT ''
                )
                """
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_runs_phase ON runs (phase_id, started_at)")
            con.execute("CREATE INDEX IF NOT EXISTS idx_runs_idempotency ON runs (idempotency_key)")

    def start_run(self, phase_id: str, intent: str, payload: dict[str, Any] | None = None) -> RunRecord:
        key = make_idempotency_key(phase_id, intent, payload)
        with self.connect() as con:
            con.execute(
                """
                INSERT INTO runs (phase_id, intent, idempotency_key, status, started_at)
                VALUES (?, ?, ?, 'running', ?)
                """,
                (phase_id, intent, key, utc_now()),
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
            metrics=json.loads(data["metrics_json"] or "{}"),
            error=data["error"],
        )

    def list_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute("SELECT * FROM runs ORDER BY run_id DESC LIMIT ?", (limit,)).fetchall()
        result = []
        for row in rows:
            data = dict(row)
            data["metrics"] = json.loads(data.pop("metrics_json") or "{}")
            result.append(data)
        return result

