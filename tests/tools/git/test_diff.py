"""Tests for the GitDiffOperation class."""

from unittest.mock import patch

import pytest

from dev_kit_mcp_server.tools.git import GitDiffOperation


@pytest.fixture
def git_diff_operation(temp_dir_git: str) -> GitDiffOperation:
    """Create a GitDiffOperation instance for testing."""
    return GitDiffOperation(root_dir=temp_dir_git)


@pytest.mark.asyncio
async def test_git_diff_operation(git_diff_operation: GitDiffOperation):
    """Test the GitDiffOperation class with a normal repository."""
    # Mock the repository
    with patch.object(git_diff_operation, "_repo") as mock_repo:
        # Set up the git.diff method to return a diff output
        mock_repo.git.diff.return_value = "diff --git a/file.txt b/file.txt\nindex 1234567..abcdef0 100644\n--- a/file.txt\n+++ b/file.txt\n@@ -1,3 +1,4 @@\n Line 1\n-Line 2\n+Line 2 modified\n+Line 3 added\n Line 4"  # noqa

        # Get the diff
        result = await git_diff_operation("file.txt")

    # Check the result
    assert result["status"] == "success"
    assert "Successfully generated diff for 'file.txt'" in result["message"]
    assert "diff --git" in result["diff"]
    assert "Line 2 modified" in result["diff"]


@pytest.mark.asyncio
async def test_git_diff_operation_with_options(git_diff_operation: GitDiffOperation):
    """Test the GitDiffOperation class with options."""
    # Mock the repository
    with patch.object(git_diff_operation, "_repo") as mock_repo:
        # Set up the git.diff method to return a diff output
        mock_repo.git.diff.return_value = "diff --git a/file.txt b/file.txt\nindex 1234567..abcdef0 100644\n--- a/file.txt\n+++ b/file.txt\n@@ -1,3 +1,4 @@\n Line 1\n-Line 2\n+Line 2 modified\n+Line 3 added\n Line 4"  # noqa

        # Get the diff with options
        result = await git_diff_operation("file.txt", options="--stat")

    # Check the result
    assert result["status"] == "success"
    assert "Successfully generated diff for 'file.txt'" in result["message"]

    # Verify that the options were passed to git.diff
    mock_repo.git.diff.assert_called_once_with("--stat", "file.txt")


@pytest.mark.asyncio
async def test_git_diff_operation_empty_path(git_diff_operation: GitDiffOperation):
    """Test the GitDiffOperation class with an empty path."""
    # Try to get diff with an empty path
    with pytest.raises(ValueError, match="Path or commit must be provided"):
        await git_diff_operation("")


@pytest.mark.asyncio
async def test_git_diff_operation_exception(git_diff_operation: GitDiffOperation, mock_repo_error):
    """Test the GitDiffOperation class when an exception occurs."""
    # Apply the mock to simulate an error
    mock_repo_error(git_diff_operation)

    # Attempt to get diff - should raise the simulated error
    with pytest.raises(Exception, match="Simulated error"):
        await git_diff_operation("file.txt")


@pytest.mark.asyncio
async def test_git_diff_operation_real_repo(temp_dir_git: str):
    """Test the GitDiffOperation class with a real repository."""
    # Create a real GitDiffOperation instance
    operation = GitDiffOperation(root_dir=temp_dir_git)

    # Create a new file to diff
    from pathlib import Path

    test_file = Path(temp_dir_git) / "test_diff_file.txt"
    test_file.write_text("This is a test file for diff operation.")

    # Add the file to the index
    from git import Repo

    repo = Repo(temp_dir_git)
    repo.git.add(str(test_file))

    # Modify the file
    test_file.write_text("This is a modified test file for diff operation.")

    # Get the diff
    result = await operation(str(test_file))

    # Check the result
    assert result["status"] == "success"
    assert f"Successfully generated diff for '{test_file}'" in result["message"]
    assert "diff" in result["diff"]
    assert "This is a modified test file" in result["diff"]
