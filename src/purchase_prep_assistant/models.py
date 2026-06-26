"""Pydantic models for Amazon Business purchase automation plans."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import BaseModel, Field, field_validator, model_validator

from purchase_prep_assistant.parsers import extract_asin_from_amazon_url


class ProductItem(BaseModel):
    """A product reference to prepare for Amazon Business Cart/Ordering payloads."""

    name: str = Field(min_length=1, max_length=160)
    url: str = Field(min_length=8, max_length=2000)
    asin: str | None = Field(default=None, min_length=10, max_length=10)
    buying_option_identifier: str | None = Field(default=None, max_length=500)
    quantity: int = Field(default=1, ge=1, le=999)
    max_unit_price_jpy: int | None = Field(default=None, ge=0)
    external_id: str | None = Field(default=None, max_length=127)
    note: str = Field(default="", max_length=500)

    @field_validator("asin")
    @classmethod
    def uppercase_asin(cls, value: str | None) -> str | None:
        return value.upper() if value else None

    @model_validator(mode="after")
    def infer_asin(self) -> Self:
        if self.asin is None:
            self.asin = extract_asin_from_amazon_url(self.url)
        return self


class RecipientProfile(BaseModel):
    """A customer/address template used for Amazon Business payload creation."""

    label: str = Field(min_length=1, max_length=80)
    recipient_name: str = Field(min_length=1, max_length=120)
    postal_code: str = Field(min_length=3, max_length=20)
    prefecture: str = Field(min_length=1, max_length=80)
    city: str = Field(min_length=1, max_length=120)
    line1: str = Field(min_length=1, max_length=160)
    line2: str = Field(default="", max_length=160)
    line3: str = Field(default="", max_length=160)
    phone: str = Field(default="", max_length=40)
    company_name: str = Field(default="", max_length=120)
    country_code: str = Field(default="JP", min_length=2, max_length=2)
    buyer_email: str = Field(default="", max_length=160)
    external_address_id: str = Field(default="", max_length=255)
    note: str = Field(default="", max_length=500)

    @field_validator("country_code")
    @classmethod
    def uppercase_country(cls, value: str) -> str:
        return value.upper()


class Allocation(BaseModel):
    """Assign product quantities to recipient labels."""

    product_name: str = Field(min_length=1, max_length=160)
    recipient_label: str = Field(min_length=1, max_length=80)
    quantity: int = Field(ge=1, le=999)


class PurchasePlan(BaseModel):
    """Top-level Amazon Business purchase automation plan."""

    project_name: str = Field(min_length=1, max_length=160)
    products: list[ProductItem] = Field(min_length=1)
    recipients: list[RecipientProfile] = Field(default_factory=list)
    allocations: list[Allocation] = Field(default_factory=list)
    workflow_mode: Literal[
        "business_api_prep",
        "business_api_cart",
        "business_api_trial_order",
        "business_api_live_ready",
    ] = "business_api_prep"
    business_region: str = Field(default="JP", min_length=2, max_length=2)
    currency_code: str = Field(default="JPY", min_length=3, max_length=3)
    buying_group_reference: str = Field(default="", max_length=255)
    payment_method_reference: str = Field(default="", max_length=255)
    buyer_reference: str = Field(default="", max_length=255)
    purchase_order_number: str = Field(default="", max_length=255)

    @field_validator("business_region", "currency_code")
    @classmethod
    def uppercase_code(cls, value: str) -> str:
        return value.upper()

    @model_validator(mode="after")
    def validate_allocations(self) -> Self:
        product_quantities = {product.name: product.quantity for product in self.products}
        recipient_labels = {recipient.label for recipient in self.recipients}

        for allocation in self.allocations:
            if allocation.product_name not in product_quantities:
                raise ValueError(f"allocation references unknown product: {allocation.product_name}")
            if allocation.recipient_label not in recipient_labels:
                raise ValueError(f"allocation references unknown recipient: {allocation.recipient_label}")

        allocated_totals: dict[str, int] = {}
        for allocation in self.allocations:
            allocated_totals[allocation.product_name] = (
                allocated_totals.get(allocation.product_name, 0) + allocation.quantity
            )

        for product_name, total in allocated_totals.items():
            if total > product_quantities[product_name]:
                raise ValueError(
                    f"allocations for {product_name} exceed requested quantity "
                    f"({total} > {product_quantities[product_name]})"
                )
        return self
