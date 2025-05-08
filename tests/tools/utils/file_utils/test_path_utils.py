"""Parameterized tests for the path_utils module."""

import os

import pytest

from py_code.tools.utils.file_utils.path_utils import normalize_path


@pytest.mark.parametrize(
    "input_path,expected_output",
    [
        # Forward slashes
        ("/path/to/file", os.path.normpath("/path/to/file")),
        # Backslashes (on Windows)
        ("\\path\\to\\file", os.path.normpath("\\path\\to\\file")),
        # Mixed slashes
        ("/path\\to/file", os.path.normpath("/path\\to/file")),
        # Redundant separators
        ("//path//to//file", os.path.normpath("//path//to//file")),
        # Relative components
        ("/path/to/../file", os.path.normpath("/path/to/../file")),
        ("/path/./to/file", os.path.normpath("/path/./to/file")),
        # Empty path
        ("", os.path.normpath("")),
        # Current directory
        (".", os.path.normpath(".")),
        # Parent directory
        ("..", os.path.normpath("..")),
    ],
)
def test_normalize_path(input_path, expected_output):
    """Test normalizing paths with various formats."""
    result = normalize_path(input_path)
    assert result == expected_output
    # Also verify that the result is the same as os.path.normpath
    assert result == os.path.normpath(input_path)
