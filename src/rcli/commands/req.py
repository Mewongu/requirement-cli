"""Requirement CRUD commands."""

from __future__ import annotations

from datetime import datetime, timezone

import click

from rcli.cli import get_formatter, get_store, error_exit
from rcli.commands.json_input import (
    parse_json_input, _pick,
    parse_metadata, apply_metadata_edits, apply_list_edits, validate_enum,
)
from rcli.models.requirement import Requirement, VALID_STATUSES, VALID_PRIORITIES
from rcli.search_engine import filter_items


@click.group()
def req() -> None:
    """Manage requirements."""
    pass


@req.command("add")
@click.argument("title", required=False, default=None)
@click.option("--description", default=None, help="Requirement description.")
@click.option("--status", default=None, type=click.Choice(VALID_STATUSES), help="Status.")
@click.option("--priority", default=None, type=click.Choice(VALID_PRIORITIES), help="Priority.")
@click.option("--parent", default=None, help="Parent requirement ID.")
@click.option("--label", multiple=True, help="Labels (repeatable).")
@click.option("--meta", multiple=True, help="Metadata KEY=VALUE (repeatable).")
@click.option("--prefix", default=None, help="ID prefix (default: from metadata).")
@click.option("--json", "json_input", default=None, help="JSON object with fields (inline or '-' for stdin).")
@click.pass_context
def req_add(ctx: click.Context, title: str | None, description: str | None,
            status: str | None, priority: str | None, parent: str | None,
            label: tuple, meta: tuple, prefix: str | None,
            json_input: str | None) -> None:
    """Add a new requirement."""
    json_data = parse_json_input(json_input, ctx)

    final_title = _pick(title, json_data, "title")
    if not final_title:
        error_exit(ctx, "Title is required (pass as argument or in --json).")
        return
    final_description = _pick(description, json_data, "description", "")
    final_status = _pick(status, json_data, "status", "draft")
    final_priority = _pick(priority, json_data, "priority", "medium")
    final_parent = _pick(parent, json_data, "parent")

    # Validate enum values that may come from JSON (Click only validates CLI-sourced values)
    if not validate_enum(final_status, VALID_STATUSES, "status", ctx):
        return
    if not validate_enum(final_priority, VALID_PRIORITIES, "priority", ctx):
        return

    store = get_store(ctx)
    metadata = store.load_metadata()
    pfx = _pick(prefix, json_data, "prefix") or metadata.default_requirement_prefix
    req_id = store.next_id(pfx)

    # Labels: CLI flags win, else JSON, else empty
    final_labels = list(label) if label else (json_data.get("labels", []) if json_data else [])

    meta_dict = parse_metadata(meta, json_data, ctx)
    if meta_dict is None:
        return

    requirement = Requirement(
        id=req_id,
        title=final_title,
        description=final_description,
        status=final_status,
        priority=final_priority,
        parent=final_parent,
        labels=final_labels,
        metadata=meta_dict,
    )
    store.save_requirement(requirement)

    fmt = get_formatter(ctx)
    fmt.output_message(f"Created {req_id}: {final_title}", requirement)


@req.command("show")
@click.argument("id")
@click.pass_context
def req_show(ctx: click.Context, id: str) -> None:
    """Show a requirement."""
    store = get_store(ctx)
    try:
        requirement = store.load_requirement(id)
    except FileNotFoundError:
        error_exit(ctx, f"Requirement {id} not found.")
        return
    fmt = get_formatter(ctx)
    fmt.output_item(requirement)


@req.command("list")
@click.option("--status", multiple=True, type=click.Choice(VALID_STATUSES), help="Filter by status (repeatable).")
@click.option("--label", multiple=True, help="Filter by label (repeatable).")
@click.option("--prefix", default=None, help="Filter by ID prefix.")
@click.option("--parent", default=None, help="Filter by parent ID.")
@click.option("--priority", multiple=True, type=click.Choice(VALID_PRIORITIES), help="Filter by priority (repeatable).")
@click.option("--orphans", is_flag=True, help="Show only root requirements (no parent).")
@click.pass_context
def req_list(ctx: click.Context, status: tuple, label: tuple, prefix: str | None,
             parent: str | None, priority: tuple, orphans: bool) -> None:
    """List requirements with optional filters."""
    store = get_store(ctx)
    reqs = store.list_requirements()
    reqs = filter_items(
        reqs,
        statuses=list(status) or None,
        labels=list(label) or None,
        prefix=prefix,
        parent=parent,
        priorities=list(priority) or None,
        orphans=orphans,
    )
    fmt = get_formatter(ctx)
    fmt.output_list(reqs)


@req.command("edit")
@click.argument("id")
@click.option("--title", default=None, help="New title.")
@click.option("--description", default=None, help="New description.")
@click.option("--status", default=None, type=click.Choice(VALID_STATUSES), help="New status.")
@click.option("--priority", default=None, type=click.Choice(VALID_PRIORITIES), help="New priority.")
@click.option("--parent", default=None, help="Set parent requirement ID.")
@click.option("--clear-parent", is_flag=True, help="Remove parent.")
@click.option("--add-label", multiple=True, help="Add label.")
@click.option("--remove-label", multiple=True, help="Remove label.")
@click.option("--set-meta", multiple=True, help="Set metadata KEY=VALUE.")
@click.option("--remove-meta", multiple=True, help="Remove metadata key.")
@click.option("--json", "json_input", default=None, help="JSON object with fields (inline or '-' for stdin).")
@click.pass_context
def req_edit(ctx: click.Context, id: str, title: str | None, description: str | None,
             status: str | None, priority: str | None, parent: str | None,
             clear_parent: bool, add_label: tuple, remove_label: tuple,
             set_meta: tuple, remove_meta: tuple, json_input: str | None) -> None:
    """Edit an existing requirement."""
    json_data = parse_json_input(json_input, ctx)

    store = get_store(ctx)
    try:
        requirement = store.load_requirement(id)
    except FileNotFoundError:
        error_exit(ctx, f"Requirement {id} not found.")
        return

    # Merge scalar fields: CLI > JSON > existing
    new_title = _pick(title, json_data, "title")
    if new_title is not None:
        requirement.title = new_title
    new_desc = _pick(description, json_data, "description")
    if new_desc is not None:
        requirement.description = new_desc
    new_status = _pick(status, json_data, "status")
    if new_status is not None:
        if not validate_enum(new_status, VALID_STATUSES, "status", ctx):
            return
        requirement.status = new_status
    new_priority = _pick(priority, json_data, "priority")
    if new_priority is not None:
        if not validate_enum(new_priority, VALID_PRIORITIES, "priority", ctx):
            return
        requirement.priority = new_priority
    new_parent = _pick(parent, json_data, "parent")
    if new_parent is not None:
        requirement.parent = new_parent
    if clear_parent:
        requirement.parent = None

    # Labels: CLI --add-label/--remove-label win; else JSON replaces list
    if add_label or remove_label:
        apply_list_edits(requirement.labels, add_label, remove_label)
    elif json_data and "labels" in json_data:
        requirement.labels = list(json_data["labels"])

    # Metadata: CLI --set-meta/--remove-meta win; else JSON replaces dict
    result = apply_metadata_edits(requirement.metadata, set_meta, remove_meta, json_data, ctx)
    if result is None:
        return
    requirement.metadata = result

    requirement.updated_at = datetime.now(timezone.utc).isoformat()
    store.save_requirement(requirement)

    fmt = get_formatter(ctx)
    fmt.output_message(f"Updated {id}", requirement)


@req.command("delete")
@click.argument("id")
@click.option("--force", is_flag=True, help="Skip confirmation.")
@click.pass_context
def req_delete(ctx: click.Context, id: str, force: bool) -> None:
    """Delete a requirement."""
    store = get_store(ctx)
    try:
        requirement = store.load_requirement(id)
    except FileNotFoundError:
        error_exit(ctx, f"Requirement {id} not found.")
        return

    root_fmt = ctx.find_root().params.get("format", "table")
    if not force and root_fmt != "json":
        if not click.confirm(f"Delete {id}: {requirement.title}?"):
            click.echo("Cancelled.", err=True)
            return

    store.delete_requirement(id)
    fmt = get_formatter(ctx)
    fmt.output_message(f"Deleted {id}")


@req.command("tree")
@click.argument("id", required=False, default=None)
@click.pass_context
def req_tree(ctx: click.Context, id: str | None) -> None:
    """Show requirement hierarchy as a tree."""
    store = get_store(ctx)
    reqs = store.list_requirements()

    if id is not None:
        # Show subtree from given root
        from rcli.search_engine import get_subtree_ids
        subtree_ids = get_subtree_ids(reqs, id)
        reqs = [r for r in reqs if r.id in subtree_ids]
        # Re-root: the specified ID becomes a root node
        for r in reqs:
            if r.id == id:
                r.parent = None

    fmt = get_formatter(ctx)
    fmt.output_tree(reqs)
