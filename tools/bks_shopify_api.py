from __future__ import annotations

import argparse
import os
import time
from pathlib import Path
from typing import Any

import requests
import urllib3

try:
    import certifi
except ImportError:
    certifi = None


BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
DEFAULT_API_VERSION = "2025-01"


def load_local_env(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def env_value(*names: str, default: str = "") -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return default


def mask_token(token: str) -> str:
    return f"{token[:6]}...{token[-4:]}" if len(token) >= 12 else "<missing>"


def add_shopify_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--shop", default="")
    parser.add_argument("--token", default="")
    parser.add_argument("--api-version", default="")
    parser.add_argument("--no-verify-ssl", action="store_true")
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--retry-delay", type=float, default=2.0)
    parser.add_argument("--request-timeout", type=float, default=45.0)


class ShopifyGraphQL:
    def __init__(
        self,
        shop: str,
        token: str,
        api_version: str,
        verify_ssl: bool = True,
        max_retries: int = 5,
        retry_delay: float = 2.0,
        request_timeout: float = 45.0,
    ) -> None:
        domain = shop.replace("https://", "").replace("http://", "").strip("/")
        self.url = f"https://{domain}/admin/api/{api_version}/graphql.json"
        self.shop = domain
        self.api_version = api_version
        self.max_retries = max(1, max_retries)
        self.retry_delay = max(0.2, retry_delay)
        self.request_timeout = request_timeout
        self.headers = {
            "X-Shopify-Access-Token": token,
            "Content-Type": "application/json",
        }
        self.verify: bool | str = certifi.where() if verify_ssl and certifi else verify_ssl
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "ShopifyGraphQL":
        load_local_env()
        shop = args.shop or env_value("SHOPIFY_MYSHOPIFY_DOMAIN", "SHOPIFY_STORE", "SHOP")
        token = args.token or env_value("SHOPIFY_ADMIN_TOKEN", "SHOPIFY_TOKEN", "TOKEN")
        api_version = args.api_version or env_value(
            "SHOPIFY_API_VERSION",
            default=DEFAULT_API_VERSION,
        )
        if not shop or not token:
            raise RuntimeError("Missing Shopify shop/token. Set .env or pass --shop and --token.")
        return cls(
            shop,
            token,
            api_version,
            verify_ssl=not args.no_verify_ssl,
            max_retries=args.max_retries,
            retry_delay=args.retry_delay,
            request_timeout=args.request_timeout,
        )

    def retry_sleep(self, attempt: int, response: requests.Response | None = None) -> float:
        retry_after = response.headers.get("Retry-After", "") if response is not None else ""
        if retry_after:
            try:
                return max(0.2, float(retry_after))
            except ValueError:
                pass
        return min(60.0, self.retry_delay * (2 ** (attempt - 1)))

    def query(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.post(
                    self.url,
                    headers=self.headers,
                    json={"query": query, "variables": variables or {}},
                    verify=self.verify,
                    timeout=self.request_timeout,
                )
                retryable_status = response.status_code == 429 or response.status_code >= 500
                if retryable_status and attempt < self.max_retries:
                    delay = self.retry_sleep(attempt, response)
                    print(
                        f"retry {attempt}/{self.max_retries} HTTP {response.status_code}; waiting {delay:.1f}s",
                        flush=True,
                    )
                    time.sleep(delay)
                    continue
                response.raise_for_status()
                data = response.json()
                if data.get("errors"):
                    raise RuntimeError(data["errors"])
                return data
            except requests.exceptions.HTTPError:
                raise
            except requests.exceptions.RequestException as exc:
                if attempt >= self.max_retries:
                    raise
                delay = self.retry_sleep(attempt)
                print(
                    f"retry {attempt}/{self.max_retries} network error: {exc}; waiting {delay:.1f}s",
                    flush=True,
                )
                time.sleep(delay)

        raise RuntimeError("Shopify request failed after retries.")
