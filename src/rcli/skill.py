"""Skill file generator for Claude Code integration."""

SKILL_CONTENT = r"""---
name: rcli
description: Manage project requirements and design decisions. Use when users discuss requirements, features, specs, or architectural decisions.
user-invocable: true
---

You are managing project requirements and design decisions using the `rcli` CLI tool.

## Important Rules
- Always use `--format json` for all commands so you can parse the output
- If there is no `.rcli/` directory, run `rcli init --name "PROJECT_NAME"` first
- Search before creating to avoid duplicates
- Keep requirements and decisions up to date as the project evolves

## Commands Reference

### Initialize
```bash
rcli init --name "project-name"
```

### Requirements
```bash
# Add a requirement
rcli req add "Title" --description "Details" --priority high --label mvp --format json

# Add via --json (inline or stdin with '-')
rcli req add --json '{"title":"Title","priority":"high","labels":["mvp"]}' --format json
echo '{"title":"Title"}' | rcli req add --json - --format json

# List requirements (with filters)
rcli req list --format json
rcli req list --status draft --status approved --label mvp --format json
rcli req list --orphans --format json

# Show a single requirement
rcli req show REQ-1 --format json

# Edit a requirement
rcli req edit REQ-1 --status approved --format json
rcli req edit REQ-1 --add-label backend --remove-label draft --format json
rcli req edit REQ-1 --parent REQ-2 --format json

# Edit via --json (replaces labels/metadata entirely)
rcli req edit REQ-1 --json '{"status":"approved","labels":["backend"]}' --format json

# Delete a requirement
rcli req delete REQ-1 --format json

# Show requirement tree
rcli req tree --format json
rcli req tree REQ-1 --format json
```

### Decisions
```bash
# Add a decision
rcli decision add "Title" --context "Why" --decision "What" --rationale "Because" --link REQ-1 --format json

# Add via --json
rcli decision add --json '{"title":"Title","context":"Why","decision":"What","linked_requirements":["REQ-1"]}' --format json

# List decisions
rcli decision list --format json
rcli decision list --status active --format json

# Show a decision
rcli decision show ADR-1 --format json

# Edit a decision
rcli decision edit ADR-1 --status obsolete --format json

# Edit via --json (replaces linked_requirements/metadata entirely)
rcli decision edit ADR-1 --json '{"status":"obsolete","linked_requirements":["REQ-2"]}' --format json

# Delete a decision
rcli decision delete ADR-1 --format json
```

### JSON Input (`--json`)
The `add` and `edit` commands accept `--json` with an inline JSON object or `-` for stdin.
- CLI flags override JSON values when both are provided
- Unknown JSON keys are silently ignored
- For `edit`, JSON `labels`/`linked_requirements`/`metadata` **replace** existing values (PUT semantics)
- CLI `--add-label`/`--remove-label`/`--add-link`/`--remove-link` take precedence over JSON lists

### Search
```bash
rcli search "query" --format json
rcli search "query" --type req --format json
```

### Export
```bash
rcli export --format markdown --output requirements.md
rcli export --format html --output requirements.html
rcli export --type req --status approved --format json
```

### Status Dashboard
```bash
rcli status --format json
```

## Workflow Guidelines
1. When the user discusses a requirement, search existing requirements first
2. Create requirements with appropriate status (draft for new ideas, approved for confirmed)
3. Record architectural decisions with context and rationale
4. Link decisions to the requirements they address
5. Update requirement status as implementation progresses
6. Use labels to categorize (e.g., mvp, backend, frontend, security)
"""


def generate_skill_content() -> str:
    """Return the skill file content."""
    return SKILL_CONTENT.strip() + "\n"
