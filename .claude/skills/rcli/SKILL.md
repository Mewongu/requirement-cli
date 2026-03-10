---
name: rcli
description: Manage project requirements and design decisions. Use when users discuss requirements, features, specs, or architectural decisions.
user-invocable: true
---

You are managing project requirements and design decisions using the `rcli` CLI tool.

## Important Rules
- Output defaults to JSON — no need to pass `--format json` unless overriding
- If there is no `.rcli/` directory, run `rcli init --name "PROJECT_NAME"` first
- Search before creating to avoid duplicates
- Keep requirements and decisions up to date as the project evolves

## Commands Reference

### Initialize
```bash
rcli init --name "project-name"
rcli init --name "project-name" --skill-dir .agents/skills
rcli init --name "project-name" --skill-dir .claude/skills
```

### Requirements
```bash
# Add a requirement
rcli req add "Title" --description "Details" --priority high --label mvp

# Add via --json (inline or stdin with '-')
rcli req add --json '{"title":"Title","priority":"high","labels":["mvp"]}'
echo '{"title":"Title"}' | rcli req add --json -

# List requirements (with filters)
rcli req list
rcli req list --status draft --status approved --label mvp
rcli req list --orphans

# Show a single requirement
rcli req show REQ-1

# Edit a requirement
rcli req edit REQ-1 --status approved
rcli req edit REQ-1 --add-label backend --remove-label draft
rcli req edit REQ-1 --parent REQ-2

# Edit via --json (replaces labels/metadata entirely)
rcli req edit REQ-1 --json '{"status":"approved","labels":["backend"]}'

# Delete a requirement
rcli req delete REQ-1

# Show requirement tree
rcli req tree
rcli req tree REQ-1
```

### Decisions
```bash
# Add a decision
rcli decision add "Title" --context "Why" --decision "What" --rationale "Because" --link REQ-1

# Add via --json
rcli decision add --json '{"title":"Title","context":"Why","decision":"What","linked_requirements":["REQ-1"]}'

# List decisions
rcli decision list
rcli decision list --status active
rcli decision list --link REQ-1

# Show a decision
rcli decision show ADR-1

# Edit a decision
rcli decision edit ADR-1 --status obsolete

# Edit via --json (replaces linked_requirements/metadata entirely)
rcli decision edit ADR-1 --json '{"status":"obsolete","linked_requirements":["REQ-2"]}'

# Delete a decision
rcli decision delete ADR-1
```

### JSON Input (`--json`)
The `add` and `edit` commands accept `--json` with an inline JSON object or `-` for stdin.
- CLI flags override JSON values when both are provided
- Unknown JSON keys are silently ignored
- For `edit`, JSON `labels`/`linked_requirements`/`metadata` **replace** existing values (PUT semantics)
- CLI `--add-label`/`--remove-label`/`--add-link`/`--remove-link` take precedence over JSON lists

### Search
```bash
rcli search "query"
rcli search "query" --type req
```

### Export
```bash
rcli export --format markdown --output requirements.md
rcli export --format html --output requirements.html
rcli export --type req --status approved
```

### Status Dashboard
```bash
rcli status
```

## Workflow Guidelines
1. When the user discusses a requirement, search existing requirements first
2. Create requirements with appropriate status (draft for new ideas, approved for confirmed)
3. Record architectural decisions with context and rationale
4. Link decisions to the requirements they address
5. Update requirement status as implementation progresses
6. Use labels to categorize (e.g., mvp, backend, frontend, security)
