"""Init command - creates .rcli/ structure."""

from __future__ import annotations

from pathlib import Path

import click

from rcli.cli import get_formatter
from rcli.storage.store import Store
from rcli.skill import (
    generate_skill_content,
    generate_agents_content,
    generate_opencode_content,
    merge_into_existing,
)

TOOL_CHOICES = ("claude", "codex", "opencode")


@click.command("init")
@click.option("--name", default="", help="Project name.")
@click.option(
    "--tool",
    "tools",
    multiple=True,
    type=click.Choice(TOOL_CHOICES, case_sensitive=False),
    help="AI tools to generate instruction files for. Defaults to claude only. Can be specified multiple times.",
)
@click.pass_context
def init_cmd(ctx: click.Context, name: str, tools: tuple[str, ...]) -> None:
    """Initialize a .rcli/ directory in the current project."""
    rcli_path = Path.cwd() / ".rcli"
    store = Store(rcli_path)
    store.init_project(project_name=name)

    if not tools:
        tools = ("claude",)

    for tool in tools:
        if tool == "claude":
            claude_dir = Path.cwd() / ".claude" / "skills" / "rcli"
            claude_dir.mkdir(parents=True, exist_ok=True)
            (claude_dir / "SKILL.md").write_text(generate_skill_content())
        elif tool == "codex":
            _write_or_merge(Path.cwd() / "AGENTS.md", generate_agents_content())
        elif tool == "opencode":
            _write_or_merge(Path.cwd() / "OPENCODE.md", generate_opencode_content())

    fmt = get_formatter(ctx)
    fmt.output_message(
        f"Initialized rcli in {rcli_path}",
    )


def _write_or_merge(path: Path, content: str) -> None:
    """Write content to a file, merging with existing content if present."""
    if path.exists():
        existing = path.read_text()
        path.write_text(merge_into_existing(existing, content))
    else:
        path.write_text(content)
