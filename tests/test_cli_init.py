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

    def test_init_creates_skill_file_in_default_location(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--name", "test"])
        assert result.exit_code == 0
        skill = tmp_path / ".agents" / "skills" / "rcli" / "SKILL.md"
        assert skill.exists()
        content = skill.read_text()
        assert "name: rcli" in content
        assert "--format json" in content

    def test_init_skill_file_has_valid_frontmatter(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        runner.invoke(cli, ["init", "--name", "test"])
        content = (tmp_path / ".agents" / "skills" / "rcli" / "SKILL.md").read_text()
        assert content.startswith("---\n")
        assert "name: rcli" in content
        assert "description:" in content

    def test_init_custom_skill_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--name", "test", "--skill-dir", ".claude/skills"])
        assert result.exit_code == 0
        skill = tmp_path / ".claude" / "skills" / "rcli" / "SKILL.md"
        assert skill.exists()
        assert "--format json" in skill.read_text()

    def test_init_custom_skill_dir_absolute(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        custom_dir = tmp_path / "my" / "skills"
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--name", "test", "--skill-dir", str(custom_dir)])
        assert result.exit_code == 0
        assert (custom_dir / "rcli" / "SKILL.md").exists()

    def test_init_does_not_create_old_tool_files(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        runner.invoke(cli, ["init", "--name", "test"])
        assert not (tmp_path / "AGENTS.md").exists()
        assert not (tmp_path / "OPENCODE.md").exists()

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

    def test_init_overwrites_skill_on_reinit(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        runner.invoke(cli, ["init", "--name", "first"])
        skill = tmp_path / ".agents" / "skills" / "rcli" / "SKILL.md"
        skill.write_text("old content")
        runner.invoke(cli, ["init", "--name", "second"])
        assert "old content" not in skill.read_text()
        assert "rcli" in skill.read_text()
