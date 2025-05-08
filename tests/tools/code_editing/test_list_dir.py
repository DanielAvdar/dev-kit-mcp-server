"""Parameterized tests for the list_dir module."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from py_code.tools.code_editing.list_dir import list_dir


@pytest.fixture
def temp_dir_with_files():
    """Create a temporary directory with files for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some files
        with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
            f.write("Test file 1")

        with open(os.path.join(temp_dir, "file2.py"), "w") as f:
            f.write("# Test file 2")

        # Create a subdirectory
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)

        with open(os.path.join(subdir, "file3.txt"), "w") as f:
            f.write("Test file 3")

        yield temp_dir


def test_list_dir_success(temp_dir_with_files):
    """Test listing a directory successfully."""
    result = list_dir(temp_dir_with_files)

    # Check the result structure
    assert "path" in result
    assert "contents" in result
    assert "total_entries" in result

    # Check the path
    assert result["path"] == temp_dir_with_files

    # Check the contents
    assert len(result["contents"]) == 3  # file1.txt, file2.py, subdir/
    assert result["total_entries"] == 3

    # Check that we have the expected files and directory
    file_names = [item["name"] for item in result["contents"]]
    assert "file1.txt" in file_names
    assert "file2.py" in file_names
    assert "subdir/" in file_names

    # Check that directories are listed first
    assert result["contents"][0]["type"] == "directory"
    assert result["contents"][0]["name"] == "subdir/"


def test_list_dir_with_context():
    """Test listing a directory with a context object."""
    mock_ctx = MagicMock()

    # Define a side effect function for os.path.isdir
    def is_dir_side_effect(path):
        if path == "/fake/path/test_dir":
            return True
        elif path.endswith("subdir"):
            return True
        else:
            return False

    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=False),
        patch("os.path.join", side_effect=lambda *args: "/".join(args)),
        patch("py_code.tools.code_editing.list_dir.normalize_path", side_effect=lambda x: x),
        patch("os.path.exists", return_value=True),
        patch("os.path.isdir", side_effect=is_dir_side_effect),
        patch("os.listdir", return_value=["file1.txt", "file2.py", "subdir"]),
        patch("os.stat") as mock_stat,
    ):
        # Configure mock_stat to return different values for different paths
        def mock_stat_side_effect(path):
            mock = MagicMock()
            mock.st_size = 100 if not path.endswith("subdir") else None
            mock.st_mtime = 1234567890
            return mock

        mock_stat.side_effect = mock_stat_side_effect

        result = list_dir("test_dir", ctx=mock_ctx)

        # Check that the context info method was called
        mock_ctx.info.assert_called_once()
        assert "Listing directory" in mock_ctx.info.call_args[0][0]

        # Check the result
        assert "path" in result
        assert "contents" in result
        assert "total_entries" in result
        assert len(result["contents"]) == 3


@pytest.mark.parametrize(
    "path_exists,is_dir,expected_error",
    [
        (False, False, "Path not found"),
        (True, False, "Not a directory"),
    ],
)
def test_list_dir_errors(path_exists, is_dir, expected_error):
    """Test error handling in list_dir."""
    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("py_code.tools.code_editing.list_dir.normalize_path", side_effect=lambda x: x),
        patch("os.path.exists", return_value=path_exists),
        patch("os.path.isdir", return_value=is_dir),
    ):
        result = list_dir("/fake/path/test_dir")

        # Check the result
        assert "error" in result
        assert expected_error in result["error"]


def test_list_dir_listdir_exception():
    """Test handling exceptions when listing directory contents."""
    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("py_code.tools.code_editing.list_dir.normalize_path", side_effect=lambda x: x),
        patch("os.path.exists", return_value=True),
        patch("os.path.isdir", return_value=True),
        patch("os.listdir", side_effect=Exception("Test error")),
    ):
        result = list_dir("/fake/path/test_dir")

        # Check the result
        assert "error" in result
        assert "Error listing directory" in result["error"]
        assert "Test error" in result["error"]


def test_list_dir_stat_exception():
    """Test handling exceptions when getting file stats."""

    # Define a side effect function for os.path.isdir
    def is_dir_side_effect(path):
        if path == "/fake/path/test_dir":
            return True
        else:
            return False

    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("py_code.tools.code_editing.list_dir.normalize_path", side_effect=lambda x: x),
        patch("os.path.exists", return_value=True),
        patch("os.path.isdir", side_effect=is_dir_side_effect),
        patch("os.listdir", return_value=["file1.txt"]),
        patch("os.path.join", return_value="/fake/path/test_dir/file1.txt"),
        patch("os.stat", side_effect=Exception("Test error")),
    ):
        result = list_dir("/fake/path/test_dir")

        # Check the result
        assert "path" in result
        assert "contents" in result
        assert "total_entries" in result

        # Check that we still have an entry for the file, but with limited info
        assert len(result["contents"]) == 1
        assert result["contents"][0]["name"] == "file1.txt"
        assert result["contents"][0]["type"] == "file"
        assert "size_bytes" not in result["contents"][0]
