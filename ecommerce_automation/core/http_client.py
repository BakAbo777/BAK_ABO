from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ApiClientError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class ApiRateLimitError(ApiClientError):
    pass


@dataclass(frozen=True)
class RetryPolicy:
    total: int = 3
    backoff_factor: float = 0.75
    status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504)


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
        raise ApiRateLimitError("API rate limit reached.", status_code=response.status_code, payload=response.text[:1000])
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

