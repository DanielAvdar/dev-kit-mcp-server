"""Tests for the GitHubRepoOperation class."""

from typing import Any, Dict
from unittest.mock import patch

import pytest

from dev_kit_mcp_server.tools.github import GitHubRepoOperation


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expected_result",
    [
        # Test case: Get repository information
        {
            "status": "success",
            "message_contains": "Successfully retrieved repository information",
            "repo_name": "test-repo",
            "repo_full_name": "test-owner/test-repo",
        },
    ],
    ids=["repo_info"],
)
async def test_github_repo_operation(
    github_repo_operation: GitHubRepoOperation,
    expected_result: Dict[str, Any],
):
    """Test the GitHubRepoOperation class with various scenarios."""
    # Mock get_repo_info to return a valid repo info
    with patch.object(github_repo_operation, "get_repo_info", return_value=("test-owner", "test-repo")):
        # Execute: Get repository information
        result = await github_repo_operation()

    # Verify: Check the result
    assert result["status"] == expected_result["status"]
    assert expected_result["message_contains"] in result["message"]
    assert result["repo"]["name"] == expected_result["repo_name"]
    assert result["repo"]["full_name"] == expected_result["repo_full_name"]


@pytest.mark.asyncio
async def test_github_repo_operation_no_git_remote(github_repo_operation: GitHubRepoOperation):
    """Test the GitHubRepoOperation class with no git remote."""
    # Mock get_repo_info to return None to simulate no git remote
    with patch.object(github_repo_operation, "get_repo_info", return_value=None):
        # Try to get repository information with no git remote
        with pytest.raises(ValueError, match="Repository information could not be extracted from git remote"):
            await github_repo_operation()


@pytest.mark.asyncio
async def test_github_repo_operation_exception(temp_dir, mock_github_error):
    """Test the GitHubRepoOperation class when an exception occurs."""
    # Create the operation with the mock that raises an exception
    operation = GitHubRepoOperation(root_dir=temp_dir, token="test-token")

    # Mock get_repo_info to return a valid repo info
    with patch.object(operation, "get_repo_info", return_value=("test-owner", "test-repo")):
        # Attempt to get repository information
        result = await operation()

        # Check the result
        assert "error" in result
        assert "Error retrieving repository information" in result["error"]
        assert result["repo_name"] == "test-repo"
        assert result["owner"] == "test-owner"


@pytest.mark.asyncio
async def test_github_repo_operation_import_error(temp_dir):
    """Test the GitHubRepoOperation class when PyGithub is not installed."""
    # Mock the import to raise an ImportError
    with patch.dict("sys.modules", {"github": None}):
        # Create the operation
        operation = GitHubRepoOperation(root_dir=temp_dir, token="test-token")

        # Mock get_repo_info to return a valid repo info
        with patch.object(operation, "get_repo_info", return_value=("test-owner", "test-repo")):
            # Attempt to get repository information
            with pytest.raises(ImportError, match="The PyGithub package is not installed"):
                await operation()
