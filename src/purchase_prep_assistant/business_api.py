"""Amazon Business official API client."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

REGION_BASE_URLS = {
    "US": "https://na.business-api.amazon.com",
    "CA": "https://na.business-api.amazon.com",
    "MX": "https://na.business-api.amazon.com",
    "UK": "https://eu.business-api.amazon.com",
    "DE": "https://eu.business-api.amazon.com",
    "FR": "https://eu.business-api.amazon.com",
    "IT": "https://eu.business-api.amazon.com",
    "ES": "https://eu.business-api.amazon.com",
    "JP": "https://fe.business-api.amazon.com",
    "AU": "https://fe.business-api.amazon.com",
    "IN": "https://fe.business-api.amazon.com",
}


@dataclass(frozen=True)
class AmazonBusinessConfig:
    client_id: str
    client_secret: str
    refresh_token: str
    region: str = "JP"
    base_url: str = "https://fe.business-api.amazon.com"
    buyer_email: str = ""
    user_agent: str = "AmazonBusinessPurchaseAutomationAssistant/0.2.0 (Language=Python/3.11)"
    token_url: str = "https://api.amazon.com/auth/o2/token"
    timeout_seconds: float = 30.0

    @classmethod
    def from_env(cls) -> "AmazonBusinessConfig":
        region = os.getenv("AMAZON_BUSINESS_REGION", "JP").upper()
        base_url = os.getenv("AMAZON_BUSINESS_BASE_URL", REGION_BASE_URLS.get(region, REGION_BASE_URLS["JP"]))
        return cls(
            client_id=os.environ["AMAZON_BUSINESS_CLIENT_ID"],
            client_secret=os.environ["AMAZON_BUSINESS_CLIENT_SECRET"],
            refresh_token=os.environ["AMAZON_BUSINESS_REFRESH_TOKEN"],
            region=region,
            base_url=base_url.rstrip("/"),
            buyer_email=os.getenv("AMAZON_BUSINESS_BUYER_EMAIL", ""),
            user_agent=os.getenv(
                "AMAZON_BUSINESS_USER_AGENT",
                "AmazonBusinessPurchaseAutomationAssistant/0.2.0 (Language=Python/3.11)",
            ),
        )


class AmazonBusinessClient:
    """Small synchronous wrapper for Amazon Business Cart and Ordering APIs."""

    def __init__(self, config: AmazonBusinessConfig, transport: httpx.BaseTransport | None = None):
        self.config = config
        self._access_token: str | None = None
        self._expires_at = datetime.min.replace(tzinfo=UTC)
        self._client = httpx.Client(timeout=config.timeout_seconds, transport=transport)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "AmazonBusinessClient":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def access_token(self) -> str:
        now = datetime.now(UTC)
        if self._access_token and now < self._expires_at - timedelta(minutes=2):
            return self._access_token

        response = self._client.post(
            self.config.token_url,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.config.refresh_token,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
            },
            headers={"user-agent": self.config.user_agent},
        )
        response.raise_for_status()
        payload = response.json()
        self._access_token = payload["access_token"]
        self._expires_at = now + timedelta(seconds=int(payload.get("expires_in", 3600)))
        return self._access_token

    def _headers(self, buyer_email: str | None = None) -> dict[str, str]:
        headers = {
            "x-amz-access-token": self.access_token(),
            "x-amz-date": datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"),
            "user-agent": self.config.user_agent,
            "content-type": "application/json",
            "accept": "application/json",
        }
        email = buyer_email or self.config.buyer_email
        if email:
            headers["x-amz-user-email"] = email
        return headers

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_payload: dict[str, Any] | None = None,
        buyer_email: str | None = None,
    ) -> dict[str, Any]:
        response = self._client.request(
            method,
            f"{self.config.base_url}{path}",
            params=params,
            json=json_payload,
            headers=self._headers(buyer_email),
        )
        if response.status_code == 204:
            return {"status_code": 204, "payload": None}
        response.raise_for_status()
        return response.json()

    def list_carts(
        self,
        *,
        region: str | None = None,
        buyer_email: str | None = None,
        page_size: int = 5,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"region": (region or self.config.region), "pageSize": page_size}
        if page_token:
            params["pageToken"] = page_token
        return self.request("GET", "/cart/2025-04-30/carts", params=params, buyer_email=buyer_email)

    def get_cart(self, cart_id: str, *, region: str | None = None) -> dict[str, Any]:
        return self.request(
            "GET", f"/cart/2025-04-30/carts/{cart_id}", params={"region": region or self.config.region}
        )

    def get_items(self, cart_id: str, *, region: str | None = None) -> dict[str, Any]:
        return self.request(
            "GET",
            f"/cart/2025-04-30/carts/{cart_id}/items",
            params={"region": region or self.config.region},
        )

    def add_items(
        self, cart_id: str, payload: dict[str, Any], *, region: str | None = None
    ) -> dict[str, Any]:
        return self.request(
            "POST",
            f"/cart/2025-04-30/carts/{cart_id}/items",
            params={"region": region or self.config.region},
            json_payload=payload,
        )

    def modify_items(
        self, cart_id: str, payload: dict[str, Any], *, region: str | None = None
    ) -> dict[str, Any]:
        return self.request(
            "PATCH",
            f"/cart/2025-04-30/carts/{cart_id}/items",
            params={"region": region or self.config.region},
            json_payload=payload,
        )

    def delete_items(self, cart_id: str, *, region: str | None = None) -> dict[str, Any]:
        return self.request(
            "DELETE",
            f"/cart/2025-04-30/carts/{cart_id}/items",
            params={"region": region or self.config.region},
        )

    def estimate_total_purchase_cost(
        self, cart_id: str, payload: dict[str, Any], *, region: str | None = None
    ) -> dict[str, Any]:
        return self.request(
            "POST",
            f"/cart/2025-04-30/carts/{cart_id}/totalPurchaseCostEstimations",
            params={"region": region or self.config.region},
            json_payload=payload,
        )

    def place_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", "/ordering/2022-10-30/orders", json_payload=payload)

    def order_details(self, external_id: str) -> dict[str, Any]:
        return self.request("GET", f"/ordering/2022-10-30/orders/{external_id}")
