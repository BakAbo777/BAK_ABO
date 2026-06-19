from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
import urllib3

from ecommerce_automation.core.http_client import build_session, decode_response


@dataclass
class PrintifyClient:
    token: str
    shop_id: str = ""
    user_agent: str = "ECAMP BakAbo/1.0"
    base_url: str = "https://api.printify.com/v1"
    last_ssl_verified: bool = True

    @property
    def configured(self) -> bool:
        return bool(self.token)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json;charset=utf-8",
            "User-Agent": self.user_agent,
        }

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        if not self.configured:
            raise RuntimeError("PRINTIFY_API_TOKEN is not configured.")
        session = build_session()
        timeout = kwargs.pop("timeout", 60)
        try:
            response = session.request(
                method,
                f"{self.base_url}{path}",
                headers=self._headers(),
                timeout=timeout,
                **kwargs,
            )
            self.last_ssl_verified = True
        except requests.exceptions.SSLError:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = session.request(
                method,
                f"{self.base_url}{path}",
                headers=self._headers(),
                timeout=timeout,
                verify=False,
                **kwargs,
            )
            self.last_ssl_verified = False
        return decode_response(response)

    def get_shops(self) -> list[dict[str, Any]]:
        data = self.request("GET", "/shops.json")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        return [item for item in data.get("data", []) if isinstance(item, dict)] if isinstance(data, dict) else []

    def resolve_shop_id(self, preferred_title: str = "bakabo.club") -> str:
        if self.shop_id.isdigit():
            return self.shop_id
        shops = self.get_shops()
        preferred = preferred_title.lower().strip()
        for shop in shops:
            title = str(shop.get("title", "")).lower()
            channel = str(shop.get("sales_channel", "")).lower()
            if preferred and (preferred in title or preferred in channel):
                return str(shop["id"])
        if not shops:
            raise RuntimeError("No Printify shops found for this token.")
        return str(shops[0]["id"])

    def list_products(self, shop_id: str, page: int = 1, limit: int = 50) -> dict[str, Any]:
        return self.request("GET", f"/shops/{shop_id}/products.json", params={"page": page, "limit": limit})

    def iter_products(
        self, shop_id: str, *, max_pages: int = 40, limit: int = 50, visible_only: bool = False
    ) -> list[dict[str, Any]]:
        products: list[dict[str, Any]] = []
        for page in range(1, max(1, max_pages) + 1):
            data = self.list_products(shop_id, page=page, limit=limit)
            page_products = data.get("data", data if isinstance(data, list) else [])
            page_products = [item for item in page_products if isinstance(item, dict)]
            if not page_products:
                break
            products.extend(page_products)
            last_page = int(data.get("last_page", page) or page) if isinstance(data, dict) else page
            if page >= last_page:
                break
        if visible_only:
            products = [p for p in products if p.get("visible")]
        return products

    def create_product(self, shop_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", f"/shops/{shop_id}/products.json", json=payload)

    def publish_product(self, shop_id: str, product_id: str, publish_payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("PUT", f"/shops/{shop_id}/products/{product_id}/publish.json", json=publish_payload)

    def list_orders(self, shop_id: str, page: int = 1, limit: int = 50) -> dict[str, Any]:
        return self.request("GET", f"/shops/{shop_id}/orders.json", params={"page": page, "limit": limit})

    def find_product_by_title(self, shop_id: str, title: str, max_pages: int = 10) -> dict[str, Any] | None:
        target = title.strip().lower()
        for page in range(1, max_pages + 1):
            data = self.list_products(shop_id, page=page)
            products = data.get("data", data if isinstance(data, list) else [])
            if not products:
                return None
            for product in products:
                if isinstance(product, dict) and str(product.get("title", "")).strip().lower() == target:
                    return product
        return None

    def health_snapshot(self, preferred_title: str = "bakabo.club") -> dict[str, Any]:
        if not self.configured:
            return {"configured": False, "status": "missing_token"}
        shops = self.get_shops()
        shop_id = self.resolve_shop_id(preferred_title)
        first_page = self.list_products(shop_id, page=1, limit=50)
        products = first_page.get("data", first_page if isinstance(first_page, list) else [])
        published = 0
        drafts = 0
        for product in products:
            if not isinstance(product, dict):
                continue
            external = product.get("external") or {}
            if product.get("visible") is True or external.get("id"):
                published += 1
            else:
                drafts += 1
        return {
            "configured": True,
            "status": "connected",
            "shops": len(shops),
            "shop_id": shop_id,
            "sample_products": len(products),
            "sample_published": published,
            "sample_drafts": drafts,
            "ssl_verified": self.last_ssl_verified,
        }
