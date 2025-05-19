"""Tests for the FastMCP server."""

from pathlib import Path

import pytest
from git import Repo


@pytest.fixture(scope="function")
def temp_dir(tmp_path) -> str:
    """Create a temporary directory for testing."""
    Repo.init(tmp_path)
    return Path(tmp_path).as_posix()
