from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BAKABO_STORE_DOMAIN = "bakabo.club"
BKS_TM04_THEME_ID = "202392961362"


class ApiClientError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload

    def __str__(self) -> str:
        base = super().__str__()
        return f"{base} (HTTP {self.status_code})" if self.status_code else base


class ApiRateLimitError(ApiClientError):
    """HTTP 429 — caller should back off and retry."""


class ApiAuthError(ApiClientError):
    """HTTP 401/403 — bad token or missing scope; do not retry automatically."""


class ApiNotFoundError(ApiClientError):
    """HTTP 404 — resource absent on this platform; handle as a gap, not a crash."""


@dataclass(frozen=True)
class RetryPolicy:
    total: int = 3
    backoff_factor: float = 0.75
    status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504)
    # recommended per-request timeout (seconds) — callers should pass this to session.get/post/put
    timeout: float = 30.0


# named presets used by BKS service clients
BKS_SHOPIFY_POLICY = RetryPolicy(total=4, backoff_factor=1.0, timeout=20.0)
BKS_PRINTIFY_POLICY = RetryPolicy(total=3, backoff_factor=0.75, timeout=30.0)
BKS_OPENAI_POLICY = RetryPolicy(total=2, backoff_factor=1.5, timeout=60.0)
BKS_HEYGEN_POLICY = RetryPolicy(total=2, backoff_factor=2.0, timeout=120.0)


def build_session(policy: RetryPolicy | None = None) -> requests.Session:
    policy = policy or RetryPolicy()
    retry = Retry(
        total=policy.total,
        connect=policy.total,
        read=policy.total,
        status=policy.total,
        backoff_factor=policy.backoff_factor,
        status_forcelist=policy.status_forcelist,
        allowed_methods=("GET", "POST", "PUT", "PATCH", "DELETE"),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def decode_response(response: requests.Response) -> Any:
    if response.status_code == 429:
        raise ApiRateLimitError(
            "API rate limit reached.",
            status_code=response.status_code,
            payload=response.text[:1000],
        )
    if response.status_code in (401, 403):
        raise ApiAuthError(
            f"API authentication failed — check token scope.",
            status_code=response.status_code,
            payload=response.text[:500],
        )
    if response.status_code == 404:
        raise ApiNotFoundError(
            "Resource not found on platform.",
            status_code=response.status_code,
            payload=response.text[:500],
        )
    try:
        payload = response.json() if response.content else {}
    except ValueError:
        payload = response.text[:1000]
    if response.status_code >= 400:
        raise ApiClientError(
            f"API request failed with HTTP {response.status_code}.",
            status_code=response.status_code,
            payload=payload,
        )
    return payload
