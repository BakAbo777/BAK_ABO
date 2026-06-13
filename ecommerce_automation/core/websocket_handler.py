from __future__ import annotations

from collections import deque
from typing import Any


class RealtimeHub:
    """Small event hub.

    It keeps the app usable without an extra WebSocket dependency. If Flask-SocketIO
    is added later, this object can be adapted to emit events from the same call site.
    """

    def __init__(self, max_events: int = 200):
        self.events: deque[dict[str, Any]] = deque(maxlen=max_events)

    def publish(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        event = {"type": event_type, "payload": payload}
        self.events.appendleft(event)
        return event

    def latest(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self.events)[:limit]

