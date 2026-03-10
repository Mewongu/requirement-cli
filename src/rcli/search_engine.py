"""Search and filter engine for requirements and decisions."""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rcli.models.requirement import Requirement
    from rcli.models.decision import Decision


def search(items: list, query: str) -> list[tuple[int, object]]:
    """Case-insensitive substring search. Returns (score, item) sorted by score desc."""
    query_lower = query.lower()
    results = []
    for item in items:
        score = 0
        if query_lower in item.title.lower():
            score += 2
        desc = getattr(item, "description", "") or ""
        if not desc:
            # For decisions, also check context/decision/rationale
            for attr in ("context", "decision", "rationale"):
                val = getattr(item, attr, "") or ""
                if query_lower in val.lower():
                    score += 1
                    break
        elif query_lower in desc.lower():
            score += 1
        if score > 0:
            results.append((score, item))
    results.sort(key=lambda x: x[0], reverse=True)
    return results


def filter_items(
    items: list,
    statuses: list[str] | None = None,
    labels: list[str] | None = None,
    prefix: str | None = None,
    parent: str | None = None,
    priorities: list[str] | None = None,
    orphans: bool = False,
    links: list[str] | None = None,
    depends_on_ids: list[str] | None = None,
) -> list:
    """Filter items. Multiple values within a type are OR'd, across types are AND'd."""
    result = items
    if statuses:
        result = [i for i in result if i.status in statuses]
    if labels:
        result = [i for i in result if hasattr(i, "labels") and any(l in i.labels for l in labels)]
    if links:
        result = [i for i in result if hasattr(i, "linked_requirements") and any(l in i.linked_requirements for l in links)]
    if depends_on_ids:
        result = [i for i in result if hasattr(i, "depends_on") and any(d in i.depends_on for d in depends_on_ids)]
    if prefix:
        result = [i for i in result if i.id.startswith(prefix + "-")]
    if parent is not None:
        result = [i for i in result if hasattr(i, "parent") and i.parent == parent]
    if priorities:
        result = [i for i in result if hasattr(i, "priority") and i.priority in priorities]
    if orphans:
        result = [i for i in result if hasattr(i, "parent") and i.parent is None]
    return result


def find_cycles(requirements: list) -> list[list[str]]:
    """Find cycles in the depends_on graph using DFS. Returns list of cycles (each a list of IDs)."""
    graph: dict[str, list[str]] = {r.id: list(r.depends_on) for r in requirements}

    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {nid: WHITE for nid in graph}
    cycles: list[list[str]] = []

    def dfs(node: str, path: list[str]) -> None:
        color[node] = GRAY
        path.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in color:
                continue  # dangling external reference
            if color[neighbor] == GRAY:
                idx = path.index(neighbor)
                cycles.append(path[idx:] + [neighbor])
            elif color[neighbor] == WHITE:
                dfs(neighbor, path)
        path.pop()
        color[node] = BLACK

    for req_id in list(graph.keys()):
        if color[req_id] == WHITE:
            dfs(req_id, [])

    return cycles


def find_impacted(requirements: list, target_id: str) -> list:
    """BFS reverse traversal: find all requirements that directly or transitively depend on target_id."""
    reverse: dict[str, list[str]] = {}
    req_by_id: dict[str, object] = {}
    for req in requirements:
        req_by_id[req.id] = req
        for dep in req.depends_on:
            reverse.setdefault(dep, []).append(req.id)

    result = []
    visited: set[str] = set()
    queue = deque([target_id])
    while queue:
        current = queue.popleft()
        for dependent_id in reverse.get(current, []):
            if dependent_id not in visited:
                visited.add(dependent_id)
                if dependent_id in req_by_id:
                    result.append(req_by_id[dependent_id])
                queue.append(dependent_id)
    return result


def get_subtree_ids(requirements: list[Requirement], root_id: str) -> set[str]:
    """BFS from root_id to find all descendant requirement IDs."""
    children: dict[str | None, list[str]] = {}
    for req in requirements:
        children.setdefault(req.parent, []).append(req.id)

    result = {root_id}
    queue = deque([root_id])
    while queue:
        current = queue.popleft()
        for child_id in children.get(current, []):
            if child_id not in result:
                result.add(child_id)
                queue.append(child_id)
    return result
