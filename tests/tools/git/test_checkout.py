"""Tests for the GitCheckoutOperation class."""

import pytest
from git import Repo

from dev_kit_mcp_server.tools.git import GitCheckoutOperation


@pytest.mark.asyncio
async def test_git_checkout_operation(temp_dir_git):
    """Test the GitCheckoutOperation class with an existing branch."""
    # Create a test branch in the repository
    repo = Repo(temp_dir_git)
    # Create a branch
    repo.git.branch("test-branch")

    # Create the operation
    operation = GitCheckoutOperation(root_dir=temp_dir_git)

    # Checkout the branch
    result = await operation("test-branch")

    # Check the result
    assert result["status"] == "success"
    assert "Successfully checked out branch 'test-branch'" in result["message"]
    assert result["branch"] == "test-branch"
    assert not result["created"]

    # Verify the branch was checked out
    assert repo.active_branch.name == "test-branch"


@pytest.mark.asyncio
async def test_git_checkout_operation_create_branch(temp_dir_git):
    """Test the GitCheckoutOperation class creating a new branch."""
    # Create the operation
    operation = GitCheckoutOperation(root_dir=temp_dir_git)

    # Checkout a new branch
    result = await operation("feature-branch", create=True)

    # Check the result
    assert result["status"] == "success"
    assert "Successfully created and checked out branch 'feature-branch'" in result["message"]
    assert result["branch"] == "feature-branch"
    assert result["created"]

    # Verify the branch was created and checked out
    repo = Repo(temp_dir_git)
    assert "feature-branch" in [b.name for b in repo.branches]
    assert repo.active_branch.name == "feature-branch"


@pytest.mark.asyncio
async def test_git_checkout_operation_nonexistent_branch(temp_dir_git):
    """Test the GitCheckoutOperation class with a nonexistent branch."""
    # Create the operation
    operation = GitCheckoutOperation(root_dir=temp_dir_git)

    # Checkout a nonexistent branch
    result = await operation("nonexistent-branch")

    # Check the result
    assert "error" in result
    assert "Branch 'nonexistent-branch' does not exist" in result["error"]
    assert result["branch"] == "nonexistent-branch"

    # Verify the branch was not created
    repo = Repo(temp_dir_git)
    assert "nonexistent-branch" not in [b.name for b in repo.branches]


@pytest.mark.asyncio
async def test_git_checkout_operation_empty_branch(temp_dir_git):
    """Test the GitCheckoutOperation class with an empty branch name."""
    # Create the operation
    operation = GitCheckoutOperation(root_dir=temp_dir_git)

    # Checkout with an empty branch name
    with pytest.raises(ValueError, match="Branch name must be provided"):
        await operation("")


@pytest.mark.asyncio
async def test_git_checkout_operation_exception(temp_dir_git):
    """Test the GitCheckoutOperation class when an exception occurs."""
    # Create a valid operation first
    operation = GitCheckoutOperation(root_dir=temp_dir_git)

    # Mock the _repo attribute to simulate an error during checkout
    class MockRepo:
        def __getattr__(self, name):
            if name == "git":
                raise Exception("Simulated error")
            return None

    # Replace the repo with our mock
    operation._repo = MockRepo()

    # Attempt to checkout a branch
    result = await operation("main")

    # Check the result
    assert "error" in result
    assert "Error checking out branch:" in result["error"]
    assert result["branch"] == "main"
