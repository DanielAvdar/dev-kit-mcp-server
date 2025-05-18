"""Tests for the GitCreateBranchOperation class."""

from typing import Any, Dict, Optional

import pytest
from git import Repo

from dev_kit_mcp_server.tools.git import GitCreateBranchOperation


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "new_branch,source_branch,setup_source,expected_result,expected_branch_exists",
    [
        # Test case 1: Create branch from current branch
        (
            "feature-branch",  # new_branch
            None,  # source_branch
            False,  # setup_source
            {
                "status": "success",
                "new_branch": "feature-branch",
                "source_branch": "master",  # Default branch is 'master' in the test repository
                "message_contains": "Successfully created and checked out branch 'feature-branch'",
            },
            True,  # expected_branch_exists
        ),
        # Test case 2: Create branch from specified source branch
        (
            "feature-branch",  # new_branch
            "source-branch",  # source_branch
            True,  # setup_source
            {
                "status": "success",
                "new_branch": "feature-branch",
                "source_branch": "source-branch",
                "message_contains": "Successfully created and checked out branch 'feature-branch' from 'source-branch'",
            },
            True,  # expected_branch_exists
        ),
        # Test case 3: Attempt to create a branch that already exists
        (
            "existing-branch",  # new_branch
            None,  # source_branch
            False,  # setup_source (we'll create the branch separately)
            {
                "error_contains": "Branch 'existing-branch' already exists",
                "new_branch": "existing-branch",
            },
            True,  # expected_branch_exists (the branch already exists)
        ),
        # Test case 4: Attempt to create a branch from a nonexistent source branch
        (
            "feature-branch",  # new_branch
            "nonexistent-branch",  # source_branch
            False,  # setup_source
            {
                "error_contains": "Source branch 'nonexistent-branch' does not exist",
                "new_branch": "feature-branch",
                "source_branch": "nonexistent-branch",
            },
            False,  # expected_branch_exists
        ),
    ],
    ids=["from_current", "from_source", "existing_branch", "nonexistent_source"],
)
async def test_git_create_branch_operation(
    git_create_branch_operation: GitCreateBranchOperation,
    temp_dir_git: str,
    new_branch: str,
    source_branch: Optional[str],
    setup_source: bool,
    expected_result: Dict[str, Any],
    expected_branch_exists: bool,
):
    """Test the GitCreateBranchOperation class with various scenarios."""
    # Setup: Create branches if needed
    repo = Repo(temp_dir_git)

    if setup_source and source_branch:
        repo.git.branch(source_branch)

    # For the "existing branch" test case
    if new_branch == "existing-branch":
        repo.git.branch(new_branch)

    # Execute: Create the branch
    result = await git_create_branch_operation(new_branch, source_branch=source_branch)

    # Verify: Check the result
    if "status" in expected_result:
        assert result["status"] == expected_result["status"]
        assert expected_result["message_contains"] in result["message"]
        assert result["new_branch"] == expected_result["new_branch"]
        assert result["source_branch"] == expected_result["source_branch"]
    else:
        assert "error" in result
        assert expected_result["error_contains"] in result["error"]
        assert result["new_branch"] == expected_result["new_branch"]
        if "source_branch" in expected_result:
            assert result["source_branch"] == expected_result["source_branch"]

    # Verify: Check if the branch exists and is checked out
    branches = [b.name for b in repo.branches]
    assert (new_branch in branches) == expected_branch_exists
    if expected_branch_exists and "status" in expected_result:
        assert repo.active_branch.name == new_branch


@pytest.mark.asyncio
async def test_git_create_branch_operation_empty_branch(git_create_branch_operation: GitCreateBranchOperation):
    """Test the GitCreateBranchOperation class with an empty branch name."""
    # Try to create a branch with an empty name
    with pytest.raises(ValueError, match="New branch name must be provided"):
        await git_create_branch_operation("")


@pytest.mark.asyncio
async def test_git_create_branch_operation_exception(
    git_create_branch_operation: GitCreateBranchOperation, mock_repo_error
):
    """Test the GitCreateBranchOperation class when an exception occurs."""
    # Apply the mock to simulate an error
    mock_repo_error(git_create_branch_operation)

    # Attempt to create a branch
    result = await git_create_branch_operation("feature-branch")

    # Check the result
    assert "error" in result
    assert "Error creating branch:" in result["error"]
    assert result["new_branch"] == "feature-branch"
