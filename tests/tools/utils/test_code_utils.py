"""Parameterized tests for the code_utils module."""

import os
import tempfile
from unittest.mock import patch

import pytest

from py_code.tools.utils.code_utils import read_code_from_path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as temp_file:
        temp_file.write("def test_function():\n    return 'test'")
        temp_file_path = temp_file.name

    yield temp_file_path

    # Clean up
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture
def temp_dir_with_files(temp_dir):
    """Create a temporary directory with Python files for testing."""
    # Create a Python file in the temp directory
    file1_path = os.path.join(temp_dir, "file1.py")
    with open(file1_path, "w") as f:
        f.write("def function1():\n    return 'file1'")

    # Create a subdirectory with a Python file
    subdir_path = os.path.join(temp_dir, "subdir")
    os.makedirs(subdir_path)
    file2_path = os.path.join(subdir_path, "file2.py")
    with open(file2_path, "w") as f:
        f.write("def function2():\n    return 'file2'")

    # Create a non-Python file
    txt_file_path = os.path.join(temp_dir, "file.txt")
    with open(txt_file_path, "w") as f:
        f.write("This is a text file")

    return temp_dir


def test_read_code_from_path_file(temp_file):
    """Test reading code from a file path."""
    # Get the directory and filename
    dir_name = os.path.dirname(temp_file)
    file_name = os.path.basename(temp_file)

    # Read the code
    code = read_code_from_path(dir_name, file_name)

    # Check the result
    assert code == "def test_function():\n    return 'test'"


def test_read_code_from_path_directory(temp_dir_with_files):
    """Test reading code from a directory path."""
    # Get the parent directory and the temp directory name
    parent_dir = os.path.dirname(temp_dir_with_files)
    dir_name = os.path.basename(temp_dir_with_files)

    # Read the code
    code = read_code_from_path(parent_dir, dir_name)

    # Check the result
    assert "def function1():" in code
    assert "def function2():" in code
    assert "# File:" in code
    assert "file1.py" in code
    assert os.path.join("subdir", "file2.py").replace("\\", "/") in code.replace("\\", "/")


def test_read_code_from_path_nonexistent():
    """Test reading code from a nonexistent path."""
    with pytest.raises(Exception) as excinfo:
        read_code_from_path("/nonexistent", "path")

    assert "Path does not exist" in str(excinfo.value)


@pytest.mark.parametrize(
    "isfile_return,isdir_return,expected_exception",
    [
        (False, False, "Path is neither a file nor a directory"),
    ],
)
def test_read_code_from_path_neither_file_nor_dir(isfile_return, isdir_return, expected_exception):
    """Test reading code from a path that is neither a file nor a directory."""
    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.isfile", return_value=isfile_return),
        patch("os.path.isdir", return_value=isdir_return),
    ):
        with pytest.raises(Exception) as excinfo:
            read_code_from_path("/fake", "path")

        assert expected_exception in str(excinfo.value)


@pytest.mark.parametrize(
    "exception_type,exception_args,exception_msg",
    [
        (PermissionError, ["Permission denied"], "Permission denied"),
        (IOError, ["IO error"], "IO error"),
    ],
)
def test_read_code_from_path_file_exception(exception_type, exception_args, exception_msg):
    """Test exceptions when reading a file."""
    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.isfile", return_value=True),
        patch("os.path.isdir", return_value=False),
        patch("builtins.open", side_effect=exception_type(*exception_args)),
    ):
        with pytest.raises(Exception) as excinfo:
            read_code_from_path("/fake", "path")

        assert "Error reading file" in str(excinfo.value)
        assert exception_msg in str(excinfo.value)


def test_read_code_from_path_dir_exception():
    """Test exceptions when reading files in a directory."""
    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.isfile", return_value=False),
        patch("os.path.isdir", return_value=True),
        patch("os.walk", return_value=[("/fake", [], ["file.py"])]),
        patch("os.path.join", return_value="/fake/file.py"),
        patch("builtins.open", side_effect=PermissionError("Permission denied")),
    ):
        with pytest.raises(Exception) as excinfo:
            read_code_from_path("/fake", "path")

        assert "Error reading file" in str(excinfo.value)
        assert "Permission denied" in str(excinfo.value)
