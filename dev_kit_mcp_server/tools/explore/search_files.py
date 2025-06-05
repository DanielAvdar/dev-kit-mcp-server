"""Module for searching files by regex pattern."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...core import AsyncOperation


@dataclass
class SearchFilesOperation(AsyncOperation):
    """Class to search for files by regex pattern in the project directory."""

    name = "search_files"

    def _search_files(self, pattern: str, root: Optional[str] = None, max_chars: int = 2000) -> Dict[str, Any]:
        """Search for files matching a regex pattern.

        Args:
            pattern: Regex pattern to match against file names
            root: Root directory to search from (optional, defaults to root_dir)
            max_chars: Maximum characters to return in output

        Returns:
            Dictionary with search results

        Raises:
            ValueError: If pattern is invalid regex or root path is invalid

        """
        # Validate regex pattern
        try:
            compiled_pattern = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {pattern}. Error: {e}") from e

        # Determine search root
        if root is None:
            search_root = self._root_path
        else:
            # Validate that the root path is within the project root directory
            abs_root = self._validate_path_in_root(self._root_path, root)
            search_root = Path(abs_root)
            if not search_root.exists():
                raise ValueError(f"Root path does not exist: {root}")
            if not search_root.is_dir():
                raise ValueError(f"Root path is not a directory: {root}")

        # Search for matching files
        matching_files: List[str] = []
        total_files_scanned = 0

        try:
            for file_path in search_root.rglob("*"):
                total_files_scanned += 1
                if file_path.is_file() and compiled_pattern.search(file_path.name):
                    # Get relative path from the project root
                    try:
                        relative_path = file_path.relative_to(self._root_path)
                        matching_files.append(str(relative_path))
                    except ValueError:
                        # File is outside root directory, use absolute path
                        matching_files.append(str(file_path))

        except (OSError, PermissionError) as e:
            raise ValueError(f"Error accessing files in directory: {e}") from e

        # Prepare output
        content_lines = [f"Files matching pattern '{pattern}':", ""]
        for file_path in matching_files:
            content_lines.append(f"  {file_path}")

        if not matching_files:
            content_lines.append("  No files found")

        content = "\n".join(content_lines)
        total_chars = len(content)
        truncated = total_chars > max_chars

        if truncated:
            content = content[:max_chars]

        return {
            "content": content,
            "total_chars": total_chars,
            "truncated": truncated,
            "matches_found": len(matching_files),
            "files_scanned": total_files_scanned,
            "pattern": pattern,
            "search_root": str(search_root.relative_to(self._root_path)) if search_root != self._root_path else ".",
        }

    async def __call__(self, pattern: str, root: Optional[str] = None, max_chars: int = 2000) -> Dict[str, Any]:
        """Search for files by regex pattern in the project directory.

        Args:
            pattern: Regex pattern to match against file names (required)
            root: Root directory to search from (optional, defaults to project root)
            max_chars: Maximum characters to return in output (optional, default 2000)

        Returns:
            A dictionary containing the search results and metadata

        """
        try:
            result = self._search_files(pattern, root, max_chars)
            return {
                "status": "success",
                "message": f"File search completed. Found {result['matches_found']} matches.",
                **result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"File search failed: {str(e)}",
                "error": str(e),
                "pattern": pattern,
                "root": root,
            }
