# Skill File Reference

`rcli init` generates a `SKILL.md` file following the [Agent Skills standard](https://agentskills.io/).

## Location

By default, the skill is written to:

```
.agents/skills/rcli/SKILL.md
```

This is the cross-client standard path scanned by Claude Code, OpenAI Codex, OpenCode, Gemini CLI, and other compatible agents.

Override with `--skill-dir`:

```bash
rcli init --name "project-name"
rcli init --name "project-name" --skill-dir .claude/skills
rcli init --name "project-name" --skill-dir /path/to/custom/skills
```

The `rcli/` subdirectory and `SKILL.md` file are always created inside the specified directory.

## Format

The generated `SKILL.md` follows the Agent Skills specification:

- YAML frontmatter with `name` and `description`
- Markdown body with commands and workflow guidelines

## Purpose

Instructs AI coding tools how to interact with the rcli database:
- Always use `--format json` for programmatic access
- Run `rcli init` if `.rcli/` doesn't exist
- Documents all commands with examples
- Provides workflow guidelines

## Regeneration

The skill file is regenerated on every `rcli init`. Re-run init to update it after upgrading rcli.
