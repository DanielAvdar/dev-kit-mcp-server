"""Tests for the FastMCP server."""

from pathlib import Path

import pytest
from git import Repo


@pytest.fixture(scope="function")
def temp_dir_git(temp_dir: str) -> str:
    """Create a temporary directory for testing."""
    repo = Repo(temp_dir)
    dummy_file = Path(temp_dir) / "dummy.txt"
    dummy_file.write_text("This is a dummy file.")
    repo.index.add([dummy_file])
    repo.index.commit("Add dummy file")
    return Path(temp_dir).as_posix()


def test_temp_dir_git(temp_dir_git):
    """Test the temporary directory fixture."""
    temp_repo = Repo(temp_dir_git)

    assert temp_repo is not None
    assert temp_repo.working_tree_dir is not None
    assert (Path(temp_repo.working_tree_dir) / "dummy.txt").exists()
    assert (Path(temp_repo.working_tree_dir) / "dummy.txt").read_text() == "This is a dummy file."
    assert temp_repo.head.commit.message == "Add dummy file"
