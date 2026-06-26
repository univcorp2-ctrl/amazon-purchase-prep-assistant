import pytest
from pydantic import ValidationError

from purchase_prep_assistant.models import PurchasePlan
from purchase_prep_assistant.safety import inspect_plan


BASE_PLAN = {
    "project_name": "sample",
    "products": [
        {
            "name": "sample item",
            "url": "https://www.amazon.co.jp/dp/B012345678",
            "quantity": 2,
            "max_unit_price_jpy": 1000,
            "buying_option_identifier": "BOI-1",
        }
    ],
    "recipients": [
        {
            "label": "home",
            "recipient_name": "山田 太郎",
            "postal_code": "100-0001",
            "prefecture": "東京都",
            "city": "千代田区",
            "line1": "千代田1-1",
        }
    ],
    "allocations": [{"product_name": "sample item", "recipient_label": "home", "quantity": 2}],
    "workflow_mode": "business_api_trial_order",
}


def test_safe_plan_passes() -> None:
    plan = PurchasePlan.model_validate(BASE_PLAN)
    report = inspect_plan(plan)
    assert report.ok
    assert report.errors == []


def test_checkout_url_fails_policy() -> None:
    data = dict(BASE_PLAN)
    data["products"] = [
        {
            "name": "checkout",
            "url": "https://www.amazon.co.jp/gp/buy/spc/handlers/display.html",
            "quantity": 1,
        }
    ]
    data["allocations"] = []
    plan = PurchasePlan.model_validate(data)
    report = inspect_plan(plan)
    assert not report.ok
    assert report.errors


def test_allocation_cannot_exceed_product_quantity() -> None:
    data = dict(BASE_PLAN)
    data["allocations"] = [{"product_name": "sample item", "recipient_label": "home", "quantity": 3}]
    with pytest.raises(ValidationError):
        PurchasePlan.model_validate(data)
