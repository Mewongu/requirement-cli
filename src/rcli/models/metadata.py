"""Project metadata model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Metadata:
    version: str = "1"
    project_name: str = ""
    counters: dict[str, int] = field(default_factory=dict)
    default_requirement_prefix: str = "REQ"
    default_decision_prefix: str = "ADR"

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "project_name": self.project_name,
            "counters": self.counters,
            "default_requirement_prefix": self.default_requirement_prefix,
            "default_decision_prefix": self.default_decision_prefix,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Metadata:
        return cls(
            version=data.get("version", "1"),
            project_name=data.get("project_name", ""),
            counters=data.get("counters", {}),
            default_requirement_prefix=data.get("default_requirement_prefix", "REQ"),
            default_decision_prefix=data.get("default_decision_prefix", "ADR"),
        )
