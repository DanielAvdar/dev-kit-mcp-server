"""Common utilities for search and navigation tools."""

import os
from typing import List, Optional


def normalize_path(path: str) -> str:
    """Normalize a file path for consistent handling.

    Args:
        path: The path to normalize

    Returns:
        The normalized file path

    """
    return os.path.normpath(path)


def is_binary_file(file_path: str) -> bool:
    """Check if a file is binary (non-text).

    Args:
        file_path: Path to the file to check

    Returns:
        True if the file is binary, False otherwise

    """
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            return b"\0" in chunk
    except Exception:
        return True


def filter_binary_files(file_paths: List[str]) -> List[str]:
    """Filter out binary files from a list of file paths.

    Args:
        file_paths: List of file paths to filter

    Returns:
        List of file paths excluding binary files

    """
    return [path for path in file_paths if not is_binary_file(path)]


def get_file_contents(file_path: str) -> str:
    """Get the contents of a file as a string.

    Args:
        file_path: Path to the file to read

    Returns:
        The contents of the file as a string or an error message

    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            # Try with a different encoding
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception:
            return f"Error: Could not read file {file_path}"
    except Exception as e:
        return f"Error: {str(e)}"


def get_lines_from_file(file_path: str, start_line: int = 0, end_line: Optional[int] = None) -> str:
    """Get specific lines from a file.

    Args:
        file_path: Path to the file to read
        start_line: Line number to start reading from (0-based)
        end_line: Line number to end reading at (0-based, inclusive)

    Returns:
        The requested lines from the file as a single string or an error message

    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if end_line is None:
            end_line = len(lines)

        return "".join(lines[start_line:end_line])
    except Exception as e:
        return f"Error: {str(e)}"


def read_code_from_path(repo_root: str, file_path: str) -> str:
    """Read code from a file path.

    Args:
        repo_root: Path to the root of the repository
        file_path: Path to the file or package to analyze, relative to repo_root

    Returns:
        The code as a string

    """
    from .code_editing.mcp_tools import read_code_from_path as read_code_impl

    return read_code_impl(repo_root, file_path)
