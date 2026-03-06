"""Tests for requirement CLI commands."""

import json
from click.testing import CliRunner

from rcli.cli import cli


def init_project(runner, tmp_path):
    """Helper to initialize a project."""
    runner.invoke(cli, ["init", "--name", "test"])


class TestReqAdd:
    def test_add_basic(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, ["--format", "json", "req", "add", "My Requirement"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"]["id"] == "REQ-1"
        assert data["data"]["title"] == "My Requirement"

    def test_add_with_options(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "req", "add", "Feature",
            "--description", "A feature",
            "--status", "approved",
            "--priority", "high",
            "--label", "mvp",
            "--label", "backend",
            "--meta", "owner=alice",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["status"] == "approved"
        assert data["priority"] == "high"
        assert data["labels"] == ["mvp", "backend"]
        assert data["metadata"] == {"owner": "alice"}

    def test_add_with_parent(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Parent"])
        result = runner.invoke(cli, [
            "--format", "json", "req", "add", "Child", "--parent", "REQ-1"
        ])
        data = json.loads(result.output)["data"]
        assert data["parent"] == "REQ-1"

    def test_add_custom_prefix(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "req", "add", "Feature", "--prefix", "FEAT"
        ])
        data = json.loads(result.output)["data"]
        assert data["id"] == "FEAT-1"

    def test_add_increments_id(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "First"])
        result = runner.invoke(cli, ["--format", "json", "req", "add", "Second"])
        data = json.loads(result.output)["data"]
        assert data["id"] == "REQ-2"


class TestReqShow:
    def test_show(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Test Req"])
        result = runner.invoke(cli, ["--format", "json", "req", "show", "REQ-1"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == "REQ-1"

    def test_show_not_found(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, ["req", "show", "REQ-99"])
        assert result.exit_code != 0


class TestReqList:
    def test_list_all(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "A"])
        runner.invoke(cli, ["req", "add", "B"])
        result = runner.invoke(cli, ["--format", "json", "req", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 2

    def test_list_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, ["--format", "json", "req", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == []

    def test_list_filter_status(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Draft"])
        runner.invoke(cli, ["req", "add", "Approved", "--status", "approved"])
        result = runner.invoke(cli, ["--format", "json", "req", "list", "--status", "approved"])
        data = json.loads(result.output)
        assert len(data) == 1
        assert data[0]["status"] == "approved"

    def test_list_filter_label(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "A", "--label", "mvp"])
        runner.invoke(cli, ["req", "add", "B", "--label", "later"])
        result = runner.invoke(cli, ["--format", "json", "req", "list", "--label", "mvp"])
        data = json.loads(result.output)
        assert len(data) == 1

    def test_list_orphans(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Root"])
        runner.invoke(cli, ["req", "add", "Child", "--parent", "REQ-1"])
        result = runner.invoke(cli, ["--format", "json", "req", "list", "--orphans"])
        data = json.loads(result.output)
        assert len(data) == 1
        assert data[0]["id"] == "REQ-1"


class TestReqEdit:
    def test_edit_title(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Original"])
        result = runner.invoke(cli, [
            "--format", "json", "req", "edit", "REQ-1", "--title", "Updated"
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["title"] == "Updated"

    def test_edit_status_and_priority(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Test"])
        result = runner.invoke(cli, [
            "--format", "json", "req", "edit", "REQ-1",
            "--status", "approved", "--priority", "critical"
        ])
        data = json.loads(result.output)["data"]
        assert data["status"] == "approved"
        assert data["priority"] == "critical"

    def test_edit_labels(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Test", "--label", "old"])
        result = runner.invoke(cli, [
            "--format", "json", "req", "edit", "REQ-1",
            "--add-label", "new", "--remove-label", "old"
        ])
        data = json.loads(result.output)["data"]
        assert "new" in data["labels"]
        assert "old" not in data["labels"]

    def test_edit_parent(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Parent"])
        runner.invoke(cli, ["req", "add", "Child"])
        result = runner.invoke(cli, [
            "--format", "json", "req", "edit", "REQ-2", "--parent", "REQ-1"
        ])
        data = json.loads(result.output)["data"]
        assert data["parent"] == "REQ-1"

    def test_edit_clear_parent(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Parent"])
        runner.invoke(cli, ["req", "add", "Child", "--parent", "REQ-1"])
        result = runner.invoke(cli, [
            "--format", "json", "req", "edit", "REQ-2", "--clear-parent"
        ])
        data = json.loads(result.output)["data"]
        assert data["parent"] is None

    def test_edit_not_found(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, ["req", "edit", "REQ-99", "--title", "X"])
        assert result.exit_code != 0

    def test_edit_metadata(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Test", "--meta", "key=val"])
        result = runner.invoke(cli, [
            "--format", "json", "req", "edit", "REQ-1",
            "--set-meta", "new=data", "--remove-meta", "key"
        ])
        data = json.loads(result.output)["data"]
        assert data["metadata"] == {"new": "data"}


class TestReqAddJson:
    def test_add_from_json_string(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "req", "add",
            "--json", '{"title": "From JSON", "priority": "high"}'
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["title"] == "From JSON"
        assert data["priority"] == "high"
        assert data["status"] == "draft"  # default

    def test_add_from_stdin(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "req", "add", "--json", "-"
        ], input='{"title": "From Stdin"}')
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["title"] == "From Stdin"

    def test_cli_flag_overrides_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "req", "add", "CLI Title",
            "--json", '{"title": "JSON Title", "priority": "low"}',
            "--priority", "high"
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["title"] == "CLI Title"
        assert data["priority"] == "high"

    def test_missing_title_errors(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "req", "add",
            "--json", '{"description": "No title"}'
        ])
        assert result.exit_code != 0

    def test_invalid_json_errors(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "req", "add", "--json", "{bad"
        ])
        assert result.exit_code != 0

    def test_invalid_status_from_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "req", "add",
            "--json", '{"title": "T", "status": "bogus"}'
        ])
        assert result.exit_code != 0

    def test_invalid_priority_from_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "req", "add",
            "--json", '{"title": "T", "priority": "bogus"}'
        ])
        assert result.exit_code != 0

    def test_unknown_keys_ignored(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "req", "add",
            "--json", '{"title": "T", "unknown_field": 123}'
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["title"] == "T"

    def test_json_labels_and_metadata(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "req", "add",
            "--json", '{"title": "T", "labels": ["a", "b"], "metadata": {"k": "v"}}'
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["labels"] == ["a", "b"]
        assert data["metadata"] == {"k": "v"}


class TestReqEditJson:
    def test_edit_from_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Original"])
        result = runner.invoke(cli, [
            "--format", "json", "req", "edit", "REQ-1",
            "--json", '{"title": "Updated", "status": "approved"}'
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["title"] == "Updated"
        assert data["status"] == "approved"

    def test_edit_json_cli_override(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Original"])
        result = runner.invoke(cli, [
            "--format", "json", "req", "edit", "REQ-1",
            "--json", '{"title": "JSON Title", "priority": "low"}',
            "--title", "CLI Title"
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["title"] == "CLI Title"
        assert data["priority"] == "low"

    def test_edit_json_replaces_labels(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Test", "--label", "old"])
        result = runner.invoke(cli, [
            "--format", "json", "req", "edit", "REQ-1",
            "--json", '{"labels": ["new1", "new2"]}'
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["labels"] == ["new1", "new2"]

    def test_edit_cli_labels_win_over_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Test", "--label", "old"])
        result = runner.invoke(cli, [
            "--format", "json", "req", "edit", "REQ-1",
            "--json", '{"labels": ["json_label"]}',
            "--add-label", "cli_label"
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert "cli_label" in data["labels"]
        assert "old" in data["labels"]  # preserved since we used --add-label

    def test_edit_json_replaces_metadata(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Test", "--meta", "old=val"])
        result = runner.invoke(cli, [
            "--format", "json", "req", "edit", "REQ-1",
            "--json", '{"metadata": {"new": "data"}}'
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["metadata"] == {"new": "data"}

    def test_edit_invalid_status_from_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Test"])
        result = runner.invoke(cli, [
            "--format", "json", "req", "edit", "REQ-1",
            "--json", '{"status": "bogus"}'
        ])
        assert result.exit_code != 0


class TestReqDelete:
    def test_delete_json_no_confirm(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "To Delete"])
        result = runner.invoke(cli, ["--format", "json", "req", "delete", "REQ-1"])
        assert result.exit_code == 0
        # Verify it's gone
        result = runner.invoke(cli, ["--format", "json", "req", "list"])
        data = json.loads(result.output)
        assert len(data) == 0

    def test_delete_force(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "To Delete"])
        result = runner.invoke(cli, ["req", "delete", "REQ-1", "--force"])
        assert result.exit_code == 0

    def test_delete_not_found(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, ["--format", "json", "req", "delete", "REQ-99"])
        assert result.exit_code != 0


class TestReqTree:
    def test_tree_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Root"])
        runner.invoke(cli, ["req", "add", "Child", "--parent", "REQ-1"])
        result = runner.invoke(cli, ["--format", "json", "req", "tree"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 2

    def test_tree_subtree(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Root1"])
        runner.invoke(cli, ["req", "add", "Child1", "--parent", "REQ-1"])
        runner.invoke(cli, ["req", "add", "Root2"])
        result = runner.invoke(cli, ["--format", "json", "req", "tree", "REQ-1"])
        data = json.loads(result.output)
        ids = [r["id"] for r in data]
        assert "REQ-1" in ids
        assert "REQ-2" in ids
        assert "REQ-3" not in ids
