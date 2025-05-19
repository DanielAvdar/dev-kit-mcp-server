"""Tests for the GitAddOperation class."""

from pathlib import Path
from typing import Any, Dict, List

import pytest
from git import Repo

from dev_kit_mcp_server.tools.git import GitAddOperation


def create_test_files(temp_dir: str, file_count: int = 1) -> List[str]:
    """Create test files in the temporary directory.

    Args:
        temp_dir: Path to the temporary directory
        file_count: Number of files to create

    Returns:
        List of file names created
    """
    test_files = []
    for i in range(file_count):
        test_file = Path(temp_dir) / f"test_file_{i}.txt"
        test_file.write_text(f"This is test file {i}.")
        test_files.append(test_file.name)
    return test_files


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "file_paths,setup_files,expected_result,should_raise",
    [
        # Test case 1: Add a single file
        (
            ["test_file_0.txt"],  # file_paths
            1,  # setup_files (create 1 file)
            {
                "status": "success",
                "file_count": 1,
                "message_contains": "Successfully added 1 files to the index",
            },
            False,  # should_raise
        ),
        # Test case 2: Add multiple files
        (
            ["test_file_0.txt", "test_file_1.txt", "test_file_2.txt"],  # file_paths
            3,  # setup_files (create 3 files)
            {
                "status": "success",
                "file_count": 3,
                "message_contains": "Successfully added 3 files to the index",
            },
            False,  # should_raise
        ),
        # Test case 3: Add a nonexistent file
        (
            ["nonexistent_file.txt"],  # file_paths
            0,  # setup_files (don't create any files)
            None,  # No expected result as we expect an exception
            True,  # should_raise
        ),
    ],
    ids=["single_file", "multiple_files", "nonexistent_file"],
)
async def test_git_add_operation(
    git_add_operation: GitAddOperation,
    temp_dir_git: str,
    file_paths: List[str],
    setup_files: int,
    expected_result: Dict[str, Any],
    should_raise: bool,
):
    """Test the GitAddOperation class with various scenarios."""
    # Setup: Create test files if needed
    if setup_files > 0:
        create_test_files(temp_dir_git, setup_files)

    if should_raise:
        # For nonexistent file, we expect a git command error
        with pytest.raises(Exception, match=".*nonexistent_file.txt.*"):
            await git_add_operation(file_paths)
    else:
        # Execute: Add the files to the index
        result = await git_add_operation(file_paths)

        # Verify: Check the result
        assert result["status"] == expected_result["status"]
        assert expected_result["message_contains"] in result["message"]
        assert len(result["added_files"]) == expected_result["file_count"]
        assert set(result["added_files"]) == set(file_paths)

        # Check that the files are in the index
        repo = Repo(temp_dir_git)
        staged_files = [item.a_path for item in repo.index.diff("HEAD")]
        for file in file_paths:
            assert file in staged_files


@pytest.mark.asyncio
async def test_git_add_operation_invalid_input(git_add_operation: GitAddOperation):
    """Test the GitAddOperation class with invalid input."""
    # Test with non-list input
    with pytest.raises(ValueError, match="Expected a list of file paths as the argument"):
        await git_add_operation("not_a_list")


@pytest.mark.asyncio
async def test_git_add_operation_exception(git_add_operation: GitAddOperation, mock_repo_error, temp_dir_git: str):
    """Test the GitAddOperation class when an exception occurs."""
    # Create a test file
    test_file = Path(temp_dir_git) / "test_file.txt"
    test_file.write_text("This is a test file.")

    # Apply the mock to simulate an error
    mock_repo_error(git_add_operation)

    # Attempt to add the file - should raise the simulated error
    with pytest.raises(Exception, match="Simulated error"):
        await git_add_operation([test_file.name])
