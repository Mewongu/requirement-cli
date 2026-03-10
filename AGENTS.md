# AGENTS.md

Instructions for AI coding agents working in this repository.

## Project Overview

`rcli` is a CLI tool for managing project requirements and architectural decisions. It stores data as individual JSON files in a `.rcli/` directory (one file per requirement/decision) for clean git diffs and merge-friendliness. It integrates with Claude Code via generated skill files.

## Environment Setup

A virtualenv exists at `.venv`. Always activate it before running any commands:

```bash
source .venv/bin/activate
pip install -e ".[dev]"   # if deps are missing
```

Never run `python` or `rcli` without the virtualenv active.

## Running Tests

```bash
source .venv/bin/activate
pytest tests/                    # full suite
pytest tests/test_cli_req.py     # single file
pytest tests/ -v --tb=short      # verbose with short tracebacks
```

Always run the full test suite before committing. All tests must pass.

## Code Style

No linter is configured. Follow existing patterns:
- Use `click` for CLI commands and options
- Use `rich` for terminal output
- Data models live in `src/rcli/models/`, storage in `src/rcli/storage/`, CLI commands in `src/rcli/commands/`
- All timestamps must be stored in UTC

## Workflow

- Commit between logical steps (setup, implementation, tests, docs)
- Commit after completing each todo item with a clean working tree
- Use `git commit` with a short, descriptive message
- Never skip pre-commit hooks (`--no-verify`)

## Working with Requirements and Decisions

When working with requirements and architectural decisions, use the `rcli` skill.

Agents can and should use the `rcli` tool directly to read, add, and update requirements and decisions. Do not edit the `.rcli/` JSON files by hand — always go through the CLI.

Key commands:
```bash
rcli req list                              # list requirements
rcli decision list                         # list decisions
rcli req add "title" --priority high       # add requirement
rcli decision add "title" --context "..."  # add decision
rcli status                                # project dashboard
rcli --format json req list               # JSON output for scripting
```

Project requirements live in `docs/REQUIREMENTS.md` and architecture in `docs/ARCHITECTURE.md`.

## Key Architecture Notes

- Storage: `.rcli/requirements/REQ-*.json` and `.rcli/decisions/ADR-*.json`
- IDs are monotonically increasing and never reused
- Requirement statuses: `draft`, `approved`, `implemented`, `verified`
- Decision statuses: `active`, `obsolete`
- Multiple `--status`/`--label` filters are OR'd within type, AND'd across types
- Use `--format json` for any programmatic access

## Project Structure

```
src/rcli/
  cli.py            # entry point
  commands/         # one file per command group (req, decision, search, export, status)
  models/           # data models (requirement, decision, metadata)
  storage/          # JSON file storage layer
  formatters/       # output formatters (table, json, markdown, html)
tests/              # pytest test suite, uses Click CliRunner
docs/               # ARCHITECTURE.md, REQUIREMENTS.md, SKILL_FILE.md
```

## What Not to Do

- Do not modify `.rcli/metadata.json` ID counters manually
- Do not rename or reorder existing CLI commands or options without updating tests
- Do not add new dependencies without updating `pyproject.toml`
- Do not use `python` outside the `.venv` virtualenv
