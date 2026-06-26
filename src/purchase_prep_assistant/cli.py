"""Command-line interface for purchase preparation."""

from __future__ import annotations

from pathlib import Path

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from purchase_prep_assistant.api import app as fastapi_app
from purchase_prep_assistant.exporters import load_plan, write_all_exports
from purchase_prep_assistant.safety import inspect_plan

app = typer.Typer(help="Prepare Amazon purchase plans for manual review.")
console = Console()


@app.command()
def validate(input: Path = typer.Option(..., "--input", "-i", help="Purchase plan JSON path")) -> None:
    """Validate a purchase plan without creating output files."""
    plan = load_plan(input)
    report = inspect_plan(plan)

    table = Table(title=f"Validation: {plan.project_name}")
    table.add_column("Type")
    table.add_column("Message")

    for warning in report.warnings:
        table.add_row("warning", warning)
    for error in report.errors:
        table.add_row("error", error)
    if not report.warnings and not report.errors:
        table.add_row("ok", "No warnings or errors")

    console.print(table)
    if not report.ok:
        raise typer.Exit(code=1)


@app.command("export")
def export_outputs(
    input: Path = typer.Option(..., "--input", "-i", help="Purchase plan JSON path"),
    output: Path = typer.Option(Path("outputs"), "--output", "-o", help="Output directory"),
) -> None:
    """Export CSV, Excel, checklist, and official API template files."""
    plan = load_plan(input)
    files = write_all_exports(plan, output)
    console.print(f"[green]Created {len(files)} file(s) in {output}[/green]")
    for file in files:
        console.print(f"- {file}")


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Bind host"),
    port: int = typer.Option(8000, help="Bind port"),
) -> None:
    """Run the FastAPI service locally."""
    uvicorn.run(fastapi_app, host=host, port=port)


if __name__ == "__main__":
    app()
