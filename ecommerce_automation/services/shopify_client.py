from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import requests
import urllib3

from ecommerce_automation.core.http_client import build_session, decode_response

BKS_TM04_THEME_ID = "202392961362"
BKS_LIVE_COLLECTIONS = frozenset({"hours", "glyph", "marker", "riviera", "pulse", "token", "flag", "origin"})


@dataclass
class ShopifyClient:
    shop: str
    token: str
    api_version: str = "2025-01"
    last_ssl_verified: bool = True
    _session: Any = field(default=None, repr=False, compare=False)

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

    def _base(self) -> str:
        return f"https://{self._domain()}/admin/api/{self.api_version}"

    def _request(self, method: str, path: str, *, params: dict | None = None, json: Any = None, timeout: int = 30) -> dict[str, Any]:
        if not self.configured:
            raise RuntimeError("Shopify credentials are not configured.")
        if self._session is None:
            self._session = build_session()
        url = f"{self._base()}{path}"
        kwargs: dict[str, Any] = {"headers": self._headers(), "timeout": timeout}
        if params:
            kwargs["params"] = params
        if json is not None:
            kwargs["json"] = json
        try:
            response = getattr(self._session, method)(url, **kwargs)
            self.last_ssl_verified = True
        except requests.exceptions.SSLError:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = getattr(self._session, method)(url, **kwargs, verify=False)
            self.last_ssl_verified = False
        if response.status_code == 429:
            retry_after = float(response.headers.get("Retry-After", "2"))
            time.sleep(min(retry_after, 10))
            response = getattr(self._session, method)(url, **kwargs)
        return decode_response(response)

    def get_shop(self) -> dict[str, Any]:
        return self._request("get", "/shop.json").get("shop", {})

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
        base = self.health()
        try:
            base["theme_id"] = self.active_theme_id()
        except Exception:
            base["theme_id"] = ""
        base["tm04_active"] = base.get("theme_id") == BKS_TM04_THEME_ID
        return base

    # --- Theme ---

    def get_themes(self) -> list[dict[str, Any]]:
        data = self._request("get", "/themes.json")
        return [t for t in data.get("themes", []) if isinstance(t, dict)]

    def active_theme_id(self) -> str:
        for theme in self.get_themes():
            if theme.get("role") == "main":
                return str(theme.get("id", ""))
        return ""

    def active_theme_summary(self) -> dict[str, Any]:
        for theme in self.get_themes():
            if theme.get("role") == "main":
                tid = str(theme.get("id", ""))
                return {
                    "theme_id": tid,
                    "name": theme.get("name", ""),
                    "status": "ready" if tid == BKS_TM04_THEME_ID else "unexpected",
                    "tm04_active": tid == BKS_TM04_THEME_ID,
                }
        return {"theme_id": "", "status": "not_found", "tm04_active": False}

    # --- Products ---

    def list_products(self, *, limit: int = 250, since_id: int = 0, status: str = "any") -> list[dict[str, Any]]:
        params: dict[str, Any] = {"limit": max(1, min(250, int(limit))), "status": status}
        if since_id:
            params["since_id"] = int(since_id)
        data = self._request("get", "/products.json", params=params, timeout=60)
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

    def get_product(self, product_id: int | str) -> dict[str, Any]:
        return self._request("get", f"/products/{product_id}.json").get("product", {})

    def update_product(self, product_id: int | str, data: dict[str, Any]) -> dict[str, Any]:
        return self._request("put", f"/products/{product_id}.json", json={"product": data}).get("product", {})

    # --- Collections ---

    def list_collections(self) -> list[dict[str, Any]]:
        custom = self._request("get", "/custom_collections.json", params={"limit": 250}).get("custom_collections", [])
        smart = self._request("get", "/smart_collections.json", params={"limit": 250}).get("smart_collections", [])
        return [c for c in custom + smart if isinstance(c, dict)]

    def collections_summary(self) -> dict[str, Any]:
        cols = self.list_collections()
        handles = {str(c.get("handle", "")).lower().removeprefix("bks-") for c in cols}
        missing = sorted(BKS_LIVE_COLLECTIONS - handles)
        rogue = sorted(handles - BKS_LIVE_COLLECTIONS - {""})
        return {
            "total": len(cols),
            "bks_present": sorted(BKS_LIVE_COLLECTIONS & handles),
            "missing": missing,
            "rogue": rogue,
            "status": "pass" if not missing else "needs_fix",
        }

    # --- Pages (trust pages) ---

    def list_pages(self, *, published_status: str = "published") -> list[dict[str, Any]]:
        params = {"limit": 250, "published_status": published_status}
        data = self._request("get", "/pages.json", params=params)
        return [p for p in data.get("pages", []) if isinstance(p, dict)]

    def trust_pages_summary(self) -> dict[str, Any]:
        pages = self.list_pages()
        handles = {str(p.get("handle", "")) for p in pages}
        required = {
            "about": "About",
            "contact": "Contact",
            "help-faq": "FAQ / Help",
        }
        results = []
        for handle, label in required.items():
            ok = handle in handles
            results.append({"check": label, "handle": handle, "status": "pass" if ok else "fail"})
        return {
            "total_pages": len(pages),
            "checks": results,
            "missing": [r["check"] for r in results if r["status"] == "fail"],
            "status": "pass" if all(r["status"] == "pass" for r in results) else "needs_fix",
        }
