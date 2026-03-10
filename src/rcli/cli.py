"""CLI entry point and top-level group."""

from __future__ import annotations

import sys

import click

from rcli.storage.paths import find_rcli_root
from rcli.storage.store import Store
from rcli.formatters.table import TableFormatter
from rcli.formatters.json_fmt import JsonFormatter
from rcli.formatters.markdown import MarkdownFormatter
from rcli.formatters.html import HtmlFormatter


FORMATTERS = {
    "table": TableFormatter,
    "json": JsonFormatter,
    "markdown": MarkdownFormatter,
    "html": HtmlFormatter,
}


def get_formatter(ctx: click.Context):
    """Get the formatter instance from the context."""
    fmt = ctx.find_root().params.get("format", "json")
    return FORMATTERS[fmt]()


def get_store(ctx: click.Context) -> Store:
    """Find and return the Store, or exit with an error."""
    root = find_rcli_root()
    if root is None:
        click.echo("Error: No .rcli/ directory found. Run 'rcli init' first.", err=True)
        ctx.exit(1)
    return Store(root)


def error_exit(ctx: click.Context, message: str) -> None:
    """Print error to stderr and exit."""
    click.echo(f"Error: {message}", err=True)
    ctx.exit(1)


@click.group()
@click.option("--format", "format", type=click.Choice(["table", "json", "markdown", "html"]), default="json", help="Output format.")
@click.pass_context
def cli(ctx: click.Context, format: str) -> None:
    """rcli - Requirement CLI."""
    ctx.ensure_object(dict)
    ctx.obj["format"] = format


# Import and register subcommands
from rcli.commands.init import init_cmd
from rcli.commands.req import req
from rcli.commands.decision import decision
from rcli.commands.search import search_cmd
from rcli.commands.export import export_cmd
from rcli.commands.status import status_cmd

cli.add_command(init_cmd, "init")
cli.add_command(req, "req")
cli.add_command(decision, "decision")
cli.add_command(search_cmd, "search")
cli.add_command(export_cmd, "export")
cli.add_command(status_cmd, "status")
