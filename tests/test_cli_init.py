"""Tests for init command."""

import json
from click.testing import CliRunner

from rcli.cli import cli


class TestInitCommand:
    def test_init_creates_structure(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--name", "test-project"])
        assert result.exit_code == 0
        assert (tmp_path / ".rcli").is_dir()
        assert (tmp_path / ".rcli" / "metadata.json").exists()
        assert (tmp_path / ".rcli" / "requirements").is_dir()
        assert (tmp_path / ".rcli" / "decisions").is_dir()

    def test_init_creates_skill_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--name", "test"])
        assert result.exit_code == 0
        skill = tmp_path / ".claude" / "skills" / "rcli" / "SKILL.md"
        assert skill.exists()
        content = skill.read_text()
        assert "--format json" in content

    def test_init_metadata(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        runner.invoke(cli, ["init", "--name", "my-project"])
        meta = json.loads((tmp_path / ".rcli" / "metadata.json").read_text())
        assert meta["project_name"] == "my-project"
        assert meta["version"] == "1"

    def test_init_json_output(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["--format", "json", "init", "--name", "test"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "message" in data

    def test_init_idempotent(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        runner.invoke(cli, ["init", "--name", "first"])
        result = runner.invoke(cli, ["init", "--name", "second"])
        assert result.exit_code == 0
