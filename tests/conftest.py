"""Shared test fixtures."""

import pytest
from pathlib import Path

from rcli.storage.store import Store
from rcli.models.requirement import Requirement
from rcli.models.decision import Decision


@pytest.fixture
def rcli_dir(tmp_path):
    """Create and return a .rcli/ directory path."""
    d = tmp_path / ".rcli"
    return d


@pytest.fixture
def store(rcli_dir):
    """Create an initialized Store."""
    s = Store(rcli_dir)
    s.init_project(project_name="test-project")
    return s


@pytest.fixture
def sample_req():
    """A sample requirement."""
    return Requirement(
        id="REQ-1",
        title="Test Requirement",
        description="A test requirement",
        status="draft",
        priority="high",
        labels=["mvp", "backend"],
    )


@pytest.fixture
def sample_decision():
    """A sample decision."""
    return Decision(
        id="ADR-1",
        title="Test Decision",
        context="We need to decide",
        decision="We decided this",
        rationale="Because reasons",
        status="active",
        linked_requirements=["REQ-1"],
    )
