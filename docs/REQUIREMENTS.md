# Requirement CLI Requirements

## REQ-1: CLI Interface
The tool provides a CLI (`rcli`) for managing requirements and decisions with full CRUD operations.

## REQ-2: JSON File Storage
All data is stored as individual JSON files in `.rcli/` for git merge-friendliness.

## REQ-3: Hierarchical Requirements
Requirements support parent-child relationships with tree visualization.

## REQ-4: Design Decisions
ADR-style decision records linked to requirements.

## REQ-5: Search
Case-insensitive substring search across titles and descriptions with relevance scoring.

## REQ-6: Multiple Output Formats
Support table, JSON, markdown, and HTML output formats via `--format` flag.

## REQ-7: Export
Export filtered subsets of requirements/decisions to markdown, HTML, or JSON files.

## REQ-8: Claude Code Integration
Generate a skill file at `.claude/skills/rcli/SKILL.md` for Claude Code integration.

## REQ-9: Monotonic IDs
ID counters are monotonic (never decremented) to prevent ID reuse after deletion.

## REQ-10: Status Dashboard
`rcli status` shows counts by status, label distribution, and prefix distribution.
