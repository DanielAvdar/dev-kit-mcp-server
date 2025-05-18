"""Tests for the GitHubPROperation class."""

from typing import Any, Dict, Optional
from unittest.mock import patch

import pytest

from dev_kit_mcp_server.tools.github import GitHubPROperation


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "repo_name,owner,pr_number,state,expected_result",
    [
        # Test case 1: Get a specific pull request
        (
            "test-repo",  # repo_name
            "test-owner",  # owner
            1,  # pr_number
            "open",  # state
            {
                "status": "success",
                "message_contains": "Successfully retrieved PR #1",
                "pr_number": 1,
                "pr_title": "Test PR",
            },
        ),
        # Test case 2: Get all pull requests
        (
            "test-repo",  # repo_name
            "test-owner",  # owner
            None,  # pr_number
            "open",  # state
            {
                "status": "success",
                "message_contains": "Successfully retrieved",
                "prs_count": 1,
            },
        ),
    ],
    ids=["specific_pr", "all_prs"],
)
async def test_github_pr_operation(
    github_pr_operation: GitHubPROperation,
    repo_name: str,
    owner: str,
    pr_number: Optional[int],
    state: str,
    expected_result: Dict[str, Any],
):
    """Test the GitHubPROperation class with various scenarios."""
    # Execute: Get pull request information
    result = await github_pr_operation(repo_name, owner, pr_number=pr_number, state=state)

    # Verify: Check the result
    assert result["status"] == expected_result["status"]
    assert expected_result["message_contains"] in result["message"]

    if pr_number is not None:
        # Check specific pull request
        assert result["pr"]["number"] == expected_result["pr_number"]
        assert result["pr"]["title"] == expected_result["pr_title"]
    else:
        # Check all pull requests
        assert len(result["prs"]) == expected_result["prs_count"]


@pytest.mark.asyncio
async def test_github_pr_operation_empty_repo_name(github_pr_operation: GitHubPROperation):
    """Test the GitHubPROperation class with an empty repository name."""
    # Try to get pull request information with an empty repository name
    with pytest.raises(ValueError, match="Repository name must be provided"):
        await github_pr_operation("", "test-owner")


@pytest.mark.asyncio
async def test_github_pr_operation_empty_owner(github_pr_operation: GitHubPROperation):
    """Test the GitHubPROperation class with an empty owner."""
    # Try to get pull request information with an empty owner
    with pytest.raises(ValueError, match="Repository owner must be provided"):
        await github_pr_operation("test-repo", "")


@pytest.mark.asyncio
async def test_github_pr_operation_exception(temp_dir, mock_github_error):
    """Test the GitHubPROperation class when an exception occurs."""
    # Create the operation with the mock that raises an exception
    operation = GitHubPROperation(root_dir=temp_dir, token="test-token")

    # Attempt to get pull request information
    result = await operation("test-repo", "test-owner", pr_number=1)

    # Check the result
    assert "error" in result
    assert "Error retrieving pull requests" in result["error"]
    assert result["repo_name"] == "test-repo"
    assert result["owner"] == "test-owner"
    assert result["pr_number"] == 1


@pytest.mark.asyncio
async def test_github_pr_operation_import_error(temp_dir):
    """Test the GitHubPROperation class when PyGithub is not installed."""
    # Mock the import to raise an ImportError
    with patch.dict("sys.modules", {"github": None}):
        # Create the operation
        operation = GitHubPROperation(root_dir=temp_dir, token="test-token")

        # Attempt to get pull request information
        with pytest.raises(ImportError, match="The PyGithub package is not installed"):
            await operation("test-repo", "test-owner")
