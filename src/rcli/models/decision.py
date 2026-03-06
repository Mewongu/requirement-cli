"""Decision data model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


VALID_STATUSES = ("active", "obsolete")


@dataclass
class Decision:
    id: str
    title: str
    context: str = ""
    decision: str = ""
    rationale: str = ""
    status: str = "active"
    linked_requirements: list[str] = field(default_factory=list)
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
            "context": self.context,
            "decision": self.decision,
            "rationale": self.rationale,
            "status": self.status,
            "linked_requirements": self.linked_requirements,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Decision:
        return cls(
            id=data["id"],
            title=data["title"],
            context=data.get("context", ""),
            decision=data.get("decision", ""),
            rationale=data.get("rationale", ""),
            status=data.get("status", "active"),
            linked_requirements=data.get("linked_requirements", []),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )
