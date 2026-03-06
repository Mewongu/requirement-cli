# Requirement CLI

A CLI tool for managing project requirements and design decisions. Stores data as individual JSON files in `.rcli/` for git merge-friendliness, and integrates with Claude Code through a generated skill file.

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick Start

```bash
# Initialize in your project
rcli init --name "my-project"

# Add requirements
rcli req add "User authentication" --description "Users must be able to log in" --priority high --label mvp
rcli req add "OAuth support" --description "Support Google OAuth" --parent REQ-1 --label mvp

# Add design decisions
rcli decision add "Use JWT tokens" \
  --context "Need stateless auth" \
  --decision "JWT with refresh tokens" \
  --rationale "Scalable, no server-side session storage" \
  --link REQ-1

# Browse and search
rcli req list --status draft --label mvp
rcli req tree
rcli search "auth"
rcli status

# Export
rcli export --format markdown --output requirements.md
```

## Output Formats

All list/show commands support `--format` with: `table` (default), `json`, `markdown`, `html`.

## Storage

Data is stored in `.rcli/` as individual JSON files:
- `.rcli/metadata.json` - project metadata and ID counters
- `.rcli/requirements/REQ-1.json` - one file per requirement
- `.rcli/decisions/ADR-1.json` - one file per decision

## Claude Code Integration

This repo ships a [skill file](.claude/skills/rcli/SKILL.md) that gives Claude Code the `/rcli` command. When you clone this repo, the skill is available immediately.

For other projects, run `rcli init --name "project-name"` to generate `.claude/skills/rcli/SKILL.md` in that project. The skill teaches Claude to use `rcli` commands automatically when you discuss requirements or decisions.
