"""FastAPI application for safe purchase preparation."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from purchase_prep_assistant.exporters import write_all_exports
from purchase_prep_assistant.models import PurchasePlan
from purchase_prep_assistant.safety import SAFETY_POLICY_TEXT, inspect_plan

app = FastAPI(
    title="Amazon Purchase Prep Assistant",
    version="0.1.0",
    description="Manual-review-only purchase preparation service.",
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
    return {"status": "ok", "mode": "manual_review_only"}


@app.get("/policy")
def policy() -> dict[str, str]:
    return {"policy": SAFETY_POLICY_TEXT}


@app.post("/validate-plan", response_model=ValidationResponse)
def validate_plan(plan: PurchasePlan) -> ValidationResponse:
    report = inspect_plan(plan)
    return ValidationResponse(ok=report.ok, warnings=report.warnings, errors=report.errors)


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
