"""Path utility functions for MCP tools."""

import os
from typing import Optional


def normalize_path(path: str, working_dir: Optional[str] = None) -> str:
    """Normalize a file path for consistent handling.

    Args:
        path: The path to normalize
        working_dir: Optional working directory to resolve relative paths against

    Returns:
        The normalized file path

    """
    # If working_dir is provided and path is not absolute, make it relative to working_dir
    if working_dir is not None and not os.path.isabs(path):
        path = os.path.join(working_dir, path)

    return os.path.normpath(path)
