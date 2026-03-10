"""Init command - creates .rcli/ structure."""

from __future__ import annotations

from pathlib import Path

import click

from rcli.cli import get_formatter
from rcli.storage.store import Store
from rcli.skill import generate_skill_content

DEFAULT_SKILL_DIR = ".agents/skills"


@click.command("init")
@click.option("--name", default="", help="Project name.")
@click.option(
    "--skill-dir",
    default=DEFAULT_SKILL_DIR,
    show_default=True,
    help="Directory to write the SKILL.md file into (e.g. .agents/skills or .claude/skills).",
)
@click.pass_context
def init_cmd(ctx: click.Context, name: str, skill_dir: str) -> None:
    """Initialize a .rcli/ directory in the current project."""
    rcli_path = Path.cwd() / ".rcli"
    store = Store(rcli_path)
    store.init_project(project_name=name)

    skill_path = Path.cwd() / skill_dir / "rcli"
    skill_path.mkdir(parents=True, exist_ok=True)
    (skill_path / "SKILL.md").write_text(generate_skill_content())

    fmt = get_formatter(ctx)
    fmt.output_message(
        f"Initialized rcli in {rcli_path}",
    )
