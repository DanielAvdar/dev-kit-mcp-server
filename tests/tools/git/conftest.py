"""Tests for the Git operations."""

from pathlib import Path
from typing import Any, Callable

import pytest
from git import Repo

from dev_kit_mcp_server.tools.git import (
    GitAddOperation,
    GitCheckoutOperation,
    GitCreateBranchOperation,
)


@pytest.fixture(scope="function")
def temp_dir_git(temp_dir: str) -> str:
    """Create a temporary directory for testing."""
    repo = Repo(temp_dir)
    cr = repo.config_writer(config_level="repository")
    cr.set_value("user", "name", "Test User")
    cr.set_value("user", "email", "TestUser@forgit.tests")
    dummy_file = Path(temp_dir) / "dummy.txt"
    dummy_file.write_text("This is a dummy file.")
    repo.index.add([dummy_file])
    repo.index.commit("Add dummy file")
    return Path(temp_dir).as_posix()


@pytest.fixture
def git_checkout_operation(temp_dir_git: str) -> GitCheckoutOperation:
    """Create a GitCheckoutOperation instance for testing."""
    return GitCheckoutOperation(root_dir=temp_dir_git)


@pytest.fixture
def git_create_branch_operation(temp_dir_git: str) -> GitCreateBranchOperation:
    """Create a GitCreateBranchOperation instance for testing."""
    return GitCreateBranchOperation(root_dir=temp_dir_git)


@pytest.fixture
def git_add_operation(temp_dir_git: str) -> GitAddOperation:
    """Create a GitAddOperation instance for testing."""
    return GitAddOperation(root_dir=temp_dir_git)


@pytest.fixture
def mock_repo_error() -> Callable[[Any], None]:
    """Create a mock repository that raises an exception when accessing git attribute."""

    class MockRepo:
        def __getattr__(self, name):
            if name == "git":
                raise Exception("Simulated error")
            return None

    def _apply_mock(operation: Any) -> None:
        operation._repo = MockRepo()

    return _apply_mock


def test_temp_dir_git(temp_dir_git):
    """Test the temporary directory fixture."""
    temp_repo = Repo(temp_dir_git)

    assert temp_repo is not None
    assert temp_repo.working_tree_dir is not None
    assert (Path(temp_repo.working_tree_dir) / "dummy.txt").exists()
    assert (Path(temp_repo.working_tree_dir) / "dummy.txt").read_text() == "This is a dummy file."
    assert temp_repo.head.commit.message == "Add dummy file"
