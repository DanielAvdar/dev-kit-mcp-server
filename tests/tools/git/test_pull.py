"""Tests for the GitPullOperation class."""

from unittest.mock import MagicMock, patch

import pytest
from git import Remote, RemoteReference

from dev_kit_mcp_server.tools.git import GitPullOperation


@pytest.mark.asyncio
async def test_git_pull_operation(temp_dir_git):
    """Test the GitPullOperation class with mocked remote."""
    # Create the operation
    operation = GitPullOperation(root_dir=temp_dir_git)

    # Mock the remote and pull method
    mock_remote = MagicMock(spec=Remote)
    mock_info = MagicMock(spec=RemoteReference)
    mock_info.ref = "refs/heads/main"
    mock_info.flags = 0
    mock_info.note = ""
    mock_info.commit = "abcdef1234567890"
    mock_remote.pull.return_value = [mock_info]

    # Patch the repo object to use our mock
    with patch.object(operation, "_repo") as mock_repo:
        # Set up the mock repo to return our mock remote
        mock_repo.remote = MagicMock(return_value=mock_remote)

        # Set up the active_branch property
        mock_branch = MagicMock()
        mock_branch.name = "main"
        type(mock_repo).active_branch = mock_branch

        # Pull from the remote
        result = await operation()

    # Check the result
    assert result["status"] == "success"
    assert "Successfully pulled from origin/" in result["message"]
    assert result["remote"] == "origin"
    assert len(result["results"]) == 1
    assert result["results"][0]["ref"] == "refs/heads/main"


@pytest.mark.asyncio
async def test_git_pull_operation_with_params(temp_dir_git):
    """Test the GitPullOperation class with explicit remote and branch."""
    # Create the operation
    operation = GitPullOperation(root_dir=temp_dir_git)

    # Mock the remote and pull method
    mock_remote = MagicMock(spec=Remote)
    mock_info = MagicMock(spec=RemoteReference)
    mock_info.ref = "refs/heads/feature"
    mock_info.flags = 0
    mock_info.note = ""
    mock_info.commit = "abcdef1234567890"
    mock_remote.pull.return_value = [mock_info]

    # Patch the repo object to use our mock
    with patch.object(operation, "_repo") as mock_repo:
        # Set up the mock repo to return our mock remote
        mock_repo.remote = MagicMock(return_value=mock_remote)

        # Pull from the remote with explicit parameters
        result = await operation("upstream", "feature")

        # Check the result
        assert result["status"] == "success"
        assert "Successfully pulled from upstream/feature" in result["message"]
        assert result["remote"] == "upstream"
        assert result["branch"] == "feature"
        assert len(result["results"]) == 1
        assert result["results"][0]["ref"] == "refs/heads/feature"

        # Verify the remote method was called with the right parameters
        mock_repo.remote.assert_called_once_with("upstream")
        mock_remote.pull.assert_called_once_with("feature")


@pytest.mark.asyncio
async def test_git_pull_operation_nonexistent_remote(temp_dir_git):
    """Test the GitPullOperation class with a nonexistent remote."""
    # Create the operation
    operation = GitPullOperation(root_dir=temp_dir_git)

    # Patch the repo object to use our mock
    with patch.object(operation, "_repo") as mock_repo:
        # Set up the mock repo to raise ValueError when remote is called
        mock_repo.remote = MagicMock(side_effect=ValueError("Remote not found"))

        # Pull from a nonexistent remote
        result = await operation("nonexistent")

    # Check the result
    assert "error" in result
    assert "Remote 'nonexistent' does not exist" in result["error"]
    assert result["remote"] == "nonexistent"


@pytest.mark.asyncio
async def test_git_pull_operation_detached_head(temp_dir_git):
    """Test the GitPullOperation class with a detached HEAD."""
    # Create the operation
    operation = GitPullOperation(root_dir=temp_dir_git)

    # Mock the remote
    mock_remote = MagicMock(spec=Remote)

    # Patch the repo object to use our mock
    with patch.object(operation, "_repo") as mock_repo:
        # Set up the mock repo to return our mock remote
        mock_repo.remote = MagicMock(return_value=mock_remote)

        # Set up the active_branch property to raise TypeError when accessed
        def active_branch_getter(self):
            raise TypeError("HEAD is detached")

        type(mock_repo).active_branch = property(active_branch_getter)

        # Pull without specifying a branch
        result = await operation()

    # Check the result
    assert "error" in result
    assert "Cannot pull when HEAD is detached" in result["error"]
    assert result["remote"] == "origin"


@pytest.mark.asyncio
async def test_git_pull_operation_exception(temp_dir_git):
    """Test the GitPullOperation class when an exception occurs."""
    # Create the operation
    operation = GitPullOperation(root_dir=temp_dir_git)

    # Mock the remote
    mock_remote = MagicMock(spec=Remote)
    mock_remote.pull.side_effect = Exception("Network error")

    # Patch the repo object to use our mock
    with patch.object(operation, "_repo") as mock_repo:
        # Set up the mock repo to return our mock remote
        mock_repo.remote = MagicMock(return_value=mock_remote)

        # Set up the active_branch property
        mock_branch = MagicMock()
        mock_branch.name = "main"
        type(mock_repo).active_branch = mock_branch

        # Pull from the remote
        result = await operation()

    # Check the result
    assert "error" in result
    assert "Error pulling changes: Network error" in result["error"]
    assert result["remote"] == "origin"
