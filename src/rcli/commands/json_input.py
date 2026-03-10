"""Shared helpers for --json input on add/edit commands."""

from __future__ import annotations

import json
import sys

import click


def parse_json_input(json_str: str | None, ctx: click.Context) -> dict | None:
    """Parse --json value (inline string or '-' for stdin).

    Returns parsed dict or None if json_str is None.
    Calls error_exit on invalid input.
    """
    if json_str is None:
        return None

    from rcli.cli import error_exit

    if json_str == "-":
        raw = sys.stdin.read()
    else:
        raw = json_str

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        error_exit(ctx, f"Invalid JSON: {e}")
        return None

    if not isinstance(data, dict):
        error_exit(ctx, "JSON input must be an object, not an array or scalar.")
        return None

    return data


def _pick(cli_value: object, json_data: dict | None, key: str, default: object = None) -> object:
    """Resolve field priority: explicit CLI value > JSON value > default.

    A CLI value is considered "set" if it is not None.
    """
    if cli_value is not None:
        return cli_value
    if json_data is not None and key in json_data:
        return json_data[key]
    return default


def _parse_kv_meta(meta: tuple, ctx: click.Context) -> dict | None:
    """Parse KEY=VALUE pairs into a dict. Returns None (after error_exit) on bad format."""
    result: dict = {}
    for m in meta:
        if "=" not in m:
            from rcli.cli import error_exit
            error_exit(ctx, f"Invalid metadata format: {m}. Use KEY=VALUE.")
            return None
        k, v = m.split("=", 1)
        result[k] = v
    return result


def parse_metadata(meta: tuple, json_data: dict | None, ctx: click.Context) -> dict | None:
    """Build metadata dict from JSON base + CLI KEY=VALUE overrides.
    Returns None (after error_exit) on invalid format."""
    meta_dict: dict = {}
    if json_data and "metadata" in json_data:
        meta_dict.update(json_data["metadata"])
    parsed = _parse_kv_meta(meta, ctx)
    if parsed is None:
        return None
    meta_dict.update(parsed)
    return meta_dict


def apply_metadata_edits(
    existing: dict,
    set_meta: tuple,
    remove_meta: tuple,
    json_data: dict | None,
    ctx: click.Context,
) -> dict | None:
    """Apply CLI mutations or JSON replacement to a metadata dict.
    Returns updated dict, or None (after error_exit) on parse error."""
    if set_meta or remove_meta:
        parsed = _parse_kv_meta(set_meta, ctx)
        if parsed is None:
            return None
        existing.update(parsed)
        for k in remove_meta:
            existing.pop(k, None)
        return existing
    if json_data and "metadata" in json_data:
        return dict(json_data["metadata"])
    return existing


def apply_list_edits(items: list, add: tuple, remove: tuple) -> None:
    """Add/remove items in a list in-place."""
    for item in add:
        if item not in items:
            items.append(item)
    for item in remove:
        if item in items:
            items.remove(item)


def validate_enum(value: str, valid_values: list[str], field_name: str, ctx: click.Context) -> bool:
    """Return True if valid; call error_exit and return False if not."""
    if value not in valid_values:
        from rcli.cli import error_exit
        error_exit(ctx, f"Invalid {field_name} '{value}'. Choose from: {', '.join(valid_values)}.")
        return False
    return True
