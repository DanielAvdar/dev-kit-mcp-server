"""Tests for the GitHubIssueOperation class."""

from typing import Any, Dict, List, Optional
from unittest.mock import patch

import pytest

from dev_kit_mcp_server.tools.github import GitHubIssueOperation


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "repo_name,owner,issue_number,state,labels,expected_result",
    [
        # Test case 1: Get a specific issue
        (
            "test-repo",  # repo_name
            "test-owner",  # owner
            1,  # issue_number
            "open",  # state
            None,  # labels
            {
                "status": "success",
                "message_contains": "Successfully retrieved issue #1",
                "issue_number": 1,
                "issue_title": "Test issue",
            },
        ),
        # Test case 2: Get all issues
        (
            "test-repo",  # repo_name
            "test-owner",  # owner
            None,  # issue_number
            "open",  # state
            None,  # labels
            {
                "status": "success",
                "message_contains": "Successfully retrieved",
                "issues_count": 1,
            },
        ),
    ],
    ids=["specific_issue", "all_issues"],
)
async def test_github_issue_operation(
    github_issue_operation: GitHubIssueOperation,
    repo_name: str,
    owner: str,
    issue_number: Optional[int],
    state: str,
    labels: Optional[List[str]],
    expected_result: Dict[str, Any],
):
    """Test the GitHubIssueOperation class with various scenarios."""
    # Execute: Get issue information
    result = await github_issue_operation(repo_name, owner, issue_number=issue_number, state=state, labels=labels)

    # Verify: Check the result
    assert result["status"] == expected_result["status"]
    assert expected_result["message_contains"] in result["message"]

    if issue_number is not None:
        # Check specific issue
        assert result["issue"]["number"] == expected_result["issue_number"]
        assert result["issue"]["title"] == expected_result["issue_title"]
    else:
        # Check all issues
        assert len(result["issues"]) == expected_result["issues_count"]


@pytest.mark.asyncio
async def test_github_issue_operation_empty_repo_name(github_issue_operation: GitHubIssueOperation):
    """Test the GitHubIssueOperation class with an empty repository name."""
    # Try to get issue information with an empty repository name
    with pytest.raises(ValueError, match="Repository name must be provided"):
        await github_issue_operation("", "test-owner")


@pytest.mark.asyncio
async def test_github_issue_operation_empty_owner(github_issue_operation: GitHubIssueOperation):
    """Test the GitHubIssueOperation class with an empty owner."""
    # Try to get issue information with an empty owner
    with pytest.raises(ValueError, match="Repository owner must be provided"):
        await github_issue_operation("test-repo", "")


@pytest.mark.asyncio
async def test_github_issue_operation_exception(temp_dir, mock_github_error):
    """Test the GitHubIssueOperation class when an exception occurs."""
    # Create the operation with the mock that raises an exception
    operation = GitHubIssueOperation(root_dir=temp_dir, token="test-token")

    # Attempt to get issue information
    result = await operation("test-repo", "test-owner", issue_number=1)

    # Check the result
    assert "error" in result
    assert "Error retrieving issues" in result["error"]
    assert result["repo_name"] == "test-repo"
    assert result["owner"] == "test-owner"
    assert result["issue_number"] == 1


@pytest.mark.asyncio
async def test_github_issue_operation_import_error(temp_dir):
    """Test the GitHubIssueOperation class when PyGithub is not installed."""
    # Mock the import to raise an ImportError
    with patch.dict("sys.modules", {"github": None}):
        # Create the operation
        operation = GitHubIssueOperation(root_dir=temp_dir, token="test-token")

        # Attempt to get issue information
        with pytest.raises(ImportError, match="The PyGithub package is not installed"):
            await operation("test-repo", "test-owner")
