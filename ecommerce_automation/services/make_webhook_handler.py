from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Any

import requests

from ecommerce_automation.core.http_client import build_session, decode_response


@dataclass
class MakeWebhookHandler:
    webhook_url: str = ""
    secret: str = ""

    @property
    def configured(self) -> bool:
        return bool(self.webhook_url)

    def sign_payload(self, body: bytes) -> str:
        if not self.secret:
            return ""
        return hmac.new(self.secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

    def send_event(self, event: str, payload: dict[str, Any], timeout: int = 30) -> dict[str, Any]:
        if not self.configured:
            raise RuntimeError("MAKE_WEBHOOK_URL is not configured.")
        body = {"event": event, "payload": payload}
        session = build_session()
        response = session.post(self.webhook_url, json=body, timeout=timeout)
        decoded = decode_response(response)
        return decoded if isinstance(decoded, dict) else {"response": decoded}

    def normalize_inbound(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "scenario": payload.get("scenario") or payload.get("scenario_name") or "",
            "status": payload.get("status") or payload.get("state") or "received",
            "external_id": payload.get("id") or payload.get("execution_id") or "",
            "raw": payload,
        }

    def health_snapshot(self) -> dict[str, Any]:
        return {
            "configured": self.configured,
            "status": "ready" if self.configured else "missing_webhook_url",
            "has_secret": bool(self.secret),
        }
