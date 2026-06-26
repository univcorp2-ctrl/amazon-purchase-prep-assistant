"""Export purchase preparation plans to review-friendly files."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

from purchase_prep_assistant.models import PurchasePlan
from purchase_prep_assistant.safety import SAFETY_POLICY_TEXT, assert_safe_plan, inspect_plan


def load_plan(path: str | Path) -> PurchasePlan:
    """Load a purchase plan from JSON."""
    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)
    return PurchasePlan.model_validate(data)


def write_csv(plan: PurchasePlan, output_path: str | Path) -> Path:
    """Write item-level purchase preparation data to CSV."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "project_name",
                "product_name",
                "url",
                "asin",
                "quantity",
                "max_unit_price_jpy",
                "note",
            ],
        )
        writer.writeheader()
        for product in plan.products:
            writer.writerow(
                {
                    "project_name": plan.project_name,
                    "product_name": product.name,
                    "url": product.url,
                    "asin": product.asin or "",
                    "quantity": product.quantity,
                    "max_unit_price_jpy": product.max_unit_price_jpy or "",
                    "note": product.note,
                }
            )
    return output


def _add_header(ws: Any, values: list[str]) -> None:
    ws.append(values)
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2E7D32", end_color="2E7D32", fill_type="solid")


def write_excel(plan: PurchasePlan, output_path: str | Path) -> Path:
    """Write an Excel workbook with products, recipients, allocations, and safety notes."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    report = inspect_plan(plan)
    workbook = Workbook()

    summary = workbook.active
    summary.title = "Summary"
    _add_header(summary, ["Field", "Value"])
    summary.append(["Project", plan.project_name])
    summary.append(["Safety mode", plan.safety_mode])
    summary.append(["Safety OK", "yes" if report.ok else "no"])
    summary.append(["Warnings", " | ".join(report.warnings) if report.warnings else "none"])

    items = workbook.create_sheet("Items")
    _add_header(items, ["Product", "URL", "ASIN", "Quantity", "Max unit price JPY", "Note"])
    for product in plan.products:
        items.append(
            [
                product.name,
                product.url,
                product.asin or "",
                product.quantity,
                product.max_unit_price_jpy or "",
                product.note,
            ]
        )

    recipients = workbook.create_sheet("Recipients")
    _add_header(
        recipients,
        ["Label", "Name", "Postal code", "Prefecture", "City", "Line1", "Line2", "Phone", "Note"],
    )
    for recipient in plan.recipients:
        recipients.append(
            [
                recipient.label,
                recipient.recipient_name,
                recipient.postal_code,
                recipient.prefecture,
                recipient.city,
                recipient.line1,
                recipient.line2,
                recipient.phone,
                recipient.note,
            ]
        )

    allocations = workbook.create_sheet("Allocations")
    _add_header(allocations, ["Product", "Recipient", "Quantity"])
    for allocation in plan.allocations:
        allocations.append([allocation.product_name, allocation.recipient_label, allocation.quantity])

    safety = workbook.create_sheet("Safety")
    _add_header(safety, ["Policy"])
    for line in SAFETY_POLICY_TEXT.splitlines():
        safety.append([line])
    for warning in report.warnings:
        safety.append([f"Warning: {warning}"])

    for worksheet in workbook.worksheets:
        for column_cells in worksheet.columns:
            max_length = max(len(str(cell.value or "")) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = min(max_length + 2, 80)

    workbook.save(output)
    return output


def write_checklist(plan: PurchasePlan, output_path: str | Path) -> Path:
    """Write a human-readable manual checkout checklist."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = inspect_plan(plan)

    lines = [
        f"# Manual purchase checklist: {plan.project_name}",
        "",
        "This file is for human review only. It is not a checkout automation script.",
        "",
        "## Safety policy",
        SAFETY_POLICY_TEXT,
        "",
        "## Products",
    ]
    for index, product in enumerate(plan.products, start=1):
        lines.extend(
            [
                f"{index}. {product.name}",
                f"   - URL: {product.url}",
                f"   - ASIN: {product.asin or 'manual confirmation required'}",
                f"   - Quantity: {product.quantity}",
                f"   - Max unit price JPY: {product.max_unit_price_jpy or 'not set'}",
                f"   - Note: {product.note or '-'}",
            ]
        )

    lines.extend(["", "## Recipient allocations"])
    if plan.allocations:
        for allocation in plan.allocations:
            lines.append(
                f"- {allocation.product_name}: {allocation.quantity} item(s) -> {allocation.recipient_label}"
            )
    else:
        lines.append("- No allocations defined.")

    lines.extend(["", "## Warnings"])
    if report.warnings:
        lines.extend([f"- {warning}" for warning in report.warnings])
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Manual final review",
            "- Confirm product title, seller, price, quantity, delivery date, and return policy on Amazon.",
            "- Confirm the delivery address manually inside the official Amazon or Amazon Business interface.",
            "- Confirm payment method and organization approval rules manually.",
            "- Do not use browser automation or bot-detection evasion to reach checkout.",
        ]
    )

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def build_amazon_business_cart_template(plan: PurchasePlan) -> dict[str, Any]:
    """Build a dry-run template for official Amazon Business API integration.

    The template is intentionally not executable. Offer IDs, OAuth tokens, and
    buying-group configuration must come from Amazon Business official setup.
    """
    return {
        "mode": "dry_run_template_only",
        "notice": "Use only with authorized Amazon Business API access. This file does not place orders.",
        "cart_api": {
            "operation_hint": "POST /cart/2025-04-30/carts/{cartId}/items",
            "items": [
                {
                    "asin": product.asin or "MANUAL_ASIN_REQUIRED",
                    "offerId": "OFFICIAL_API_OFFER_ID_REQUIRED",
                    "quantity": product.quantity,
                    "maxUnitPriceJpy": product.max_unit_price_jpy,
                    "sourceUrl": product.url,
                }
                for product in plan.products
            ],
        },
        "ordering_api": {
            "operation_hint": "POST /ordering/2022-10-30/orders",
            "requires": [
                "OAuth/Login with Amazon authorization",
                "AmazonBusinessOrderPlacement role",
                "BuyingGroup reference",
                "configured payment method",
                "configured shipping addresses",
                "organization approval rules",
            ],
        },
    }


def write_business_api_template(plan: PurchasePlan, output_path: str | Path) -> Path:
    """Write a JSON template for official Amazon Business API integration design."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(build_amazon_business_cart_template(plan), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output


def write_all_exports(plan: PurchasePlan, output_dir: str | Path) -> list[Path]:
    """Validate a plan and write all supported outputs."""
    assert_safe_plan(plan)
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    safe_name = plan.project_name.replace(" ", "-").lower()
    return [
        write_csv(plan, directory / f"{safe_name}.csv"),
        write_excel(plan, directory / f"{safe_name}.xlsx"),
        write_checklist(plan, directory / f"{safe_name}-checklist.txt"),
        write_business_api_template(plan, directory / f"{safe_name}-amazon-business-template.json"),
    ]
