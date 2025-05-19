"""Tests for the GitStatusOperation class."""

from unittest.mock import MagicMock, patch

import pytest
from git import DiffIndex

from dev_kit_mcp_server.tools.git import GitStatusOperation


@pytest.fixture
def git_status_operation(temp_dir_git: str) -> GitStatusOperation:
    """Create a GitStatusOperation instance for testing."""
    return GitStatusOperation(root_dir=temp_dir_git)


@pytest.mark.asyncio
async def test_git_status_operation(git_status_operation: GitStatusOperation):
    """Test the GitStatusOperation class with a normal repository."""
    # Mock the repository
    with patch.object(git_status_operation, "_repo") as mock_repo:
        # Set up the active branch
        mock_branch = MagicMock()
        mock_branch.name = "main"
        type(mock_repo).active_branch = mock_branch

        # Set up empty diffs for changed and staged files
        mock_diff_index = MagicMock(spec=DiffIndex)
        mock_diff_index.__iter__.return_value = []
        mock_repo.index.diff.return_value = mock_diff_index

        # Set up empty untracked files
        mock_repo.untracked_files = []

        # Get the status
        result = await git_status_operation()

    # Check the result
    assert result["status"] == "success"
    assert result["branch"] == "main"
    assert isinstance(result["changed_files"], list)
    assert len(result["changed_files"]) == 0
    assert isinstance(result["untracked_files"], list)
    assert len(result["untracked_files"]) == 0
    assert isinstance(result["staged_files"], list)
    assert len(result["staged_files"]) == 0


@pytest.mark.asyncio
async def test_git_status_operation_with_changes(git_status_operation: GitStatusOperation):
    """Test the GitStatusOperation class with changes in the repository."""
    # Mock the repository
    with patch.object(git_status_operation, "_repo") as mock_repo:
        # Set up the active branch
        mock_branch = MagicMock()
        mock_branch.name = "feature-branch"
        type(mock_repo).active_branch = mock_branch

        # Set up diffs for changed files
        mock_changed_item1 = MagicMock()
        mock_changed_item1.a_path = "file1.txt"
        mock_changed_item1.change_type = "M"
        mock_changed_item2 = MagicMock()
        mock_changed_item2.a_path = "file2.txt"
        mock_changed_item2.change_type = "D"

        # Set up diffs for staged files
        mock_staged_item = MagicMock()
        mock_staged_item.a_path = "file3.txt"
        mock_staged_item.change_type = "A"

        # Configure the diff method to return different results based on the argument
        def mock_diff(arg):
            if arg is None:
                return [mock_changed_item1, mock_changed_item2]
            elif arg == "HEAD":
                return [mock_staged_item]
            return []

        mock_repo.index.diff = mock_diff

        # Set up untracked files
        mock_repo.untracked_files = ["new_file.txt", "another_new_file.txt"]

        # Get the status
        result = await git_status_operation()

    # Check the result
    assert result["status"] == "success"
    assert result["branch"] == "feature-branch"

    # Check changed files
    assert len(result["changed_files"]) == 2
    assert result["changed_files"][0]["path"] == "file1.txt"
    assert result["changed_files"][0]["change_type"] == "M"
    assert result["changed_files"][1]["path"] == "file2.txt"
    assert result["changed_files"][1]["change_type"] == "D"

    # Check untracked files
    assert len(result["untracked_files"]) == 2
    assert "new_file.txt" in result["untracked_files"]
    assert "another_new_file.txt" in result["untracked_files"]

    # Check staged files
    assert len(result["staged_files"]) == 1
    assert result["staged_files"][0]["path"] == "file3.txt"
    assert result["staged_files"][0]["change_type"] == "A"


@pytest.mark.asyncio
async def test_git_status_operation_detached_head(git_status_operation: GitStatusOperation):
    """Test the GitStatusOperation class with a detached HEAD."""
    # Mock the repository
    with patch.object(git_status_operation, "_repo") as mock_repo:
        # Set up the active_branch property to raise TypeError when accessed
        def active_branch_getter(self):
            raise TypeError("HEAD is detached")

        type(mock_repo).active_branch = property(active_branch_getter)

        # Set up empty diffs and untracked files
        mock_diff_index = MagicMock(spec=DiffIndex)
        mock_diff_index.__iter__.return_value = []
        mock_repo.index.diff.return_value = mock_diff_index
        mock_repo.untracked_files = []

        # Get the status
        result = await git_status_operation()

    # Check the result
    assert result["status"] == "success"
    assert result["branch"] == "DETACHED_HEAD"
    assert len(result["changed_files"]) == 0
    assert len(result["untracked_files"]) == 0
    assert len(result["staged_files"]) == 0


@pytest.mark.asyncio
async def test_git_status_operation_real_repo(temp_dir_git: str):
    """Test the GitStatusOperation class with a real repository."""
    # Create a real GitStatusOperation instance
    operation = GitStatusOperation(root_dir=temp_dir_git)

    # Get the status
    result = await operation()

    # Check the result
    assert result["status"] == "success"
    assert isinstance(result["branch"], str)
    assert isinstance(result["changed_files"], list)
    assert isinstance(result["untracked_files"], list)
    assert isinstance(result["staged_files"], list)
