"""Tests for the GitCommitOperation class."""

from unittest.mock import patch

import pytest
from git import Repo

from dev_kit_mcp_server.tools.git import GitCommitOperation


@pytest.fixture
def git_commit_operation(temp_dir_git: str) -> GitCommitOperation:
    """Create a GitCommitOperation instance for testing."""
    return GitCommitOperation(root_dir=temp_dir_git)


@pytest.mark.asyncio
async def test_git_commit_operation(git_commit_operation: GitCommitOperation):
    """Test the GitCommitOperation class with a valid commit message."""
    # Mock the repository
    with patch.object(git_commit_operation, "_repo") as mock_repo:
        # Set up the git.commit method to return a commit hash
        mock_repo.git.commit.return_value = "abcdef1234567890"

        # Commit changes
        result = await git_commit_operation("Test commit message")

    # Check the result
    assert result["status"] == "success"
    assert "Successfully committed changes: Test commit message" in result["message"]
    assert result["commit"] == "abcdef1234567890"

    # Verify the commit method was called with the right parameters
    mock_repo.git.commit.assert_called_once_with(m="Test commit message")


@pytest.mark.asyncio
async def test_git_commit_operation_empty_message(git_commit_operation: GitCommitOperation):
    """Test the GitCommitOperation class with an empty commit message."""
    # Mock the repository
    with patch.object(git_commit_operation, "_repo") as mock_repo:
        # Commit changes with an empty message
        result = await git_commit_operation("")

    # Check the result
    assert "error" in result
    assert result["error"] == "Commit message cannot be empty"

    # Verify the commit method was not called
    mock_repo.git.commit.assert_not_called()


@pytest.mark.asyncio
async def test_git_commit_operation_exception(git_commit_operation: GitCommitOperation):
    """Test the GitCommitOperation class when an exception occurs."""
    # Mock the repository
    with patch.object(git_commit_operation, "_repo") as mock_repo:
        # Set up the git.commit method to raise an exception
        mock_repo.git.commit.side_effect = Exception("No changes to commit")

        # Attempt to commit changes - should raise the exception
        with pytest.raises(Exception, match="No changes to commit"):
            await git_commit_operation("Test commit message")


@pytest.mark.asyncio
async def test_git_commit_operation_real_repo(temp_dir_git: str):
    """Test the GitCommitOperation class with a real repository."""
    # Create a real GitCommitOperation instance
    operation = GitCommitOperation(root_dir=temp_dir_git)

    # Create a new file to commit
    from pathlib import Path

    test_file = Path(temp_dir_git) / "test_commit_file.txt"
    test_file.write_text("This is a test file for commit operation.")

    # Add the file to the index
    repo = Repo(temp_dir_git)
    repo.git.add(str(test_file))

    # Commit the changes
    result = await operation("Test commit from real repo")

    # Check the result
    assert result["status"] == "success"
    assert "Successfully committed changes: Test commit from real repo" in result["message"]
    assert result["commit"] is not None

    # Verify the commit was actually made
    repo = Repo(temp_dir_git)
    assert repo.head.commit.message.strip() == "Test commit from real repo"
