"""Tests for the GitCheckoutOperation class."""

from typing import Any, Dict

import pytest
from git import Repo

from dev_kit_mcp_server.tools.git import GitCheckoutOperation


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "branch_name,create,setup_branch,expected_result,expected_branch_exists,should_raise",
    [
        # Test case 1: Checkout existing branch
        (
            "test-branch",  # branch_name
            False,  # create
            True,  # setup_branch
            {
                "status": "success",
                "branch": "test-branch",
                "created": False,
                "message_contains": "Successfully checked out branch 'test-branch'",
            },
            True,  # expected_branch_exists
            False,  # should_raise
        ),
        # Test case 2: Create and checkout new branch
        (
            "feature-branch",  # branch_name
            True,  # create
            False,  # setup_branch
            {
                "status": "success",
                "branch": "feature-branch",
                "created": True,
                "message_contains": "Successfully created and checked out branch 'feature-branch'",
            },
            True,  # expected_branch_exists
            False,  # should_raise
        ),
        # Test case 3: Attempt to checkout nonexistent branch
        (
            "nonexistent-branch",  # branch_name
            False,  # create
            False,  # setup_branch
            None,  # No expected result as we expect an exception
            False,  # expected_branch_exists
            True,  # should_raise
        ),
    ],
    ids=["existing_branch", "create_branch", "nonexistent_branch"],
)
async def test_git_checkout_operation(
    git_checkout_operation: GitCheckoutOperation,
    temp_dir_git: str,
    branch_name: str,
    create: bool,
    setup_branch: bool,
    expected_result: Dict[str, Any],
    expected_branch_exists: bool,
    should_raise: bool,
):
    """Test the GitCheckoutOperation class with various scenarios."""
    # Setup: Create a branch if needed
    repo = Repo(temp_dir_git)
    if setup_branch:
        repo.git.branch(branch_name)

    if should_raise:
        # For nonexistent branch, we expect an exception
        with pytest.raises(Exception, match=f"Branch '{branch_name}' does not exist"):
            await git_checkout_operation(branch_name, create=create)
    else:
        # Execute: Checkout the branch
        result = await git_checkout_operation(branch_name, create=create)

        # Verify: Check the result
        assert result["status"] == expected_result["status"]
        assert expected_result["message_contains"] in result["message"]
        assert result["branch"] == expected_result["branch"]
        assert result["created"] == expected_result["created"]

        # Verify: Check if the branch exists and is checked out
        branches = [b.name for b in repo.branches]
        assert (branch_name in branches) == expected_branch_exists
        if expected_branch_exists:
            assert repo.active_branch.name == branch_name


@pytest.mark.asyncio
async def test_git_checkout_operation_empty_branch(git_checkout_operation: GitCheckoutOperation):
    """Test the GitCheckoutOperation class with an empty branch name."""
    # Checkout with an empty branch name
    with pytest.raises(ValueError, match="Branch name must be provided"):
        await git_checkout_operation("")


@pytest.mark.asyncio
async def test_git_checkout_operation_exception(git_checkout_operation: GitCheckoutOperation, mock_repo_error):
    """Test the GitCheckoutOperation class when an exception occurs."""
    # Apply the mock to simulate an error
    mock_repo_error(git_checkout_operation)

    # Attempt to checkout a branch - should raise the simulated error
    with pytest.raises(Exception):
        await git_checkout_operation("main")
