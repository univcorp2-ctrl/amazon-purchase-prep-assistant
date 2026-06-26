"""Amazon Business Cart API and Ordering API payload builders."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from purchase_prep_assistant.models import ProductItem, PurchasePlan, RecipientProfile


def money(amount: float | int, currency_code: str = "JPY") -> dict[str, Any]:
    return {"amount": amount, "currencyCode": currency_code.upper()}


def physical_address(recipient: RecipientProfile) -> dict[str, Any]:
    address: dict[str, Any] = {
        "addressType": "PhysicalAddress",
        "fullName": recipient.recipient_name,
        "addressLine1": recipient.line1,
        "city": recipient.city,
        "stateOrRegion": recipient.prefecture,
        "postalCode": recipient.postal_code,
        "countryCode": recipient.country_code,
    }
    if recipient.line2:
        address["addressLine2"] = recipient.line2
    if recipient.line3:
        address["addressLine3"] = recipient.line3
    if recipient.phone:
        address["phoneNumber"] = recipient.phone
    if recipient.company_name:
        address["companyName"] = recipient.company_name
    return address


def external_or_physical_address(recipient: RecipientProfile) -> dict[str, Any]:
    address = physical_address(recipient)
    if recipient.external_address_id:
        return {
            "addressType": "ExternalAddress",
            "addressId": recipient.external_address_id,
            "address": address,
        }
    return address


def product_external_id(product: ProductItem, index: int) -> str:
    return product.external_id or str(index)


def build_cart_add_items_payload(plan: PurchasePlan) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for index, product in enumerate(plan.products, start=1):
        item: dict[str, Any] = {
            "productIdentifier": product.asin or "ASIN_REQUIRED",
            "buyingOptionIdentifier": product.buying_option_identifier or "BUYING_OPTION_IDENTIFIER_REQUIRED",
            "quantity": product.quantity,
            "externalId": product_external_id(product, index),
        }
        items.append(item)
    return {"items": items}


def _reference_attribute(attribute_type: str, field_name: str, reference_type: str, identifier: str) -> dict[str, Any]:
    return {
        "attributeType": attribute_type,
        field_name: {
            f"{field_name}Type": reference_type,
            "identifier": identifier,
        },
    }


def _order_attributes(
    plan: PurchasePlan,
    recipient: RecipientProfile,
    trial: bool = True,
) -> list[dict[str, Any]]:
    attrs: list[dict[str, Any]] = [
        {"attributeType": "Region", "region": plan.business_region},
        {"attributeType": "ShippingAddress", "address": external_or_physical_address(recipient)},
    ]
    if trial:
        attrs.append({"attributeType": "TrialMode"})
    if plan.buying_group_reference:
        attrs.append(
            _reference_attribute(
                "BuyingGroupReference",
                "groupReference",
                "GroupReference",
                plan.buying_group_reference,
            )
        )
    if plan.payment_method_reference:
        attrs.append(
            _reference_attribute(
                "SelectedPaymentMethodReference",
                "paymentMethodReference",
                "PaymentMethodReference",
                plan.payment_method_reference,
            )
        )
    if plan.buyer_reference:
        attrs.append(
            _reference_attribute("BuyerReference", "userReference", "UserReference", plan.buyer_reference)
        )
    if plan.purchase_order_number:
        attrs.append(
            {
                "attributeType": "PurchaseOrderNumber",
                "purchaseOrderNumber": plan.purchase_order_number,
            }
        )
    return attrs


def _line_item_attributes(product: ProductItem) -> list[dict[str, Any]]:
    attrs: list[dict[str, Any]] = []
    if product.asin:
        attrs.append(
            {
                "attributeType": "SelectedProductReference",
                "productReference": {
                    "productReferenceType": "ProductIdentifier",
                    "identifierType": "ASIN",
                    "identifier": product.asin,
                },
            }
        )
    if product.buying_option_identifier:
        attrs.append(
            {
                "attributeType": "SelectedBuyingOptionReference",
                "buyingOptionReference": {
                    "buyingOptionReferenceType": "BuyingOptionIdentifier",
                    "identifier": product.buying_option_identifier,
                },
            }
        )
    return attrs


def _line_item_expectations(product: ProductItem, currency_code: str) -> list[dict[str, Any]]:
    expectations: list[dict[str, Any]] = []
    if product.max_unit_price_jpy is not None:
        expectations.append(
            {
                "expectationType": "ExpectedUnitPrice",
                "amount": money(product.max_unit_price_jpy, currency_code),
            }
        )
    return expectations


def build_order_payload(
    plan: PurchasePlan,
    recipient_label: str,
    external_id: str | None = None,
    trial: bool = True,
) -> dict[str, Any]:
    recipients = {recipient.label: recipient for recipient in plan.recipients}
    if recipient_label not in recipients:
        raise ValueError(f"recipient_label not found: {recipient_label}")
    recipient = recipients[recipient_label]

    target_quantities: dict[str, int] = {}
    if plan.allocations:
        for allocation in plan.allocations:
            if allocation.recipient_label == recipient_label:
                target_quantities[allocation.product_name] = allocation.quantity
    else:
        target_quantities = {product.name: product.quantity for product in plan.products}

    products = [product for product in plan.products if target_quantities.get(product.name, 0) > 0]
    if not products:
        raise ValueError(f"no products allocated to recipient_label: {recipient_label}")

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    order_external_id = external_id or f"{plan.project_name}-{recipient_label}-{stamp}"
    return {
        "externalId": order_external_id[:255],
        "attributes": _order_attributes(plan, recipient, trial=trial),
        "expectations": [],
        "lineItems": [
            {
                "externalId": product_external_id(product, index),
                "quantity": target_quantities[product.name],
                "attributes": _line_item_attributes(product),
                "expectations": _line_item_expectations(product, plan.currency_code),
            }
            for index, product in enumerate(products, start=1)
        ],
    }


def build_total_cost_estimation_payload(recipient: RecipientProfile) -> dict[str, Any]:
    return {"address": physical_address(recipient)}
