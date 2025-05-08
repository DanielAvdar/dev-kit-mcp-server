"""Parameterized tests for the file_operations module."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from py_code.tools.code_editing.file_operations import delete_file, move_file_or_folder


@pytest.fixture
def temp_source_file():
    """Create a temporary source file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Test content")
        temp_file_path = temp_file.name

    yield temp_file_path

    # Clean up
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture
def temp_source_dir():
    """Create a temporary source directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a file in the directory
        with open(os.path.join(temp_dir, "test_file.txt"), "w") as f:
            f.write("Test content")

        yield temp_dir


@pytest.fixture
def temp_destination_dir():
    """Create a temporary destination directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_move_file_or_folder_file_success(temp_source_file, temp_destination_dir):
    """Test moving a file successfully."""
    destination_path = os.path.join(temp_destination_dir, "moved_file.txt")

    result = move_file_or_folder(temp_source_file, destination_path)

    # Check the result
    assert "success" in result
    assert result["success"] is True
    assert result["source"] == temp_source_file
    assert result["destination"] == destination_path
    assert result["type"] == "file"

    # Check that the file was actually moved
    assert not os.path.exists(temp_source_file)
    assert os.path.exists(destination_path)


def test_move_file_or_folder_dir_success(temp_source_dir, temp_destination_dir):
    """Test moving a directory successfully."""
    destination_path = os.path.join(temp_destination_dir, "moved_dir")

    result = move_file_or_folder(temp_source_dir, destination_path)

    # Check the result
    assert "success" in result
    assert result["success"] is True
    assert result["source"] == temp_source_dir
    assert result["destination"] == destination_path
    assert result["type"] == "directory"

    # Check that the directory was actually moved
    assert not os.path.exists(temp_source_dir)
    assert os.path.exists(destination_path)
    assert os.path.exists(os.path.join(destination_path, "test_file.txt"))


def test_move_file_or_folder_with_context():
    """Test moving a file with a context object."""
    mock_ctx = MagicMock()

    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=False),
        patch("os.path.join", side_effect=lambda *args: "/".join(args)),
        patch("py_code.tools.code_editing.file_operations.normalize_path", side_effect=lambda x: x),
        patch("os.path.exists", side_effect=lambda path: False if path == "/fake/path/dest/file.txt" else True),
        patch("os.path.dirname", return_value="/fake/path/dest"),
        patch("shutil.move"),
        patch("os.path.isdir", return_value=False),
    ):
        result = move_file_or_folder("source.txt", "dest/file.txt", ctx=mock_ctx)

        # Check that the context info method was called
        mock_ctx.info.assert_called_once()
        assert "Moving from" in mock_ctx.info.call_args[0][0]

        # Check the result
        assert "success" in result
        assert result["success"] is True


@pytest.mark.parametrize(
    "source_exists,dest_dir_exists,dest_exists,expected_error",
    [
        (False, True, False, "Source path not found"),
        (True, False, False, "Destination directory not found"),
        (True, True, True, "Destination already exists"),
    ],
)
def test_move_file_or_folder_errors(source_exists, dest_dir_exists, dest_exists, expected_error):
    """Test error handling in move_file_or_folder."""
    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("py_code.tools.code_editing.file_operations.normalize_path", side_effect=lambda x: x),
        patch(
            "os.path.exists",
            side_effect=lambda path: source_exists
            if path == "/source.txt"
            else dest_dir_exists
            if path == "/fake/path/dest"
            else dest_exists
            if path == "/fake/path/dest/file.txt"
            else False,
        ),
        patch("os.path.dirname", return_value="/fake/path/dest"),
    ):
        result = move_file_or_folder("/source.txt", "/fake/path/dest/file.txt")

        # Check the result
        assert "error" in result
        assert expected_error in result["error"]


def test_move_file_or_folder_exception():
    """Test handling exceptions in move_file_or_folder."""
    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("py_code.tools.code_editing.file_operations.normalize_path", side_effect=lambda x: x),
        patch("os.path.exists", side_effect=lambda path: False if path == "/fake/path/dest/file.txt" else True),
        patch("os.path.dirname", return_value="/fake/path/dest"),
        patch("shutil.move", side_effect=Exception("Test error")),
    ):
        result = move_file_or_folder("/source.txt", "/fake/path/dest/file.txt")

        # Check the result
        assert "error" in result
        assert "Error moving file or folder" in result["error"]
        assert "Test error" in result["error"]


def test_delete_file_success(temp_source_file):
    """Test deleting a file successfully."""
    result = delete_file(temp_source_file)

    # Check the result
    assert "success" in result
    assert result["success"] is True
    assert result["path"] == temp_source_file

    # Check that the file was actually deleted
    assert not os.path.exists(temp_source_file)


def test_delete_file_with_context():
    """Test deleting a file with a context object."""
    mock_ctx = MagicMock()

    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=False),
        patch("os.path.join", side_effect=lambda *args: "/".join(args)),
        patch("py_code.tools.code_editing.file_operations.normalize_path", side_effect=lambda x: x),
        patch("os.path.exists", return_value=True),
        patch("os.path.isdir", return_value=False),
        patch("os.remove"),
    ):
        result = delete_file("file.txt", ctx=mock_ctx)

        # Check that the context info method was called
        mock_ctx.info.assert_called_once()
        assert "Deleting file" in mock_ctx.info.call_args[0][0]

        # Check the result
        assert "success" in result
        assert result["success"] is True


@pytest.mark.parametrize(
    "file_exists,is_dir,expected_error",
    [
        (False, False, "File not found"),
        (True, True, "Cannot delete directory with this function"),
    ],
)
def test_delete_file_errors(file_exists, is_dir, expected_error):
    """Test error handling in delete_file."""
    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("py_code.tools.code_editing.file_operations.normalize_path", side_effect=lambda x: x),
        patch("os.path.exists", return_value=file_exists),
        patch("os.path.isdir", return_value=is_dir),
    ):
        result = delete_file("/fake/path/file.txt")

        # Check the result
        assert "error" in result
        assert expected_error in result["error"]


def test_delete_file_exception():
    """Test handling exceptions in delete_file."""
    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("py_code.tools.code_editing.file_operations.normalize_path", side_effect=lambda x: x),
        patch("os.path.exists", return_value=True),
        patch("os.path.isdir", return_value=False),
        patch("os.remove", side_effect=Exception("Test error")),
    ):
        result = delete_file("/fake/path/file.txt")

        # Check the result
        assert "error" in result
        assert "Error deleting file" in result["error"]
        assert "Test error" in result["error"]
