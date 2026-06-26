"""Plan inspection and quality checks."""

from __future__ import annotations

from dataclasses import dataclass

from purchase_prep_assistant.models import PurchasePlan
from purchase_prep_assistant.parsers import is_allowed_amazon_product_url

SAFETY_POLICY_TEXT = """
This project structures purchase plans, customer delivery profiles, and Amazon Business API request payloads for official API-based procurement workflows.
""".strip()


@dataclass(frozen=True)
class SafetyReport:
    ok: bool
    warnings: list[str]
    errors: list[str]


def inspect_plan(plan: PurchasePlan) -> SafetyReport:
    """Validate plan structure before export and API payload generation."""
    warnings: list[str] = []
    errors: list[str] = []

    for product in plan.products:
        if not is_allowed_amazon_product_url(product.url):
            errors.append(f"unsupported product reference URL: {product.name}")
        if product.asin is None:
            warnings.append(
                f"ASIN could not be inferred for '{product.name}'. Set asin explicitly before live API calls."
            )
        if product.buying_option_identifier is None:
            warnings.append(
                f"buying_option_identifier is empty for '{product.name}'. Product Search API or Cart API response data is needed for live ordering."
            )
        if product.max_unit_price_jpy is None:
            warnings.append(f"No max_unit_price_jpy set for '{product.name}'.")

    if not plan.allocations and plan.recipients:
        warnings.append("Recipients exist, but no quantity allocations are defined.")
    if not plan.recipients:
        warnings.append("No recipients are defined. Address-based API payloads require a recipient profile.")
    if len(plan.products) > 50:
        errors.append("Ordering API payloads support up to 50 line items per order request.")

    return SafetyReport(ok=not errors, warnings=warnings, errors=errors)


def assert_safe_plan(plan: PurchasePlan) -> SafetyReport:
    """Raise ValueError if the plan cannot be exported."""
    report = inspect_plan(plan)
    if not report.ok:
        raise ValueError("; ".join(report.errors))
    return report
