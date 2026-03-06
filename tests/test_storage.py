"""Tests for storage engine."""

import pytest
from rcli.storage.store import Store
from rcli.storage.paths import find_rcli_root
from rcli.models.requirement import Requirement
from rcli.models.decision import Decision


class TestStore:
    def test_init_project(self, rcli_dir):
        store = Store(rcli_dir)
        store.init_project(project_name="my-project")
        assert rcli_dir.exists()
        assert (rcli_dir / "metadata.json").exists()
        assert (rcli_dir / "requirements").is_dir()
        assert (rcli_dir / "decisions").is_dir()
        meta = store.load_metadata()
        assert meta.project_name == "my-project"

    def test_next_id_monotonic(self, store):
        assert store.next_id("REQ") == "REQ-1"
        assert store.next_id("REQ") == "REQ-2"
        assert store.next_id("REQ") == "REQ-3"
        assert store.next_id("ADR") == "ADR-1"
        meta = store.load_metadata()
        assert meta.counters["REQ"] == 3
        assert meta.counters["ADR"] == 1

    def test_save_load_requirement(self, store, sample_req):
        store.save_requirement(sample_req)
        loaded = store.load_requirement("REQ-1")
        assert loaded.title == sample_req.title
        assert loaded.labels == sample_req.labels

    def test_delete_requirement(self, store, sample_req):
        store.save_requirement(sample_req)
        store.delete_requirement("REQ-1")
        with pytest.raises(FileNotFoundError):
            store.load_requirement("REQ-1")

    def test_list_requirements(self, store):
        for i in range(3):
            req = Requirement(id=f"REQ-{i+1}", title=f"Req {i+1}")
            store.save_requirement(req)
        reqs = store.list_requirements()
        assert len(reqs) == 3
        assert [r.id for r in reqs] == ["REQ-1", "REQ-2", "REQ-3"]

    def test_list_requirements_empty(self, store):
        assert store.list_requirements() == []

    def test_save_load_decision(self, store, sample_decision):
        store.save_decision(sample_decision)
        loaded = store.load_decision("ADR-1")
        assert loaded.title == sample_decision.title
        assert loaded.linked_requirements == ["REQ-1"]

    def test_delete_decision(self, store, sample_decision):
        store.save_decision(sample_decision)
        store.delete_decision("ADR-1")
        with pytest.raises(FileNotFoundError):
            store.load_decision("ADR-1")

    def test_list_decisions(self, store):
        for i in range(2):
            dec = Decision(id=f"ADR-{i+1}", title=f"Dec {i+1}")
            store.save_decision(dec)
        decs = store.list_decisions()
        assert len(decs) == 2

    def test_id_not_reused_after_delete(self, store):
        """IDs must never be reused even after deletion."""
        id1 = store.next_id("REQ")
        assert id1 == "REQ-1"
        req = Requirement(id=id1, title="Will delete")
        store.save_requirement(req)
        store.delete_requirement(id1)
        id2 = store.next_id("REQ")
        assert id2 == "REQ-2"


class TestPaths:
    def test_find_rcli_root_exists(self, tmp_path):
        d =tmp_path / ".rcli"
        d.mkdir()
        found = find_rcli_root(tmp_path)
        assert found == d

    def test_find_rcli_root_nested(self, tmp_path):
        d =tmp_path / ".rcli"
        d.mkdir()
        nested = tmp_path / "a" / "b" / "c"
        nested.mkdir(parents=True)
        found = find_rcli_root(nested)
        assert found == d

    def test_find_rcli_root_not_found(self, tmp_path):
        nested = tmp_path / "no_rcli"
        nested.mkdir()
        found = find_rcli_root(nested)
        assert found is None
