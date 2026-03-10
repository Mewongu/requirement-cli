"""Decision CRUD commands."""

from __future__ import annotations

from datetime import datetime, timezone

import click

from rcli.cli import get_formatter, get_store, error_exit
from rcli.commands.json_input import (
    parse_json_input, _pick,
    parse_metadata, apply_metadata_edits, apply_list_edits, validate_enum,
)
from rcli.models.decision import Decision, VALID_STATUSES
from rcli.search_engine import filter_items


@click.group()
def decision() -> None:
    """Manage design decisions."""
    pass


@decision.command("add")
@click.argument("title", required=False, default=None)
@click.option("--context", default=None, help="Decision context.")
@click.option("--decision", "decision_text", default=None, help="The decision made.")
@click.option("--rationale", default=None, help="Rationale for the decision.")
@click.option("--status", default=None, type=click.Choice(VALID_STATUSES), help="Status.")
@click.option("--link", multiple=True, help="Linked requirement ID (repeatable).")
@click.option("--meta", multiple=True, help="Metadata KEY=VALUE (repeatable).")
@click.option("--prefix", default=None, help="ID prefix (default: from metadata).")
@click.option("--json", "json_input", default=None, help="JSON object with fields (inline or '-' for stdin).")
@click.pass_context
def decision_add(ctx: click.Context, title: str | None, context: str | None,
                 decision_text: str | None, rationale: str | None, status: str | None,
                 link: tuple, meta: tuple, prefix: str | None,
                 json_input: str | None) -> None:
    """Add a new design decision."""
    json_data = parse_json_input(json_input, ctx)

    final_title = _pick(title, json_data, "title")
    if not final_title:
        error_exit(ctx, "Title is required (pass as argument or in --json).")
        return
    final_context = _pick(context, json_data, "context", "")
    final_decision = _pick(decision_text, json_data, "decision", "")
    final_rationale = _pick(rationale, json_data, "rationale", "")
    final_status = _pick(status, json_data, "status", "active")

    if not validate_enum(final_status, VALID_STATUSES, "status", ctx):
        return

    store = get_store(ctx)
    metadata = store.load_metadata()
    pfx = _pick(prefix, json_data, "prefix") or metadata.default_decision_prefix
    dec_id = store.next_id(pfx)

    # Linked requirements: CLI flags win, else JSON, else empty
    final_links = list(link) if link else (json_data.get("linked_requirements", []) if json_data else [])

    meta_dict = parse_metadata(meta, json_data, ctx)
    if meta_dict is None:
        return

    dec = Decision(
        id=dec_id,
        title=final_title,
        context=final_context,
        decision=final_decision,
        rationale=final_rationale,
        status=final_status,
        linked_requirements=final_links,
        metadata=meta_dict,
    )
    store.save_decision(dec)

    fmt = get_formatter(ctx)
    fmt.output_message(f"Created {dec_id}: {final_title}", dec)


@decision.command("show")
@click.argument("id")
@click.pass_context
def decision_show(ctx: click.Context, id: str) -> None:
    """Show a decision."""
    store = get_store(ctx)
    try:
        dec = store.load_decision(id)
    except FileNotFoundError:
        error_exit(ctx, f"Decision {id} not found.")
        return
    fmt = get_formatter(ctx)
    fmt.output_item(dec)


@decision.command("list")
@click.option("--status", multiple=True, type=click.Choice(VALID_STATUSES), help="Filter by status.")
@click.option("--label", multiple=True, help="Filter by linked requirement.")
@click.option("--prefix", default=None, help="Filter by ID prefix.")
@click.pass_context
def decision_list(ctx: click.Context, status: tuple, label: tuple,
                  prefix: str | None) -> None:
    """List decisions with optional filters."""
    store = get_store(ctx)
    decs = store.list_decisions()
    decs = filter_items(
        decs,
        statuses=list(status) or None,
        prefix=prefix,
    )
    fmt = get_formatter(ctx)
    fmt.output_list(decs)


@decision.command("edit")
@click.argument("id")
@click.option("--title", default=None, help="New title.")
@click.option("--context", default=None, help="New context.")
@click.option("--decision", "decision_text", default=None, help="New decision.")
@click.option("--rationale", default=None, help="New rationale.")
@click.option("--status", default=None, type=click.Choice(VALID_STATUSES), help="New status.")
@click.option("--add-link", multiple=True, help="Add linked requirement.")
@click.option("--remove-link", multiple=True, help="Remove linked requirement.")
@click.option("--set-meta", multiple=True, help="Set metadata KEY=VALUE.")
@click.option("--remove-meta", multiple=True, help="Remove metadata key.")
@click.option("--json", "json_input", default=None, help="JSON object with fields (inline or '-' for stdin).")
@click.pass_context
def decision_edit(ctx: click.Context, id: str, title: str | None, context: str | None,
                  decision_text: str | None, rationale: str | None, status: str | None,
                  add_link: tuple, remove_link: tuple,
                  set_meta: tuple, remove_meta: tuple, json_input: str | None) -> None:
    """Edit an existing decision."""
    json_data = parse_json_input(json_input, ctx)

    store = get_store(ctx)
    try:
        dec = store.load_decision(id)
    except FileNotFoundError:
        error_exit(ctx, f"Decision {id} not found.")
        return

    # Merge scalar fields: CLI > JSON > existing
    new_title = _pick(title, json_data, "title")
    if new_title is not None:
        dec.title = new_title
    new_context = _pick(context, json_data, "context")
    if new_context is not None:
        dec.context = new_context
    new_decision = _pick(decision_text, json_data, "decision")
    if new_decision is not None:
        dec.decision = new_decision
    new_rationale = _pick(rationale, json_data, "rationale")
    if new_rationale is not None:
        dec.rationale = new_rationale
    new_status = _pick(status, json_data, "status")
    if new_status is not None:
        if not validate_enum(new_status, VALID_STATUSES, "status", ctx):
            return
        dec.status = new_status

    # Linked requirements: CLI --add-link/--remove-link win; else JSON replaces list
    if add_link or remove_link:
        apply_list_edits(dec.linked_requirements, add_link, remove_link)
    elif json_data and "linked_requirements" in json_data:
        dec.linked_requirements = list(json_data["linked_requirements"])

    # Metadata: CLI --set-meta/--remove-meta win; else JSON replaces dict
    result = apply_metadata_edits(dec.metadata, set_meta, remove_meta, json_data, ctx)
    if result is None:
        return
    dec.metadata = result

    dec.updated_at = datetime.now(timezone.utc).isoformat()
    store.save_decision(dec)

    fmt = get_formatter(ctx)
    fmt.output_message(f"Updated {id}", dec)


@decision.command("delete")
@click.argument("id")
@click.option("--force", is_flag=True, help="Skip confirmation.")
@click.pass_context
def decision_delete(ctx: click.Context, id: str, force: bool) -> None:
    """Delete a decision."""
    store = get_store(ctx)
    try:
        dec = store.load_decision(id)
    except FileNotFoundError:
        error_exit(ctx, f"Decision {id} not found.")
        return

    root_fmt = ctx.find_root().params.get("format", "table")
    if not force and root_fmt != "json":
        if not click.confirm(f"Delete {id}: {dec.title}?"):
            click.echo("Cancelled.", err=True)
            return

    store.delete_decision(id)
    fmt = get_formatter(ctx)
    fmt.output_message(f"Deleted {id}")
