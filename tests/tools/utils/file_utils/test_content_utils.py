"""Parameterized tests for the content_utils module."""

import os
import tempfile
from unittest.mock import mock_open, patch

import pytest

from py_code.tools.utils.file_utils.content_utils import get_file_contents, get_lines_from_file


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
        temp_file_path = temp_file.name

    yield temp_file_path

    # Clean up
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


def test_get_file_contents_success(temp_file):
    """Test getting file contents successfully."""
    contents = get_file_contents(temp_file)
    assert contents == "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"


@pytest.mark.parametrize(
    "exception,expected_result",
    [
        (FileNotFoundError("No such file"), "Error: No such file"),
        (PermissionError("Permission denied"), "Error: Permission denied"),
        (IOError("IO error"), "Error: IO error"),
    ],
)
def test_get_file_contents_exception(exception, expected_result):
    """Test getting file contents with exceptions."""
    with patch("builtins.open", side_effect=exception):
        result = get_file_contents("fake_file.txt")
        assert result == expected_result


def test_get_file_contents_unicode_error():
    """Test getting file contents with UnicodeDecodeError and successful fallback."""
    # Mock the first open to raise UnicodeDecodeError, then succeed with latin-1
    mock_file = mock_open(read_data="Latin-1 encoded text")

    with patch("builtins.open") as mock_open_func:
        # First call raises UnicodeDecodeError
        mock_open_func.side_effect = [
            UnicodeDecodeError("utf-8", b"", 0, 1, "invalid continuation byte"),
            mock_file.return_value,
        ]

        result = get_file_contents("fake_file.txt")

        assert result == "Latin-1 encoded text"
        assert mock_open_func.call_count == 2
        # First call with utf-8
        assert mock_open_func.call_args_list[0][0][1] == "r"
        assert mock_open_func.call_args_list[0][1]["encoding"] == "utf-8"
        # Second call with latin-1
        assert mock_open_func.call_args_list[1][0][1] == "r"
        assert mock_open_func.call_args_list[1][1]["encoding"] == "latin-1"


def test_get_file_contents_unicode_error_fallback_fails():
    """Test getting file contents with UnicodeDecodeError and failed fallback."""
    with patch("builtins.open") as mock_open_func:
        # First call raises UnicodeDecodeError, second call raises another exception
        mock_open_func.side_effect = [
            UnicodeDecodeError("utf-8", b"", 0, 1, "invalid continuation byte"),
            IOError("Failed to read with latin-1"),
        ]

        result = get_file_contents("fake_file.txt")

        assert result == "Error: Could not read file fake_file.txt"
        assert mock_open_func.call_count == 2


def test_get_lines_from_file_success(temp_file):
    """Test getting specific lines from a file successfully."""
    # Test with default parameters (all lines)
    lines = get_lines_from_file(temp_file)
    assert lines == "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

    # Test with start_line only
    lines = get_lines_from_file(temp_file, start_line=2)
    assert lines == "Line 3\nLine 4\nLine 5"

    # Test with both start_line and end_line
    lines = get_lines_from_file(temp_file, start_line=1, end_line=3)
    assert lines == "Line 2\nLine 3\n"


@pytest.mark.parametrize(
    "exception,expected_result",
    [
        (FileNotFoundError("No such file"), "Error: No such file"),
        (PermissionError("Permission denied"), "Error: Permission denied"),
        (IOError("IO error"), "Error: IO error"),
    ],
)
def test_get_lines_from_file_exception(exception, expected_result):
    """Test getting lines from a file with exceptions."""
    with patch("builtins.open", side_effect=exception):
        result = get_lines_from_file("fake_file.txt")
        assert result == expected_result
