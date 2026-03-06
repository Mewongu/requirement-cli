"""Export command."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from rcli.cli import get_store, error_exit
from rcli.search_engine import filter_items, get_subtree_ids
from rcli.formatters.markdown import MarkdownFormatter
from rcli.formatters.html import HtmlFormatter


@click.command("export")
@click.option("--type", "item_type", type=click.Choice(["req", "decision", "all"]), default="all", help="Item type to export.")
@click.option("--status", multiple=True, help="Filter by status.")
@click.option("--label", multiple=True, help="Filter by label.")
@click.option("--prefix", default=None, help="Filter by ID prefix.")
@click.option("--parent", default=None, help="Export subtree from parent ID.")
@click.option("--format", "fmt", type=click.Choice(["markdown", "html", "json"]), default="markdown", help="Export format.")
@click.option("--output", default=None, help="Output file (default: stdout).")
@click.pass_context
def export_cmd(ctx: click.Context, item_type: str, status: tuple, label: tuple,
               prefix: str | None, parent: str | None, fmt: str, output: str | None) -> None:
    """Export requirements and decisions."""
    store = get_store(ctx)

    reqs = []
    decs = []

    if item_type in ("req", "all"):
        reqs = store.list_requirements()
        if parent:
            subtree_ids = get_subtree_ids(reqs, parent)
            reqs = [r for r in reqs if r.id in subtree_ids]
        reqs = filter_items(
            reqs,
            statuses=list(status) or None,
            labels=list(label) or None,
            prefix=prefix,
        )
    if item_type in ("decision", "all"):
        decs = store.list_decisions()
        decs = filter_items(
            decs,
            statuses=list(status) or None,
            prefix=prefix,
        )

    if fmt == "markdown":
        content = MarkdownFormatter().format_export(reqs, decs)
    elif fmt == "html":
        content = HtmlFormatter().format_export(reqs, decs)
    elif fmt == "json":
        data = {
            "requirements": [r.to_dict() for r in reqs],
            "decisions": [d.to_dict() for d in decs],
        }
        content = json.dumps(data, indent=2) + "\n"
    else:
        error_exit(ctx, f"Unknown format: {fmt}")
        return

    if output:
        Path(output).write_text(content)
        click.echo(f"Exported to {output}", err=True)
    else:
        sys.stdout.write(content)
