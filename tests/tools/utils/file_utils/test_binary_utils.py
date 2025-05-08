"""Parameterized tests for the binary_utils module."""

import os
import tempfile
from unittest.mock import patch

import pytest

from py_code.tools.utils.file_utils.binary_utils import filter_binary_files, is_binary_file


@pytest.fixture
def temp_text_file():
    """Create a temporary text file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("This is a text file with no null bytes.")
        temp_file_path = temp_file.name

    yield temp_file_path

    # Clean up
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture
def temp_binary_file():
    """Create a temporary binary file for testing."""
    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as temp_file:
        # Write some text and a null byte
        temp_file.write(b"This is a binary file with a null byte: \x00")
        temp_file_path = temp_file.name

    yield temp_file_path

    # Clean up
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


def test_is_binary_file_text(temp_text_file):
    """Test is_binary_file with a text file."""
    result = is_binary_file(temp_text_file)
    assert result is False


def test_is_binary_file_binary(temp_binary_file):
    """Test is_binary_file with a binary file."""
    result = is_binary_file(temp_binary_file)
    assert result is True


def test_is_binary_file_nonexistent():
    """Test is_binary_file with a nonexistent file."""
    result = is_binary_file("/nonexistent/file.txt")
    assert result is True  # Should return True for exceptions


@pytest.mark.parametrize(
    "exception_type",
    [
        FileNotFoundError,
        PermissionError,
        IOError,
    ],
)
def test_is_binary_file_exception(exception_type):
    """Test is_binary_file with various exceptions."""
    with patch("builtins.open", side_effect=exception_type("Test error")):
        result = is_binary_file("fake_file.txt")
        assert result is True  # Should return True for exceptions


def test_filter_binary_files(temp_text_file, temp_binary_file):
    """Test filter_binary_files with a mix of text and binary files."""
    # Create a list of file paths
    file_paths = [temp_text_file, temp_binary_file, "/nonexistent/file.txt"]

    # Filter the list
    result = filter_binary_files(file_paths)

    # Should only contain the text file
    assert len(result) == 1
    assert result[0] == temp_text_file


def test_filter_binary_files_empty():
    """Test filter_binary_files with an empty list."""
    result = filter_binary_files([])
    assert result == []


@pytest.mark.parametrize(
    "file_paths,expected_count",
    [
        ([], 0),  # Empty list
        (["file1.txt"], 0),  # Single file (mocked to be binary)
        (["file1.txt", "file2.txt"], 0),  # Multiple files (all mocked to be binary)
    ],
)
def test_filter_binary_files_all_binary(file_paths, expected_count):
    """Test filter_binary_files when all files are binary."""
    with patch("py_code.tools.utils.file_utils.binary_utils.is_binary_file", return_value=True):
        result = filter_binary_files(file_paths)
        assert len(result) == expected_count
        assert result == []


@pytest.mark.parametrize(
    "file_paths,expected_count",
    [
        (["file1.txt"], 1),  # Single file (mocked to be text)
        (["file1.txt", "file2.txt"], 2),  # Multiple files (all mocked to be text)
    ],
)
def test_filter_binary_files_all_text(file_paths, expected_count):
    """Test filter_binary_files when all files are text."""
    with patch("py_code.tools.utils.file_utils.binary_utils.is_binary_file", return_value=False):
        result = filter_binary_files(file_paths)
        assert len(result) == expected_count
        assert result == file_paths
