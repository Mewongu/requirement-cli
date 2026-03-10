"""Lint command for structural graph checks."""

from __future__ import annotations

import sys

import click

from rcli.cli import get_formatter, get_store
from rcli.search_engine import find_cycles


@click.command("lint")
@click.pass_context
def lint_cmd(ctx: click.Context) -> None:
    """Check for structural issues: dependency cycles and dangling references."""
    store = get_store(ctx)
    reqs = store.list_requirements()
    req_ids = {r.id for r in reqs}

    issues: list[dict] = []

    # Cycles in depends_on graph
    for cycle in find_cycles(reqs):
        issues.append({
            "type": "cycle",
            "ids": cycle,
            "message": f"Dependency cycle: {' → '.join(cycle)}",
        })

    # Dangling depends_on references
    for req in reqs:
        for dep in req.depends_on:
            if dep not in req_ids:
                issues.append({
                    "type": "dangling_dep",
                    "id": req.id,
                    "ref": dep,
                    "message": f"{req.id} depends_on {dep!r} which does not exist",
                })

    # Dangling parent references
    for req in reqs:
        if req.parent and req.parent not in req_ids:
            issues.append({
                "type": "dangling_parent",
                "id": req.id,
                "ref": req.parent,
                "message": f"{req.id} has parent {req.parent!r} which does not exist",
            })

    fmt = get_formatter(ctx)
    fmt.output_lint(issues)

    if issues:
        sys.exit(1)
