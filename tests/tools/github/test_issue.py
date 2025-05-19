"""Tests for the GitHubIssueOperation class."""

from typing import Any, Dict, List, Optional
from unittest.mock import patch

import pytest

from dev_kit_gh_mcp_server.tools import GitHubIssueOperation


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "issue_number,state,labels,expected_result",
    [
        # Test case 1: Get a specific issue
        (
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
    issue_number: Optional[int],
    state: str,
    labels: Optional[List[str]],
    expected_result: Dict[str, Any],
):
    """Test the GitHubIssueOperation class with various scenarios."""
    # Mock get_repo_info to return a valid repo info
    with patch.object(github_issue_operation, "get_repo_info", return_value=("test-owner", "test-repo")):
        # Execute: Get issue information
        result = await github_issue_operation(issue_number=issue_number, state=state, labels=labels)

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
async def test_github_issue_operation_no_git_remote(github_issue_operation: GitHubIssueOperation):
    """Test the GitHubIssueOperation class with no git remote."""
    # Mock get_repo_info to return None to simulate no git remote
    with patch.object(github_issue_operation, "get_repo_info", return_value=None):
        # Try to get issue information with no git remote
        with pytest.raises(ValueError, match="Repository information could not be extracted from git remote"):
            await github_issue_operation()


@pytest.mark.asyncio
async def test_github_issue_operation_exception(temp_dir, mock_github_error):
    """Test the GitHubIssueOperation class when an exception occurs."""
    # Create the operation with the mock that raises an exception
    operation = GitHubIssueOperation(root_dir=temp_dir, token="test-token")

    # Mock get_repo_info to return a valid repo info
    with patch.object(operation, "get_repo_info", return_value=("test-owner", "test-repo")):
        # Attempt to get issue information
        with pytest.raises(Exception, match="Simulated error"):
            await operation(issue_number=1)


@pytest.mark.asyncio
async def test_github_issue_operation_import_error(temp_dir):
    """Test the GitHubIssueOperation class when PyGithub is not installed."""
    # Mock the import to raise an ImportError
    with patch.dict("sys.modules", {"github": None}):
        # Create the operation
        operation = GitHubIssueOperation(root_dir=temp_dir, token="test-token")

        # Mock get_repo_info to return a valid repo info
        with patch.object(operation, "get_repo_info", return_value=("test-owner", "test-repo")):
            # Attempt to get issue information
            with pytest.raises(ImportError, match="The PyGithub package is not installed"):
                await operation()
