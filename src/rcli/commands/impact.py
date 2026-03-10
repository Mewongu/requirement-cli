"""Impact analysis command."""

from __future__ import annotations

import click

from rcli.cli import get_formatter, get_store, error_exit
from rcli.search_engine import find_impacted


@click.command("impact")
@click.argument("id")
@click.pass_context
def impact_cmd(ctx: click.Context, id: str) -> None:
    """Show all requirements that depend on ID (directly or transitively)."""
    store = get_store(ctx)
    reqs = store.list_requirements()
    impacted = find_impacted(reqs, id)
    fmt = get_formatter(ctx)
    if not impacted:
        fmt.output_message(f"No requirements depend on {id}.")
        return
    fmt.output_list(impacted)
