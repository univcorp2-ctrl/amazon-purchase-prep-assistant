"""Command-line interface for Amazon Business purchase automation preparation."""

from __future__ import annotations

import json
from pathlib import Path

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from purchase_prep_assistant.api import app as fastapi_app
from purchase_prep_assistant.business_api import AmazonBusinessClient, AmazonBusinessConfig
from purchase_prep_assistant.business_payloads import build_cart_add_items_payload, build_order_payload
from purchase_prep_assistant.exporters import load_plan, write_all_exports
from purchase_prep_assistant.safety import inspect_plan

app = typer.Typer(help="Prepare Amazon Business purchase plans and official API payloads.")
console = Console()


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


@app.command("business-cart-payload")
def business_cart_payload(
    input: Path = typer.Option(..., "--input", "-i", help="Purchase plan JSON path"),
    output: Path = typer.Option(Path("outputs/cart-add-items.json"), "--output", "-o"),
) -> None:
    """Generate a Cart API addItems JSON payload."""
    plan = load_plan(input)
    payload = build_cart_add_items_payload(plan)
    _write_json(output, payload)
    console.print(f"[green]Wrote Cart API payload:[/green] {output}")


@app.command("business-order-payload")
def business_order_payload(
    input: Path = typer.Option(..., "--input", "-i", help="Purchase plan JSON path"),
    recipient_label: str = typer.Option(..., "--recipient-label", help="Recipient label"),
    output: Path = typer.Option(Path("outputs/order-payload.json"), "--output", "-o"),
    external_id: str | None = typer.Option(None, "--external-id"),
    trial: bool = typer.Option(True, "--trial/--no-trial"),
) -> None:
    """Generate an Ordering API JSON payload for one recipient."""
    plan = load_plan(input)
    payload = build_order_payload(plan, recipient_label, external_id=external_id, trial=trial)
    _write_json(output, payload)
    console.print(f"[green]Wrote Ordering API payload:[/green] {output}")


@app.command("business-list-carts")
def business_list_carts(
    region: str = typer.Option("JP", "--region"),
    live: bool = typer.Option(False, "--live"),
) -> None:
    """List Amazon Business carts through the official Cart API."""
    if not live:
        console.print("Set --live after configuring Amazon Business API environment variables.")
        return
    with AmazonBusinessClient(AmazonBusinessConfig.from_env()) as client:
        console.print_json(data=client.list_carts(region=region))


@app.command("business-add-items")
def business_add_items(
    input: Path = typer.Option(..., "--input", "-i"),
    cart_id: str = typer.Option(..., "--cart-id"),
    region: str = typer.Option("JP", "--region"),
    live: bool = typer.Option(False, "--live"),
) -> None:
    """Add plan items to an Amazon Business cart through the official Cart API."""
    plan = load_plan(input)
    payload = build_cart_add_items_payload(plan)
    if not live:
        console.print_json(data=payload)
        return
    with AmazonBusinessClient(AmazonBusinessConfig.from_env()) as client:
        console.print_json(data=client.add_items(cart_id, payload, region=region))


@app.command("business-place-order")
def business_place_order(
    payload: Path = typer.Option(..., "--payload", help="Ordering API payload JSON"),
    live: bool = typer.Option(False, "--live"),
) -> None:
    """Submit an Ordering API payload through the official Ordering API."""
    data = json.loads(payload.read_text(encoding="utf-8"))
    if not live:
        console.print_json(data=data)
        return
    with AmazonBusinessClient(AmazonBusinessConfig.from_env()) as client:
        console.print_json(data=client.place_order(data))


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Bind host"),
    port: int = typer.Option(8000, help="Bind port"),
) -> None:
    """Run the FastAPI service locally."""
    uvicorn.run(fastapi_app, host=host, port=port)


if __name__ == "__main__":
    app()
