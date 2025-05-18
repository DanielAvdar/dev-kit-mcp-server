"""Tests for the GitHubRepoOperation class."""

from typing import Any, Dict, Optional
from unittest.mock import patch

import pytest

from dev_kit_mcp_server.tools.github import GitHubRepoOperation


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "repo_name,owner,expected_result",
    [
        # Test case 1: Get repository with owner
        (
            "test-repo",  # repo_name
            "test-owner",  # owner
            {
                "status": "success",
                "message_contains": "Successfully retrieved repository information",
                "repo_name": "test-repo",
                "repo_full_name": "test-owner/test-repo",
            },
        ),
        # Test case 2: Get repository without owner (uses authenticated user)
        (
            "test-repo",  # repo_name
            None,  # owner
            {
                "status": "success",
                "message_contains": "Successfully retrieved repository information",
                "repo_name": "test-repo",
                "repo_full_name": "test-owner/test-repo",
            },
        ),
    ],
    ids=["with_owner", "without_owner"],
)
async def test_github_repo_operation(
    github_repo_operation: GitHubRepoOperation,
    repo_name: str,
    owner: Optional[str],
    expected_result: Dict[str, Any],
):
    """Test the GitHubRepoOperation class with various scenarios."""
    # Execute: Get repository information
    result = await github_repo_operation(repo_name, owner=owner)

    # Verify: Check the result
    assert result["status"] == expected_result["status"]
    assert expected_result["message_contains"] in result["message"]
    assert result["repo"]["name"] == expected_result["repo_name"]
    assert result["repo"]["full_name"] == expected_result["repo_full_name"]


@pytest.mark.asyncio
async def test_github_repo_operation_empty_repo_name(github_repo_operation: GitHubRepoOperation):
    """Test the GitHubRepoOperation class with an empty repository name."""
    # Try to get repository information with an empty name
    with pytest.raises(ValueError, match="Repository name must be provided"):
        await github_repo_operation("")


@pytest.mark.asyncio
async def test_github_repo_operation_exception(temp_dir, mock_github_error):
    """Test the GitHubRepoOperation class when an exception occurs."""
    # Create the operation with the mock that raises an exception
    operation = GitHubRepoOperation(root_dir=temp_dir, token="test-token")

    # Attempt to get repository information
    result = await operation("test-repo", owner="test-owner")

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

        # Attempt to get repository information
        with pytest.raises(ImportError, match="The PyGithub package is not installed"):
            await operation("test-repo", owner="test-owner")
