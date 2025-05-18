"""Tests for the GitAddOperation class."""

from pathlib import Path

import pytest

from dev_kit_mcp_server.tools.git import GitAddOperation


@pytest.mark.asyncio
async def test_git_add_operation(temp_dir_git):
    """Test the GitAddOperation class."""
    # Create a test file
    test_file = Path(temp_dir_git) / "test_file.txt"
    test_file.write_text("This is a test file.")

    # Create the operation
    operation = GitAddOperation(root_dir=temp_dir_git)

    # Add the file to the index
    result = await operation([test_file.name])

    # Check the result
    assert result["status"] == "success"
    assert "Successfully added 1 files to the index" in result["message"]
    assert len(result["added_files"]) == 1
    assert result["added_files"][0] == test_file.name

    # Check that the file is in the index
    repo = operation._repo
    assert test_file.name in [item.a_path for item in repo.index.diff("HEAD")]


@pytest.mark.asyncio
async def test_git_add_operation_invalid_input(temp_dir_git):
    """Test the GitAddOperation class with invalid input."""
    # Create the operation
    operation = GitAddOperation(root_dir=temp_dir_git)

    # Test with non-list input
    with pytest.raises(ValueError, match="Expected a list of file paths as the argument"):
        await operation("not_a_list")


@pytest.mark.asyncio
async def test_git_add_operation_nonexistent_file(temp_dir_git):
    """Test the GitAddOperation class with a nonexistent file."""
    # Create the operation
    operation = GitAddOperation(root_dir=temp_dir_git)

    # Add a nonexistent file to the index
    result = await operation(["nonexistent_file.txt"])

    # Check the result
    assert "error" in result
    assert "Error adding files to the index" in result["error"]
    assert result["paths"] == ["nonexistent_file.txt"]


@pytest.mark.asyncio
async def test_git_add_operation_multiple_files(temp_dir_git):
    """Test the GitAddOperation class with multiple files."""
    # Create test files
    test_files = []
    for i in range(3):
        test_file = Path(temp_dir_git) / f"test_file_{i}.txt"
        test_file.write_text(f"This is test file {i}.")
        test_files.append(test_file.name)

    # Create the operation
    operation = GitAddOperation(root_dir=temp_dir_git)

    # Add the files to the index
    result = await operation(test_files)

    # Check the result
    assert result["status"] == "success"
    assert "Successfully added 3 files to the index" in result["message"]
    assert len(result["added_files"]) == 3
    assert set(result["added_files"]) == set(test_files)

    # Check that the files are in the index
    repo = operation._repo
    staged_files = [item.a_path for item in repo.index.diff("HEAD")]
    for file in test_files:
        assert file in staged_files
