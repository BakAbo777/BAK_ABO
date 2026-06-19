from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any

BAKABO_STORE_DOMAIN = "bakabo.club"
BKS_TM04_THEME_ID = "202392961362"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class RealtimeHub:
    """In-process event bus for BKS dashboard real-time updates.

    Stores events in a bounded deque so the app stays usable without a WebSocket
    dependency. If Flask-SocketIO is added later, adapt publish() — no consumer changes.
    """

    def __init__(self, max_events: int = 200):
        self.events: deque[dict[str, Any]] = deque(maxlen=max_events)

    def __len__(self) -> int:
        return len(self.events)

    def publish(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        event = {"type": event_type, "ts": _utc_now(), "payload": payload}
        self.events.appendleft(event)
        return event

    def latest(self, limit: int = 50, *, event_type: str = "") -> list[dict[str, Any]]:
        limit = max(1, min(500, int(limit)))
        stream: list[dict[str, Any]] = list(self.events)
        if event_type:
            stream = [e for e in stream if e.get("type") == event_type]
        return stream[:limit]

    def clear(self) -> None:
        self.events.clear()

    def snapshot(self) -> dict[str, Any]:
        total = len(self.events)
        by_type: dict[str, int] = {}
        for event in self.events:
            t = str(event.get("type") or "unknown")
            by_type[t] = by_type.get(t, 0) + 1
        head = list(self.events)[:1]
        return {
            "total": total,
            "by_type": dict(sorted(by_type.items())),
            "latest_ts": head[0].get("ts", "") if head else "",
            "max_events": self.events.maxlen,
        }
