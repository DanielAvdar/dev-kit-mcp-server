"""Tool for listing the contents of a directory."""

import os
from typing import Any, Dict, Optional

from fastmcp import Context

from ..utils import normalize_path


def list_dir(path: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """List the contents of a directory.

    Args:
        path: The path to the directory to list
        ctx: Optional MCP context

    Returns:
        Dictionary containing directory listing

    """
    if ctx:
        ctx.info(f"Listing directory: {path}")

    # Normalize path and handle both absolute and relative paths
    if not os.path.isabs(path):
        workspace_root = os.getcwd()
        path = os.path.join(workspace_root, path)

    path = normalize_path(path)

    if not os.path.exists(path):
        return {"error": f"Path not found: {path}", "path": path}

    if not os.path.isdir(path):
        return {"error": f"Not a directory: {path}", "path": path}

    try:
        # Get directory contents
        entries = os.listdir(path)

        # Process each entry
        contents = []
        for entry in entries:
            entry_path = os.path.join(path, entry)
            is_dir = os.path.isdir(entry_path)

            try:
                stats = os.stat(entry_path)
                contents.append({
                    "name": entry + ("/" if is_dir else ""),
                    "type": "directory" if is_dir else "file",
                    "size_bytes": stats.st_size if not is_dir else None,
                    "modified": stats.st_mtime,
                })
            except Exception:
                # If we can't get stats, just add basic info
                contents.append({"name": entry + ("/" if is_dir else ""), "type": "directory" if is_dir else "file"})

        # Sort directories first, then files, both alphabetically
        contents.sort(key=lambda x: (0 if x["type"] == "directory" else 1, x["name"]))

        return {"path": path, "contents": contents, "total_entries": len(contents)}
    except Exception as e:
        return {"error": f"Error listing directory: {str(e)}", "path": path}
