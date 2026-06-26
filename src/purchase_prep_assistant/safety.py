"""Safety policy enforcement for purchase preparation."""

from __future__ import annotations

from dataclasses import dataclass

from purchase_prep_assistant.models import PurchasePlan
from purchase_prep_assistant.parsers import is_allowed_amazon_product_url

SAFETY_POLICY_TEXT = """
This project supports manual purchase preparation only. It does not implement
browser automation, checkout automation, address form autofill on Amazon,
CAPTCHA/2FA bypass, bot detection evasion, proxy rotation, human-like behavior
simulation, or automatic purchase confirmation.
""".strip()


@dataclass(frozen=True)
class SafetyReport:
    ok: bool
    warnings: list[str]
    errors: list[str]


def inspect_plan(plan: PurchasePlan) -> SafetyReport:
    """Validate that a plan stays within manual-review boundaries."""
    warnings: list[str] = []
    errors: list[str] = []

    if plan.safety_mode != "manual_review_only":
        errors.append("safety_mode must remain manual_review_only")

    for product in plan.products:
        if not is_allowed_amazon_product_url(product.url):
            errors.append(f"unsafe or unsupported product URL: {product.name}")
        if product.asin is None:
            warnings.append(
                f"ASIN could not be inferred for '{product.name}'. "
                "Short links and campaign links require manual confirmation."
            )
        if product.max_unit_price_jpy is None:
            warnings.append(f"No max_unit_price_jpy set for '{product.name}'.")

    if not plan.allocations and plan.recipients:
        warnings.append("Recipients exist, but no quantity allocations are defined.")
    if not plan.recipients:
        warnings.append("No recipients are defined. Output will be product-only.")

    return SafetyReport(ok=not errors, warnings=warnings, errors=errors)


def assert_safe_plan(plan: PurchasePlan) -> SafetyReport:
    """Raise ValueError if the plan violates the safety policy."""
    report = inspect_plan(plan)
    if not report.ok:
        raise ValueError("; ".join(report.errors))
    return report
