"""Storage engine for .rcli/ data."""

from __future__ import annotations

import json
from pathlib import Path

from rcli.models.requirement import Requirement
from rcli.models.decision import Decision
from rcli.models.metadata import Metadata
from rcli.storage import paths


class Store:
    """Manages reading and writing of .rcli/ data files."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def init_project(self, project_name: str = "") -> None:
        """Create .rcli/ directory structure and initial metadata."""
        self.root.mkdir(parents=True, exist_ok=True)
        paths.requirements_dir(self.root).mkdir(exist_ok=True)
        paths.decisions_dir(self.root).mkdir(exist_ok=True)
        meta = Metadata(project_name=project_name)
        self.save_metadata(meta)

    # -- Metadata --

    def load_metadata(self) -> Metadata:
        p = paths.metadata_path(self.root)
        with open(p) as f:
            return Metadata.from_dict(json.load(f))

    def save_metadata(self, meta: Metadata) -> None:
        p = paths.metadata_path(self.root)
        with open(p, "w") as f:
            json.dump(meta.to_dict(), f, indent=2)
            f.write("\n")

    def next_id(self, prefix: str) -> str:
        """Generate the next monotonic ID for the given prefix."""
        meta = self.load_metadata()
        current = meta.counters.get(prefix, 0)
        next_val = current + 1
        meta.counters[prefix] = next_val
        self.save_metadata(meta)
        return f"{prefix}-{next_val}"

    # -- Requirements --

    def save_requirement(self, req: Requirement) -> None:
        p = paths.requirement_path(self.root, req.id)
        with open(p, "w") as f:
            json.dump(req.to_dict(), f, indent=2)
            f.write("\n")

    def load_requirement(self, req_id: str) -> Requirement:
        p = paths.requirement_path(self.root, req_id)
        with open(p) as f:
            return Requirement.from_dict(json.load(f))

    def delete_requirement(self, req_id: str) -> None:
        p = paths.requirement_path(self.root, req_id)
        p.unlink()

    def list_requirements(self) -> list[Requirement]:
        req_dir = paths.requirements_dir(self.root)
        if not req_dir.exists():
            return []
        reqs = []
        for f in sorted(req_dir.glob("*.json")):
            with open(f) as fh:
                reqs.append(Requirement.from_dict(json.load(fh)))
        return reqs

    # -- Decisions --

    def save_decision(self, dec: Decision) -> None:
        p = paths.decision_path(self.root, dec.id)
        with open(p, "w") as f:
            json.dump(dec.to_dict(), f, indent=2)
            f.write("\n")

    def load_decision(self, dec_id: str) -> Decision:
        p = paths.decision_path(self.root, dec_id)
        with open(p) as f:
            return Decision.from_dict(json.load(f))

    def delete_decision(self, dec_id: str) -> None:
        p = paths.decision_path(self.root, dec_id)
        p.unlink()

    def list_decisions(self) -> list[Decision]:
        dec_dir = paths.decisions_dir(self.root)
        if not dec_dir.exists():
            return []
        decs = []
        for f in sorted(dec_dir.glob("*.json")):
            with open(f) as fh:
                decs.append(Decision.from_dict(json.load(fh)))
        return decs
