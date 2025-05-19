"""Tests for the GitHubPROperation class."""

from typing import Any, Dict, Optional
from unittest.mock import patch

import pytest

from dev_kit_mcp_server.tools.github import GitHubPROperation


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "pr_number,state,expected_result",
    [
        # Test case 1: Get a specific pull request
        (
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
    pr_number: Optional[int],
    state: str,
    expected_result: Dict[str, Any],
):
    """Test the GitHubPROperation class with various scenarios."""
    # Mock get_repo_info to return a valid repo info
    with patch.object(github_pr_operation, "get_repo_info", return_value=("test-owner", "test-repo")):
        # Execute: Get pull request information
        result = await github_pr_operation(pr_number=pr_number, state=state)

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
async def test_github_pr_operation_no_git_remote(github_pr_operation: GitHubPROperation):
    """Test the GitHubPROperation class with no git remote."""
    # Mock get_repo_info to return None to simulate no git remote
    with patch.object(github_pr_operation, "get_repo_info", return_value=None):
        # Try to get pull request information with no git remote
        with pytest.raises(ValueError, match="Repository information could not be extracted from git remote"):
            await github_pr_operation(pr_number=1)


@pytest.mark.asyncio
async def test_github_pr_operation_exception(temp_dir, mock_github_error):
    """Test the GitHubPROperation class when an exception occurs."""
    # Create the operation with the mock that raises an exception
    operation = GitHubPROperation(root_dir=temp_dir, token="test-token")

    # Mock get_repo_info to return a valid repo info
    with patch.object(operation, "get_repo_info", return_value=("test-owner", "test-repo")):
        # Attempt to get pull request information
        result = await operation(pr_number=1)

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

        # Mock get_repo_info to return a valid repo info
        with patch.object(operation, "get_repo_info", return_value=("test-owner", "test-repo")):
            # Attempt to get pull request information
            with pytest.raises(ImportError, match="The PyGithub package is not installed"):
                await operation()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "pr_number,review_id,expected_result",
    [
        # Test case 1: Get a specific review
        (
            1,  # pr_number
            1,  # review_id
            {
                "status": "success",
                "message_contains": "Successfully retrieved review #1",
                "review_id": 1,
                "review_state": "APPROVED",
            },
        ),
        # Test case 2: Get all reviews
        (
            1,  # pr_number
            None,  # review_id
            {
                "status": "success",
                "message_contains": "Successfully retrieved",
                "reviews_count": 1,
            },
        ),
    ],
    ids=["specific_review", "all_reviews"],
)
async def test_github_pr_get_review(
    github_pr_operation: GitHubPROperation,
    pr_number: int,
    review_id: Optional[int],
    expected_result: Dict[str, Any],
):
    """Test the get_review method of GitHubPROperation class with various scenarios."""
    # Mock get_repo_info to return a valid repo info
    with patch.object(github_pr_operation, "get_repo_info", return_value=("test-owner", "test-repo")):
        # Execute: Get review information
        result = await github_pr_operation.get_review(pr_number, review_id=review_id)

    # Verify: Check the result
    assert result["status"] == expected_result["status"]
    assert expected_result["message_contains"] in result["message"]

    if review_id is not None:
        # Check specific review
        assert result["review"]["id"] == expected_result["review_id"]
        assert result["review"]["state"] == expected_result["review_state"]
    else:
        # Check all reviews
        assert len(result["reviews"]) == expected_result["reviews_count"]


@pytest.mark.asyncio
async def test_github_pr_get_review_no_git_remote(github_pr_operation: GitHubPROperation):
    """Test the get_review method with no git remote."""
    # Mock get_repo_info to return None to simulate no git remote
    with patch.object(github_pr_operation, "get_repo_info", return_value=None):
        # Try to get review information with no git remote
        with pytest.raises(ValueError, match="Repository information could not be extracted from git remote"):
            await github_pr_operation.get_review(1)


@pytest.mark.asyncio
async def test_github_pr_get_review_empty_pr_number(github_pr_operation: GitHubPROperation):
    """Test the get_review method with an empty PR number."""
    # Mock get_repo_info to return a valid repo info
    with patch.object(github_pr_operation, "get_repo_info", return_value=("test-owner", "test-repo")):
        # Try to get review information with an empty PR number
        with pytest.raises(ValueError, match="Pull request number must be provided"):
            await github_pr_operation.get_review(0)


@pytest.mark.asyncio
async def test_github_pr_get_review_exception(temp_dir, mock_github_error):
    """Test the get_review method when an exception occurs."""
    # Create the operation with the mock that raises an exception
    operation = GitHubPROperation(root_dir=temp_dir, token="test-token")

    # Mock get_repo_info to return a valid repo info
    with patch.object(operation, "get_repo_info", return_value=("test-owner", "test-repo")):
        # Attempt to get review information
        result = await operation.get_review(1)

        # Check the result
        assert "error" in result
        assert "Error retrieving reviews" in result["error"]
        assert result["repo_name"] == "test-repo"
        assert result["owner"] == "test-owner"
        assert result["pr_number"] == 1


@pytest.mark.asyncio
async def test_github_pr_get_review_import_error(temp_dir):
    """Test the get_review method when PyGithub is not installed."""
    # Mock the import to raise an ImportError
    with patch.dict("sys.modules", {"github": None}):
        # Create the operation
        operation = GitHubPROperation(root_dir=temp_dir, token="test-token")

        # Mock get_repo_info to return a valid repo info
        with patch.object(operation, "get_repo_info", return_value=("test-owner", "test-repo")):
            # Attempt to get review information
            with pytest.raises(ImportError, match="The PyGithub package is not installed"):
                await operation.get_review(1)
