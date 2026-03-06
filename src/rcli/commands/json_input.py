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
