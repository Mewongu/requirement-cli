"""Markdown output formatter."""

from __future__ import annotations

import sys

from rcli.models.requirement import Requirement
from rcli.models.decision import Decision


class MarkdownFormatter:
    """Outputs data as Markdown."""

    def output_item(self, item) -> None:
        if isinstance(item, Requirement):
            sys.stdout.write(self._format_requirement(item))
        elif isinstance(item, Decision):
            sys.stdout.write(self._format_decision(item))

    def _format_requirement(self, req: Requirement) -> str:
        lines = [
            f"## {req.id}: {req.title}",
            "",
            f"- **Status:** {req.status}",
            f"- **Priority:** {req.priority}",
        ]
        if req.parent:
            lines.append(f"- **Parent:** {req.parent}")
        if req.labels:
            lines.append(f"- **Labels:** {', '.join(req.labels)}")
        if req.depends_on:
            lines.append(f"- **Depends On:** {', '.join(req.depends_on)}")
        if req.description:
            lines.extend(["", req.description])
        if req.metadata:
            lines.extend(["", "### Metadata", ""])
            for k, v in req.metadata.items():
                lines.append(f"- **{k}:** {v}")
        lines.append("")
        return "\n".join(lines)

    def _format_decision(self, dec: Decision) -> str:
        lines = [
            f"## {dec.id}: {dec.title}",
            "",
            f"- **Status:** {dec.status}",
        ]
        if dec.linked_requirements:
            lines.append(f"- **Linked Requirements:** {', '.join(dec.linked_requirements)}")
        if dec.context:
            lines.extend(["", "### Context", "", dec.context])
        if dec.decision:
            lines.extend(["", "### Decision", "", dec.decision])
        if dec.rationale:
            lines.extend(["", "### Rationale", "", dec.rationale])
        lines.append("")
        return "\n".join(lines)

    def output_list(self, items: list) -> None:
        for item in items:
            self.output_item(item)

    def output_tree(self, requirements: list[Requirement]) -> None:
        by_id = {r.id: r for r in requirements}
        children: dict[str | None, list[str]] = {}
        for r in requirements:
            children.setdefault(r.parent, []).append(r.id)
        lines: list[str] = ["# Requirements Tree", ""]
        self._build_tree(lines, None, children, by_id, 0)
        sys.stdout.write("\n".join(lines))

    def _build_tree(
        self, lines: list[str], parent_id: str | None,
        children: dict, by_id: dict, depth: int,
    ) -> None:
        for child_id in children.get(parent_id, []):
            req = by_id[child_id]
            indent = "  " * depth
            lines.append(f"{indent}- **{req.id}**: {req.title} ({req.status}, {req.priority})")
            self._build_tree(lines, child_id, children, by_id, depth + 1)

    def output_search(self, results: list[tuple[int, object]]) -> None:
        lines = ["# Search Results", ""]
        for score, item in results:
            lines.append(f"- **{item.id}**: {item.title} (score: {score})")
        lines.append("")
        sys.stdout.write("\n".join(lines))

    def output_status(self, status_data: dict) -> None:
        lines = ["# Project Status", ""]
        if "project_name" in status_data:
            lines.append(f"**Project:** {status_data['project_name']}")
            lines.append("")
        for section_name, section_data in status_data.get("sections", {}).items():
            lines.append(f"## {section_name}")
            lines.append("")
            for key, val in section_data.items():
                lines.append(f"- {key}: {val}")
            lines.append("")
        sys.stdout.write("\n".join(lines))

    def output_graph(self, requirements: list) -> None:
        deps = [r for r in requirements if r.depends_on]
        lines = ["# Dependency Graph", ""]
        if not deps:
            lines.append("_No dependencies defined._")
        else:
            for req in deps:
                lines.append(f"- **{req.id}** ({req.title}) depends on: {', '.join(req.depends_on)}")
        lines.append("")
        sys.stdout.write("\n".join(lines))

    def output_lint(self, issues: list[dict]) -> None:
        lines = ["# Lint Issues", ""]
        if not issues:
            lines.append("No issues found.")
        else:
            for issue in issues:
                lines.append(f"- **{issue['type']}**: {issue['message']}")
        lines.append("")
        sys.stdout.write("\n".join(lines))

    def output_message(self, message: str, data: object | None = None) -> None:
        sys.stdout.write(message + "\n")

    def format_export(self, reqs: list[Requirement], decs: list[Decision]) -> str:
        lines = ["# Requirements Export", ""]
        if reqs:
            lines.append("## Requirements")
            lines.append("")
            for req in reqs:
                lines.append(self._format_requirement(req))
        if decs:
            lines.append("## Decisions")
            lines.append("")
            for dec in decs:
                lines.append(self._format_decision(dec))
        return "\n".join(lines)
