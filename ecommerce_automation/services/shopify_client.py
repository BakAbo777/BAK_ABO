from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
import urllib3

from ecommerce_automation.core.http_client import build_session, decode_response


@dataclass
class ShopifyClient:
    shop: str
    token: str
    api_version: str = "2025-01"
    last_ssl_verified: bool = True

    @property
    def configured(self) -> bool:
        return bool(self.shop and self.token)

    def _domain(self) -> str:
        return self.shop.replace("https://", "").replace("http://", "").strip("/")

    def _headers(self) -> dict[str, str]:
        return {
            "X-Shopify-Access-Token": self.token,
            "Content-Type": "application/json",
        }

    def get_shop(self) -> dict[str, Any]:
        if not self.configured:
            raise RuntimeError("Shopify credentials are not configured.")
        url = f"https://{self._domain()}/admin/api/{self.api_version}/shop.json"
        session = build_session()
        try:
            response = session.get(url, headers=self._headers(), timeout=30)
            self.last_ssl_verified = True
        except requests.exceptions.SSLError:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = session.get(url, headers=self._headers(), timeout=30, verify=False)
            self.last_ssl_verified = False
        return decode_response(response).get("shop", {})

    def health(self) -> dict[str, Any]:
        shop = self.get_shop()
        return {
            "configured": True,
            "status": "connected",
            "name": shop.get("name", ""),
            "domain": shop.get("domain", ""),
            "myshopify_domain": shop.get("myshopify_domain", ""),
            "plan_name": shop.get("plan_name", ""),
            "ssl_verified": self.last_ssl_verified,
        }

    def health_snapshot(self, *, live: bool = False) -> dict[str, Any]:
        if not self.configured:
            return {"configured": False, "status": "missing_credentials"}
        if not live:
            return {"configured": True, "status": "configured", "shop": self._domain(), "api_version": self.api_version}
        return self.health()

    def list_products(self, *, limit: int = 250, since_id: int = 0, status: str = "any") -> list[dict[str, Any]]:
        if not self.configured:
            raise RuntimeError("Shopify credentials are not configured.")
        params: dict[str, Any] = {"limit": max(1, min(250, int(limit))), "status": status}
        if since_id:
            params["since_id"] = int(since_id)
        url = f"https://{self._domain()}/admin/api/{self.api_version}/products.json"
        session = build_session()
        try:
            response = session.get(url, headers=self._headers(), params=params, timeout=60)
            self.last_ssl_verified = True
        except requests.exceptions.SSLError:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = session.get(url, headers=self._headers(), params=params, timeout=60, verify=False)
            self.last_ssl_verified = False
        data = decode_response(response)
        return [item for item in data.get("products", []) if isinstance(item, dict)]

    def iter_products(self, *, max_pages: int = 20, limit: int = 250, status: str = "any") -> list[dict[str, Any]]:
        products: list[dict[str, Any]] = []
        since_id = 0
        for _ in range(max(1, max_pages)):
            page = self.list_products(limit=limit, since_id=since_id, status=status)
            if not page:
                break
            products.extend(page)
            next_id = max(int(item.get("id", 0) or 0) for item in page)
            if not next_id or next_id == since_id or len(page) < limit:
                break
            since_id = next_id
        return products
