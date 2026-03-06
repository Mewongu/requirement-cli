# Architecture

## Storage Format

```
.rcli/
  metadata.json
  requirements/
    REQ-1.json
    REQ-2.json
  decisions/
    ADR-1.json
```

Each entity is a single JSON file named `{ID}.json`. This makes git diffs clean and merges conflict-free in most cases.

## Data Models

### Requirement
Fields: id, title, description, status (draft|approved|implemented|verified), priority (low|medium|high|critical), parent, labels, metadata, created_at, updated_at.

### Decision
Fields: id, title, context, decision, rationale, status (active|obsolete), linked_requirements, metadata, created_at, updated_at.

### Metadata
Fields: version, project_name, counters (per-prefix monotonic), default_requirement_prefix, default_decision_prefix.

## CLI Design

Top-level group with `--format` option. Subcommand groups: `req`, `decision`, `search`, `export`, `status`.

Error output goes to stderr (plain text). Data output goes to stdout. When `--format json`, stdout contains only valid JSON.

## Filter Semantics

Multiple `--status` or `--label` values are OR'd within type, AND'd across types. Example: `--status draft --status approved --label mvp` means (status=draft OR status=approved) AND (label=mvp).
