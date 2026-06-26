"""FastAPI application for Amazon Business purchase automation preparation."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from purchase_prep_assistant.business_payloads import build_cart_add_items_payload, build_order_payload
from purchase_prep_assistant.exporters import write_all_exports
from purchase_prep_assistant.models import PurchasePlan
from purchase_prep_assistant.safety import SAFETY_POLICY_TEXT, inspect_plan

app = FastAPI(
    title="Amazon Business Purchase Automation Assistant",
    version="0.2.0",
    description="Purchase plan, customer delivery profile, and official API payload service.",
)


class ValidationResponse(BaseModel):
    ok: bool
    warnings: list[str]
    errors: list[str]


class ExportResponse(BaseModel):
    ok: bool
    output_dir: str
    files: list[str]
    warnings: list[str]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "business_api_prep"}


@app.get("/policy")
def policy() -> dict[str, str]:
    return {"scope": SAFETY_POLICY_TEXT}


@app.post("/validate-plan", response_model=ValidationResponse)
def validate_plan(plan: PurchasePlan) -> ValidationResponse:
    report = inspect_plan(plan)
    return ValidationResponse(ok=report.ok, warnings=report.warnings, errors=report.errors)


@app.post("/cart-add-items-payload")
def cart_add_items_payload(plan: PurchasePlan) -> dict[str, object]:
    report = inspect_plan(plan)
    if not report.ok:
        raise HTTPException(status_code=400, detail={"errors": report.errors})
    return build_cart_add_items_payload(plan)


@app.post("/order-payload/{recipient_label}")
def order_payload(recipient_label: str, plan: PurchasePlan) -> dict[str, object]:
    report = inspect_plan(plan)
    if not report.ok:
        raise HTTPException(status_code=400, detail={"errors": report.errors})
    return build_order_payload(plan, recipient_label)


@app.post("/export-plan", response_model=ExportResponse)
def export_plan(plan: PurchasePlan) -> ExportResponse:
    report = inspect_plan(plan)
    if not report.ok:
        raise HTTPException(status_code=400, detail={"errors": report.errors})
    output_dir = Path(tempfile.mkdtemp(prefix="purchase-prep-"))
    files = write_all_exports(plan, output_dir)
    return ExportResponse(
        ok=True,
        output_dir=str(output_dir),
        files=[str(path) for path in files],
        warnings=report.warnings,
    )
