"""Tests for export, search, and status CLI commands."""

import json
from click.testing import CliRunner

from rcli.cli import cli


def setup_project(runner):
    runner.invoke(cli, ["init", "--name", "test"])
    runner.invoke(cli, ["req", "add", "Auth", "--label", "mvp", "--priority", "high"])
    runner.invoke(cli, ["req", "add", "OAuth", "--parent", "REQ-1", "--label", "mvp"])
    runner.invoke(cli, ["req", "add", "Logging", "--label", "ops", "--status", "approved"])
    runner.invoke(cli, [
        "decision", "add", "Use JWT",
        "--context", "Need tokens",
        "--decision", "JWT",
        "--rationale", "Scalable",
        "--link", "REQ-1",
    ])


class TestExport:
    def test_export_markdown(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        setup_project(runner)
        result = runner.invoke(cli, ["export", "--format", "markdown"])
        assert result.exit_code == 0
        assert "# Requirements Export" in result.output
        assert "REQ-1" in result.output
        assert "ADR-1" in result.output

    def test_export_html(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        setup_project(runner)
        result = runner.invoke(cli, ["export", "--format", "html"])
        assert result.exit_code == 0
        assert "<!DOCTYPE html>" in result.output

    def test_export_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        setup_project(runner)
        result = runner.invoke(cli, ["export", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "requirements" in data
        assert "decisions" in data
        assert len(data["requirements"]) == 3
        assert len(data["decisions"]) == 1

    def test_export_filter_type(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        setup_project(runner)
        result = runner.invoke(cli, ["export", "--format", "json", "--type", "req"])
        data = json.loads(result.output)
        assert len(data["requirements"]) == 3
        assert len(data["decisions"]) == 0

    def test_export_filter_status(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        setup_project(runner)
        result = runner.invoke(cli, ["export", "--format", "json", "--status", "approved"])
        data = json.loads(result.output)
        assert len(data["requirements"]) == 1
        assert data["requirements"][0]["id"] == "REQ-3"

    def test_export_filter_label(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        setup_project(runner)
        result = runner.invoke(cli, ["export", "--format", "json", "--type", "req", "--label", "mvp"])
        data = json.loads(result.output)
        assert len(data["requirements"]) == 2

    def test_export_subtree(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        setup_project(runner)
        result = runner.invoke(cli, ["export", "--format", "json", "--type", "req", "--parent", "REQ-1"])
        data = json.loads(result.output)
        ids = [r["id"] for r in data["requirements"]]
        assert "REQ-1" in ids
        assert "REQ-2" in ids
        assert "REQ-3" not in ids

    def test_export_to_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        setup_project(runner)
        outfile = str(tmp_path / "out.md")
        result = runner.invoke(cli, ["export", "--format", "markdown", "--output", outfile])
        assert result.exit_code == 0
        content = (tmp_path / "out.md").read_text()
        assert "REQ-1" in content


class TestSearch:
    def test_search_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        setup_project(runner)
        result = runner.invoke(cli, ["--format", "json", "search", "Auth"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) >= 1
        assert any(d["id"] == "REQ-1" for d in data)

    def test_search_type_filter(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        setup_project(runner)
        result = runner.invoke(cli, ["--format", "json", "search", "JWT", "--type", "decision"])
        data = json.loads(result.output)
        assert all(d["id"].startswith("ADR") for d in data)

    def test_search_no_results(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        setup_project(runner)
        result = runner.invoke(cli, ["--format", "json", "search", "xyznonexistent"])
        data = json.loads(result.output)
        assert data == []


class TestStatus:
    def test_status_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        setup_project(runner)
        result = runner.invoke(cli, ["--format", "json", "status"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["project_name"] == "test"
        assert data["totals"]["requirements"] == 3
        assert data["totals"]["decisions"] == 1
        assert data["sections"]["Labels"]["mvp"] == 2

    def test_status_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        runner.invoke(cli, ["init", "--name", "empty"])
        result = runner.invoke(cli, ["--format", "json", "status"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["totals"]["requirements"] == 0
