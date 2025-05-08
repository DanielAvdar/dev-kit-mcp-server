"""Binary file utility functions for MCP tools."""

from typing import List


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
