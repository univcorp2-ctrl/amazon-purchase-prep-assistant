from purchase_prep_assistant.business_payloads import (
    build_cart_add_items_payload,
    build_order_payload,
)
from purchase_prep_assistant.exporters import load_plan


def test_build_cart_add_items_payload() -> None:
    plan = load_plan("sample_data/purchase_plan.json")
    payload = build_cart_add_items_payload(plan)
    assert payload["items"][0]["productIdentifier"] == "B012345678"
    assert payload["items"][0]["quantity"] == 2
    assert "buyingOptionIdentifier" in payload["items"][0]


def test_build_order_payload_for_recipient() -> None:
    plan = load_plan("sample_data/purchase_plan.json")
    payload = build_order_payload(plan, "customer-a", external_id="ORDER-1")
    assert payload["externalId"] == "ORDER-1"
    assert payload["lineItems"][0]["quantity"] == 1
    assert payload["attributes"][0]["attributeType"] == "Region"
    assert any(attr["attributeType"] == "ShippingAddress" for attr in payload["attributes"])
    assert any(attr["attributeType"] == "TrialMode" for attr in payload["attributes"])


def test_build_order_payload_for_second_recipient() -> None:
    plan = load_plan("sample_data/purchase_plan.json")
    payload = build_order_payload(plan, "customer-b", external_id="ORDER-2")
    shipping = next(attr for attr in payload["attributes"] if attr["attributeType"] == "ShippingAddress")
    assert shipping["address"]["addressId"] == "ADDR-CUSTOMER-B"
    assert payload["lineItems"][0]["quantity"] == 1
