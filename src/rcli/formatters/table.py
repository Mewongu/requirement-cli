"""Rich table/panel output formatter."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text

from rcli.models.requirement import Requirement
from rcli.models.decision import Decision

console = Console()


PRIORITY_COLORS = {
    "critical": "red bold",
    "high": "red",
    "medium": "yellow",
    "low": "green",
}

STATUS_COLORS = {
    "draft": "dim",
    "approved": "blue",
    "implemented": "green",
    "verified": "green bold",
    "active": "green",
    "obsolete": "dim",
}


class TableFormatter:
    """Outputs data using Rich tables and panels."""

    def output_item(self, item) -> None:
        if isinstance(item, Requirement):
            self._show_requirement(item)
        elif isinstance(item, Decision):
            self._show_decision(item)

    def _show_requirement(self, req: Requirement) -> None:
        lines = [
            f"[bold]ID:[/bold] {req.id}",
            f"[bold]Title:[/bold] {req.title}",
            f"[bold]Status:[/bold] [{STATUS_COLORS.get(req.status, '')}]{req.status}[/]",
            f"[bold]Priority:[/bold] [{PRIORITY_COLORS.get(req.priority, '')}]{req.priority}[/]",
        ]
        if req.parent:
            lines.append(f"[bold]Parent:[/bold] {req.parent}")
        if req.labels:
            lines.append(f"[bold]Labels:[/bold] {', '.join(req.labels)}")
        if req.depends_on:
            lines.append(f"[bold]Depends On:[/bold] {', '.join(req.depends_on)}")
        if req.description:
            lines.append(f"\n[bold]Description:[/bold]\n{req.description}")
        if req.metadata:
            meta_str = ", ".join(f"{k}={v}" for k, v in req.metadata.items())
            lines.append(f"[bold]Metadata:[/bold] {meta_str}")
        lines.append(f"[bold]Created:[/bold] {req.created_at}")
        lines.append(f"[bold]Updated:[/bold] {req.updated_at}")
        console.print(Panel("\n".join(lines), title=req.id))

    def _show_decision(self, dec: Decision) -> None:
        lines = [
            f"[bold]ID:[/bold] {dec.id}",
            f"[bold]Title:[/bold] {dec.title}",
            f"[bold]Status:[/bold] [{STATUS_COLORS.get(dec.status, '')}]{dec.status}[/]",
        ]
        if dec.context:
            lines.append(f"\n[bold]Context:[/bold]\n{dec.context}")
        if dec.decision:
            lines.append(f"\n[bold]Decision:[/bold]\n{dec.decision}")
        if dec.rationale:
            lines.append(f"\n[bold]Rationale:[/bold]\n{dec.rationale}")
        if dec.linked_requirements:
            lines.append(f"[bold]Linked Requirements:[/bold] {', '.join(dec.linked_requirements)}")
        if dec.metadata:
            meta_str = ", ".join(f"{k}={v}" for k, v in dec.metadata.items())
            lines.append(f"[bold]Metadata:[/bold] {meta_str}")
        lines.append(f"[bold]Created:[/bold] {dec.created_at}")
        lines.append(f"[bold]Updated:[/bold] {dec.updated_at}")
        console.print(Panel("\n".join(lines), title=dec.id))

    def output_list(self, items: list) -> None:
        if not items:
            console.print("[dim]No items found.[/dim]")
            return
        if isinstance(items[0], Requirement):
            self._list_requirements(items)
        elif isinstance(items[0], Decision):
            self._list_decisions(items)

    def _list_requirements(self, reqs: list[Requirement]) -> None:
        table = Table(title="Requirements")
        table.add_column("ID", style="bold")
        table.add_column("Title")
        table.add_column("Status")
        table.add_column("Priority")
        table.add_column("Parent")
        table.add_column("Labels")
        table.add_column("Depends On")
        for req in reqs:
            status = Text(req.status, style=STATUS_COLORS.get(req.status, ""))
            priority = Text(req.priority, style=PRIORITY_COLORS.get(req.priority, ""))
            table.add_row(
                req.id, req.title, status, priority,
                req.parent or "", ", ".join(req.labels),
                ", ".join(req.depends_on),
            )
        console.print(table)

    def _list_decisions(self, decs: list[Decision]) -> None:
        table = Table(title="Decisions")
        table.add_column("ID", style="bold")
        table.add_column("Title")
        table.add_column("Status")
        table.add_column("Links")
        for dec in decs:
            status = Text(dec.status, style=STATUS_COLORS.get(dec.status, ""))
            table.add_row(
                dec.id, dec.title, status,
                ", ".join(dec.linked_requirements),
            )
        console.print(table)

    def output_tree(self, requirements: list[Requirement]) -> None:
        if not requirements:
            console.print("[dim]No requirements found.[/dim]")
            return
        by_id = {r.id: r for r in requirements}
        children: dict[str | None, list[str]] = {}
        for r in requirements:
            children.setdefault(r.parent, []).append(r.id)

        tree = Tree("[bold]Requirements[/bold]")
        self._build_tree(tree, None, children, by_id)
        console.print(tree)

    def _build_tree(
        self, parent_node: Tree, parent_id: str | None,
        children: dict, by_id: dict,
    ) -> None:
        for child_id in children.get(parent_id, []):
            req = by_id[child_id]
            status_style = STATUS_COLORS.get(req.status, "")
            priority_style = PRIORITY_COLORS.get(req.priority, "")
            label = f"[bold]{req.id}[/bold] {req.title} [{status_style}]{req.status}[/] [{priority_style}]{req.priority}[/]"
            node = parent_node.add(label)
            self._build_tree(node, child_id, children, by_id)

    def output_search(self, results: list[tuple[int, object]]) -> None:
        if not results:
            console.print("[dim]No results found.[/dim]")
            return
        table = Table(title="Search Results")
        table.add_column("Score", justify="right")
        table.add_column("ID", style="bold")
        table.add_column("Title")
        table.add_column("Status")
        for score, item in results:
            status = Text(item.status, style=STATUS_COLORS.get(item.status, ""))
            table.add_row(str(score), item.id, item.title, status)
        console.print(table)

    def output_status(self, status_data: dict) -> None:
        console.print(Panel("[bold]Project Status[/bold]"))
        if "project_name" in status_data:
            console.print(f"  Project: [bold]{status_data['project_name']}[/bold]")

        for section_name, section_data in status_data.get("sections", {}).items():
            console.print(f"\n  [bold]{section_name}:[/bold]")
            for key, val in section_data.items():
                console.print(f"    {key}: {val}")

    def output_graph(self, requirements: list) -> None:
        deps = [r for r in requirements if r.depends_on]
        if not deps:
            console.print("[dim]No dependencies defined.[/dim]")
            return
        table = Table(title="Dependency Graph")
        table.add_column("ID", style="bold")
        table.add_column("Title")
        table.add_column("Depends On")
        for req in deps:
            table.add_row(req.id, req.title, ", ".join(req.depends_on))
        console.print(table)

    def output_lint(self, issues: list[dict]) -> None:
        if not issues:
            console.print("[green]No issues found.[/green]")
            return
        table = Table(title="Lint Issues")
        table.add_column("Type", style="bold")
        table.add_column("Message")
        for issue in issues:
            table.add_row(issue["type"], issue["message"])
        console.print(table)

    def output_message(self, message: str, data: object | None = None) -> None:
        console.print(message)
