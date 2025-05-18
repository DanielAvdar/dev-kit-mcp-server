"""Tests for the GitCreateBranchOperation class."""

import pytest
from git import Repo

from dev_kit_mcp_server.tools.git import GitCreateBranchOperation


@pytest.mark.asyncio
async def test_git_create_branch_operation(temp_dir_git):
    """Test the GitCreateBranchOperation class with a new branch from the current branch."""
    # Create the operation
    operation = GitCreateBranchOperation(root_dir=temp_dir_git)

    # Create a new branch
    result = await operation("feature-branch")

    # Check the result
    assert result["status"] == "success"
    assert "Successfully created and checked out branch 'feature-branch'" in result["message"]
    assert result["new_branch"] == "feature-branch"
    assert result["source_branch"] == "master"  # Default branch is 'master' in the test repository

    # Verify the branch was created and checked out
    repo = Repo(temp_dir_git)
    assert "feature-branch" in [b.name for b in repo.branches]
    assert repo.active_branch.name == "feature-branch"


@pytest.mark.asyncio
async def test_git_create_branch_operation_with_source(temp_dir_git):
    """Test the GitCreateBranchOperation class with a new branch from a specified source branch."""
    # Create a test branch in the repository
    repo = Repo(temp_dir_git)
    # Create a source branch
    repo.git.branch("source-branch")

    # Create the operation
    operation = GitCreateBranchOperation(root_dir=temp_dir_git)

    # Create a new branch from the source branch
    result = await operation("feature-branch", source_branch="source-branch")

    # Check the result
    assert result["status"] == "success"
    assert "Successfully created and checked out branch 'feature-branch' from 'source-branch'" in result["message"]
    assert result["new_branch"] == "feature-branch"
    assert result["source_branch"] == "source-branch"

    # Verify the branch was created and checked out
    repo = Repo(temp_dir_git)
    assert "feature-branch" in [b.name for b in repo.branches]
    assert repo.active_branch.name == "feature-branch"


@pytest.mark.asyncio
async def test_git_create_branch_operation_existing_branch(temp_dir_git):
    """Test the GitCreateBranchOperation class with an existing branch."""
    # Create a test branch in the repository
    repo = Repo(temp_dir_git)
    # Create a branch
    repo.git.branch("existing-branch")

    # Create the operation
    operation = GitCreateBranchOperation(root_dir=temp_dir_git)

    # Try to create a branch that already exists
    result = await operation("existing-branch")

    # Check the result
    assert "error" in result
    assert "Branch 'existing-branch' already exists" in result["error"]
    assert result["new_branch"] == "existing-branch"


@pytest.mark.asyncio
async def test_git_create_branch_operation_nonexistent_source(temp_dir_git):
    """Test the GitCreateBranchOperation class with a nonexistent source branch."""
    # Create the operation
    operation = GitCreateBranchOperation(root_dir=temp_dir_git)

    # Try to create a branch from a nonexistent source branch
    result = await operation("feature-branch", source_branch="nonexistent-branch")

    # Check the result
    assert "error" in result
    assert "Source branch 'nonexistent-branch' does not exist" in result["error"]
    assert result["new_branch"] == "feature-branch"
    assert result["source_branch"] == "nonexistent-branch"


@pytest.mark.asyncio
async def test_git_create_branch_operation_empty_branch(temp_dir_git):
    """Test the GitCreateBranchOperation class with an empty branch name."""
    # Create the operation
    operation = GitCreateBranchOperation(root_dir=temp_dir_git)

    # Try to create a branch with an empty name
    with pytest.raises(ValueError, match="New branch name must be provided"):
        await operation("")


@pytest.mark.asyncio
async def test_git_create_branch_operation_exception(temp_dir_git):
    """Test the GitCreateBranchOperation class when an exception occurs."""
    # Create a valid operation first
    operation = GitCreateBranchOperation(root_dir=temp_dir_git)

    # Mock the _repo attribute to simulate an error during branch creation
    class MockRepo:
        def __getattr__(self, name):
            if name == "git":
                raise Exception("Simulated error")
            return None

    # Replace the repo with our mock
    operation._repo = MockRepo()

    # Attempt to create a branch
    result = await operation("feature-branch")

    # Check the result
    assert "error" in result
    assert "Error creating branch:" in result["error"]
    assert result["new_branch"] == "feature-branch"
