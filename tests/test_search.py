"""Tests for search engine."""

from rcli.models.requirement import Requirement
from rcli.models.decision import Decision
from rcli.search_engine import search, filter_items, get_subtree_ids


class TestSearch:
    def test_search_title_match(self):
        items = [
            Requirement(id="REQ-1", title="User authentication"),
            Requirement(id="REQ-2", title="Database schema"),
        ]
        results = search(items, "auth")
        assert len(results) == 1
        assert results[0][1].id == "REQ-1"
        assert results[0][0] == 2  # title match score

    def test_search_description_match(self):
        items = [
            Requirement(id="REQ-1", title="Feature", description="Uses authentication flow"),
        ]
        results = search(items, "auth")
        assert len(results) == 1
        assert results[0][0] == 1  # description match score

    def test_search_both_match(self):
        items = [
            Requirement(id="REQ-1", title="Auth feature", description="Handles auth"),
        ]
        results = search(items, "auth")
        assert len(results) == 1
        assert results[0][0] == 3  # both title + description

    def test_search_case_insensitive(self):
        items = [Requirement(id="REQ-1", title="Authentication")]
        results = search(items, "AUTHENTICATION")
        assert len(results) == 1

    def test_search_no_results(self):
        items = [Requirement(id="REQ-1", title="Something")]
        results = search(items, "xyz")
        assert len(results) == 0

    def test_search_decisions(self):
        items = [
            Decision(id="ADR-1", title="Use JWT", context="Need tokens for auth"),
        ]
        results = search(items, "JWT")
        assert len(results) == 1
        assert results[0][0] == 2

    def test_search_decision_context(self):
        items = [
            Decision(id="ADR-1", title="Something", context="Need tokens for auth"),
        ]
        results = search(items, "tokens")
        assert len(results) == 1
        assert results[0][0] == 1

    def test_search_sorted_by_score(self):
        items = [
            Requirement(id="REQ-1", title="Other", description="auth here"),
            Requirement(id="REQ-2", title="Auth feature", description="auth desc"),
        ]
        results = search(items, "auth")
        assert results[0][1].id == "REQ-2"  # higher score first


class TestFilter:
    def test_filter_by_status(self):
        items = [
            Requirement(id="REQ-1", title="A", status="draft"),
            Requirement(id="REQ-2", title="B", status="approved"),
            Requirement(id="REQ-3", title="C", status="draft"),
        ]
        result = filter_items(items, statuses=["draft"])
        assert len(result) == 2

    def test_filter_by_multiple_statuses(self):
        items = [
            Requirement(id="REQ-1", title="A", status="draft"),
            Requirement(id="REQ-2", title="B", status="approved"),
            Requirement(id="REQ-3", title="C", status="implemented"),
        ]
        result = filter_items(items, statuses=["draft", "approved"])
        assert len(result) == 2

    def test_filter_by_label(self):
        items = [
            Requirement(id="REQ-1", title="A", labels=["mvp", "backend"]),
            Requirement(id="REQ-2", title="B", labels=["frontend"]),
        ]
        result = filter_items(items, labels=["mvp"])
        assert len(result) == 1
        assert result[0].id == "REQ-1"

    def test_filter_by_prefix(self):
        items = [
            Requirement(id="REQ-1", title="A"),
            Requirement(id="FEAT-1", title="B"),
        ]
        result = filter_items(items, prefix="FEAT")
        assert len(result) == 1
        assert result[0].id == "FEAT-1"

    def test_filter_by_priority(self):
        items = [
            Requirement(id="REQ-1", title="A", priority="high"),
            Requirement(id="REQ-2", title="B", priority="low"),
        ]
        result = filter_items(items, priorities=["high"])
        assert len(result) == 1

    def test_filter_orphans(self):
        items = [
            Requirement(id="REQ-1", title="A", parent=None),
            Requirement(id="REQ-2", title="B", parent="REQ-1"),
        ]
        result = filter_items(items, orphans=True)
        assert len(result) == 1
        assert result[0].id == "REQ-1"

    def test_filter_combined(self):
        """Multiple filter types are AND'd."""
        items = [
            Requirement(id="REQ-1", title="A", status="draft", labels=["mvp"]),
            Requirement(id="REQ-2", title="B", status="approved", labels=["mvp"]),
            Requirement(id="REQ-3", title="C", status="draft", labels=["later"]),
        ]
        result = filter_items(items, statuses=["draft"], labels=["mvp"])
        assert len(result) == 1
        assert result[0].id == "REQ-1"


class TestSubtree:
    def test_get_subtree_ids(self):
        reqs = [
            Requirement(id="REQ-1", title="Root", parent=None),
            Requirement(id="REQ-2", title="Child", parent="REQ-1"),
            Requirement(id="REQ-3", title="Grandchild", parent="REQ-2"),
            Requirement(id="REQ-4", title="Other root", parent=None),
        ]
        ids = get_subtree_ids(reqs, "REQ-1")
        assert ids == {"REQ-1", "REQ-2", "REQ-3"}

    def test_get_subtree_leaf(self):
        reqs = [
            Requirement(id="REQ-1", title="Root", parent=None),
            Requirement(id="REQ-2", title="Leaf", parent="REQ-1"),
        ]
        ids = get_subtree_ids(reqs, "REQ-2")
        assert ids == {"REQ-2"}
