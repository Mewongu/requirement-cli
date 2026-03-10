"""Requirement data model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


VALID_STATUSES = ("draft", "approved", "implemented", "verified")
VALID_PRIORITIES = ("low", "medium", "high", "critical")


@dataclass
class Requirement:
    id: str
    title: str
    description: str = ""
    status: str = "draft"
    priority: str = "medium"
    parent: str | None = None
    labels: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "parent": self.parent,
            "labels": self.labels,
            "depends_on": self.depends_on,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Requirement:
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", "draft"),
            priority=data.get("priority", "medium"),
            parent=data.get("parent"),
            labels=data.get("labels", []),
            depends_on=data.get("depends_on", []),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )
