"""Tests for decision CLI commands."""

import json
from click.testing import CliRunner

from rcli.cli import cli


def init_project(runner, tmp_path):
    runner.invoke(cli, ["init", "--name", "test"])


class TestDecisionAdd:
    def test_add_basic(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, ["--format", "json", "decision", "add", "Use REST"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"]["id"] == "ADR-1"

    def test_add_with_options(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "Auth"])
        result = runner.invoke(cli, [
            "--format", "json", "decision", "add", "Use JWT",
            "--context", "Need stateless auth",
            "--decision", "JWT tokens",
            "--rationale", "Scalable",
            "--link", "REQ-1",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["context"] == "Need stateless auth"
        assert data["linked_requirements"] == ["REQ-1"]

    def test_add_custom_prefix(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "decision", "add", "Decision", "--prefix", "DEC"
        ])
        data = json.loads(result.output)["data"]
        assert data["id"] == "DEC-1"


class TestDecisionShow:
    def test_show(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["decision", "add", "Test"])
        result = runner.invoke(cli, ["--format", "json", "decision", "show", "ADR-1"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == "ADR-1"

    def test_show_not_found(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, ["decision", "show", "ADR-99"])
        assert result.exit_code != 0


class TestDecisionList:
    def test_list_all(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["decision", "add", "A"])
        runner.invoke(cli, ["decision", "add", "B"])
        result = runner.invoke(cli, ["--format", "json", "decision", "list"])
        data = json.loads(result.output)
        assert len(data) == 2

    def test_list_filter_status(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["decision", "add", "Active"])
        runner.invoke(cli, ["decision", "add", "Old", "--status", "obsolete"])
        result = runner.invoke(cli, ["--format", "json", "decision", "list", "--status", "active"])
        data = json.loads(result.output)
        assert len(data) == 1
        assert data[0]["status"] == "active"


class TestDecisionEdit:
    def test_edit(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["decision", "add", "Original"])
        result = runner.invoke(cli, [
            "--format", "json", "decision", "edit", "ADR-1",
            "--title", "Updated", "--status", "obsolete"
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["title"] == "Updated"
        assert data["status"] == "obsolete"

    def test_edit_links(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["req", "add", "R1"])
        runner.invoke(cli, ["req", "add", "R2"])
        runner.invoke(cli, ["decision", "add", "Dec", "--link", "REQ-1"])
        result = runner.invoke(cli, [
            "--format", "json", "decision", "edit", "ADR-1",
            "--add-link", "REQ-2", "--remove-link", "REQ-1"
        ])
        data = json.loads(result.output)["data"]
        assert data["linked_requirements"] == ["REQ-2"]


class TestDecisionAddJson:
    def test_add_from_json_string(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "decision", "add",
            "--json", '{"title": "Use REST", "context": "Need API", "decision": "REST", "rationale": "Simple"}'
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["title"] == "Use REST"
        assert data["context"] == "Need API"
        assert data["decision"] == "REST"
        assert data["rationale"] == "Simple"

    def test_add_from_stdin(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "decision", "add", "--json", "-"
        ], input='{"title": "From Stdin"}')
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["title"] == "From Stdin"

    def test_cli_flag_overrides_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "decision", "add", "CLI Title",
            "--json", '{"title": "JSON Title", "context": "JSON ctx"}',
            "--context", "CLI ctx"
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["title"] == "CLI Title"
        assert data["context"] == "CLI ctx"

    def test_missing_title_errors(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "decision", "add",
            "--json", '{"context": "No title"}'
        ])
        assert result.exit_code != 0

    def test_invalid_json_errors(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "decision", "add", "--json", "{bad"
        ])
        assert result.exit_code != 0

    def test_invalid_status_from_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "decision", "add",
            "--json", '{"title": "T", "status": "bogus"}'
        ])
        assert result.exit_code != 0

    def test_unknown_keys_ignored(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "decision", "add",
            "--json", '{"title": "T", "unknown_field": 123}'
        ])
        assert result.exit_code == 0

    def test_json_linked_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        result = runner.invoke(cli, [
            "--format", "json", "decision", "add",
            "--json", '{"title": "T", "linked_requirements": ["REQ-1", "REQ-2"]}'
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["linked_requirements"] == ["REQ-1", "REQ-2"]


class TestDecisionEditJson:
    def test_edit_from_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["decision", "add", "Original"])
        result = runner.invoke(cli, [
            "--format", "json", "decision", "edit", "ADR-1",
            "--json", '{"title": "Updated", "status": "obsolete"}'
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["title"] == "Updated"
        assert data["status"] == "obsolete"

    def test_edit_json_cli_override(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["decision", "add", "Original"])
        result = runner.invoke(cli, [
            "--format", "json", "decision", "edit", "ADR-1",
            "--json", '{"title": "JSON Title", "context": "JSON ctx"}',
            "--title", "CLI Title"
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["title"] == "CLI Title"
        assert data["context"] == "JSON ctx"

    def test_edit_json_replaces_linked_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["decision", "add", "Dec", "--link", "REQ-1"])
        result = runner.invoke(cli, [
            "--format", "json", "decision", "edit", "ADR-1",
            "--json", '{"linked_requirements": ["REQ-2", "REQ-3"]}'
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["linked_requirements"] == ["REQ-2", "REQ-3"]

    def test_edit_cli_links_win_over_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["decision", "add", "Dec", "--link", "REQ-1"])
        result = runner.invoke(cli, [
            "--format", "json", "decision", "edit", "ADR-1",
            "--json", '{"linked_requirements": ["REQ-99"]}',
            "--add-link", "REQ-2"
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert "REQ-2" in data["linked_requirements"]
        assert "REQ-1" in data["linked_requirements"]

    def test_edit_invalid_status_from_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["decision", "add", "Test"])
        result = runner.invoke(cli, [
            "--format", "json", "decision", "edit", "ADR-1",
            "--json", '{"status": "bogus"}'
        ])
        assert result.exit_code != 0


class TestDecisionDelete:
    def test_delete_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        init_project(runner, tmp_path)
        runner.invoke(cli, ["decision", "add", "To Delete"])
        result = runner.invoke(cli, ["--format", "json", "decision", "delete", "ADR-1"])
        assert result.exit_code == 0
        result = runner.invoke(cli, ["--format", "json", "decision", "list"])
        data = json.loads(result.output)
        assert len(data) == 0
