"""Tool for searching text in files."""

import glob
import os
import re
from typing import Any, Dict, Optional, cast

from fastmcp import Context

from ..utils import filter_binary_files


def grep_search(
    query: str, include_pattern: Optional[str] = None, is_regexp: bool = False, ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """Search for text in files.

    Args:
        query: The text pattern to search for
        include_pattern: Optional glob pattern to limit which files to search
        is_regexp: Whether the query is a regular expression
        ctx: Optional MCP context

    Returns:
        Dictionary containing search results

    """
    if ctx:
        ctx.info(
            f"Searching for text: {query}"
            + (f" with pattern: {include_pattern}" if include_pattern else "")
            + (" (regexp)" if is_regexp else "")
        )

    workspace_root = os.getcwd()
    results = []

    # Prepare file list to search
    file_paths = []
    if include_pattern:
        # Convert to absolute path if it's relative
        if not os.path.isabs(include_pattern):
            search_pattern = os.path.join(workspace_root, include_pattern)
        else:
            search_pattern = include_pattern

        file_paths = glob.glob(search_pattern, recursive=True)
    else:
        # If no include pattern, search all text files
        for root, _, files in os.walk(workspace_root):
            for file in files:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)

    # Filter out binary files
    file_paths = filter_binary_files(file_paths)

    # Prepare search pattern
    if is_regexp:
        try:
            pattern = re.compile(query)
        except re.error:
            # Fall back to literal search if regexp is invalid
            pattern = re.compile(re.escape(query))
            if ctx:
                ctx.warning("Invalid regular expression, falling back to literal search.")
    else:
        pattern = re.compile(re.escape(query))

    # Search in files
    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            file_matches = []
            for i, line in enumerate(lines):
                if pattern.search(line):
                    file_matches.append({"line": i + 1, "content": line.strip()})

            if file_matches:
                relative_path = os.path.relpath(file_path, workspace_root)
                results.append({
                    "file_path": relative_path,
                    "matches": file_matches[:10],  # Limit matches per file
                    "total_matches": len(file_matches),
                })
        except UnicodeDecodeError:
            # Skip files that can't be decoded as text
            continue
        except Exception as e:
            if ctx:
                ctx.warning(f"Error processing file {file_path}: {str(e)}")

    # Sort by number of matches
    results.sort(key=lambda x: cast(int, x["total_matches"]), reverse=True)

    # Limit results
    limited_results = results[:20]

    return {
        "query": query,
        "is_regexp": is_regexp,
        "include_pattern": include_pattern,
        "results": limited_results,
        "total_files": len(results),
        "limited": len(results) > len(limited_results),
    }
