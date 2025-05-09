"""Tool for searching files by glob pattern."""

import glob
import os
from typing import Any, Dict, Optional

from mcp.server.fastmcp import Context


def file_search(query: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """Search for files by glob pattern.

    Args:
        query: The glob pattern to search for
        ctx: Optional MCP context

    Returns:
        Dictionary containing matching files

    """
    if ctx:
        ctx.info(f"Searching for files matching pattern: {query}")

    workspace_root = os.getcwd()

    # Handle absolute paths and adjust relative patterns
    if os.path.isabs(query):
        search_pattern = query
    else:
        search_pattern = os.path.join(workspace_root, query)

    # Perform glob search
    matches = glob.glob(search_pattern, recursive=True)

    # Convert to relative paths and sort
    relative_matches = [os.path.relpath(m, workspace_root) for m in matches]
    relative_matches.sort()

    # Limit to 20 results
    limited_matches = relative_matches[:20]

    return {
        "pattern": query,
        "matches": limited_matches,
        "total_matches": len(matches),
        "limited": len(matches) > len(limited_matches),
    }
