from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class AgentKnowledgeStore:
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
                CREATE TABLE IF NOT EXISTS agent_knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    area TEXT NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT '',
                    evidence TEXT NOT NULL DEFAULT '',
                    source TEXT NOT NULL DEFAULT '',
                    payload_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                )
                """
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_agent_knowledge_area ON agent_knowledge(area)")
            con.execute("CREATE INDEX IF NOT EXISTS idx_agent_knowledge_created ON agent_knowledge(created_at)")

    def add(self, *, area: str, title: str, status: str = "", evidence: str = "", source: str = "", payload: dict[str, Any] | None = None) -> dict[str, Any]:
        with self.connect() as con:
            cur = con.execute(
                """
                INSERT INTO agent_knowledge (area, title, status, evidence, source, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (area, title, status, evidence, source, json.dumps(payload or {}, ensure_ascii=False, sort_keys=True), utc_now()),
            )
        return self.get(cur.lastrowid)

    def get(self, row_id: int) -> dict[str, Any]:
        with self.connect() as con:
            row = con.execute("SELECT * FROM agent_knowledge WHERE id = ?", (row_id,)).fetchone()
        if row is None:
            raise KeyError(row_id)
        return self._row(row)

    def latest(self, *, limit: int = 80, area: str = "") -> list[dict[str, Any]]:
        query = "SELECT * FROM agent_knowledge"
        params: list[Any] = []
        if area:
            query += " WHERE area = ?"
            params.append(area)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        with self.connect() as con:
            rows = con.execute(query, params).fetchall()
        return [self._row(row) for row in rows]

    def search(self, text: str, *, limit: int = 30) -> list[dict[str, Any]]:
        like = f"%{text}%"
        with self.connect() as con:
            rows = con.execute(
                """
                SELECT * FROM agent_knowledge
                WHERE area LIKE ? OR title LIKE ? OR evidence LIKE ? OR source LIKE ?
                ORDER BY id DESC LIMIT ?
                """,
                (like, like, like, like, limit),
            ).fetchall()
        return [self._row(row) for row in rows]

    def seed_from_snapshot(self, snapshot: dict[str, Any]) -> int:
        entries = _entries_from_snapshot(snapshot)
        count = 0
        for entry in entries:
            self.add(**entry)
            count += 1
        return count

    @staticmethod
    def _row(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["payload"] = json.loads(data.pop("payload_json") or "{}")
        return data


def _entries_from_snapshot(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for key in (
        "google",
        "trust_contract",   # was "trust" — snapshot key is trust_contract
        "marketing_logic",
        "market",
        "payments",
        "agent_os",
        "always_on",
        "weekly",
        "daily",
        "network",
        "product_names",
        "official_inbox",
        "social_campaigns",
        "legal_guardrails",
        "growth_crm",
        "photo_studio",
        "theme_assistant",
        "dialogic",
        "catalog_sync",
        "canva",
        "hyperframes",
        "skills",
        "openai_alliance",
        "sales_channels",
    ):
        data = snapshot.get(key, {})
        summary = data.get("summary", {}) if isinstance(data, dict) else {}
        if summary:
            entries.append(
                {
                    "area": key,
                    "title": f"{key} summary",
                    "status": str(summary.get("status") or summary.get("mode") or summary.get("best_logic") or ""),
                    "evidence": json.dumps(summary, ensure_ascii=False, sort_keys=True),
                    "source": "dashboard_snapshot",
                    "payload": summary,
                }
            )
    actions = snapshot.get("actions", {}).get("actions", [])
    for action in actions[:12]:
        entries.append(
            {
                "area": "action",
                "title": action.get("title", action.get("id", "")),
                "status": action.get("status", ""),
                "evidence": action.get("why", ""),
                "source": action.get("id", ""),
                "payload": action,
            }
        )
    return entries
