"""Tests for the GitHub operations."""

from unittest.mock import MagicMock, patch

import pytest

from dev_kit_gh_mcp_server.tools import (
    GitHubIssueOperation,
    GitHubPROperation,
    GitHubRepoOperation,
)


@pytest.fixture
def mock_github():
    """Mock the Github class."""
    with patch("github.Github") as mock_github:
        # Create a mock instance
        mock_instance = MagicMock()
        mock_github.return_value = mock_instance

        # Set up the mock repository
        mock_repo = MagicMock()
        mock_repo.name = "test-repo"
        mock_repo.full_name = "test-owner/test-repo"
        mock_repo.description = "Test repository"
        mock_repo.html_url = "https://github.com/test-owner/test-repo"
        mock_repo.stargazers_count = 10
        mock_repo.forks_count = 5
        mock_repo.open_issues_count = 3
        mock_repo.default_branch = "main"
        mock_repo.private = False

        # Set up the mock user
        mock_user = MagicMock()
        mock_user.login = "test-user"
        mock_user.get_repo.return_value = mock_repo
        mock_instance.get_user.return_value = mock_user

        # Set up the mock repository retrieval
        mock_instance.get_repo.return_value = mock_repo

        # Set up the mock issue
        mock_issue = MagicMock()
        mock_issue.number = 1
        mock_issue.title = "Test issue"
        mock_issue.body = "This is a test issue"
        mock_issue.state = "open"
        mock_issue.created_at = None
        mock_issue.updated_at = None
        mock_issue.closed_at = None
        mock_issue.labels = []
        mock_issue.assignees = []
        mock_issue.html_url = "https://github.com/test-owner/test-repo/issues/1"

        # Set up the mock pull request
        mock_pr = MagicMock()
        mock_pr.number = 1
        mock_pr.title = "Test PR"
        mock_pr.body = "This is a test PR"
        mock_pr.state = "open"
        mock_pr.created_at = None
        mock_pr.updated_at = None
        mock_pr.closed_at = None
        mock_pr.merged_at = None
        mock_pr.user = mock_user
        mock_pr.head.ref = "feature-branch"
        mock_pr.head.sha = "abcdef123456"
        mock_pr.head.repo = mock_repo
        mock_pr.base.ref = "main"
        mock_pr.base.sha = "123456abcdef"
        mock_pr.base.repo = mock_repo
        mock_pr.mergeable = True
        mock_pr.merged = False
        mock_pr.html_url = "https://github.com/test-owner/test-repo/pull/1"

        # Set up the mock review
        mock_review = MagicMock()
        mock_review.id = 1
        mock_review.user = mock_user
        mock_review.body = "This is a test review"
        mock_review.state = "APPROVED"
        mock_review.submitted_at = None
        mock_review.commit_id = "abcdef123456"
        mock_review.html_url = "https://github.com/test-owner/test-repo/pull/1#pullrequestreview-1"

        # Set up the mock issue and PR retrieval
        mock_repo.get_issue.return_value = mock_issue
        mock_repo.get_issues.return_value = [mock_issue]
        mock_repo.get_pull.return_value = mock_pr
        mock_repo.get_pulls.return_value = [mock_pr]

        # Set up the mock PR review retrieval
        mock_pr.get_review.return_value = mock_review
        mock_pr.get_reviews.return_value = [mock_review]

        yield mock_github


@pytest.fixture
def github_repo_operation(mock_github, temp_dir) -> GitHubRepoOperation:
    """Create a GitHubRepoOperation instance for testing."""
    return GitHubRepoOperation(root_dir=temp_dir, token="test-token")


@pytest.fixture
def github_issue_operation(mock_github, temp_dir) -> GitHubIssueOperation:
    """Create a GitHubIssueOperation instance for testing."""
    return GitHubIssueOperation(root_dir=temp_dir, token="test-token")


@pytest.fixture
def github_pr_operation(mock_github, temp_dir) -> GitHubPROperation:
    """Create a GitHubPROperation instance for testing."""
    return GitHubPROperation(root_dir=temp_dir, token="test-token")


@pytest.fixture
def mock_github_error():
    """Create a mock that raises an exception when accessing GitHub."""
    with patch("github.Github") as mock_github:
        mock_github.side_effect = Exception("Simulated error")
        yield mock_github
