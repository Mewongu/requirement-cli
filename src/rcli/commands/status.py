"""Status dashboard command."""

from __future__ import annotations

from collections import Counter

import click

from rcli.cli import get_formatter, get_store


@click.command("status")
@click.pass_context
def status_cmd(ctx: click.Context) -> None:
    """Show project status dashboard."""
    store = get_store(ctx)
    metadata = store.load_metadata()
    reqs = store.list_requirements()
    decs = store.list_decisions()

    # Requirement counts by status
    req_status = Counter(r.status for r in reqs)
    # Decision counts by status
    dec_status = Counter(d.status for d in decs)
    # Label distribution
    label_counts = Counter(l for r in reqs for l in r.labels)
    # Priority distribution
    priority_counts = Counter(r.priority for r in reqs)
    # Prefix distribution
    prefix_counts = Counter(r.id.split("-")[0] for r in reqs)
    prefix_counts.update(d.id.split("-")[0] for d in decs)

    status_data = {
        "project_name": metadata.project_name,
        "sections": {
            "Requirements by Status": dict(req_status),
            "Decisions by Status": dict(dec_status),
            "Requirements by Priority": dict(priority_counts),
            "Labels": dict(label_counts),
            "Prefixes": dict(prefix_counts),
        },
        "totals": {
            "requirements": len(reqs),
            "decisions": len(decs),
        },
    }

    fmt = get_formatter(ctx)
    fmt.output_status(status_data)
