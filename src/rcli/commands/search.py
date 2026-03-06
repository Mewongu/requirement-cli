"""Search command."""

from __future__ import annotations

import click

from rcli.cli import get_formatter, get_store
from rcli.search_engine import search, filter_items


@click.command("search")
@click.argument("query")
@click.option("--type", "item_type", type=click.Choice(["req", "decision", "all"]), default="all", help="Item type to search.")
@click.option("--status", multiple=True, help="Filter by status.")
@click.option("--label", multiple=True, help="Filter by label.")
@click.option("--prefix", default=None, help="Filter by ID prefix.")
@click.pass_context
def search_cmd(ctx: click.Context, query: str, item_type: str, status: tuple,
               label: tuple, prefix: str | None) -> None:
    """Search requirements and decisions."""
    store = get_store(ctx)
    items = []

    if item_type in ("req", "all"):
        items.extend(store.list_requirements())
    if item_type in ("decision", "all"):
        items.extend(store.list_decisions())

    items = filter_items(
        items,
        statuses=list(status) or None,
        labels=list(label) or None,
        prefix=prefix,
    )

    results = search(items, query)
    fmt = get_formatter(ctx)
    fmt.output_search(results)
