"""Tests for formatters."""

import json

from rcli.models.requirement import Requirement
from rcli.models.decision import Decision
from rcli.formatters.json_fmt import JsonFormatter
from rcli.formatters.markdown import MarkdownFormatter
from rcli.formatters.html import HtmlFormatter


class TestJsonFormatter:
    def test_output_item(self, capsys, sample_req):
        fmt = JsonFormatter()
        fmt.output_item(sample_req)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["id"] == "REQ-1"
        assert data["title"] == "Test Requirement"

    def test_output_list(self, capsys):
        fmt = JsonFormatter()
        reqs = [
            Requirement(id="REQ-1", title="A"),
            Requirement(id="REQ-2", title="B"),
        ]
        fmt.output_list(reqs)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert len(data) == 2

    def test_output_search(self, capsys, sample_req):
        fmt = JsonFormatter()
        fmt.output_search([(2, sample_req)])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert len(data) == 1
        assert data[0]["score"] == 2

    def test_output_message(self, capsys, sample_req):
        fmt = JsonFormatter()
        fmt.output_message("Created REQ-1", sample_req)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["message"] == "Created REQ-1"
        assert data["data"]["id"] == "REQ-1"

    def test_output_status(self, capsys):
        fmt = JsonFormatter()
        status_data = {"project_name": "test", "sections": {}, "totals": {}}
        fmt.output_status(status_data)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["project_name"] == "test"


class TestMarkdownFormatter:
    def test_output_requirement(self, capsys, sample_req):
        fmt = MarkdownFormatter()
        fmt.output_item(sample_req)
        out = capsys.readouterr().out
        assert "## REQ-1: Test Requirement" in out
        assert "**Status:** draft" in out
        assert "**Priority:** high" in out

    def test_output_decision(self, capsys, sample_decision):
        fmt = MarkdownFormatter()
        fmt.output_item(sample_decision)
        out = capsys.readouterr().out
        assert "## ADR-1: Test Decision" in out
        assert "### Context" in out

    def test_format_export(self, sample_req, sample_decision):
        fmt = MarkdownFormatter()
        content = fmt.format_export([sample_req], [sample_decision])
        assert "# Requirements Export" in content
        assert "REQ-1" in content
        assert "ADR-1" in content


class TestHtmlFormatter:
    def test_output_requirement(self, capsys, sample_req):
        fmt = HtmlFormatter()
        fmt.output_item(sample_req)
        out = capsys.readouterr().out
        assert "<!DOCTYPE html>" in out
        assert "REQ-1" in out
        assert "Test Requirement" in out

    def test_output_decision(self, capsys, sample_decision):
        fmt = HtmlFormatter()
        fmt.output_item(sample_decision)
        out = capsys.readouterr().out
        assert "<!DOCTYPE html>" in out
        assert "ADR-1" in out

    def test_format_export(self, sample_req, sample_decision):
        fmt = HtmlFormatter()
        content = fmt.format_export([sample_req], [sample_decision])
        assert "<!DOCTYPE html>" in content
        assert "REQ-1" in content
        assert "ADR-1" in content

    def test_html_escaping(self, capsys):
        req = Requirement(id="REQ-1", title="<script>alert('xss')</script>")
        fmt = HtmlFormatter()
        fmt.output_item(req)
        out = capsys.readouterr().out
        assert "<script>" not in out
        assert "&lt;script&gt;" in out
