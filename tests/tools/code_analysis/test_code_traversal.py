"""Parameterized tests for the code_traversal module."""

import os
import tempfile
from unittest.mock import patch

import pytest

from py_code.tools.code_analysis.code_traversal import (
    find_python_files,
    is_ignored,
    parse_gitignore,
    resolve_path_pattern,
)


@pytest.fixture
def temp_gitignore():
    """Create a temporary .gitignore file for testing."""
    gitignore_content = """
# Comment line
*.pyc
__pycache__/
/dist/
build/
!important.py
/src/specific/
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write(gitignore_content)
        temp_file_path = temp_file.name

    yield temp_file_path

    # Clean up
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture
def temp_dir_with_files():
    """Create a temporary directory with Python files for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create Python files
        with open(os.path.join(temp_dir, "file1.py"), "w") as f:
            f.write("# Python file 1")

        with open(os.path.join(temp_dir, "file2.py"), "w") as f:
            f.write("# Python file 2")

        # Create a non-Python file
        with open(os.path.join(temp_dir, "file.txt"), "w") as f:
            f.write("Text file")

        # Create a subdirectory with Python files
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)

        with open(os.path.join(subdir, "file3.py"), "w") as f:
            f.write("# Python file 3")

        # Create a hidden directory with Python files
        hidden_dir = os.path.join(temp_dir, ".hidden")
        os.makedirs(hidden_dir)

        with open(os.path.join(hidden_dir, "hidden.py"), "w") as f:
            f.write("# Hidden Python file")

        # Create a __pycache__ directory
        pycache_dir = os.path.join(temp_dir, "__pycache__")
        os.makedirs(pycache_dir)

        with open(os.path.join(pycache_dir, "cached.py"), "w") as f:
            f.write("# Cached Python file")

        yield temp_dir


def test_parse_gitignore_valid(temp_gitignore):
    """Test parsing a valid .gitignore file."""
    patterns = parse_gitignore(temp_gitignore)

    assert "*.pyc" in patterns
    assert "__pycache__/" in patterns
    assert "dist/" in patterns
    assert "build/" in patterns
    assert "src/specific/" in patterns

    # Comments and negation patterns should be skipped
    assert "# Comment line" not in patterns
    assert "!important.py" not in patterns


def test_parse_gitignore_nonexistent():
    """Test parsing a nonexistent .gitignore file."""
    patterns = parse_gitignore("/nonexistent/gitignore")
    assert patterns == []


def test_parse_gitignore_exception():
    """Test handling exceptions when parsing .gitignore."""
    with patch("builtins.open", side_effect=IOError("Test error")):
        patterns = parse_gitignore("fake_gitignore")
        assert patterns == []


@pytest.mark.parametrize(
    "file_path,root_dir,ignore_patterns,expected_result",
    [
        # Test with hidden directory
        ("/root/.git/file.py", "/root", [], True),
        # Test with __pycache__ directory
        ("/root/__pycache__/file.py", "/root", [], True),
        # Test with venv directory
        ("/root/venv/file.py", "/root", [], True),
        # Test with .venv directory
        ("/root/.venv/file.py", "/root", [], True),
        # Test with file pattern
        ("/root/file.pyc", "/root", ["*.pyc"], True),
        # Test with non-ignored file
        ("/root/src/file.py", "/root", ["*.pyc"], False),
    ],
)
def test_is_ignored(file_path, root_dir, ignore_patterns, expected_result):
    """Test checking if a file should be ignored."""
    with patch("os.path.isdir", return_value=True):  # Mock isdir for directory-only patterns
        result = is_ignored(file_path, root_dir, ignore_patterns)
        assert result == expected_result


def test_find_python_files_file_path():
    """Test finding Python files when path is a file."""
    with (
        patch("os.path.isfile", return_value=True),
        patch("os.path.isdir", return_value=False),
        patch("py_code.tools.code_analysis.code_traversal.is_ignored", return_value=False),
    ):
        # Test with Python file
        result = find_python_files("/path/to/file.py", "/path", [])
        assert result == ["/path/to/file.py"]

        # Test with non-Python file
        result = find_python_files("/path/to/file.txt", "/path", [])
        assert result == []

        # Test with ignored Python file
        with patch("py_code.tools.code_analysis.code_traversal.is_ignored", return_value=True):
            result = find_python_files("/path/to/file.py", "/path", [])
            assert result == []


def test_find_python_files_directory(temp_dir_with_files):
    """Test finding Python files in a directory."""
    # Find all Python files (excluding hidden and __pycache__)
    result = find_python_files(temp_dir_with_files, temp_dir_with_files, [])

    # Should find file1.py, file2.py, and subdir/file3.py
    assert len(result) == 3

    # Check that the files are in the result
    file_names = [os.path.basename(path) for path in result]
    assert "file1.py" in file_names
    assert "file2.py" in file_names
    assert "file3.py" in file_names

    # Check that hidden.py and cached.py are not in the result
    assert "hidden.py" not in file_names
    assert "cached.py" not in file_names


def test_find_python_files_with_ignore_patterns():
    """Test finding Python files with ignore patterns."""
    with (
        patch("os.path.isfile", return_value=False),
        patch("os.path.isdir", return_value=True),
        patch("os.walk") as mock_walk,
    ):
        # Mock os.walk to return some files
        mock_walk.return_value = [
            ("/root", ["subdir"], ["file1.py", "file2.py", "file.txt"]),
            ("/root/subdir", [], ["file3.py"]),
        ]

        # Mock is_ignored to ignore file2.py
        def mock_is_ignored(file_path, root_dir, ignore_patterns):
            return "file2.py" in file_path

        with patch("py_code.tools.code_analysis.code_traversal.is_ignored", side_effect=mock_is_ignored):
            result = find_python_files("/root", "/root", ["*.pyc"])

            # Should find file1.py and subdir/file3.py, but not file2.py
            assert len(result) == 2

            # Use os.path.basename to make the test OS-independent
            file_names = [os.path.basename(path) for path in result]
            assert "file1.py" in file_names
            assert "file3.py" in file_names
            assert "file2.py" not in file_names

            # Check that the paths contain the expected directories
            assert any("file1.py" in path for path in result)
            assert any(
                os.path.join("subdir", "file3.py").replace("\\", "/") in path.replace("\\", "/") for path in result
            )


@pytest.mark.parametrize(
    "pattern,is_abs,exists,glob_result,expected_result",
    [
        # Absolute path that exists
        ("/abs/path", True, True, [], ["/abs/path"]),
        # Absolute path that doesn't exist, but matches glob
        ("/abs/path*", True, False, ["/abs/path1", "/abs/path2"], ["/abs/path1", "/abs/path2"]),
        # Absolute path that doesn't exist and doesn't match glob
        ("/abs/path*", True, False, [], []),
        # Relative path that exists
        ("rel/path", False, True, [], ["/root/rel/path"]),
        # Relative path that doesn't exist, but matches glob
        ("rel/path*", False, False, ["/root/rel/path1", "/root/rel/path2"], ["/root/rel/path1", "/root/rel/path2"]),
        # Relative path that doesn't exist and doesn't match glob
        ("rel/path*", False, False, [], []),
    ],
)
def test_resolve_path_pattern(pattern, is_abs, exists, glob_result, expected_result):
    """Test resolving path patterns."""
    with (
        patch("os.path.isabs", return_value=is_abs),
        patch("os.path.exists", return_value=exists),
        patch("os.path.join", return_value="/root/rel/path"),
        patch("glob.glob", return_value=glob_result),
    ):
        result = resolve_path_pattern(pattern, "/root")
        assert result == expected_result
