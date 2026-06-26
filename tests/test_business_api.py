import httpx

from purchase_prep_assistant.business_api import AmazonBusinessClient, AmazonBusinessConfig


def test_client_add_items_uses_official_cart_path() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if str(request.url) == "https://api.amazon.com/auth/o2/token":
            return httpx.Response(200, json={"access_token": "token", "expires_in": 3600})
        assert request.url.path == "/cart/2025-04-30/carts/cart-123/items"
        assert request.url.params["region"] == "JP"
        assert request.headers["x-amz-access-token"] == "token"
        return httpx.Response(200, json={"items": [], "rejectedItems": []})

    transport = httpx.MockTransport(handler)
    config = AmazonBusinessConfig(
        client_id="client",
        client_secret="secret",
        refresh_token="refresh",
        region="JP",
        base_url="https://fe.business-api.amazon.com",
        buyer_email="buyer@example.co.jp",
    )
    with AmazonBusinessClient(config, transport=transport) as client:
        result = client.add_items("cart-123", {"items": []}, region="JP")

    assert result == {"items": [], "rejectedItems": []}
    assert len(requests) == 2


def test_client_place_order_uses_ordering_path() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == "https://api.amazon.com/auth/o2/token":
            return httpx.Response(200, json={"access_token": "token", "expires_in": 3600})
        assert request.url.path == "/ordering/2022-10-30/orders"
        return httpx.Response(200, json={"lineItems": [], "acceptanceArtifacts": [], "rejectionArtifacts": []})

    transport = httpx.MockTransport(handler)
    config = AmazonBusinessConfig(
        client_id="client",
        client_secret="secret",
        refresh_token="refresh",
        base_url="https://fe.business-api.amazon.com",
    )
    with AmazonBusinessClient(config, transport=transport) as client:
        result = client.place_order(
            {"externalId": "ORDER-1", "attributes": [], "expectations": [], "lineItems": []}
        )

    assert "lineItems" in result
