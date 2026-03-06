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

## AI Coding Tool Integration

`rcli init` generates a Claude Code skill file by default. Use `--tool` to also generate instruction files for other AI coding tools:

```bash
# Claude Code only (default)
rcli init --name "my-project"

# Multiple tools
rcli init --name "my-project" --tool claude --tool codex --tool opencode
```

| Tool | Flag | Generated File |
|------|------|----------------|
| Claude Code | `--tool claude` | `.claude/skills/rcli/SKILL.md` |
| OpenAI Codex | `--tool codex` | `AGENTS.md` |
| OpenCode | `--tool opencode` | `OPENCODE.md` |

All files contain the same core instructions. For `AGENTS.md` and `OPENCODE.md`, rcli merges its section into existing files using HTML comment markers, so other tool instructions are preserved.
