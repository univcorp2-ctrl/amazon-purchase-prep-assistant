from fastapi.testclient import TestClient

from purchase_prep_assistant.api import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["mode"] == "business_api_prep"


def test_validate_plan() -> None:
    payload = {
        "project_name": "api-test",
        "products": [
            {
                "name": "sample item",
                "url": "https://www.amazon.co.jp/dp/B012345678",
                "quantity": 1,
                "max_unit_price_jpy": 1000,
                "buying_option_identifier": "BOI-1",
            }
        ],
        "recipients": [],
        "allocations": [],
        "workflow_mode": "business_api_prep",
    }
    response = client.post("/validate-plan", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["warnings"]


def test_cart_payload_endpoint() -> None:
    payload = {
        "project_name": "api-test",
        "products": [
            {
                "name": "sample item",
                "url": "https://www.amazon.co.jp/dp/B012345678",
                "quantity": 1,
                "buying_option_identifier": "BOI-1",
            }
        ],
        "recipients": [],
        "allocations": [],
    }
    response = client.post("/cart-add-items-payload", json=payload)
    assert response.status_code == 200
    assert response.json()["items"][0]["buyingOptionIdentifier"] == "BOI-1"
