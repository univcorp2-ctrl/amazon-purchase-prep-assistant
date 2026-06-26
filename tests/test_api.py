from fastapi.testclient import TestClient

from purchase_prep_assistant.api import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["mode"] == "manual_review_only"


def test_validate_plan() -> None:
    payload = {
        "project_name": "api-test",
        "products": [
            {
                "name": "sample item",
                "url": "https://www.amazon.co.jp/dp/B012345678",
                "quantity": 1,
                "max_unit_price_jpy": 1000,
            }
        ],
        "recipients": [],
        "allocations": [],
        "safety_mode": "manual_review_only",
    }
    response = client.post("/validate-plan", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["warnings"]
