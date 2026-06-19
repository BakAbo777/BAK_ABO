from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import urllib3

from ecommerce_automation.core.http_client import build_session, decode_response

# Known BKS event types sent through Make — agent validates before dispatch
BKS_EVENTS = frozenset({
    "agent.snapshot_refresh",    # daily 12:00 CET via bks-agent-refresh Cloudflare Worker
    "catalog.sync_complete",     # after Printify/Shopify catalog sync
    "catalog.product_updated",   # product published or updated on Shopify
    "order.new",                 # new Shopify order received
    "order.fulfilled",           # order marked fulfilled by Printify
    "member.tier_upgrade",       # Metal tier upgrade (Lead→Iron→Brass→Silver→Gold)
    "member.camerino_ready",     # Try-On asset generated for member
    "campaign.drop_start",       # BKS release formula 0h public drop live
    "campaign.drop_close",       # drop closed (+48h), archive entry created
    "google.p0_resolved",        # trust contract P0 blocker marked resolved
    "google.merchant_appeal",    # Merchant Center appeal submitted
    "theme.deployed",            # TM04 section deployed via deploy_theme_section.py
})


@dataclass
class MakeWebhookHandler:
    webhook_url: str = ""
    secret: str = ""
    api_key: str = ""
    _session: Any = field(default=None, repr=False, compare=False)

    @property
    def configured(self) -> bool:
        return bool(self.webhook_url)

    def _get_session(self) -> Any:
        if self._session is None:
            self._session = build_session()
        return self._session

    def sign_payload(self, body: bytes) -> str:
        if not self.secret:
            return ""
        return hmac.new(self.secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

    def _headers(self, body_bytes: bytes) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        sig = self.sign_payload(body_bytes)
        if sig:
            headers["X-BKS-Signature"] = sig
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def send_event(self, event: str, payload: dict[str, Any], timeout: int = 30) -> dict[str, Any]:
        if not self.configured:
            raise RuntimeError("MAKE_WEBHOOK_URL is not configured.")
        body = {
            "event": event,
            "source": "bks-master-agent",
            "sent_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "payload": payload,
        }
        body_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers = self._headers(body_bytes)
        session = self._get_session()
        try:
            response = session.post(self.webhook_url, data=body_bytes, headers=headers, timeout=timeout)
        except Exception:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = session.post(self.webhook_url, data=body_bytes, headers=headers, timeout=timeout, verify=False)
        if response.status_code == 429:
            retry_after = float(response.headers.get("Retry-After", "2"))
            time.sleep(min(retry_after, 10))
            response = session.post(self.webhook_url, data=body_bytes, headers=headers, timeout=timeout)
        decoded = decode_response(response)
        return decoded if isinstance(decoded, dict) else {"response": decoded}

    def send_bks_event(self, event: str, **kwargs: Any) -> dict[str, Any]:
        """Shortcut for known BKS events. Validates event name before dispatch."""
        if event not in BKS_EVENTS:
            raise ValueError(f"Unknown BKS event '{event}'. Known events: {sorted(BKS_EVENTS)}")
        return self.send_event(event, dict(kwargs))

    def verify_signature(self, body: bytes, signature: str) -> bool:
        """Verify an inbound Make webhook signature."""
        if not self.secret or not signature:
            return False
        expected = hmac.new(self.secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def normalize_inbound(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "scenario": payload.get("scenario") or payload.get("scenario_name") or "",
            "status": payload.get("status") or payload.get("state") or "received",
            "external_id": str(payload.get("id") or payload.get("execution_id") or ""),
            "timestamp": payload.get("timestamp") or payload.get("created_at") or "",
            "source": payload.get("source") or "make",
            "raw": payload,
        }

    def health_snapshot(self) -> dict[str, Any]:
        domain = ""
        if self.webhook_url:
            try:
                from urllib.parse import urlparse
                domain = urlparse(self.webhook_url).hostname or ""
            except Exception:
                pass
        return {
            "configured": self.configured,
            "status": "ready" if self.configured else "missing_webhook_url",
            "has_secret": bool(self.secret),
            "has_api_key": bool(self.api_key),
            "webhook_domain": domain,
            "known_events": len(BKS_EVENTS),
        }
