"""Parameterized tests for the file_operations module."""

import os
import tempfile
from unittest.mock import MagicMock, mock_open, patch

import pytest

from py_code.tools.code_editing.file_operations import (
    create_file_or_folder,
    delete_file,
    delete_file_or_folder,
    move_file_or_folder,
)


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


def test_delete_file_or_folder_file(temp_source_file):
    """Test deleting a file using delete_file_or_folder."""
    result = delete_file_or_folder(temp_source_file)

    # Check the result
    assert "success" in result
    assert result["success"] is True
    assert result["path"] == temp_source_file
    assert result["type"] == "file"

    # Check that the file was actually deleted
    assert not os.path.exists(temp_source_file)


def test_delete_file_or_folder_directory(temp_source_dir):
    """Test deleting a directory using delete_file_or_folder."""
    result = delete_file_or_folder(temp_source_dir)

    # Check the result
    assert "success" in result
    assert result["success"] is True
    assert result["path"] == temp_source_dir
    assert result["type"] == "directory"

    # Check that the directory was actually deleted
    assert not os.path.exists(temp_source_dir)


def test_delete_file_or_folder_with_context():
    """Test deleting a file or folder with a context object."""
    mock_ctx = MagicMock()

    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=False),
        patch("os.path.join", side_effect=lambda *args: "/".join(args)),
        patch("py_code.tools.code_editing.file_operations.normalize_path", side_effect=lambda x: x),
        patch("os.path.exists", return_value=True),
        patch("os.path.isdir", return_value=True),
        patch("shutil.rmtree"),
    ):
        result = delete_file_or_folder("folder", ctx=mock_ctx)

        # Check that the context info method was called
        mock_ctx.info.assert_called_once()
        assert "Deleting" in mock_ctx.info.call_args[0][0]

        # Check the result
        assert "success" in result
        assert result["success"] is True
        assert result["type"] == "directory"


def test_delete_file_or_folder_not_found():
    """Test error handling when path doesn't exist."""
    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("py_code.tools.code_editing.file_operations.normalize_path", side_effect=lambda x: x),
        patch("os.path.exists", return_value=False),
    ):
        result = delete_file_or_folder("/fake/path/nonexistent")

        # Check the result
        assert "error" in result
        assert "Path not found" in result["error"]


def test_delete_file_or_folder_exception():
    """Test handling exceptions in delete_file_or_folder."""
    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("py_code.tools.code_editing.file_operations.normalize_path", side_effect=lambda x: x),
        patch("os.path.exists", return_value=True),
        patch("os.path.isdir", return_value=True),
        patch("shutil.rmtree", side_effect=Exception("Test error")),
    ):
        result = delete_file_or_folder("/fake/path/folder")

        # Check the result
        assert "error" in result
        assert "Error deleting" in result["error"]
        assert "Test error" in result["error"]


@pytest.fixture
def temp_destination_file():
    """Create a temporary destination file path for testing."""
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        file_path = temp_file.name

    # The file should not exist after the NamedTemporaryFile context exits
    yield file_path

    # Clean up if the file still exists
    if os.path.exists(file_path):
        os.unlink(file_path)


def test_create_file_or_folder_file(temp_destination_file):
    """Test creating a file."""
    content = "Test content"
    result = create_file_or_folder(temp_destination_file, content)

    # Check the result
    assert "success" in result
    assert result["success"] is True
    assert result["path"] == temp_destination_file
    assert result["type"] == "file"

    # Check that the file was actually created with the correct content
    assert os.path.exists(temp_destination_file)
    with open(temp_destination_file, "r") as f:
        assert f.read() == content


def test_create_file_or_folder_directory(temp_destination_dir):
    """Test creating a directory."""
    new_dir_path = os.path.join(temp_destination_dir, "new_dir")
    result = create_file_or_folder(new_dir_path)

    # Check the result
    assert "success" in result
    assert result["success"] is True
    assert result["path"] == new_dir_path
    assert result["type"] == "directory"

    # Check that the directory was actually created
    assert os.path.exists(new_dir_path)
    assert os.path.isdir(new_dir_path)


def test_create_file_or_folder_with_context():
    """Test creating a file or folder with a context object."""
    mock_ctx = MagicMock()

    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=False),
        patch("os.path.join", side_effect=lambda *args: "/".join(args)),
        patch("py_code.tools.code_editing.file_operations.normalize_path", side_effect=lambda x: x),
        patch("os.path.exists", return_value=False),
        patch("os.path.dirname", return_value="/fake/path"),
        patch("os.makedirs", return_value=None),  # Ensure parent directory creation succeeds
        patch("os.path.splitext", return_value=("file", ".txt")),
        patch("builtins.open", mock_open()),
    ):
        result = create_file_or_folder("file.txt", "content", ctx=mock_ctx)

        # Check that the context info method was called
        mock_ctx.info.assert_called_once()
        assert "Creating" in mock_ctx.info.call_args[0][0]

        # Check the result
        assert "success" in result
        assert result["success"] is True
        assert result["type"] == "file"


def test_create_file_or_folder_already_exists():
    """Test error handling when path already exists."""
    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("py_code.tools.code_editing.file_operations.normalize_path", side_effect=lambda x: x),
        patch("os.path.exists", return_value=True),
    ):
        result = create_file_or_folder("/fake/path/existing")

        # Check the result
        assert "error" in result
        assert "Path already exists" in result["error"]


def test_create_file_or_folder_parent_dir_error():
    """Test error handling when parent directory creation fails."""
    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("py_code.tools.code_editing.file_operations.normalize_path", side_effect=lambda x: x),
        patch("os.path.exists", side_effect=lambda path: False if path == "/fake/path/new" else False),
        patch("os.path.dirname", return_value="/fake/path/parent"),
        patch("os.makedirs", side_effect=Exception("Test error")),
    ):
        result = create_file_or_folder("/fake/path/new/file.txt")

        # Check the result
        assert "error" in result
        assert "Error creating parent directory" in result["error"]


def test_create_file_or_folder_exception():
    """Test handling exceptions in create_file_or_folder."""
    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("py_code.tools.code_editing.file_operations.normalize_path", side_effect=lambda x: x),
        patch("os.path.exists", return_value=False),
        patch("os.path.dirname", return_value="/fake/path"),
        patch("os.makedirs", return_value=None),  # Ensure parent directory creation succeeds
        patch("os.path.splitext", return_value=("file", ".txt")),
        patch("builtins.open", side_effect=Exception("Test error")),
    ):
        result = create_file_or_folder("/fake/path/file.txt", "content")

        # Check the result
        assert "error" in result
        assert "Error creating" in result["error"]
        assert "Test error" in result["error"]
