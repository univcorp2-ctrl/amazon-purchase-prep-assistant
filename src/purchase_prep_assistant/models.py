"""Pydantic models for purchase preparation plans."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import BaseModel, Field, field_validator, model_validator

from purchase_prep_assistant.parsers import extract_asin_from_amazon_url


class ProductItem(BaseModel):
    """A product reference to prepare for manual purchase review."""

    name: str = Field(min_length=1, max_length=160)
    url: str = Field(min_length=8, max_length=2000)
    asin: str | None = Field(default=None, min_length=10, max_length=10)
    quantity: int = Field(default=1, ge=1, le=999)
    max_unit_price_jpy: int | None = Field(default=None, ge=0)
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
    """A recipient/address template used for planning and manual confirmation."""

    label: str = Field(min_length=1, max_length=80)
    recipient_name: str = Field(min_length=1, max_length=120)
    postal_code: str = Field(min_length=3, max_length=20)
    prefecture: str = Field(min_length=1, max_length=80)
    city: str = Field(min_length=1, max_length=120)
    line1: str = Field(min_length=1, max_length=160)
    line2: str = Field(default="", max_length=160)
    phone: str = Field(default="", max_length=40)
    note: str = Field(default="", max_length=500)


class Allocation(BaseModel):
    """Assign product quantities to recipient labels."""

    product_name: str = Field(min_length=1, max_length=160)
    recipient_label: str = Field(min_length=1, max_length=80)
    quantity: int = Field(ge=1, le=999)


class PurchasePlan(BaseModel):
    """Top-level purchase preparation plan."""

    project_name: str = Field(min_length=1, max_length=160)
    products: list[ProductItem] = Field(min_length=1)
    recipients: list[RecipientProfile] = Field(default_factory=list)
    allocations: list[Allocation] = Field(default_factory=list)
    safety_mode: Literal["manual_review_only"] = "manual_review_only"

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
