"""Init command - creates .rcli/ structure."""

from __future__ import annotations

from pathlib import Path

import click

from rcli.cli import get_formatter
from rcli.storage.store import Store
from rcli.skill import generate_skill_content


@click.command("init")
@click.option("--name", default="", help="Project name.")
@click.pass_context
def init_cmd(ctx: click.Context, name: str) -> None:
    """Initialize a .rcli/ directory in the current project."""
    rcli_path = Path.cwd() / ".rcli"
    store = Store(rcli_path)
    store.init_project(project_name=name)

    # Generate skill file
    claude_dir = Path.cwd() / ".claude" / "skills" / "rcli"
    claude_dir.mkdir(parents=True, exist_ok=True)
    skill_path = claude_dir / "SKILL.md"
    skill_path.write_text(generate_skill_content())

    fmt = get_formatter(ctx)
    fmt.output_message(
        f"Initialized rcli in {rcli_path}",
    )
