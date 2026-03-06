"""Path helpers for .rcli/ storage."""

from __future__ import annotations

from pathlib import Path


RCLI_DIR = ".rcli"
METADATA_FILE = "metadata.json"
REQUIREMENTS_DIR = "requirements"
DECISIONS_DIR = "decisions"


def find_rcli_root(start: Path | None = None) -> Path | None:
    """Walk up from start (default CWD) to find a directory containing .rcli/."""
    current = start or Path.cwd()
    current = current.resolve()
    while True:
        if (current / RCLI_DIR).is_dir():
            return current / RCLI_DIR
        parent = current.parent
        if parent == current:
            return None
        current = parent


def rcli_dir(root: Path) -> Path:
    return root


def metadata_path(root: Path) -> Path:
    return root / METADATA_FILE


def requirements_dir(root: Path) -> Path:
    return root / REQUIREMENTS_DIR


def decisions_dir(root: Path) -> Path:
    return root / DECISIONS_DIR


def requirement_path(root: Path, req_id: str) -> Path:
    return requirements_dir(root) / f"{req_id}.json"


def decision_path(root: Path, dec_id: str) -> Path:
    return decisions_dir(root) / f"{dec_id}.json"
