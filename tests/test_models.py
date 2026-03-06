"""Tests for data models."""

from rcli.models.requirement import Requirement
from rcli.models.decision import Decision
from rcli.models.metadata import Metadata


class TestRequirement:
    def test_create_default(self):
        req = Requirement(id="REQ-1", title="Test")
        assert req.id == "REQ-1"
        assert req.title == "Test"
        assert req.status == "draft"
        assert req.priority == "medium"
        assert req.parent is None
        assert req.labels == []
        assert req.metadata == {}
        assert req.created_at != ""
        assert req.updated_at != ""

    def test_to_dict(self, sample_req):
        d = sample_req.to_dict()
        assert d["id"] == "REQ-1"
        assert d["title"] == "Test Requirement"
        assert d["status"] == "draft"
        assert d["priority"] == "high"
        assert d["labels"] == ["mvp", "backend"]
        assert d["parent"] is None

    def test_from_dict(self):
        data = {
            "id": "REQ-5",
            "title": "From dict",
            "description": "desc",
            "status": "approved",
            "priority": "critical",
            "parent": "REQ-1",
            "labels": ["ui"],
            "metadata": {"key": "val"},
            "created_at": "2024-01-01T00:00:00+00:00",
            "updated_at": "2024-01-01T00:00:00+00:00",
        }
        req = Requirement.from_dict(data)
        assert req.id == "REQ-5"
        assert req.status == "approved"
        assert req.parent == "REQ-1"
        assert req.labels == ["ui"]
        assert req.metadata == {"key": "val"}

    def test_roundtrip(self, sample_req):
        d = sample_req.to_dict()
        restored = Requirement.from_dict(d)
        assert restored.to_dict() == d


class TestDecision:
    def test_create_default(self):
        dec = Decision(id="ADR-1", title="Test")
        assert dec.id == "ADR-1"
        assert dec.status == "active"
        assert dec.linked_requirements == []

    def test_to_dict(self, sample_decision):
        d = sample_decision.to_dict()
        assert d["id"] == "ADR-1"
        assert d["context"] == "We need to decide"
        assert d["linked_requirements"] == ["REQ-1"]

    def test_from_dict(self):
        data = {
            "id": "ADR-2",
            "title": "Another",
            "context": "ctx",
            "decision": "dec",
            "rationale": "rat",
            "status": "obsolete",
            "linked_requirements": ["REQ-1", "REQ-2"],
            "metadata": {},
            "created_at": "2024-01-01T00:00:00+00:00",
            "updated_at": "2024-01-01T00:00:00+00:00",
        }
        dec = Decision.from_dict(data)
        assert dec.status == "obsolete"
        assert dec.linked_requirements == ["REQ-1", "REQ-2"]

    def test_roundtrip(self, sample_decision):
        d = sample_decision.to_dict()
        restored = Decision.from_dict(d)
        assert restored.to_dict() == d


class TestMetadata:
    def test_defaults(self):
        m = Metadata()
        assert m.version == "1"
        assert m.default_requirement_prefix == "REQ"
        assert m.default_decision_prefix == "ADR"
        assert m.counters == {}

    def test_roundtrip(self):
        m = Metadata(project_name="test", counters={"REQ": 5, "ADR": 2})
        d = m.to_dict()
        restored = Metadata.from_dict(d)
        assert restored.project_name == "test"
        assert restored.counters == {"REQ": 5, "ADR": 2}
