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
) -> list:
    """Filter items. Multiple values within a type are OR'd, across types are AND'd."""
    result = items
    if statuses:
        result = [i for i in result if i.status in statuses]
    if labels:
        result = [i for i in result if hasattr(i, "labels") and any(l in i.labels for l in labels)]
    if prefix:
        result = [i for i in result if i.id.startswith(prefix + "-")]
    if parent is not None:
        result = [i for i in result if hasattr(i, "parent") and i.parent == parent]
    if priorities:
        result = [i for i in result if hasattr(i, "priority") and i.priority in priorities]
    if orphans:
        result = [i for i in result if hasattr(i, "parent") and i.parent is None]
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
