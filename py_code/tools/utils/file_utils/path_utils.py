"""Path utility functions for MCP tools."""

import os


def normalize_path(path: str) -> str:
    """Normalize a file path for consistent handling.

    Args:
        path: The path to normalize

    Returns:
        The normalized file path

    """
    return os.path.normpath(path)
