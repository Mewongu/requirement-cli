"""HTML output formatter."""

from __future__ import annotations

import html
import sys

from rcli.models.requirement import Requirement
from rcli.models.decision import Decision


CSS = """
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 900px; margin: 2em auto; padding: 0 1em; color: #333; }
  h1 { border-bottom: 2px solid #333; padding-bottom: 0.3em; }
  h2 { border-bottom: 1px solid #ddd; padding-bottom: 0.2em; }
  .item { margin: 1.5em 0; padding: 1em; border: 1px solid #ddd; border-radius: 4px; }
  .badge { display: inline-block; padding: 0.2em 0.6em; border-radius: 3px; font-size: 0.85em; font-weight: 600; margin-right: 0.3em; }
  .status-draft { background: #e0e0e0; }
  .status-approved { background: #bbdefb; }
  .status-implemented { background: #c8e6c9; }
  .status-verified { background: #a5d6a7; }
  .status-active { background: #c8e6c9; }
  .status-obsolete { background: #e0e0e0; }
  .priority-critical { background: #ffcdd2; }
  .priority-high { background: #ffcdd2; }
  .priority-medium { background: #fff9c4; }
  .priority-low { background: #c8e6c9; }
  table { border-collapse: collapse; width: 100%; margin: 1em 0; }
  th, td { border: 1px solid #ddd; padding: 0.5em 0.8em; text-align: left; }
  th { background: #f5f5f5; }
  .meta { color: #666; font-size: 0.9em; }
</style>
"""


def _esc(text: str) -> str:
    return html.escape(text)


class HtmlFormatter:
    """Outputs data as self-contained HTML."""

    def output_item(self, item) -> None:
        if isinstance(item, Requirement):
            sys.stdout.write(self._render_requirement_page(item))
        elif isinstance(item, Decision):
            sys.stdout.write(self._render_decision_page(item))

    def _render_requirement_page(self, req: Requirement) -> str:
        return f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{_esc(req.id)}</title>{CSS}</head><body>{self._render_requirement(req)}</body></html>\n"

    def _render_decision_page(self, dec: Decision) -> str:
        return f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{_esc(dec.id)}</title>{CSS}</head><body>{self._render_decision(dec)}</body></html>\n"

    def _render_requirement(self, req: Requirement) -> str:
        parts = [
            f'<div class="item">',
            f'<h2>{_esc(req.id)}: {_esc(req.title)}</h2>',
            f'<span class="badge status-{req.status}">{_esc(req.status)}</span>',
            f'<span class="badge priority-{req.priority}">{_esc(req.priority)}</span>',
        ]
        if req.parent:
            parts.append(f'<p>Parent: {_esc(req.parent)}</p>')
        if req.labels:
            parts.append(f'<p>Labels: {_esc(", ".join(req.labels))}</p>')
        if req.depends_on:
            parts.append(f'<p>Depends On: {_esc(", ".join(req.depends_on))}</p>')
        if req.description:
            parts.append(f'<p>{_esc(req.description)}</p>')
        parts.append(f'<p class="meta">Created: {_esc(req.created_at)} | Updated: {_esc(req.updated_at)}</p>')
        parts.append('</div>')
        return "\n".join(parts)

    def _render_decision(self, dec: Decision) -> str:
        parts = [
            f'<div class="item">',
            f'<h2>{_esc(dec.id)}: {_esc(dec.title)}</h2>',
            f'<span class="badge status-{dec.status}">{_esc(dec.status)}</span>',
        ]
        if dec.context:
            parts.append(f'<h3>Context</h3><p>{_esc(dec.context)}</p>')
        if dec.decision:
            parts.append(f'<h3>Decision</h3><p>{_esc(dec.decision)}</p>')
        if dec.rationale:
            parts.append(f'<h3>Rationale</h3><p>{_esc(dec.rationale)}</p>')
        if dec.linked_requirements:
            parts.append(f'<p>Linked: {_esc(", ".join(dec.linked_requirements))}</p>')
        parts.append(f'<p class="meta">Created: {_esc(dec.created_at)} | Updated: {_esc(dec.updated_at)}</p>')
        parts.append('</div>')
        return "\n".join(parts)

    def output_list(self, items: list) -> None:
        parts = [f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>Export</title>{CSS}</head><body>"]
        for item in items:
            if isinstance(item, Requirement):
                parts.append(self._render_requirement(item))
            elif isinstance(item, Decision):
                parts.append(self._render_decision(item))
        parts.append("</body></html>\n")
        sys.stdout.write("\n".join(parts))

    def output_tree(self, requirements: list[Requirement]) -> None:
        self.output_list(requirements)

    def output_search(self, results: list[tuple[int, object]]) -> None:
        parts = [f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>Search Results</title>{CSS}</head><body>"]
        parts.append("<h1>Search Results</h1>")
        parts.append("<table><tr><th>Score</th><th>ID</th><th>Title</th><th>Status</th></tr>")
        for score, item in results:
            parts.append(f"<tr><td>{score}</td><td>{_esc(item.id)}</td><td>{_esc(item.title)}</td><td>{_esc(item.status)}</td></tr>")
        parts.append("</table></body></html>\n")
        sys.stdout.write("\n".join(parts))

    def output_status(self, status_data: dict) -> None:
        parts = [f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>Status</title>{CSS}</head><body>"]
        parts.append("<h1>Project Status</h1>")
        if "project_name" in status_data:
            parts.append(f"<p>Project: <strong>{_esc(status_data['project_name'])}</strong></p>")
        for section_name, section_data in status_data.get("sections", {}).items():
            parts.append(f"<h2>{_esc(section_name)}</h2><ul>")
            for key, val in section_data.items():
                parts.append(f"<li>{_esc(key)}: {val}</li>")
            parts.append("</ul>")
        parts.append("</body></html>\n")
        sys.stdout.write("\n".join(parts))

    def output_graph(self, requirements: list) -> None:
        deps = [r for r in requirements if r.depends_on]
        parts = [f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>Dependency Graph</title>{CSS}</head><body>"]
        parts.append("<h1>Dependency Graph</h1>")
        if not deps:
            parts.append("<p><em>No dependencies defined.</em></p>")
        else:
            parts.append("<table><tr><th>ID</th><th>Title</th><th>Depends On</th></tr>")
            for req in deps:
                parts.append(f"<tr><td>{_esc(req.id)}</td><td>{_esc(req.title)}</td><td>{_esc(', '.join(req.depends_on))}</td></tr>")
            parts.append("</table>")
        parts.append("</body></html>\n")
        sys.stdout.write("\n".join(parts))

    def output_lint(self, issues: list[dict]) -> None:
        parts = [f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>Lint Issues</title>{CSS}</head><body>"]
        parts.append("<h1>Lint Issues</h1>")
        if not issues:
            parts.append("<p>No issues found.</p>")
        else:
            parts.append("<table><tr><th>Type</th><th>Message</th></tr>")
            for issue in issues:
                parts.append(f"<tr><td>{_esc(issue['type'])}</td><td>{_esc(issue['message'])}</td></tr>")
            parts.append("</table>")
        parts.append("</body></html>\n")
        sys.stdout.write("\n".join(parts))

    def output_message(self, message: str, data: object | None = None) -> None:
        sys.stdout.write(message + "\n")

    def format_export(self, reqs: list[Requirement], decs: list[Decision]) -> str:
        parts = [f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>Export</title>{CSS}</head><body>"]
        parts.append("<h1>Requirements Export</h1>")
        if reqs:
            parts.append("<h2>Requirements</h2>")
            for req in reqs:
                parts.append(self._render_requirement(req))
        if decs:
            parts.append("<h2>Decisions</h2>")
            for dec in decs:
                parts.append(self._render_decision(dec))
        parts.append("</body></html>\n")
        return "\n".join(parts)
