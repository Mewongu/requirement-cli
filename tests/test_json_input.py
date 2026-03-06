"""Tests for json_input helpers."""

import click
import pytest
from click.testing import CliRunner

from rcli.commands.json_input import parse_json_input, _pick


class TestParseJsonInput:
    def _make_ctx(self):
        """Create a minimal Click context for testing."""
        @click.command()
        @click.pass_context
        def dummy(ctx):
            pass
        runner = CliRunner()
        # Invoke to get a real context, but we just need one for error_exit
        return click.Context(dummy)

    def test_none_returns_none(self):
        ctx = self._make_ctx()
        assert parse_json_input(None, ctx) is None

    def test_valid_json(self):
        ctx = self._make_ctx()
        result = parse_json_input('{"title": "Test", "priority": "high"}', ctx)
        assert result == {"title": "Test", "priority": "high"}

    def test_invalid_json(self):
        @click.command()
        @click.pass_context
        def cmd(ctx):
            parse_json_input("{bad json", ctx)
        runner = CliRunner()
        result = runner.invoke(cmd)
        assert result.exit_code != 0

    def test_array_rejected(self):
        @click.command()
        @click.pass_context
        def cmd(ctx):
            parse_json_input('[{"title": "A"}]', ctx)
        runner = CliRunner()
        result = runner.invoke(cmd)
        assert result.exit_code != 0

    def test_empty_object(self):
        ctx = self._make_ctx()
        result = parse_json_input('{}', ctx)
        assert result == {}


class TestPick:
    def test_cli_wins_over_json(self):
        assert _pick("cli_val", {"key": "json_val"}, "key", "default") == "cli_val"

    def test_json_wins_over_default(self):
        assert _pick(None, {"key": "json_val"}, "key", "default") == "json_val"

    def test_default_when_no_cli_no_json(self):
        assert _pick(None, {}, "key", "default") == "default"

    def test_default_when_no_json_data(self):
        assert _pick(None, None, "key", "default") == "default"

    def test_none_default(self):
        assert _pick(None, None, "key") is None

    def test_json_falsy_value_used(self):
        assert _pick(None, {"key": ""}, "key", "default") == ""

    def test_json_zero_value_used(self):
        assert _pick(None, {"key": 0}, "key", "default") == 0
