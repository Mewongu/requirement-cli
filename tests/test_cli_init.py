"""Tests for init command."""

import json
from click.testing import CliRunner

from rcli.cli import cli
from rcli.skill import SECTION_MARKER_START, SECTION_MARKER_END


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

    def test_init_creates_skill_file_by_default(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--name", "test"])
        assert result.exit_code == 0
        skill = tmp_path / ".claude" / "skills" / "rcli" / "SKILL.md"
        assert skill.exists()
        content = skill.read_text()
        assert "--format json" in content
        # Should not create other files by default
        assert not (tmp_path / "AGENTS.md").exists()
        assert not (tmp_path / "OPENCODE.md").exists()

    def test_init_tool_codex(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--name", "test", "--tool", "codex"])
        assert result.exit_code == 0
        agents = tmp_path / "AGENTS.md"
        assert agents.exists()
        content = agents.read_text()
        assert "--format json" in content
        # Should not create claude skill when only codex requested
        assert not (tmp_path / ".claude").exists()

    def test_init_tool_opencode(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--name", "test", "--tool", "opencode"])
        assert result.exit_code == 0
        opencode = tmp_path / "OPENCODE.md"
        assert opencode.exists()
        content = opencode.read_text()
        assert "--format json" in content
        assert not (tmp_path / ".claude").exists()

    def test_init_multiple_tools(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, [
            "init", "--name", "test",
            "--tool", "claude", "--tool", "codex", "--tool", "opencode",
        ])
        assert result.exit_code == 0
        assert (tmp_path / ".claude" / "skills" / "rcli" / "SKILL.md").exists()
        assert (tmp_path / "AGENTS.md").exists()
        assert (tmp_path / "OPENCODE.md").exists()

    def test_init_merges_into_existing_agents_md(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        agents = tmp_path / "AGENTS.md"
        agents.write_text("# My Project\n\nExisting instructions here.\n")
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--name", "test", "--tool", "codex"])
        assert result.exit_code == 0
        content = agents.read_text()
        assert "Existing instructions here." in content
        assert "--format json" in content
        assert SECTION_MARKER_START in content

    def test_init_replaces_rcli_section_on_reinit(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        runner.invoke(cli, ["init", "--name", "first", "--tool", "codex"])
        # Add extra content after the section
        agents = tmp_path / "AGENTS.md"
        content = agents.read_text()
        agents.write_text(content + "\n# Other Tool\n\nKeep this.\n")
        # Re-init
        runner.invoke(cli, ["init", "--name", "second", "--tool", "codex"])
        content = agents.read_text()
        assert content.count(SECTION_MARKER_START) == 1
        assert "Keep this." in content

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

    def test_init_shared_content_across_tools(self, tmp_path, monkeypatch):
        """All three files contain the same core instructions."""
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        runner.invoke(cli, [
            "init", "--name", "test",
            "--tool", "claude", "--tool", "codex", "--tool", "opencode",
        ])
        skill = (tmp_path / ".claude" / "skills" / "rcli" / "SKILL.md").read_text()
        agents = (tmp_path / "AGENTS.md").read_text()
        opencode = (tmp_path / "OPENCODE.md").read_text()
        for content in [skill, agents, opencode]:
            assert "rcli req add" in content
            assert "rcli decision add" in content
            assert "rcli search" in content
            assert "Workflow Guidelines" in content

    def test_init_invalid_tool(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--name", "test", "--tool", "invalid"])
        assert result.exit_code != 0
